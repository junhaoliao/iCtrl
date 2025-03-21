import os
import uuid
from pathlib import Path
from typing import Optional
from clp_logging.handlers import CLPFileHandler, CLPLogLevelTimeout, EOF_CHAR, FLUSH_FRAME
from datetime import datetime


class RotatingCLPFileHandler(CLPFileHandler):
    """
    Extends `CLPFileHandler` to support file size-based log rotation.
    """

    def __init__(
            self,
            filename_prefix: str,
            log_dir: Path,
            max_bytes: int,
            backup_count: int = 20,
            mode: str = "ab",
            enable_compression: bool = True,
            timestamp_format: str = "%Y-%m-%d_%H-%M-%S",
            loglevel_timeout: Optional[CLPLogLevelTimeout] = None,
    ) -> None:
        self.filename_prefix = filename_prefix
        self.log_dir = Path(log_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.timestamp_format = timestamp_format

        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Initialize the base filename with a timestamp
        self.current_log_file = self._generate_log_filename()

        super().__init__(
            fpath=self.current_log_file,
            mode=mode,
            enable_compression=enable_compression,
            timestamp_format=timestamp_format,
            loglevel_timeout=loglevel_timeout,
        )

    @staticmethod
    def _get_persistent_machine_uuid() -> str:
        """
        Retrieves a persistent machine-specific UUID:
        - First checks the `iCtrl_LOG_UUID` environment variable.
        - If not found, checks a system-wide file (`/etc/iCtrl_machine_log_uuid` or `~/.iCtrl_machine_log_uuid`).
        - If still not found, generates a new UUID, saves it, and returns only the first 8 characters.
        """
        env_var_name = "iCtrl_LOG_UUID"

        # 1️⃣ Check if UUID exists in an environment variable
        env_uuid = os.getenv(env_var_name)
        if env_uuid:
            return env_uuid.strip()[:8]  # Limit to first 8 characters

        # 2️⃣ Define a persistent file path
        if os.name == "nt":  # Windows
            uuid_file = Path(os.getenv("APPDATA", "C:/ProgramData")) / "iCtrl_machine_log_uuid.txt"
        else:  # Linux/macOS
            uuid_file = Path(
                "/etc/iCtrl_machine_log_uuid") if os.geteuid() == 0 else Path.home() / ".iCtrl_machine_log_uuid"

        # 3️⃣ Check if the file exists and read the UUID
        if uuid_file.exists():
            with open(uuid_file, "r") as f:
                machine_uuid = f.read().strip()[:8]  # Limit to first 8 characters
                os.environ[env_var_name] = machine_uuid  # Store in environment for future use
                return machine_uuid

        # 4️⃣ Generate a new UUID and store only the first 8 characters
        new_uuid = str(uuid.uuid4())[:8]

        try:
            with open(uuid_file, "w") as f:
                f.write(new_uuid)
            os.environ[env_var_name] = new_uuid  # Store in environment
        except PermissionError:
            print(f"Warning: Could not save machine UUID to {uuid_file}. Using in-memory only.")

        return new_uuid

    def _generate_log_filename(self) -> Path:
        """
        Generate a log filename with the prefix, persistent UUID and timestamp.
        If a file with the same name already exists, append a counter (_1, _2, etc.).
        """
        uuid_str = self._get_persistent_machine_uuid()  # Get the persistent UUID
        timestamp = datetime.now().strftime(self.timestamp_format)

        base_filename = f"{self.filename_prefix}_{uuid_str}_{timestamp}"
        file_path = self.log_dir / f"{base_filename}.clp.zst"

        # Check for name conflicts and append a counter if necessary
        counter = 1
        while file_path.exists():
            file_path = self.log_dir / f"{base_filename}_{counter}.clp.zst"
            counter += 1

        return file_path

    def _open_new_log_file(self) -> None:
        """
            Generate a new log filename, open the file for writing, and switch the handler's stream.

            This method updates `self.current_log_file`, opens a new stream in append-binary mode,
            and reinitializes the handler to use the new stream. It should be called when the
            current log file is deleted or after rotation.
        """
        new_log_file = self._generate_log_filename()

        try:
            new_stream = open(new_log_file, "ab")
        except Exception as e:
            raise RuntimeError(f"Failed to open new log file {new_log_file}: {e}")

        self.acquire()
        try:
            self.stream = new_stream
            self.init(new_stream)
            self.current_log_file = new_log_file
        finally:
            self.release()

    def _should_rotate(self) -> bool:
        """
        Check if the current file exceeds the maximum size.
        """
        try:
            return self.current_log_file.stat().st_size >= self.max_bytes
        except FileNotFoundError:
            return False

    def _rotate(self) -> None:
        """
        Perform log rotation by finalizing the current stream, creating a new log file,
        and reinitializing the handler with the new stream.

        This method is responsible for:
        1. Flushing and writing any remaining buffered data in the current stream.
        2. Writing a logical end-of-file (EOF) marker to signal the end of the log stream.
        3. Closing the current stream to release any associated resources.
        4. Generating a new log file name based on the current timestamp.
        5. Opening a new stream for the new log file and reinitializing the handler to use it.
        6. Removing old log files if the number of backups exceeds the specified backup count.

        Thread safety is ensured by acquiring and releasing the handler's lock during the
        transition between streams.
        """
        try:
            self.ostream.flush(FLUSH_FRAME)
            self.ostream.write(EOF_CHAR)
        finally:
            self.ostream.close()

        self._open_new_log_file()
        self._remove_old_backups()

    def _remove_old_backups(self) -> None:
        """
        Remove old log files exceeding the backup count, but only for the current machine UUID.
        """
        if not self.backup_count:
            return

        uuid_str = self._get_persistent_machine_uuid()  # Get the persistent UUID

        log_files = sorted(
            self.log_dir.glob(f"{self.filename_prefix}_{uuid_str}_*.clp.zst"),
            key=os.path.getmtime,
        )
        if len(log_files) > self.backup_count:
            for old_file in log_files[:-self.backup_count]:
                try:
                    old_file.unlink()
                except Exception as e:
                    print(f"Error deleting old log file {old_file}: {e}")

    def _write(self, loglevel: int, msg: str) -> None:
        """
        Override `_write` to add rotation logic.
        """
        if self._should_rotate():
            self._rotate()
        elif not os.path.exists(self.current_log_file):
            self._open_new_log_file()
        super()._write(loglevel, msg)
