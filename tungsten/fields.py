from __future__ import annotations

import enum
from enum import Enum


class SdsQueryFieldNames(Enum):
    META_VERSION = enum.auto()  # Document meta version
    META_REVISION_DATE = enum.auto()  # Document supplier-provided revision date
    META_PRINT_DATE = enum.auto()  # Document supplier-provided print date\

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
