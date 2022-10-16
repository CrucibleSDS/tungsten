import json
import os
import time
from dataclasses import asdict

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import \
    GhsSdsJsonEncoder
from tungsten.parsers.supplier.sigma_aldrich.sds_parser import \
    SigmaAldrichSdsParser


def main() -> None:
    files = os.listdir("./tests/samples/")
    paths = ["./tests/samples/" + file for file in files]

    for i in range(len(paths)):
        start = time.perf_counter()
        sds_name = files[i].split(sep=".")[0]
        # noinspection PyTypeChecker
        ghs_sds = SigmaAldrichSdsParser().parse(open(paths[i], "rb", buffering=0),
                                                sds_name=sds_name)
        file = open("./output/" + sds_name + ".json", "w")
        json.dump(asdict(ghs_sds), file, cls=GhsSdsJsonEncoder, skipkeys=True)
        file.close()
        print(time.perf_counter() - start, "seconds")


if __name__ == "__main__":
    main()
