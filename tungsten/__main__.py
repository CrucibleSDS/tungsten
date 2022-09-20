from tungsten.parsers.sigma_aldrich import parse_sigma_aldrich


def main() -> None:
    parse_sigma_aldrich("tests/samples/sigma_aldrich_sigma_w5402.pdf")


if __name__ == "__main__":
    main()
