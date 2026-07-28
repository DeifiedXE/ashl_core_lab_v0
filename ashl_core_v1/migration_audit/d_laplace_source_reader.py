"""Static, non-importing readers for D-Laplace directories and ZIP archives."""

from __future__ import annotations

import hashlib
import os
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator
from zipfile import ZipFile, ZipInfo


class DLaplaceSourceError(RuntimeError):
    pass


class DLaplaceSourceBoundaryError(DLaplaceSourceError):
    pass


@dataclass(frozen=True)
class SourceEntry:
    relative_path: str
    size_bytes: int
    is_symlink: bool
    symlink_target: str | None


def _normalized_zip_path(name: str) -> str:
    candidate = name.replace("\\", "/")
    path = PurePosixPath(candidate)
    parts = path.parts
    if (
        not candidate
        or candidate.startswith("/")
        or any(part in {"", ".", ".."} for part in parts)
        or (parts and ":" in parts[0])
    ):
        raise DLaplaceSourceBoundaryError(
            f"unsafe ZIP entry path rejected: {name!r}"
        )
    return path.as_posix()


def _sha256_stream(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


class ReadOnlyDLaplaceSource:
    source_kind: str

    def __init__(self, source_path: str | Path) -> None:
        self.source_path = Path(source_path).resolve()

    @property
    def path_fingerprint(self) -> str:
        normalized = os.path.normcase(str(self.source_path))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @property
    def original_archive_sha256(self) -> str | None:
        return None

    def entries(self) -> tuple[SourceEntry, ...]:
        raise NotImplementedError

    @contextmanager
    def open_binary(self, relative_path: str) -> Iterator[BinaryIO]:
        raise NotImplementedError

    def read_bytes(self, relative_path: str, *, maximum_bytes: int) -> bytes:
        entry = next(
            (item for item in self.entries() if item.relative_path == relative_path),
            None,
        )
        if entry is None:
            raise FileNotFoundError(relative_path)
        if entry.is_symlink:
            raise DLaplaceSourceBoundaryError("symlink content is never followed")
        if entry.size_bytes > maximum_bytes:
            raise DLaplaceSourceError(
                f"source entry exceeds static read limit: {relative_path}"
            )
        with self.open_binary(relative_path) as stream:
            return stream.read(maximum_bytes + 1)

    def read_text(
        self,
        relative_path: str,
        *,
        maximum_bytes: int = 8 * 1024 * 1024,
    ) -> str:
        data = self.read_bytes(relative_path, maximum_bytes=maximum_bytes)
        if len(data) > maximum_bytes:
            raise DLaplaceSourceError(
                f"source entry exceeds static read limit: {relative_path}"
            )
        return data.decode("utf-8-sig", errors="replace")

    def sha256(self, relative_path: str) -> str:
        entry = next(
            (item for item in self.entries() if item.relative_path == relative_path),
            None,
        )
        if entry is None:
            raise FileNotFoundError(relative_path)
        if entry.is_symlink:
            return hashlib.sha256(
                (entry.symlink_target or "").encode("utf-8")
            ).hexdigest()
        with self.open_binary(relative_path) as stream:
            return _sha256_stream(stream)

    def entry_hashes(
        self,
        entries: tuple[SourceEntry, ...],
    ) -> dict[str, str]:
        return {entry.relative_path: self.sha256(entry.relative_path) for entry in entries}


class DirectoryDLaplaceSource(ReadOnlyDLaplaceSource):
    source_kind = "directory"

    def __init__(self, source_path: str | Path) -> None:
        super().__init__(source_path)
        if not self.source_path.is_dir():
            raise DLaplaceSourceError("D-Laplace source directory is unavailable")

    def entries(self) -> tuple[SourceEntry, ...]:
        records: list[SourceEntry] = []
        for root, directory_names, file_names in os.walk(
            self.source_path,
            followlinks=False,
        ):
            root_path = Path(root)
            retained_directories: list[str] = []
            for name in sorted(directory_names, key=str.casefold):
                path = root_path / name
                if path.is_symlink():
                    records.append(self._symlink_entry(path))
                else:
                    retained_directories.append(name)
            directory_names[:] = retained_directories
            for name in sorted(file_names, key=str.casefold):
                path = root_path / name
                if path.is_symlink():
                    records.append(self._symlink_entry(path))
                    continue
                relative_path = path.relative_to(self.source_path).as_posix()
                records.append(
                    SourceEntry(
                        relative_path=relative_path,
                        size_bytes=path.stat(follow_symlinks=False).st_size,
                        is_symlink=False,
                        symlink_target=None,
                    )
                )
        return tuple(sorted(records, key=lambda item: item.relative_path.casefold()))

    def _symlink_entry(self, path: Path) -> SourceEntry:
        target = os.readlink(path)
        return SourceEntry(
            relative_path=path.relative_to(self.source_path).as_posix(),
            size_bytes=len(os.fsencode(target)),
            is_symlink=True,
            symlink_target=target,
        )

    @contextmanager
    def open_binary(self, relative_path: str) -> Iterator[BinaryIO]:
        path = self.source_path.joinpath(*PurePosixPath(relative_path).parts)
        resolved_parent = path.parent.resolve()
        try:
            resolved_parent.relative_to(self.source_path)
        except ValueError as error:
            raise DLaplaceSourceBoundaryError(
                "source path escaped directory root"
            ) from error
        if path.is_symlink():
            raise DLaplaceSourceBoundaryError("symlink content is never followed")
        stream = path.open("rb")
        try:
            yield stream
        finally:
            stream.close()


class ZipDLaplaceSource(ReadOnlyDLaplaceSource):
    source_kind = "zip"

    def __init__(self, source_path: str | Path) -> None:
        super().__init__(source_path)
        if not self.source_path.is_file():
            raise DLaplaceSourceError("D-Laplace ZIP source is unavailable")
        self._entry_map = self._validate_entries()

    @property
    def original_archive_sha256(self) -> str:
        with self.source_path.open("rb") as stream:
            return _sha256_stream(stream)

    def _validate_entries(self) -> dict[str, ZipInfo]:
        result: dict[str, ZipInfo] = {}
        with ZipFile(self.source_path, "r") as archive:
            for info in archive.infolist():
                normalized = _normalized_zip_path(info.filename)
                if info.is_dir():
                    continue
                if normalized in result:
                    raise DLaplaceSourceBoundaryError(
                        f"duplicate normalized ZIP entry: {normalized}"
                    )
                result[normalized] = info
        return result

    @staticmethod
    def _is_symlink(info: ZipInfo) -> bool:
        unix_mode = (info.external_attr >> 16) & 0xFFFF
        return stat.S_ISLNK(unix_mode)

    def entries(self) -> tuple[SourceEntry, ...]:
        records: list[SourceEntry] = []
        with ZipFile(self.source_path, "r") as archive:
            for relative_path, info in self._entry_map.items():
                is_symlink = self._is_symlink(info)
                target: str | None = None
                if is_symlink:
                    target = archive.read(info).decode("utf-8", errors="replace")
                records.append(
                    SourceEntry(
                        relative_path=relative_path,
                        size_bytes=info.file_size,
                        is_symlink=is_symlink,
                        symlink_target=target,
                    )
                )
        return tuple(sorted(records, key=lambda item: item.relative_path.casefold()))

    def entry_hashes(
        self,
        entries: tuple[SourceEntry, ...],
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        with ZipFile(self.source_path, "r") as archive:
            for entry in entries:
                info = self._entry_map[entry.relative_path]
                if entry.is_symlink:
                    result[entry.relative_path] = hashlib.sha256(
                        (entry.symlink_target or "").encode("utf-8")
                    ).hexdigest()
                    continue
                with archive.open(info, "r") as stream:
                    result[entry.relative_path] = _sha256_stream(stream)
        return result

    @contextmanager
    def open_binary(self, relative_path: str) -> Iterator[BinaryIO]:
        info = self._entry_map.get(relative_path)
        if info is None:
            raise FileNotFoundError(relative_path)
        if self._is_symlink(info):
            raise DLaplaceSourceBoundaryError("ZIP symlink content is never followed")
        archive = ZipFile(self.source_path, "r")
        stream = archive.open(info, "r")
        try:
            yield stream
        finally:
            stream.close()
            archive.close()


def open_d_laplace_source(
    source_path: str | Path,
) -> ReadOnlyDLaplaceSource:
    path = Path(source_path)
    if path.is_dir():
        return DirectoryDLaplaceSource(path)
    if path.is_file() and path.suffix.casefold() == ".zip":
        return ZipDLaplaceSource(path)
    raise DLaplaceSourceError(
        "D-Laplace source must be an existing directory or ZIP archive"
    )
