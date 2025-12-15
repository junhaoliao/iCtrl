# iCtrl Frontend Rewrite Specification

This document specifies the behaviors and API contracts that must be preserved when rewriting the iCtrl frontend from React + Material-UI to TypeScript + Ant Design.

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [API Contracts](#api-contracts)
3. [WebSocket Protocols](#websocket-protocols)
4. [Error and Step Codes](#error-and-step-codes)
5. [Feature Specifications](#feature-specifications)
6. [BDD Playwright Test Scenarios](#bdd-playwright-test-scenarios)
7. [Utility Functions](#utility-functions)

---

## Technology Stack

### Current Stack (to be replaced)

- **Framework**: React 18 (Class Components)
- **UI Library**: Material-UI (MUI) v5
- **HTTP Client**: Axios
- **Terminal**: xterm.js + xterm-addon-attach + xterm-addon-fit
- **VNC**: noVNC (@novnc/novnc)
- **Audio**: PCMPlayer (custom) + pako (zlib decompression) + WebSocket
- **Build Tool**: Create React App
- **Styling**: CSS + MUI sx prop

### Target Stack

- **Framework**: React 18 (Functional Components + Hooks) or alternative
- **Language**: TypeScript
- **UI Library**: Ant Design v5
- **HTTP Client**: Axios or fetch API
- **Terminal**: xterm.js (same)
- **VNC**: noVNC (same)
- **Audio**: WebRTC with Zstandard (zstd) compression (NEW - replacing WebSocket + zlib)
- **Build Tool**: Vite or similar
- **Styling**: CSS Modules or Tailwind CSS

---

## API Contracts

### Auto-Generated TypeScript Types

TypeScript type definitions are **NOT manually maintained** in the frontend. Instead, they are auto-generated from the backend OpenAPI specification:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Rust Backend (Axum + utoipa)                                           │
│                                                                         │
│  #[derive(ToSchema, Serialize, Deserialize)]                           │
│  struct LoginRequest {                                                  │
│      username: String,                                                  │
│      password: String,                                                  │
│  }                                                                      │
│                                                                         │
│  #[utoipa::path(post, path = "/api/login", request_body = LoginRequest)]│
│  async fn login(...) { ... }                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        GET /api/openapi.json
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  openapi-typescript                                                     │
│                                                                         │
│  $ npx openapi-typescript http://localhost:5000/api/openapi.json \     │
│        --output src/api/schema.d.ts                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Generated: src/api/schema.d.ts                                         │
│                                                                         │
│  export interface components {                                          │
│    schemas: {                                                           │
│      LoginRequest: {                                                    │
│        username: string;                                                │
│        password: string;                                                │
│      };                                                                 │
│      // ... all other types auto-generated                              │
│    };                                                                   │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Build Pipeline Integration

package.json
```json
{
  "scripts": {
    "generate:api": "openapi-typescript $API_URL/api/openapi.json -o src/api/schema.d.ts",
    "prebuild": "npm run generate:api",
    "build": "vite build"
  }
}
```

#### Type-Safe API Client Usage

```typescript
// src/api/client.ts
import createClient from 'openapi-fetch';
import type { paths } from './schema';

const client = createClient<paths>({ baseUrl: '' });

// Fully typed request/response
const { data, error } = await client.POST('/api/login', {
  body: { username: 'user', password: 'pass' }  // Type-checked!
});
// data is typed as LoginResponse
// error is typed as error responses
```

### API Endpoint Reference

The following endpoints must be defined in the Rust backend with utoipa annotations. This section documents the **semantic behavior** rather than TypeScript types (which are auto-generated).

#### Authentication (DB Mode Only)

| Method | Endpoint                 | Description                                    |
|--------|--------------------------|------------------------------------------------|
| POST   | `/api/login`             | Authenticate user, set session cookie          |
| POST   | `/api/register`          | Create new user account, send activation email |
| POST   | `/api/resend_activation` | Resend activation email                        |
| GET    | `/api/userid`            | Get current user ID (401 if not logged in)     |
| POST   | `/api/logout`            | Clear session                                  |

**Error codes for login:**

- `ACCOUNT_WRONG_PASSWORD` - Invalid password
- `ACCOUNT_WRONG_USERNAME` - User not found
- `ACCOUNT_NOT_ACTIVATED` - Email not verified

**Error codes for register:**

- `ACCOUNT_DUPLICATE_USERNAME` - Username taken
- `ACCOUNT_DUPLICATE_EMAIL` - Email already registered

#### Session Management

| Method | Endpoint       | Description                       |
|--------|----------------|-----------------------------------|
| GET    | `/api/profile` | Get all sessions for current user |
| POST   | `/api/session` | Add new SSH session (saves keys)  |
| PATCH  | `/api/session` | Update host or nickname           |
| DELETE | `/api/session` | Delete session and SSH keys       |

#### Terminal

| Method | Endpoint               | Description                             |
|--------|------------------------|-----------------------------------------|
| POST   | `/api/terminal`        | **Streaming** - Connect to SSH terminal |
| PATCH  | `/api/terminal_resize` | Resize terminal (cols, rows)            |

**Streaming response format:** `[STEP_CODES...] | DONE(31) | JSON_PAYLOAD`

#### VNC

| Method | Endpoint               | Description                            |
|--------|------------------------|----------------------------------------|
| POST   | `/api/vnc`             | **Streaming** - Connect to VNC session |
| POST   | `/api/vncpasswd`       | Set VNC password for session           |
| POST   | `/api/vnc_reset`       | Kill existing VNC server               |
| PUT    | `/api/vnc_credentials` | Save VNC credentials                   |

#### Audio (WebSocket - Legacy)

| Method | Endpoint     | Description                            |
|--------|--------------|----------------------------------------|
| POST   | `/api/audio` | Get WebSocket port for audio streaming |

#### Audio (WebRTC - New)

| Method | Endpoint                | Description                   |
|--------|-------------------------|-------------------------------|
| POST   | `/api/audio_rtc`        | Get SDP offer and ICE servers |
| POST   | `/api/audio_rtc/answer` | Send SDP answer               |
| POST   | `/api/audio_rtc/ice`    | Send ICE candidate            |

#### SFTP

| Method | Endpoint                        | Description                                |
|--------|---------------------------------|--------------------------------------------|
| GET    | `/api/sftp_ls/{session_id}`     | List directory contents                    |
| GET    | `/api/sftp_dl/{session_id}`     | Download file(s) - ZIP for multiple        |
| POST   | `/api/sftp_ul/{session_id}`     | Upload file (binary body, path in headers) |
| PATCH  | `/api/sftp_rename/{session_id}` | Rename file/directory                      |
| POST   | `/api/sftp_rm/{session_id}`     | Delete files/directories                   |
| PATCH  | `/api/sftp_chmod/{session_id}`  | Change permissions                         |

#### Utility

| Method | Endpoint             | Description                       |
|--------|----------------------|-----------------------------------|
| POST   | `/api/exec_blocking` | Execute command and return stdout |

---

## WebSocket Protocols

### Terminal WebSocket

```
URL: wss://{host}:{port}/{term_id}
Protocol: xterm.js AttachAddon compatible
- Client sends: raw terminal input bytes
- Server sends: raw terminal output bytes
- On close: Display reconnection message
```

### VNC WebSocket

```
URL: wss://{host}:{port}
Protocol: noVNC RFB compatible
- Binary frames with RFB protocol messages
- Supports: scaling, resizing, clipboard sync
```

### Audio WebSocket (Current - to be deprecated)

```
URL: wss://{host}:{port}/{audio_id}
Protocol: Binary zlib-compressed PCM audio
- Format: s16le (signed 16-bit little-endian)
- Channels: 2 (stereo)
- Sample rate: 44100 Hz
- Client decompresses with pako.inflate()
- Feed to PCMPlayer
```

### Audio WebRTC (NEW - Target Implementation)

```
Protocol: WebRTC with DataChannel for compressed audio
- Signaling: Via existing HTTP API or WebSocket signaling endpoint
- Compression: Zstandard (zstd) - better compression ratio and speed than zlib
- Format: s16le (signed 16-bit little-endian)
- Channels: 2 (stereo)
- Sample rate: 44100 Hz

Benefits over WebSocket:
- Lower latency (UDP-based, no head-of-line blocking)
- NAT traversal via ICE/STUN/TURN
- Better suited for real-time audio streaming
- Potential for adaptive bitrate based on network conditions

Implementation Options:
1. DataChannel approach (recommended for compressed audio):
   - Use RTCDataChannel with binary mode
   - Client decompresses zstd frames with fzstd or zstd-wasm
   - Feed to PCMPlayer or Web Audio API

2. MediaStream approach (alternative):
   - Use RTCPeerConnection with audio track
   - Server encodes with Opus codec (built into WebRTC)
   - No manual decompression needed
   - Trade-off: Less control over compression, but simpler

Signaling Flow:
1. POST /api/audio_rtc -> Returns session info + offer SDP
2. Client creates RTCPeerConnection
3. Client sets remote description (offer)
4. Client creates answer SDP
5. POST /api/audio_rtc/answer -> Send answer SDP
6. ICE candidates exchanged via trickle ICE or bundled
7. DataChannel opens, audio frames flow
```

#### New Audio API Endpoints (WebRTC)

> **Note:** TypeScript interfaces below are for documentation only. Actual types are auto-generated from the Rust backend's utoipa/OpenAPI definitions via `openapi-typescript`.

##### POST /api/audio_rtc

- **Request:** `{ session_id: string }`
- **Response:** `{ audio_id: string, offer: RTCSessionDescriptionInit, ice_servers?: RTCIceServer[] }`

##### POST /api/audio_rtc/answer

- **Request:** `{ audio_id: string, answer: RTCSessionDescriptionInit }`
- **Response:** `200 OK`

##### POST /api/audio_rtc/ice

- **Request:** `{ audio_id: string, candidate: RTCIceCandidateInit }`
- **Response:** `200 OK`

---

## Error and Step Codes

### Step Codes (Progress Indicators)

**Terminal Steps**: `SSH_AUTH=0`, `CHECK_LOAD=1`, `LAUNCH_SHELL=2`, `DONE=31`

**VNC Steps**: `SSH_AUTH=0`, `CHECK_LOAD=1`, `PARSE_PASSWD=2`, `LAUNCH_VNC=3`, `CREATE_TUNNEL=4`, `DONE=31`

### Error Codes

**SSH Errors (200-299)**: `GENERAL=200`, `HOST_UNREACHABLE=201`, `AUTH_MISSING=202`, `AUTH_WRONG=203`, `OVER_LOADED=204`

**VNC Errors (120-129)**: `GENERAL=120`, `PASSWD_MISSING=121`, `QUOTA_EXCEEDED=122`

### Streaming Response Parsing

Parse streaming responses using `ReadableStreamDefaultReader`:

1. Read all chunks into byte array
2. Find `DONE (31)` marker index
3. Bytes before marker = step codes
4. Bytes after marker = JSON payload (decode with `TextDecoder`)

---

## Feature Specifications

### F1: Home Page / Login

#### Behaviors

1. **Auto-redirect**: If user is logged in (`GET /api/userid` returns 200), redirect to `/dashboard`
2. **Login tab**: Username + Password fields, submit calls `POST /api/login`
3. **Signup tab**: Username + Email + Password + Confirm Password fields
4. **Password validation** (signup only):
   - Length: 6-32 characters
   - Must contain: uppercase, lowercase, numeral, special symbol
   - Special symbols allowed: `!@#$%^&*()_+-=[]{}|;':\",./<>?`
5. **Error handling**:
   - Wrong password: Show "Forgot password" link
   - Unknown username: Show "Register" link
   - Not activated: Show "Resend activation" button
   - Duplicate username/email: Show appropriate warning
6. **Local storage**: Remember last username

### F2: Dashboard

#### Behaviors

1. **Session list**: Display all sessions from `GET /api/profile`
2. **Session card actions**:
   - Click avatar: Edit nickname (max 8 chars)
   - Double-click: Open VNC in new tab
   - Triple-click: Open Terminal in new tab
   - Right-click: Context menu
   - Icon buttons: VNC, Terminal, File Manager
3. **Change Machine** (only for .eecg.toronto.edu and .ecf.utoronto.ca hosts):
   - Show host list with load averages
   - Parse from `ruptime -a | grep up`
4. **Reset VNC**: Kill existing VNC server
5. **Delete session**: Remove session and SSH keys
6. **Add new session**: Host + Username + Password form

### F3: Terminal Viewer

#### Behaviors

1. **Connection flow**:
   - Show loading steps (SSH_AUTH -> CHECK_LOAD -> LAUNCH_SHELL -> DONE)
   - Handle errors with appropriate UI
2. **Terminal features**:
   - xterm.js with FitAddon (auto-resize)
   - Bell sound support
   - Copy/paste via right-click (if clipboard permission granted)
3. **Mobile support**:
   - On-screen keyboard with modifier keys (Ctrl, Alt, Shift, Meta)
   - Arrow keys, Tab, Esc, Delete buttons
   - Pinch-to-zoom (Chromium only)
4. **Keyboard handling**:
   - Full escape sequence support (arrow keys, function keys, etc.)
   - Ctrl+key combinations
   - Alt+key as Escape prefix
5. **Resize**: Debounced (500ms) terminal resize API calls
6. **Reconnection**: On WebSocket close, show reload prompt

### F4: VNC Viewer

#### Behaviors

1. **Connection flow**:
   - Show loading steps (SSH_AUTH -> CHECK_LOAD -> PARSE_PASSWD -> LAUNCH_VNC -> CREATE_TUNNEL -> DONE)
   - Handle VNC password prompt if credentials missing
2. **VNC features**:
   - noVNC with scaling and resize support
   - Bi-directional clipboard sync
   - Forward/backward mouse buttons -> Alt+Arrow
3. **Mobile support**:
   - On-screen keyboard via textarea
   - Modifier key toolbar
   - Ctrl+Alt+Delete button
4. **Speed dial menu**:
   - Audio toggle (launches audio WebSocket)
   - Keyboard toggle
   - Hide FAB option
5. **Authentication dialog**:
   - Triggered by `credentialsrequired` event
   - Save credentials option
   - Support for password and username/password modes
6. **Disconnection**: Show reconnect button

### F5: File Manager

#### Behaviors

1. **Directory listing**:
   - DataGrid with columns: Name, Size, Modified, Permissions
   - Double-click to navigate into directory or download file
   - Click on breadcrumb to navigate
2. **File operations**:
   - Download: Single file direct, multiple/directory as ZIP
   - Upload: File picker with progress, cancel support
   - Directory upload: webkitdirectory support
   - Rename: Inline editing
   - Delete: Multi-select delete
   - New folder: Modal dialog
   - Change permissions: chmod dialog with recursive option
3. **Drag and drop**: Upload files by dropping
4. **Quota display**: Parse from `quota | tail -n 1` command
5. **Error handling**: Display alerts for permission errors

### F6: Audio Streaming

#### Current Behaviors (WebSocket + zlib)

1. **Activation**: Toggle from VNC speed dial
2. **Audio format**: s16le, stereo, 44100Hz
3. **Decompression**: pako.inflate() on incoming data
4. **Playback**: PCMPlayer with 100ms flush interval
5. **Cleanup**: Destroy player on WebSocket close

#### Target Behaviors (WebRTC + Zstandard)

1. **Activation**: Toggle from VNC speed dial
2. **Connection establishment**:
   - Request offer SDP from `/api/audio_rtc`
   - Create RTCPeerConnection with provided ICE servers
   - Set remote description (offer)
   - Create and send answer to `/api/audio_rtc/answer`
   - Handle ICE candidate exchange
3. **Audio format**: s16le, stereo, 44100Hz (unchanged)
4. **Decompression**: zstd decompression via fzstd or @aspect-build/aspect-bundler-zstd
5. **Playback**: PCMPlayer or Web Audio API with AudioWorklet
6. **Latency optimization**:
   - Smaller buffer size for lower latency
   - Adaptive jitter buffer based on network conditions
7. **Cleanup**: Close RTCPeerConnection and destroy player
8. **Fallback**: If WebRTC fails (firewall/NAT issues), fallback to WebSocket

#### WebRTC Client Implementation

The audio client should implement:

- `connect(sessionId)`: Fetch offer from `/api/audio_rtc`, create RTCPeerConnection, set remote description, create answer, send to `/api/audio_rtc/answer`, handle ICE candidates via `/api/audio_rtc/ice`
- `onAudioFrame(data)`: Receive binary frames from DataChannel
- `decompressAndPlay(compressed)`: Decompress zstd frames and feed to PCMPlayer
- `disconnect()`: Close DataChannel, RTCPeerConnection, and destroy player

---

## BDD Playwright Test Scenarios

Use Playwright's native `test.describe()` and `test.step()` for BDD-style tests without additional frameworks.

### Test Structure

- Use `test.describe('Feature: ...')` for feature grouping
- Use `test.describe('Scenario: ...')` for scenario grouping
- Use `test.step('Given/When/Then/And ...')` for BDD steps within tests

### Required Test Scenarios

#### Authentication Tests

| Scenario            | Given             | When                                 | Then                                         |
|---------------------|-------------------|--------------------------------------|----------------------------------------------|
| Successful login    | On home page      | Enter valid credentials, click login | Redirect to dashboard                        |
| Wrong password      | On home page      | Enter wrong password, click login    | Show error with "Forgot password" option     |
| Unactivated account | On home page      | Login with unactivated account       | Show warning with "Resend activation" option |
| Password validation | On signup tab     | Enter password missing requirements  | Show specific requirement errors             |
| Auto-redirect       | Already logged in | Navigate to home page                | Redirect to dashboard                        |

#### Dashboard Tests

| Scenario                     | Given             | When                                             | Then                                                 |
|------------------------------|-------------------|--------------------------------------------------|------------------------------------------------------|
| View session list            | On dashboard      | Page loads                                       | Display sessions with host, username, nickname       |
| Open VNC (double-click)      | On dashboard      | Double-click session                             | Open VNC in new tab at `/vnc/{session_id}`           |
| Open Terminal (triple-click) | On dashboard      | Triple-click session                             | Open terminal in new tab at `/terminal/{session_id}` |
| Edit nickname                | On dashboard      | Click avatar, enter name (≤8 chars), press Enter | Update nickname via PATCH `/api/session`             |
| Delete session               | On dashboard      | Right-click → Delete                             | Remove session via DELETE `/api/session`             |
| Change Machine visibility    | EECG/ECF host     | Right-click                                      | Show "Change Machine" option                         |
| Change Machine hidden        | Non-EECG/ECF host | Right-click                                      | Hide "Change Machine" option                         |

#### Terminal Tests

| Scenario                | Given                        | When                                 | Then                                             |
|-------------------------|------------------------------|--------------------------------------|--------------------------------------------------|
| Successful connection   | Navigate to `/terminal/{id}` | Streaming response with steps + DONE | Show terminal, loading progress during steps     |
| Host unreachable (201)  | Terminal connection          | Receive error code 201               | Show "unreachable" error with refresh button     |
| Auth failed (203)       | Terminal connection          | Receive error code 203               | Show authentication error                        |
| Server overloaded (204) | Terminal connection          | Receive error code 204               | Show overload warning                            |
| Mobile toolbar          | Mobile viewport              | Terminal loads                       | Show Ctrl, Alt, Tab, arrow keys toolbar          |
| Terminal resize         | Active terminal              | Window resize (debounced 500ms)      | Call PATCH `/api/terminal_resize` with cols/rows |

#### VNC Tests

| Scenario                | Given                              | When                                 | Then                                                 |
|-------------------------|------------------------------------|--------------------------------------|------------------------------------------------------|
| Successful connection   | Navigate to `/vnc/{id}`            | Streaming response with steps + DONE | Show VNC screen, loading progress during steps       |
| Password required (121) | VNC connection                     | Receive error code 121               | Show password input prompt                           |
| Credential dialog       | noVNC `credentialsrequired` event  | Event triggers                       | Show username/password dialog with save option       |
| Quota exceeded (122)    | VNC connection                     | Receive error code 122               | Show quota exceeded message                          |
| Disconnection           | Active VNC disconnects             | WebSocket closes                     | Show "disconnected" message with reconnect button    |
| Speed dial menu         | Active VNC                         | Click speed dial FAB                 | Show Audio, Keyboard options                         |
| Mobile toolbar          | Mobile viewport + keyboard enabled | Toggle keyboard                      | Show Ctrl, Alt, Shift, Meta, Ctrl+Alt+Delete buttons |

#### File Manager Tests

| Scenario                 | Given                   | When                              | Then                                                       |
|--------------------------|-------------------------|-----------------------------------|------------------------------------------------------------|
| View directory listing   | Navigate to `/fm/{id}`  | Page loads                        | Show cwd path, files with icons (folder/file), size, mtime |
| Navigate into directory  | In file manager         | Double-click folder               | Load subdirectory, update path breadcrumb                  |
| Download single file     | In file manager         | Double-click file                 | Trigger download via GET `/api/sftp_dl`                    |
| Download multiple as ZIP | Multiple files selected | Click download                    | Download ZIP via GET `/api/sftp_dl` with files array       |
| Upload with progress     | In file manager         | Select file(s) via picker         | Show progress bar, POST to `/api/sftp_ul`                  |
| Rename file              | File selected           | F2 or right-click → Rename        | Inline edit, PATCH `/api/sftp_rename`                      |
| Delete files             | Files selected          | Click delete                      | POST `/api/sftp_rm`, refresh list                          |
| Create folder            | In file manager         | Click new folder, enter name      | Execute `mkdir` via `/api/exec_blocking`                   |
| Change permissions       | File selected           | Right-click → Permissions → Apply | PATCH `/api/sftp_chmod` with mode and recursive flag       |
| Display quota            | In file manager         | Page loads                        | Parse `quota` command output, show used/total              |
| Permission error         | Access restricted dir   | Double-click                      | Show "Permission denied" alert                             |

#### Audio Streaming Tests (WebRTC)

| Scenario               | Given              | When                      | Then                                                                   |
|------------------------|--------------------|---------------------------|------------------------------------------------------------------------|
| Enable via WebRTC      | Active VNC         | Click Audio in speed dial | POST `/api/audio_rtc` for offer, create RTCPeerConnection, send answer |
| WebRTC fallback        | WebRTC fails (500) | Enable audio              | Fallback to POST `/api/audio` (WebSocket)                              |
| ICE candidate exchange | WebRTC connecting  | ICE candidates generated  | POST each to `/api/audio_rtc/ice`                                      |
| Zstd decompression     | DataChannel open   | Receive compressed frames | Decompress with fzstd, feed to PCMPlayer                               |
| Disable audio          | Audio streaming    | Click Audio toggle        | Close RTCPeerConnection, stop playback                                 |

---

## Utility Functions

### Functions to Preserve

Port these pure utility functions to TypeScript. See `client/src/actions/utils.js` for current implementations.

| Function                                        | Module     | Description                                                 |
|-------------------------------------------------|------------|-------------------------------------------------------------|
| `isIOS()`                                       | device     | Detect iOS devices via navigator.platform and userAgent     |
| `isMobile()`                                    | device     | Detect mobile devices via userAgent regex patterns          |
| `canChangeMachine(hostname)`                    | device     | Check if host is EECG/ECF domain (allows machine switching) |
| `htmlResponseToReason(response, withoutStatus)` | response   | Extract error message from HTML error response              |
| `sortListByKey(list, key)`                      | sort       | In-place sort array of objects by numeric key               |
| `openInNewWindow(url, ev)`                      | navigation | Open URL in new tab/window (Electron-aware)                 |
| `getAvatarName(fullname)`                       | session    | Extract short hostname for avatar display                   |
| `hasLowerCase(str)`                             | password   | Check if string contains lowercase letter                   |
| `hasUpperCase(str)`                             | password   | Check if string contains uppercase letter                   |
| `hasNumeral(str)`                               | password   | Check if string contains digit                              |
| `hasSpecialSymbols(str)`                        | password   | Check if string contains special symbol from allowed set    |
| `LocalStorage.getLastUsername()`                | storage    | Get last used username from localStorage                    |
| `LocalStorage.setLastUsername(username)`        | storage    | Save username to localStorage                               |

---

## Implementation Checklist

When rewriting the frontend, ensure:

### Core Functionality

- [ ] All API contracts are preserved exactly
- [ ] Streaming response parsing works correctly for Terminal and VNC
- [ ] WebSocket protocols remain compatible (Terminal, VNC)
- [ ] Error codes trigger appropriate UI behaviors
- [ ] Step codes update loading progress correctly
- [ ] Mobile device detection works for toolbar display
- [ ] Keyboard event handling matches current escape sequences
- [ ] Clipboard sync works bi-directionally for VNC
- [ ] File permissions display correctly (Unix mode to rwx)
- [ ] Upload progress tracking works with cancellation
- [ ] All BDD test scenarios pass
- [ ] Electron desktop client compatibility maintained

### Audio Streaming (NEW - WebRTC + Zstandard)

- [ ] WebRTC signaling implemented with new `/api/audio_rtc` endpoints
- [ ] RTCPeerConnection created with provided ICE servers
- [ ] SDP offer/answer exchange working correctly
- [ ] ICE candidate trickle implemented
- [ ] DataChannel receives binary audio frames
- [ ] Zstandard (zstd) decompression library integrated (fzstd or zstd-wasm)
- [ ] Decompressed PCM audio fed to player (PCMPlayer or Web Audio API)
- [ ] Lower latency achieved compared to WebSocket
- [ ] Graceful fallback to WebSocket when WebRTC fails
- [ ] Clean disconnect on audio disable (close RTCPeerConnection)
- [ ] Audio works through NAT/firewalls via STUN/TURN

### Zstandard Library Options

Choose one of these libraries for zstd decompression in browser:

- [ ] `fzstd` - Pure JS, smaller bundle (~30KB)
- [ ] `@aspect-build/aspect-bundler-zstd` - WASM-based, faster for large frames
- [ ] `zstd-codec` - Another WASM option with streaming support
