import os
from pathlib import Path

from tungsten.globally_harmonized_system.safety_data_sheet import (
    GhsSdsJsonEncoder
)
from tungsten.parsers.field_parse import SdsQueryFieldName
from tungsten.parsers.supplier.sigma_aldrich.field_parse import (
    SigmaAldrichFieldMapper
)
from tungsten.parsers.supplier.sigma_aldrich.sds_parser import (
    SigmaAldrichSdsParser
)

os.environ["TABULA_JAR"] = str(
    (Path(__file__).parent.parent / "tabula-1.0.6-SNAPSHOT-jar-with-dependencies.jar").resolve())

__all__ = ("GhsSdsJsonEncoder", "SigmaAldrichSdsParser", "SigmaAldrichFieldMapper",
           "SdsQueryFieldName")
