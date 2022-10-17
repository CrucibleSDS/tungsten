import json
import time
from dataclasses import asdict
from pathlib import Path

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import \
    GhsSdsJsonEncoder
from tungsten.parsers.supplier.sigma_aldrich.sds_parser import \
    SigmaAldrichSdsParser


def main() -> None:
    paths = Path(".").glob("./tests/samples/*.pdf")

    for path in paths:
        start = time.perf_counter()

        with open(path, "rb", buffering=0) as f:
            ghs_sds = SigmaAldrichSdsParser().parse_to_ghs_sds(f, sds_name=path.stem)

        with open(Path("./output") / (path.stem + ".json"), "w") as f:
            json.dump(asdict(ghs_sds), f, cls=GhsSdsJsonEncoder, skipkeys=True)

        print(time.perf_counter() - start, "seconds")


if __name__ == "__main__":
    main()
