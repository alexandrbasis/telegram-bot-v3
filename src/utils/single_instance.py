"""
Single-instance guard using a cross-platform file lock.

Prevents multiple bot processes from running concurrently on the same host.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InstanceLock:
    """A context manager that acquires an exclusive file lock.

    On POSIX systems, uses fcntl.flock. On Windows, uses msvcrt.locking.
    The lock is held for the lifetime of the context. If the lock cannot be
    acquired immediately, raises RuntimeError.
    """

    path: Path

    def __post_init__(self) -> None:
        self._fd: int | None = None
        self._fh = None

    def __enter__(self):
        # Ensure parent directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

        flags = os.O_RDWR | os.O_CREAT
        # 0o644 file permissions
        self._fd = os.open(self.path, flags, 0o644)
        self._fh = os.fdopen(self._fd, mode="r+", buffering=1, encoding="utf-8", errors="ignore")

        try:
            if sys.platform.startswith("win"):
                # Windows non-blocking lock on 1 byte at start of file
                import msvcrt
                self._fh.seek(0)
                try:
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError:
                    raise RuntimeError(self._conflict_message())
            else:
                # POSIX non-blocking exclusive lock
                import fcntl
                try:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    raise RuntimeError(self._conflict_message())

            # Write our PID for visibility
            try:
                self._fh.seek(0)
                self._fh.truncate()
                self._fh.write(str(os.getpid()))
                self._fh.flush()
            except Exception:
                # Non-fatal: lock is already held
                pass

            return self
        except Exception:
            # Clean up on failure to avoid leaking fd
            try:
                if self._fh:
                    self._fh.close()
            finally:
                self._fh = None
                self._fd = None
            raise

    def __exit__(self, exc_type, exc, tb) -> None:
        # Release lock by closing the file handle
        try:
            if self._fh:
                self._fh.close()
        finally:
            self._fh = None
            self._fd = None
        # Best-effort: remove lock file for tidiness
        try:
            self.path.unlink(missing_ok=True)
        except Exception:
            pass

    def _conflict_message(self) -> str:
        other_pid = None
        try:
            # Try to read existing PID for a clearer error
            with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if content.isdigit():
                    other_pid = int(content)
        except Exception:
            pass

        suffix = f" (pid {other_pid})" if other_pid else ""
        return (
            f"Another instance of the bot is already running{suffix}.\n"
            f"If this seems incorrect, delete '{self.path}' and try again."
        )

