from dataclasses import dataclass
from typing import Optional


@dataclass(order=True)
class Entity:
    label: str
    is_start: bool
    render_slot: int
    kb_id: Optional[str]
    kb_url: Optional[str]
    kb_link: Optional[str]


@dataclass
class TokenInfo:
    text: str
    entities: list[Entity]
