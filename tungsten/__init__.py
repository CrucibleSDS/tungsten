import os

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSdsJsonEncoder
)
from tungsten.parsers.supplier.sigma_aldrich.sds_parser import (
    SigmaAldrichSdsParser
)

__all__ = ("GhsSdsJsonEncoder", "SigmaAldrichSdsParser")

os.environ["TABULA_JAR"] = "tabula-1.0.6-SNAPSHOT-jar-with-dependencies.jar"
