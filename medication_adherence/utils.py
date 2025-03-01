import json
from enum import Enum
from pathlib import Path
from typing import Dict


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class StrEnum(str, ExtendedEnum):
    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


def load_json_file(file_path: Path) -> Dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
