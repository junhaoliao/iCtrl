import os
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
        backup_count: int = 5,
        mode: str = "ab",
        enable_compression: bool = True,
        timestamp_format: str = "%Y%m%d_%H%M%S",
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
    
    def _generate_log_filename(self) -> Path:
        """
        Generate a log filename with the timestamp and prefix.
        """
        start_time = datetime.now()
        timestamp = start_time.strftime(self.timestamp_format)
        self.current_log_file = Path(f"{self.log_dir}/{self.filename_prefix}_{timestamp}.clp.zst")

        return self.current_log_file

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

        # Generate a new log filename
        new_log_file = self._generate_log_filename()

        # Initialize the new stream
        try:
            new_stream = open(new_log_file, "ab")
        except Exception as e:
            raise RuntimeError(f"Failed to open new log file {new_log_file}: {e}")

        self.acquire()
        try:
            self.stream = new_stream
            self.init(new_stream)
        finally:
            self.release()

        # Remove old backups
        self._remove_old_backups()

    def _remove_old_backups(self) -> None:
        """
        Remove old log files exceeding the backup count.
        """
        if not self.backup_count:
            return

        log_files = sorted(
            self.log_dir.glob(f"{self.filename_prefix}_*.clp.zst"),
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
        super()._write(loglevel, msg)