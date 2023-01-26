from __future__ import annotations

import abc
import enum
import logging
from dataclasses import dataclass
from enum import Enum
from typing import IO, Optional

from tungsten.globally_harmonized_system.safety_data_sheet import (
    GhsSafetyDataSheet
)
from tungsten.parsers.parsing_hierarchy import HierarchyElement, HierarchyNode


class SdsParser(metaclass=abc.ABCMeta):
    injectors: list[SdsParserInjector] = []
    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(f"tungsten:{self.__class__.__name__}")

    def parse_to_ghs_sds(self, io: IO[bytes]) -> GhsSafetyDataSheet:
        """Parses a PDF into a :class:`GhsSafetyDataSheet`."""
        # Generate text hierarchy
        hierarchy = self._parse_to_hierarchy(io)
        # Call injectors and collect injections
        injections: list[Injection] = []
        for injector in self.injectors:
            injections += injector.generate_injections(io)
        # Inject collected injections into the text hierarchy
        self._process_injections(injections, hierarchy)
        self.logger.info(hierarchy)
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

    def _process_injections(self, injections: list[Injection], root: HierarchyNode) -> None:
        """Operates on a hierarchy with gathered injections."""
        # First step is to delete original text elements to match the specific overwrite condition
        # This feels like a LeetCode problem, I wonder if there's a better way to do this?
        # Currently runs O(N*M), N = # of HierarchyNode objects, M = # of InjectionBox objects
        bounds: list[tuple[InjectionBox, InjectionOverwriteBoundaryMode, HierarchyElement]] = []

        for injection in injections:
            for box in injection.boxes:
                bounds.append((box, injection.mode, injection.payload))

        # Boxes look like this for some reason
        # +--------------+ (x1,y1)
        # |              |
        # |(x0,y0)       |
        # +--------------+
        # x1 > x0, y1 > y0, as page coordinates start from the bottom left (see PDF User Space)

        # Mark all children that should be deleted
        stack: list[HierarchyNode] = [root]  # Stack used for tree traversal
        while len(stack) != 0:
            hand = stack.pop()

            for (box, mode, payload) in bounds:
                box: InjectionBox
                if box.type == CoordinateType.DOCUMENT:
                    raise NotImplementedError
                if hand.data is None:
                    break
                rightest_left = max(hand.data.page_x0, box.x0)
                leftest_right = min(hand.data.page_x1, box.x1)
                topest_bottom = max(hand.data.page_y0, box.y0)
                bottomest_top = min(hand.data.page_y1, box.y1)
                match mode:
                    case InjectionOverwriteBoundaryMode.NO_ACTION:
                        pass
                    case InjectionOverwriteBoundaryMode.INTERSECTS:
                        if leftest_right >= rightest_left and bottomest_top >= topest_bottom and \
                                hand.data.page_num == box.page_num:
                            hand.data.set_delete()
                    case InjectionOverwriteBoundaryMode.CONTAINS:
                        raise NotImplementedError

            for child in hand.children:
                stack.append(child)

        # Remove tagged children
        stack.append(root)
        while len(stack) != 0:
            hand = stack.pop()
            i: int = 0
            while i < len(hand.children):
                if hand.children[i].data.to_delete:
                    hand.children.pop(i)
                else:
                    stack.append(hand.children[i])
                    i += 1

        # Second step is to place the injected element into an appropriate location
        for injection in injections:
            # take first box TODO check if highest box
            box = injection.boxes[0]
            exit_flag = False
            # Iterate backwards through each section
            for i in range(len(root.children) - 1, 0, -1):
                if exit_flag:
                    break
                stack = [root.children[i]]
                order = []
                while len(stack) != 0:
                    hand = stack.pop()
                    order.append(hand)
                    for child in reversed(hand.children):
                        stack.append(child)
                order.reverse()
                for element in order:
                    if box.y1 <= element.data.page_y0 \
                            and box.page_num == element.data.page_num:
                        element.add_child(HierarchyNode(injection.payload))
                        exit_flag = True
                        break


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

    def __str__(self):
        return f"InjectionBox(({self.x0}, {self.y0}) ({self.x1}, {self.y1}), {self.type}, " \
               f"page_num={self.page_num})"


class CoordinateType(Enum):
    PAGE = enum.auto()
    DOCUMENT = enum.auto()


class InjectionOverwriteBoundaryMode(Enum):
    NO_ACTION = enum.auto()
    INTERSECTS = enum.auto()
    CONTAINS = enum.auto()
