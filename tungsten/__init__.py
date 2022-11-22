import os
from pathlib import Path

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSdsJsonEncoder
)
from tungsten.parsers.supplier.sigma_aldrich.sds_parser import (
    SigmaAldrichSdsParser
)

os.environ["TABULA_JAR"] = str(
    (Path(__file__).parent.parent / "tabula-1.0.6-SNAPSHOT-jar-with-dependencies.jar").resolve())

__all__ = ("GhsSdsJsonEncoder", "SigmaAldrichSdsParser")
