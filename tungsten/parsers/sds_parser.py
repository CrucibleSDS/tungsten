from __future__ import annotations

import abc
import enum
from dataclasses import dataclass
from enum import Enum
from typing import IO, Optional

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSafetyDataSheet
)
from tungsten.parsers.parsing_hierarchy import HierarchyElement, HierarchyNode


class SdsParser(metaclass=abc.ABCMeta):
    injectors: list[SdsParserInjector] = []

    def parse_to_ghs_sds(self, io: IO[bytes]) -> GhsSafetyDataSheet:
        """Parses a PDF into a :class:`GhsSafetyDataSheet`."""
        # Generate text hierarchy
        hierarchy = self._parse_to_hierarchy(io)
        # Call injectors and collect injections
        injections: list[Injection] = []
        for injector in self.injectors:
            injections += injector.generate_injections(io)
        # Inject collected injections into the text hierarchy
        self._perform_injection(injections, hierarchy)
        # Create GHS SDS document from result
        return self._hierarchy_to_ghs_sds(hierarchy)

    @abc.abstractmethod
    def _parse_to_hierarchy(self, io: IO[bytes]) -> HierarchyNode:
        """Parses a PDF into an internal hierarchy. Used for subsequent steps."""
        pass

    @abc.abstractmethod
    def _hierarchy_to_ghs_sds(self, root: HierarchyNode) -> GhsSafetyDataSheet:
        pass

    def register_injector(self, injector: SdsParserInjector) -> None:
        """Registers an injector class for use in the parsing pipeline."""
        self.injectors.append(injector)

    def _perform_injection(self, injections: list[Injection], root: HierarchyNode) -> None:
        """Operates on a hierarchy with gathered injections."""
        # This feels like a LeetCode problem, I wonder if there's a better way to do this?
        # Currently runs O(N*M), N = # of HierarchyNode objects, M = # of InjectionBox objects


class SdsParserInjector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_injections(self, io: IO[bytes]) -> list[Injection]:
        pass


@dataclass
class Injection:
    boxes: list[InjectionBox]
    mode: InjectionOverwriteBoundaryMode
    payload: HierarchyElement


class InjectionBox:
    page_num: Optional[int]
    x0: float
    y0: float
    x1: float
    y1: float
    coord_type: CoordinateType

    def __init__(self, x0: float, y0: float, x1: float, y1: float, coord_type: CoordinateType,
                 page_num: Optional[int]):
        if coord_type == CoordinateType.PAGE and page_num is None:
            raise AttributeError("Cannot work in page coordinates without page number reference.")
        self.page_num = page_num
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.type = coord_type


class CoordinateType(Enum):
    PAGE = enum.auto()
    DOCUMENT = enum.auto()


class InjectionOverwriteBoundaryMode(Enum):
    NO_ACTION = enum.auto()
    INTERSECTS = enum.auto()
    CONTAINS = enum.auto()
