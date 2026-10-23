from dataclasses import dataclass, field

@dataclass
class Card:
    id: int
    language: str
    prompt: str
    answer: str
    accepted_variants: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)