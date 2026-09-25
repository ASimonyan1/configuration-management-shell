"""CSV-файловая система; после загрузки все операции идут в памяти."""

import base64
import binascii
import csv
import posixpath
from dataclasses import dataclass
from pathlib import Path

from .errors import EmulatorError

CSV_FIELDS = {"path", "type", "content", "encoding", "owner"}


@dataclass
class VFSNode:
    """Узел: абсолютный путь, тип file/dir, байты, двоичность и владелец."""

    path: str
    kind: str
    content: bytes = b""
    is_binary: bool = False
    owner: str = "root"


def normalize(path, cwd="/"):
    """Получить нормализованный абсолютный POSIX-путь внутри VFS."""
    joined = path if path.startswith("/") else posixpath.join(cwd, path)
    return "/" + posixpath.normpath(joined).lstrip("/")


def decode_content(content, encoding):
    """Преобразовать текст или base64 в байты без записи на диск."""
    if encoding == "text":
        return content.encode("utf-8")
    try:
        return base64.b64decode(content, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise EmulatorError("VFS: неверный base64") from exc


def validate_node_fields(path, kind, encoding):
    """Проверить обязательный путь и допустимые значения типа и кодировки."""
    if not path:
        raise EmulatorError("VFS: пустой путь")
    if kind not in {"file", "dir"}:
        raise EmulatorError(f"VFS: неверный type: {kind!r}")
    if encoding not in {"text", "base64"}:
        raise EmulatorError(f"VFS: неверный encoding: {encoding!r}")


def parse_node(row):
    """Проверить одну строку CSV и создать узел файловой системы."""
    path = (row.get("path") or "").strip()
    kind = (row.get("type") or "").strip().lower()
    encoding = (row.get("encoding") or "text").strip().lower()
    owner = (row.get("owner") or "root").strip() or "root"
    validate_node_fields(path, kind, encoding)
    content = b""
    if kind == "file":
        content = decode_content(row.get("content") or "", encoding)
    return VFSNode(normalize(path), kind, content, encoding == "base64", owner)


class VirtualFileSystem:
    """Дерево узлов и текущий каталог; исходный CSV не изменяется."""

    def __init__(self):
        """Создать пустую файловую систему с корневым каталогом."""
        self.nodes = {"/": VFSNode("/", "dir")}
        self.cwd = "/"

    def resolve(self, path):
        """Разрешить путь относительно текущего каталога."""
        return normalize(path, self.cwd)

    def load_csv(self, csv_path):
        """Атомарно загрузить CSV; ошибочный файл не портит текущую VFS."""
        candidate = VirtualFileSystem()
        try:
            with Path(csv_path).open(
                "r", encoding="utf-8-sig", newline=""
            ) as stream:
                candidate._read_rows(csv.DictReader(stream, strict=True))
        except (OSError, UnicodeError, csv.Error) as exc:
            raise EmulatorError(f"VFS: ошибка чтения CSV: {exc}") from exc
        self.nodes = candidate.nodes
        self.cwd = "/"

    def _read_rows(self, reader):
        """Проверить заголовок CSV и добавить узлы с номерами строк ошибок."""
        if not CSV_FIELDS.issubset(reader.fieldnames or []):
            raise EmulatorError(
                "VFS: нужны поля path,type,content,encoding,owner"
            )
        explicit_paths = set()
        for row in reader:
            try:
                node = parse_node(row)
                if node.path in explicit_paths:
                    raise EmulatorError(f"VFS: повтор пути: {node.path}")
                self._add_node(node)
                explicit_paths.add(node.path)
            except EmulatorError as exc:
                raise EmulatorError(
                    f"Строка CSV {reader.line_num}: {exc}"
                ) from exc

    def _add_node(self, node):
        """Добавить узел, создав родителей и проверив конфликты типов."""
        existing = self.nodes.get(node.path)
        if existing is not None and existing.kind != node.kind:
            raise EmulatorError(f"VFS: конфликт типов: {node.path}")
        parent = posixpath.dirname(node.path)
        while parent != "/":
            ancestor = self.nodes.get(parent)
            if ancestor is not None and ancestor.kind != "dir":
                raise EmulatorError(f"VFS: родитель не каталог: {parent}")
            self.nodes.setdefault(
                parent, VFSNode(parent, "dir", owner=node.owner)
            )
            parent = posixpath.dirname(parent)
        self.nodes[node.path] = node

    def exists(self, path):
        """Проверить существование пути в памяти."""
        return self.resolve(path) in self.nodes

    def get(self, path):
        """Найти узел или сообщить об отсутствующем пути."""
        resolved = self.resolve(path)
        if resolved not in self.nodes:
            raise EmulatorError(f"Нет такого файла или каталога: {path}")
        return self.nodes[resolved]

    def list_dir(self, path="."):
        """Вернуть файл либо отсортированных непосредственных детей каталога."""
        node = self.get(path)
        if node.kind == "file":
            return [node]
        children = [
            child for child in self.nodes.values()
            if child.path != node.path
            and posixpath.dirname(child.path) == node.path
        ]
        return sorted(children, key=lambda child: (
            child.kind != "dir", posixpath.basename(child.path)
        ))

    def change_dir(self, path):
        """Перейти в каталог внутри VFS."""
        node = self.get(path)
        if node.kind != "dir":
            raise EmulatorError(f"cd: не каталог: {path}")
        self.cwd = node.path

    def read_text(self, path):
        """Прочитать текстовый файл; каталоги и двоичные файлы отклоняются."""
        node = self.get(path)
        if node.kind != "file":
            raise EmulatorError(f"Это каталог, а не файл: {path}")
        if node.is_binary:
            raise EmulatorError(
                f"Двоичный файл нельзя читать как текст: {path}"
            )
        return node.content.decode("utf-8")

