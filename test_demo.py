from __future__ import annotations

import glob
import json
import logging
from pathlib import Path
from time import perf_counter

from tungsten import SdsQueryFieldName, SigmaAldrichFieldMapper
from tungsten.parsers.supplier.sigma_aldrich.sds_parser import (
    SigmaAldrichSdsParser
)

# from tungsten.parsers.supplier.sigma_aldrich.table_injector import (
#     SigmaAldrichTableInjector
# )


def main():
    formatter = MultiLineFormatter(
        fmt=u"[%(asctime)s][%(levelname)s][%(name)s] - %(message)s",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setStream(open("table.log", "w", encoding="utf-8"))
    # logging.basicConfig(level=logging.DEBUG, handlers=[handler])
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    parser = SigmaAldrichSdsParser()
    # table_parser = SigmaAldrichTableInjector()

    field_mapper = SigmaAldrichFieldMapper()

    fields = [
        SdsQueryFieldName.PRODUCT_NAME,
        SdsQueryFieldName.PRODUCT_NUMBER,
        SdsQueryFieldName.CAS_NUMBER,
        SdsQueryFieldName.PRODUCT_BRAND,
        SdsQueryFieldName.RECOMMENDED_USE_AND_RESTRICTIONS,
        SdsQueryFieldName.SUPPLIER_ADDRESS,
        SdsQueryFieldName.SUPPLIER_TELEPHONE,
        SdsQueryFieldName.SUPPLIER_FAX,
        SdsQueryFieldName.EMERGENCY_TELEPHONE,
        SdsQueryFieldName.IDENTIFICATION_OTHER,
        SdsQueryFieldName.SUBSTANCE_CLASSIFICATION,
        SdsQueryFieldName.PICTOGRAM,
        SdsQueryFieldName.SIGNAL_WORD,
        SdsQueryFieldName.HNOC_HAZARD,
    ]

    for filename in glob.glob(str(Path('msds', '*.pdf').absolute())):
        file_start_time = perf_counter()
        logging.info(f"Processing {filename}")
        with open(filename, "rb") as f:
            parsed = parser.parse_to_ghs_sds(f)
            with open(Path('msds', 'output',
                           str(Path(filename).relative_to(Path('msds').absolute())) + ".json"),
                      'w') as fw:
                parsed.dump(fw)
            with open(Path('msds', 'mapped',
                           str(Path(filename).relative_to(Path('msds').absolute())) + ".json"),
                      'w') as fw:
                temp = {}
                for field in fields:
                    temp[field.name] = field_mapper.getField(field, json.loads(parsed.dumps()))
                json.dump(temp, fw)
            # table_parser.generate_injections(f)
        logging.info(f'Parse complete in {perf_counter() - file_start_time} seconds.')


class MultiLineFormatter(logging.Formatter):
    def format(self, record):
        header: str = super().format(
            logging.LogRecord(
                name=record.name,
                level=record.levelno,
                pathname=record.pathname,
                lineno=record.lineno,
                msg="",  # omit record.msg
                args=(),  # omit record.args
                exc_info=None  # omit record.exc_info
            ))
        first, *trailing = super().format(record).splitlines(keepends=False)
        return first + ('\n' if len(trailing) else '') + ''.join(
            f"{header[0:-2]}  {line}\n" for line in trailing)[0:-1]


if __name__ == "__main__":
    main()
