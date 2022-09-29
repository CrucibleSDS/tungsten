from tungsten.parsers.sigma_aldrich import parse_sigma_aldrich


def main() -> None:
    # noinspection PyTypeChecker
    parse_sigma_aldrich(open("tests/samples/sigma_aldrich_sigma_w5402.pdf", "rb", buffering=0))


if __name__ == "__main__":
    main()
