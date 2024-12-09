from dataclasses import dataclass
from typing import Optional


@dataclass(order=True)
class Entity:
    label: str
    is_start: bool
    render_slot: int
    sublabel: Optional[str]
    tags: Optional[list[str]]


@dataclass
class TokenInfo:
    text: str
    entities: list[Entity]
