import json

from tungsten.parsers.globally_harmonized_system import GhsSdsJsonEncoder
from tungsten.parsers.sigma_aldrich import parse_sigma_aldrich
from dataclasses import asdict;

def main() -> None:
    file = open("output.json", "w")
    # noinspection PyTypeChecker
    ghssds = parse_sigma_aldrich(open("tests/samples/sigma_aldrich_sigma_w5402.pdf", "rb", buffering=0))
    json.dump(asdict(ghssds), file, cls=GhsSdsJsonEncoder, skipkeys=True)
    file.close()


if __name__ == "__main__":
    main()
