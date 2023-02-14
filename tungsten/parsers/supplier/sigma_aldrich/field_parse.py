import re
from typing import Callable

from tungsten.parsers.field_parse import (
    FieldMapper,
    SdsQueryFieldName,
    SelectCommand
)


class SigmaAldrichFieldMapper(FieldMapper):
    def getFieldMappings(self, field: SdsQueryFieldName) -> tuple[list[SelectCommand], Callable]:
        return {
            # SdsQueryFieldName.META_VERSION: [],
            # SdsQueryFieldName.META_REVISION_DATE: [],
            # SdsQueryFieldName.META_PRINT_DATE: [],
            SdsQueryFieldName.PRODUCT_NAME: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_PRODUCT_IDENTIFIER"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Product\sname", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.PRODUCT_NUMBER: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_PRODUCT_IDENTIFIER"),
                SelectCommand(key="items"),
                SelectCommand(key="name",
                              where_value=re.compile(r"Product\sNumber", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.CAS_NUMBER: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_PRODUCT_IDENTIFIER"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"CAS", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.PRODUCT_BRAND: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_PRODUCT_IDENTIFIER"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Brand", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.RECOMMENDED_USE_AND_RESTRICTIONS: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="RECOMMENDED_USE_AND_RESTRICTIONS"),
                SelectCommand(key="items"),
                SelectCommand(key="name",
                              where_value=re.compile(r"Identified\suses", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.SUPPLIER_ADDRESS: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="SUPPLIER_DETAILS"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Company", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", "".join(x), re.DOTALL).group(1)),
            SdsQueryFieldName.SUPPLIER_TELEPHONE: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="SUPPLIER_DETAILS"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Telephone", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.SUPPLIER_FAX: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="SUPPLIER_DETAILS"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Fax", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", x[0]).group(1)),
            SdsQueryFieldName.EMERGENCY_TELEPHONE: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="EMERGENCY_PHONE_NUMBER"),
                SelectCommand(key="items"),
                SelectCommand(key="name",
                              where_value=re.compile(r"Emergency\sPhone", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.match(r"\:?\s*(.*)", "".join(x), re.DOTALL).group(1)),
            SdsQueryFieldName.IDENTIFICATION_OTHER: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="IDENTIFICATION"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="IDENTIFICATION_OTHER"),
                SelectCommand(key="items")
            ], lambda x: x),
            SdsQueryFieldName.SUBSTANCE_CLASSIFICATION: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="HAZARDS"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_SUBSTANCE_CLASSIFICATION"),
                SelectCommand(key="items")
            ], lambda x: "\n".join(map(lambda y: y["name"], x))),
            SdsQueryFieldName.PICTOGRAM: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="HAZARDS"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_LABEL_ELEMENTS"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Pictogram", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: x),
            SdsQueryFieldName.SIGNAL_WORD: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="HAZARDS"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="GHS_LABEL_ELEMENTS"),
                SelectCommand(key="items"),
                SelectCommand(key="name", where_value=re.compile(r"Signal\sword", re.IGNORECASE)),
                SelectCommand(key="data")
            ], lambda x: re.search(r"(danger|warning)", "".join(x), re.IGNORECASE).group(1)),
            SdsQueryFieldName.HNOC_HAZARD: ([
                SelectCommand(key="sections"),
                SelectCommand(key="title", where_value="HAZARDS"),
                SelectCommand(key="subsections"),
                SelectCommand(key="title", where_value="OTHER_HAZARDS"),
                SelectCommand(key="items"),
            ], lambda x: x)
        }[field]
