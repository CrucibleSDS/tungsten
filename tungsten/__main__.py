import json
import os
import time

from tungsten.parsers.globally_harmonized_system import GhsSdsJsonEncoder
from tungsten.parsers.sigma_aldrich import parse_sigma_aldrich
from dataclasses import asdict;


def main() -> None:
    files = os.listdir("./tests/samples/")
    paths = ["./tests/samples/" + file for file in files]

    for i in range(len(paths)):
        start = time.perf_counter()
        # noinspection PyTypeChecker
        ghssds = parse_sigma_aldrich(open(paths[i], "rb", buffering=0))
        file = open("./output/" + files[i].split(sep=".")[0] + ".json", "w")
        json.dump(asdict(ghssds), file, cls=GhsSdsJsonEncoder, skipkeys=True)
        file.close()
        print(time.perf_counter() - start, "seconds")


if __name__ == "__main__":
    main()
