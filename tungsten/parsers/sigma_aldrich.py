from pprint import pprint

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def parse_sigma_aldrich(filename) -> None:
    elements = [element for elements in extract_pages(filename) for element in elements]

    headers = [
        (index, element)
        for index, element in enumerate(elements)
        if element.x0 == 53.88 and not element.is_empty()
    ]

    raw_sections = [
        elements[header[0]:nheader[0]]
        for (header, nheader) in zip(headers, headers[1:])
    ][1:]

    sections = [
        [element for element in section if not element.is_empty()]
        for section in raw_sections
        if isinstance(section[0], LTTextContainer)
        and not "SECTION" in section[0].get_text()
    ]

    pprint(sections)
