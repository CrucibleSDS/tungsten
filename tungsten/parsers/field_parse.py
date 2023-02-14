from __future__ import annotations

import abc
import enum
from dataclasses import dataclass
from enum import Enum
from re import Pattern
from typing import Callable


class FieldMapper(metaclass=abc.ABCMeta):
    def getField(self, field: SdsQueryFieldName, target: dict):
        mapping = self.getFieldMappings(field)
        commands, post_process = mapping
        for command in commands:
            target = command.match(target)
        try:
            result = post_process(target)
        except (KeyError, AttributeError, TypeError, IndexError):
            result = None
        return result

    @abc.abstractmethod
    def getFieldMappings(self, field: SdsQueryFieldName) -> tuple[list[SelectCommand], Callable]:
        pass


@dataclass
class SelectCommand:
    key: str
    where_value: any | Pattern

    def __init__(self, key, where_value=None):
        self.key = key
        self.where_value = where_value

    def match(self, targets: dict | list):
        if isinstance(targets, dict):
            return (targets if isinstance(targets, dict) else targets.__dict__)[self.key]
        if targets is None:
            return None
        for target in targets:
            compare = (target if isinstance(target, dict) else target.__dict__)[self.key]
            if isinstance(self.where_value, Pattern):
                if self.where_value.match(compare) is not None:
                    return target
            else:
                if self.where_value == compare:
                    return target


class SdsQueryFieldName(Enum):
    META_VERSION = enum.auto()  # Document meta version
    META_REVISION_DATE = enum.auto()  # Document supplier-provided revision date
    META_PRINT_DATE = enum.auto()  # Document supplier-provided print date

    PRODUCT_NAME = enum.auto()
    PRODUCT_NUMBER = enum.auto()
    CAS_NUMBER = enum.auto()
    PRODUCT_BRAND = enum.auto()
    RECOMMENDED_USE_AND_RESTRICTIONS = enum.auto()  # Ref. RECOMMENDED_USE_AND_RESTRICTIONS

    SUPPLIER_ADDRESS = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS
    SUPPLIER_TELEPHONE = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS
    SUPPLIER_FAX = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS

    EMERGENCY_TELEPHONE = enum.auto()  # Ref. EMERGENCY_PHONE_NUMBER

    # Ref. OTHER_MEANS_OF_IDENTIFICATION, IDENTIFICATION_OTHER Data dump! No Schema!
    IDENTIFICATION_OTHER = enum.auto()

    SUBSTANCE_CLASSIFICATION = enum.auto()  # Ref. GHS_SUBSTANCE_CLASSIFICATION

    PICTOGRAM = enum.auto()  # Ref. (INSIDE OF!!!) GHS_LABEL_ELEMENTS
    SIGNAL_WORD = enum.auto()  # Ref. (INSIDE OF!!!) GHS_LABEL_ELEMENTS

    HNOC_HAZARD = enum.auto()  # Ref. OTHER_HAZARDS, HAZARDS_OTHER. Data dump! No Schema!
