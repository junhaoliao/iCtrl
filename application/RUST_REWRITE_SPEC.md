# iCtrl Server - Rust Rewrite Specification

This document provides a comprehensive specification for rewriting the iCtrl server from Python to Rust, including library choices, architecture mapping, and implementation details.

## Table of Contents

1. [Overview](#overview)
2. [Rust Library Stack](#rust-library-stack)
3. [Architecture](#architecture)
4. [Configuration and Environment](#configuration-and-environment)
5. [Profile Management](#profile-management)
6. [SSH Connection Management](#ssh-connection-management)
7. [Terminal Feature](#terminal-feature)
8. [VNC Feature](#vnc-feature)
9. [SFTP Feature](#sftp-feature)
10. [Audio Feature](#audio-feature)
11. [User Authentication](#user-authentication)
12. [Utility Functions](#utility-functions)
13. [Error Codes and Constants](#error-codes-and-constants)
14. [Migration Notes](#migration-notes)

---

## Overview

iCtrl is a remote access application providing:

- **SSH Session Management**: Store and manage multiple SSH sessions
- **Terminal Access**: Web-based terminal via WebSocket
- **VNC Remote Desktop**: noVNC-compatible remote desktop
- **SFTP File Transfer**: File browsing, upload, download, and management
- **Audio Streaming**: Remote audio capture and streaming

### Current Python Stack

| Component                  | Python Library                |
|----------------------------|-------------------------------|
| HTTP API                   | Flask                         |
| SSH/SFTP                   | Paramiko                      |
| WebSocket (Terminal/Audio) | SimpleWebSocketServer         |
| VNC Proxy                  | websockify                    |
| Database ORM               | SQLAlchemy + Flask-SQLAlchemy |
| Password Hashing           | bcrypt                        |
| Key Encryption             | cryptography (Fernet)         |

---

## Rust Library Stack

### Recommended Dependencies

```toml
[dependencies]
# === Web Framework ===
axum = { version = "0.7", features = ["ws", "multipart"] }
tokio = { version = "1", features = ["full"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "fs", "trace"] }
hyper = { version = "1", features = ["full"] }

# === SSH/SFTP ===
russh = "0.45"
russh-sftp = "2.0"
russh-keys = "0.45"

# === WebSocket ===
tokio-tungstenite = { version = "0.24", features = ["rustls-tls-native-roots"] }
futures-util = "0.3"

# === Database ===
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres", "uuid", "chrono"] }

# === Authentication & Crypto ===
argon2 = "0.5"                    # Password hashing (modern alternative to bcrypt)
aes-gcm = "0.10"                  # Authenticated encryption for private keys
pbkdf2 = { version = "0.12", features = ["simple"] }
sha2 = "0.10"
rand = "0.8"

# === Serialization ===
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# === Utilities ===
uuid = { version = "1", features = ["v4", "serde"] }
async-zip = { version = "0.0.17", features = ["tokio", "deflate"] }
base64 = "0.22"
flate2 = "1.0"                    # zlib compression for audio
chrono = { version = "0.4", features = ["serde"] }
thiserror = "1"                   # Error types
anyhow = "1"                      # Error handling
tracing = "0.1"                   # Logging
tracing-subscriber = "0.3"
directories = "5"                 # Cross-platform paths
lettre = { version = "0.11", features = ["tokio1-native-tls"] }  # Email
des = "0.8"                       # VNC password DES encryption
```

### Library Comparison

| Purpose              | Python                | Rust                                 | Notes                                            |
|----------------------|-----------------------|--------------------------------------|--------------------------------------------------|
| **HTTP Framework**   | Flask                 | **Axum**                             | Async-first, Tokio ecosystem, built-in WebSocket |
| **SSH Client**       | Paramiko              | **russh**                            | Pure Rust, async, actively maintained            |
| **SFTP**             | Paramiko              | **russh-sftp**                       | Works with russh                                 |
| **WebSocket Server** | SimpleWebSocketServer | **Axum WS / tokio-tungstenite**      | Unified with HTTP server                         |
| **VNC Proxy**        | websockify            | **Custom (tokio-tungstenite + TCP)** | ~50 lines, better auth integration               |
| **Database**         | SQLAlchemy            | **SQLx**                             | Compile-time checked queries                     |
| **Password Hash**    | bcrypt                | **Argon2**                           | More secure, recommended for new projects        |
| **Key Encryption**   | Fernet (AES-128-CBC)  | **AES-256-GCM**                      | Authenticated encryption                         |
| **ZIP Streaming**    | zipstream             | **async-zip**                        | Async streaming                                  |

### Alternative Library Options

#### Web Framework Alternatives

| Library                | Pros                                                  | Cons                      |
|------------------------|-------------------------------------------------------|---------------------------|
| **Axum** (Recommended) | Tokio native, gentle learning curve, great WS support | -                         |
| Actix Web              | Highest performance, mature                           | Steeper learning curve    |
| Rocket                 | Most Flask-like, intuitive                            | Slower, less async-native |
| Poem                   | Lightweight, OpenAPI support                          | Smaller ecosystem         |

#### SSH Library Alternatives

| Library                 | Pros                                          | Cons                  |
|-------------------------|-----------------------------------------------|-----------------------|
| **russh** (Recommended) | Pure Rust, async, client+server, SFTP support | -                     |
| async-ssh2-tokio        | Simpler high-level API                        | Built on russh anyway |
| ssh2 (libssh2)          | Mature C library bindings                     | Sync, not pure Rust   |

#### SFTP Alternatives

| Library                      | Pros                   | Cons                        |
|------------------------------|------------------------|-----------------------------|
| **russh-sftp** (Recommended) | Integrates with russh  | -                           |
| openssh-sftp-client          | Pure Rust, cancel-safe | Requires separate SSH setup |

---

## Architecture

### Application Modes

The application operates in two distinct modes:

#### 1. Local Mode (Desktop App)

- Profile stored locally in JSON file
- SSH private keys stored as files
- Authentication via `LOCAL_AUTH_KEY` Bearer token
- No database required

#### 2. Database Mode (Web App)

- Profile stored in PostgreSQL database
- SSH private keys encrypted and stored in DB
- Session-based authentication with cookies
- Keys encrypted using password-derived key

### Rust Project Structure

```
ictrl-server/
├── Cargo.toml
├── src/
│   ├── main.rs              # Entry point, server setup
│   ├── lib.rs               # Library root
│   ├── config.rs            # Configuration and environment
│   ├── error.rs             # Error types (thiserror)
│   ├── codes.rs             # Error codes and step enums
│   │
│   ├── routes/
│   │   ├── mod.rs           # Route module
│   │   ├── common.rs        # Session management, profiles, exec
│   │   ├── user.rs          # User auth (register, login, activate)
│   │   ├── term.rs          # Terminal endpoints
│   │   ├── vnc.rs           # VNC endpoints
│   │   ├── sftp.rs          # SFTP endpoints
│   │   └── audio.rs         # Audio endpoints
│   │
│   ├── features/
│   │   ├── mod.rs           # Features module
│   │   ├── connection.rs    # Base SSH connection
│   │   ├── term.rs          # Terminal WebSocket handler
│   │   ├── vnc.rs           # VNC session management
│   │   ├── sftp.rs          # SFTP operations
│   │   ├── audio.rs         # Audio streaming
│   │   └── vncpasswd.rs     # VNC password encryption
│   │
│   ├── profile/
│   │   ├── mod.rs           # Profile trait
│   │   ├── local.rs         # File-based profile
│   │   └── database.rs      # PostgreSQL profile
│   │
│   └── utils.rs             # Utility functions
│
├── migrations/              # SQLx migrations
└── resources/
    └── activation_email.html
```

### Rust Architectural Patterns

**AppState** (shared via `Arc<AppState>` in Axum extractors):

- `profile: Arc<dyn Profile + Send + Sync>` - Profile backend implementation
- `term_connections: Arc<RwLock<HashMap<String, TermConnection>>>` - Active terminal sessions
- `audio_connections: Arc<RwLock<HashMap<String, AudioConnection>>>` - Active audio streams
- `config: Config` - Server configuration

**Profile trait** (replaces Python ABC): Defines async methods for session management, user auth, and profile storage. Implementations: `LocalProfile` (JSON file) and `DBProfile` (PostgreSQL).

---

## Configuration and Environment

### Command Line Arguments

Use `clap` crate with `#[derive(Parser)]`:

- `-p, --port` (default: 5000): Server port number
- `-a, --auth-key` (default: ""): Bearer token for local mode API auth

### Environment Variables

| Variable         | Description                  | Required               | Mode  |
|------------------|------------------------------|------------------------|-------|
| `SECRET_KEY`     | Session secret key           | No (random if not set) | Both  |
| `LOCAL_AUTH_KEY` | Bearer token for API auth    | Set via CLI            | Local |
| `DATABASE_URL`   | PostgreSQL connection string | Yes (triggers DB mode) | DB    |
| `SSL_CERT_PATH`  | Path to SSL certificate      | No                     | Both  |
| `SSL_KEY_PATH`   | Path to SSL private key      | No                     | Both  |
| `SMTP_SERVER`    | SMTP server address          | Yes (for email)        | DB    |
| `SMTP_PORT`      | SMTP server port             | Yes (for email)        | DB    |
| `SMTP_EMAIL`     | Sender email address         | Yes (for email)        | DB    |
| `SMTP_PASSWORD`  | Sender email password        | Yes (for email)        | DB    |

### Profile Paths (Local Mode)

Use `directories` crate `ProjectDirs::from("", "", "ictrl")` → `data_local_dir()`:

- Windows: `%LOCALAPPDATA%\ictrl\`
- macOS: `~/Library/Application Support/ictrl/`
- Linux: `~/.local/share/ictrl/`

Fallback: `.ictrl/` in current directory.

### Logging Configuration

Use `tracing_subscriber` with `EnvFilter` for log level control via `RUST_LOG` environment variable.

---

## Profile Management

### Profile Data Structure

**ProfileData**: `version: u32`, `sessions: HashMap<Uuid, SessionInfo>`

**SessionInfo**: `host: String`, `username: String`, `nickname: Option<String>`, `vnc_credentials: Option<String>` (base64)

Both derive `Serialize, Deserialize` with `#[serde(skip_serializing_if = "Option::is_none")]` for optional fields.

### Profile Trait

`#[async_trait] pub trait Profile: Send + Sync` with methods:

| Method                                       | Description                                  |
|----------------------------------------------|----------------------------------------------|
| `login(username, password)`                  | Authenticate user, return `User`             |
| `logout()`                                   | End session                                  |
| `query()`                                    | Get full `ProfileData`                       |
| `add_user(username, password, email)`        | Create account (DB mode)                     |
| `activate_user(user_id, code)`               | Verify email activation code                 |
| `get_user()`                                 | Get current authenticated user               |
| `add_session(host, username, conn)`          | Create new SSH session, optionally save keys |
| `save_profile()`                             | Persist to file/DB                           |
| `delete_session(session_id)`                 | Remove session and keys                      |
| `change_host(session_id, new_host)`          | Update session host                          |
| `get_session_info(session_id)`               | Get session details                          |
| `set_session_nickname(session_id, nickname)` | Set/remove nickname (max 8 chars)            |
| `set/get_session_vnc_credentials(...)`       | Store/retrieve VNC credentials               |
| `send_activation_email(username)`            | Resend verification email                    |

### Database Schema (SQLx Migrations)

```sql
-- migrations/001_initial.sql
CREATE SCHEMA IF NOT EXISTS ictrl;

CREATE TABLE ictrl.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Argon2 hash
    email VARCHAR(255) UNIQUE NOT NULL,
    activation_type INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ictrl.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES ictrl.users(id) ON DELETE CASCADE NOT NULL,
    host VARCHAR(255) NOT NULL,
    nickname VARCHAR(8),
    username VARCHAR(255) NOT NULL,
    private_key_encrypted TEXT,  -- AES-256-GCM encrypted
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ictrl.vnc_credentials (
    session_id UUID REFERENCES ictrl.sessions(id) ON DELETE CASCADE PRIMARY KEY,
    credentials_encrypted TEXT NOT NULL  -- base64 encoded, encrypted JSON
);

CREATE INDEX idx_sessions_user_id ON ictrl.sessions(user_id);
```

### Password Hashing (Argon2)

Use `argon2` crate with default Argon2id parameters:

- `hash_password(password) -> Result<String>`: Generate random salt, hash with Argon2, return PHC string format
- `verify_password(password, hash) -> Result<bool>`: Parse PHC hash, verify against input

### Private Key Encryption (AES-256-GCM)

Use `aes-gcm` and `pbkdf2` crates:

- **Key derivation**: PBKDF2-HMAC-SHA256 with 1,000,000 iterations and fixed salt
- **Encryption format**: `[12-byte nonce][ciphertext][16-byte auth tag]`
- `derive_key(password) -> [u8; 32]`: Derive 256-bit key from password
- `encrypt_private_key(key, plaintext) -> Vec<u8>`: Random nonce, AES-256-GCM encrypt, prepend nonce
- `decrypt_private_key(key, data) -> Vec<u8>`: Split nonce/ciphertext, decrypt

### Validation Rules

| Function            | Rule                                                                |
|---------------------|---------------------------------------------------------------------|
| `validate_username` | Must match `^[A-Za-z0-9_-]+$`                                       |
| `validate_email`    | Must match standard email regex                                     |
| `validate_password` | 6-32 chars, must contain: digit, uppercase, lowercase, special char |
| `validate_nickname` | Max 8 characters                                                    |

---

## SSH Connection Management

### Connection Struct

Use `russh` crate for async SSH client. Connection holds:

- `session`: SSH session handle (wrapped in `Arc<Mutex<>>`)
- `host`, `username`: Connection info
- `jump_session`: Optional jump host session for ECF machines

Implement `client::Handler` trait with auto-accept for server keys (like Paramiko's `AutoAddPolicy`).

### Connection Methods

| Method                                 | Description                                                             |
|----------------------------------------|-------------------------------------------------------------------------|
| `connect(host, username, auth)`        | Connect with password or private key. Auto-detect jump host for ECF.    |
| `needs_jump_host(host)`                | Returns true for `ecf.utoronto.ca`/`ecf.toronto.edu` (except `remote*`) |
| `exec_command(command)`                | Execute command, return `(exit_status, stdout, stderr)`                 |
| `generate_keypair()`                   | Generate RSA-3072 keypair with SHA256 signature                         |
| `save_keys(keypair, comment)`          | Append public key to remote `~/.ssh/authorized_keys`                    |
| `is_eecg()` / `is_ecf()` / `is_uoft()` | Check host domain                                                       |
| `is_load_high()`                       | Parse `uptime` output, return true if load > 1.0 or many other users    |

### AuthMethod Enum

- `Password(String)` - Password authentication
- `PrivateKey(KeyPair)` - Public key authentication

### Port Forwarding

`port_forward(local_port, remote_port)`: Spawns a Tokio task that binds to `127.0.0.1:local_port`, accepts connections, and for each connection opens an SSH `direct-tcpip` channel to `127.0.0.1:remote_port`. Implements bidirectional data forwarding between the TCP stream and SSH channel using `tokio::select!`.

---

## Terminal Feature

### TermConnection Struct

Holds `id: String` and `channel: russh::Channel<ClientHandler>`. Stored in `AppState.term_connections` (a `RwLock<HashMap<String, TermConnection>>`).

### WebSocket Handler

`handle_terminal_ws(ws, term_id, state)`:

1. Look up `TermConnection` by `term_id`
2. Split WebSocket into sender/receiver
3. Spawn two concurrent tasks:
   - **SSH→WS**: Loop on `channel.wait()`, forward `ChannelMsg::Data` as `Message::Binary`
   - **WS→SSH**: Loop on `ws_receiver.next()`, forward binary/text data via `channel.data()`
4. Use `tokio::select!` to wait for either task to complete
5. Remove connection from state on cleanup

### Routes

| Route                   | Method | Handler           | Description                                                        |
|-------------------------|--------|-------------------|--------------------------------------------------------------------|
| `/terminal`             | POST   | `start_terminal`  | Connect SSH, open PTY, stream step codes, return `{port, term_id}` |
| `/terminal_resize`      | PATCH  | `resize_terminal` | Send `pty_change_size` to SSH channel                              |
| `/terminal/ws/:term_id` | GET    | `terminal_ws`     | WebSocket upgrade for terminal I/O                                 |

### Streaming Response Protocol

`start_terminal` returns a streaming response with single-byte step codes:

1. `TermStep::SshAuth (0)` - Starting SSH authentication
2. `TermStep::CheckLoad (1)` - Checking server load (UofT only)
3. `TermStep::LaunchShell (2)` - Opening PTY with `xterm-256color`, 80x24
4. `TermStep::Done (31)` - Success, followed by JSON `{port, term_id}`
5. On error: `SshError::*` code (200-204)

---

## VNC Feature

### VNC Password Encryption (DES)

Use `des` crate with fixed key `[232, 74, 214, 96, 196, 114, 26, 224]` (standard VNC obfuscation):

- `decrypt_vnc_password(encrypted: &[u8]) -> String`: DES decrypt first 8 bytes, strip null padding
- `encrypt_vnc_password(password: &str) -> Vec<u8>`: Pad to 8 bytes, DES encrypt

### VncConnection Methods

| Method                       | Description                                                                                               |
|------------------------------|-----------------------------------------------------------------------------------------------------------|
| `get_vnc_password()`         | Run `hexdump ~/.vnc/passwd`, hex-decode, DES-decrypt                                                      |
| `check_5900_open()`          | Check if port 5900 is listening via `ss` (Linux) or `netstat` (macOS)                                     |
| `launch_vnc()`               | List existing servers via `vncserver -list`; if ≠1 server, kill all and relaunch; return 5900+display_num |
| `create_tunnel(remote_port)` | Find two free local ports, SSH port-forward to VNC, spawn WebSocket proxy, return WS port                 |

**EECG Workaround**: If `is_eecg()`, launch `xvfb-run -a xterm` in background for virtual framebuffer.

### VNC WebSocket Proxy

`vnc_ws_proxy(ws_port, vnc_port)`:

1. Bind TCP listener on `127.0.0.1:ws_port`
2. Accept single connection, upgrade to WebSocket via `tokio_tungstenite`
3. Connect to `127.0.0.1:vnc_port` (local end of SSH tunnel)
4. Bidirectional forwarding: WS binary ↔ TCP with 64KB buffer
5. Use `tokio::select!` for concurrent read/write

---

## SFTP Feature

### SftpConnection

Created via `SftpConnection::new(connection)`: Opens SSH session channel, requests "sftp" subsystem, wraps in `russh_sftp::SftpSession`.

### Methods

| Method                         | Description                                                                    |
|--------------------------------|--------------------------------------------------------------------------------|
| `ls(path)`                     | Canonicalize path (or "." if empty), `read_dir`, return `(cwd, Vec<FileInfo>)` |
| `download_stream(path)`        | Open file, yield 32KB chunks via `async_stream` until EOF                      |
| `upload(path, data)`           | Create file, write 1MB chunks from `AsyncRead` source                          |
| `rename(cwd, old, new)`        | SFTP rename operation                                                          |
| `chmod(path, mode, recursive)` | Execute `chmod [-R] MODE PATH` via SSH                                         |
| `mkdir(cwd, name)`             | Execute `cd CWD && mkdir NAME` via SSH                                         |
| `rm(cwd, files)`               | Execute `rm -rf` in batches of 50 files via SSH                                |

### FileInfo Struct

Fields: `id: String` (filename), `mode: u32`, `size: u64`, `atime: u32`, `mtime: u32`

### ZIP Streaming

`create_zip_stream(sftp, cwd, files)`: Uses `async-zip` with Deflate compression. Recursively adds files/directories via `add_to_zip_recursive()` which:

- For directories: Recursively process children
- For regular files: Create ZIP entry, stream file content in chunks

---

## Audio Feature

### AudioConnection Struct

Fields: `id: String`, `connection: Connection`, `remote_port: u16`, `module_id: Option<u32>`

`launch()`: Request reverse port forward via SSH (`request_port_forward("127.0.0.1", 0)`), generate UUID for `id`.

### WebSocket Handler

`handle_audio_ws(ws, audio_id, state)`:

1. Look up `AudioConnection` by `audio_id`
2. Create PulseAudio null sink named `remote_{username}` via `pactl load-module module-null-sink`
3. Launch `ffmpeg` in background: capture from sink monitor, output PCM s16le stereo 44.1kHz to reverse-forwarded TCP port
4. Wait 4 seconds for ffmpeg to connect
5. Accept port forward channel, buffer 20KB of audio data
6. Compress with zlib (level 4), send as WebSocket binary message
7. On disconnect: unload PulseAudio module, remove from state

---

## User Authentication

### Local Mode Middleware

`local_auth_middleware(state, request, next)`:

- If `local_auth_key` is empty, pass through (no auth required)
- Otherwise, extract `Authorization` header, verify `Bearer {token}` matches `local_auth_key`
- Return `403 FORBIDDEN` on mismatch

### Database Mode Login

`login(state, jar, req)`:

1. Lowercase username, query `ictrl.users` table
2. Return `WrongUsername` if not found
3. Return `NotActivated` if `activation_type == 0`
4. Verify password with Argon2, return `WrongPassword` on mismatch
5. Derive encryption key from password (for private key decryption)
6. Create session with UUID, store `user_id` and `encryption_key` in state
7. Set `session_id` cookie (HttpOnly, Secure, SameSite=Strict)

---

## Utility Functions

| Function                                | Description                                  |
|-----------------------------------------|----------------------------------------------|
| `find_free_port()`                      | Bind to `127.0.0.1:0`, return assigned port  |
| `int_to_byte(num)`                      | Convert `u8` to single-byte `Bytes`          |
| `parse_headers(str)`                    | Parse `Key: Value\n` lines into `HashMap`    |
| `send_email(to, subject, body, config)` | Send HTML email via `lettre` + SMTP with TLS |

---

## Error Codes and Constants

All enums use `#[repr(u8)]` for single-byte wire representation.

### ConnectionType

`General=1`, `Vnc=2`, `Term=3`, `Sftp=4`, `Audio=5`

### VncStep

`SshAuth=0`, `CheckLoad=1`, `ParsePasswd=2`, `LaunchVnc=3`, `CreateTunnel=4`, `Done=31`

### TermStep

`SshAuth=0`, `CheckLoad=1`, `LaunchShell=2`, `Done=31`

### VncError

`General=120`, `PasswdMissing=121`, `QuotaExceeded=122`

### SshError

`General=200`, `HostUnreachable=201`, `AuthMissing=202`, `AuthWrong=203`, `OverLoaded=204`

### Error Mapping

`map_ssh_error(error_str)` returns:

- `HostUnreachable` for: `[Errno 60/64/51]`, "timed out", "Connection refused"
- `AuthWrong` for: "encountered RSA key, expected OPENSSH key"
- `General` otherwise

---

## Migration Notes

### Key Differences from Python

| Aspect                | Python                    | Rust                             |
|-----------------------|---------------------------|----------------------------------|
| **Async Model**       | Threading + async (mixed) | Fully async with Tokio           |
| **Error Handling**    | Exceptions                | `Result<T, E>` with `?` operator |
| **Memory Management** | GC, `__del__`             | RAII, `Drop` trait               |
| **Shared State**      | Global variables          | `Arc<RwLock<T>>`                 |
| **Streaming**         | Generators                | `async_stream` / `Stream` trait  |
| **Type System**       | Dynamic                   | Static, compile-time checked     |

### Implementation Priorities

1. **Phase 1: Core Infrastructure**
   - Axum server setup with routes
   - Configuration and environment handling
   - Error types and codes

2. **Phase 2: Profile Management**
   - LocalProfile (JSON file)
   - Database schema and migrations
   - DBProfile with SQLx

3. **Phase 3: SSH/Connection**
   - Basic SSH connection with russh
   - Key generation and storage
   - Port forwarding

4. **Phase 4: Features**
   - Terminal WebSocket
   - SFTP operations
   - VNC proxy
   - Audio streaming

5. **Phase 5: Authentication**
   - Local auth middleware
   - Session-based auth for DB mode
   - Password hashing and key encryption

### Testing Strategy

Use `#[tokio::test]` for async tests. Key test areas:

- **Validation**: Password rules (length, character requirements), username format, email format
- **Crypto**: VNC password encrypt/decrypt roundtrip, Argon2 hash/verify, AES-GCM encrypt/decrypt
- **Connection**: Mock SSH sessions for unit tests, Docker-based integration tests for real SSH
- **API**: Axum test utilities with `TestClient` for route testing

### Performance Considerations

1. **Connection Pooling**: Consider connection reuse for frequent SSH operations
2. **Buffer Sizes**: Tune SFTP/audio buffer sizes for performance
3. **Concurrent Connections**: Tokio handles this well, but monitor resource usage
4. **Memory**: Streaming prevents loading large files into memory

### Security Improvements Over Python Version

1. **Argon2** instead of bcrypt (memory-hard, more resistant to GPU attacks)
2. **AES-256-GCM** instead of Fernet (authenticated encryption, 256-bit key)
3. **Compile-time SQL validation** with SQLx
4. **Type safety** prevents many runtime errors
5. **No GIL** - true parallelism for better resource utilization
