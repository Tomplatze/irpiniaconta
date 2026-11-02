"""Shared, typed adapter contracts for the institutional ingestion pipeline."""
from dataclasses import dataclass, field
from typing import Literal

ValueStatus = Literal['observed', 'missing', 'suppressed']

@dataclass(frozen=True)
class Observation:
    """A single municipal measurement, preserving missingness and period."""
    municipality_code: str
    indicator_id: str
    period: str
    value: float | None
    status: ValueStatus = 'observed'

@dataclass(frozen=True)
class Entity:
    """A source-identified place, authority, infrastructure or funded application."""
    municipality_code: str | None
    dataset_id: str
    source_id: str
    title: str
    kind: str
    payload: dict[str, object]
    period: str

@dataclass
class AdapterResult:
    """Source verification and normalized observations returned by an adapter."""
    metadata: dict[str, object]
    observations: list[Observation] = field(default_factory=list)
    municipalities: list[dict[str, str]] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
