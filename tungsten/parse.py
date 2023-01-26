from __future__ import annotations

import abc
import enum
from dataclasses import dataclass
from enum import Enum


class Parser:
    pass


class FieldMapper(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getFieldMappings(self, field: SdsQueryFieldName) -> list[SelectCommand]:
        return {
            SdsQueryFieldName.META_VERSION: [],
            SdsQueryFieldName.META_REVISION_DATE: [],
            SdsQueryFieldName.META_PRINT_DATE: [],
            SdsQueryFieldName.PRODUCT_IDENTIFIER: [],
            SdsQueryFieldName.RECOMMENDED_USE_AND_RESTRICTIONS: [],
            SdsQueryFieldName.SUPPLIER_COMPANY: [],
            SdsQueryFieldName.SUPPLIER_ADDRESS: [],
            SdsQueryFieldName.SUPPLIER_TELEPHONE: [],
            SdsQueryFieldName.SUPPLIER_FAX: [],
            SdsQueryFieldName.EMERGENCY_TELEPHONE: [],
            SdsQueryFieldName.IDENTIFICATION_OTHER: [],
            SdsQueryFieldName.SUBSTANCE_CLASSIFICATION: [],
            SdsQueryFieldName.PICTOGRAM: [],
            SdsQueryFieldName.SIGNAL_WORD: [],
            SdsQueryFieldName.HAZARD_STATEMENT: [],
            SdsQueryFieldName.PRECAUTIONARY_STATEMENT: [],
            SdsQueryFieldName.HNOC_HAZARD: [],
        }[field]

    def select(self, target: list[dict] | dict, command: SelectCommand):
        assert isinstance(target, list) and command.where or isinstance(target,
                                                                        dict) and not command.where
        if not command.where:
            return target[command.key]
        else:
            return self.select_where(target, command.key, command.where_value)

    @staticmethod
    def select_where(target: list[dict], where_key: str, where_value: any):
        for item in target:
            for key, value in item.items():
                if where_key == key and where_value == value:
                    return item


@dataclass
class SelectCommand:
    where: bool
    key: str
    where_value: any

    def __init__(self, key, where_value=None):
        self.where = where_value is not None
        self.key = key
        self.where_value = where_value


class SdsQueryFieldName(Enum):
    META_VERSION = enum.auto()  # Document meta version
    META_REVISION_DATE = enum.auto()  # Document supplier-provided revision date
    META_PRINT_DATE = enum.auto()  # Document supplier-provided print date

    PRODUCT_IDENTIFIER = enum.auto()  # Ref. GHS_PRODUCT_IDENTIFIER
    RECOMMENDED_USE_AND_RESTRICTIONS = enum.auto()  # Ref. RECOMMENDED_USE_AND_RESTRICTIONS

    SUPPLIER_COMPANY = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS
    SUPPLIER_ADDRESS = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS
    SUPPLIER_TELEPHONE = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS
    SUPPLIER_FAX = enum.auto()  # Ref. (INSIDE OF!!!) SUPPLIER_DETAILS

    EMERGENCY_TELEPHONE = enum.auto()  # Ref. EMERGENCY_PHONE_NUMBER

    # Ref. OTHER_MEANS_OF_IDENTIFICATION, IDENTIFICATION_OTHER Data dump! No Schema!
    IDENTIFICATION_OTHER = enum.auto()

    SUBSTANCE_CLASSIFICATION = enum.auto()  # Ref. GHS_SUBSTANCE_CLASSIFICATION

    PICTOGRAM = enum.auto()  # Ref. (INSIDE OF!!!) GHS_LABEL_ELEMENTS
    SIGNAL_WORD = enum.auto()  # Ref. (INSIDE OF!!!) GHS_LABEL_ELEMENTS
    HAZARD_STATEMENT = enum.auto()  # Ref. (INSIDE OF!!!) (GHS prefix H) GHS_LABEL_ELEMENTS
    PRECAUTIONARY_STATEMENT = enum.auto()  # Ref. (INSIDE OF!!!) (GHS prefix P) GHS_LABEL_ELEMENTS

    HNOC_HAZARD = enum.auto()  # Ref. OTHER_HAZARDS, HAZARDS_OTHER. Data dump! No Schema!
