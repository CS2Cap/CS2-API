"""Thin filesystem abstraction for easy handling of temporary files and JSON data."""
import json
import os
from typing import Any


def read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def exists(path: str) -> bool:
    return os.path.exists(path)


def read_json(path: str) -> dict | None:
    text = read(path)
    if text is None:
        return None
    return json.loads(text)


def write_json(path: str, data: Any, indent: int = 1) -> None:
    write(path, json.dumps(data, indent=indent, ensure_ascii=False))
