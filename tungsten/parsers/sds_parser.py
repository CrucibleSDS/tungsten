from __future__ import annotations

import abc
import enum
from dataclasses import dataclass
from typing import IO

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSafetyDataSheet
)
from tungsten.parsers.parsing_hierarchy import HierarchyNode


class SdsParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_to_ghs_sds(self, io: IO[bytes], sds_name="default") -> GhsSafetyDataSheet:
        """Parses a PDF into a :class:`GhsSafetyDataSheet`."""
        pass


class SdsParserInjector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_injections(self, io: IO[bytes]) -> list[Injection]:
        pass

    def injection_hook(self, injections: list[Injection], root: HierarchyNode):
        pass


@dataclass
class Injection:
    page_num: int
    x: float
    y: float
    xl_case: InjectionOverwriteBoundaryCase
    xr_case: InjectionOverwriteBoundaryCase
    yl_case: InjectionOverwriteBoundaryCase
    yr_case: InjectionOverwriteBoundaryCase
    payload: HierarchyNode


class InjectionOverwriteBoundaryCase(enum.Enum):
    NO_ACTION: enum.auto()
    INTERSECTS: enum.auto()
    CONTAINS: enum.auto()
