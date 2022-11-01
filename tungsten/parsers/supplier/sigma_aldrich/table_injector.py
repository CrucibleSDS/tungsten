from __future__ import annotations

from io import IOBase
from subprocess import CalledProcessError
from typing import IO

import tabula

from tungsten.parsers.sds_parser import SdsParserInjector, Injection


class SigmaAldrichTableInjector(SdsParserInjector):
    def generate_injections(self, io: IO[bytes]) -> list[Injection]:
        page_num: int = 1
        out_of_pages = False
        while not out_of_pages:
            try:
                # noinspection PyTypeChecker
                json_list: list[dict] = tabula.read_pdf(
                    io,
                    "json",
                    multiple_tables=True,
                    pages=page_num,
                    guess=True,
                    stream=True,
                    silent=False
                )
                tables: list[TabulaTable] = []
                for json_dict in json_list:
                    tables.append(TabulaTable(json_dict))
                    tables[-1].merge_rows()

                print(f"Page {page_num} has {len(tables)} tables.")
                for table in tables:
                    print(table)
                page_num += 1
            # tabula-java crashes when it tries to parse a page that doesn't exist
            except CalledProcessError:
                # tabula-py seems to put tabula-java traces on stderr, so there doesn't seem to
                # be a way to check if the error was specifically caused by a page not existing
                # (i.e. IndexOutOfBoundsException)
                out_of_pages = True
        return []

    def injection_hook(self, injections: list[Injection]):
        pass


class TabulaTable:
    """Represents an auto-detected table by Tabula in a PDF."""
    extraction_method: str  # "lattice" or "stream"
    top: float  # Distance of top of table from top of page, in points
    bottom: float  # Distance of bottom of table from top of page, in points
    left: float  # Distance of left of table from left of page, in points
    right: float  # Distance of right of table from left of page, in points
    width: float  # Width of table, in points
    height: float  # Height of table, in points
    data: list[list[TabulaTableCell]]  # Double-dimensioned in rows[columns[cell]]

    def __init__(self, json_dict: dict):
        self.extraction_method = json_dict["extraction_method"]
        self.top = json_dict["top"]
        self.bottom = json_dict["bottom"]
        self.left = json_dict["left"]
        self.right = json_dict["right"]
        self.width = json_dict["width"]
        self.height = json_dict["height"]
        self.data = [
            [TabulaTableCell(cell) for cell in row
             ] for row in json_dict["data"]
        ]

    def merge_rows(self, line_threshold: float = 12.5):
        """Merges rows that are within line_threshold points of each other."""
        i: int = 1
        last_row_top: float = max([cell.top for cell in self.data[0]])
        while i < len(self.data):
            row_top = max([cell.top for cell in self.data[i]])
            row_height = max([cell.height for cell in self.data[i]])
            if row_top - last_row_top < line_threshold:
                # This row is within line_threshold points of the top of the page
                # Merge it with the row above it
                for j in range(len(self.data[i])):
                    # Above cell is not an empty cell (Tabula fills empty cells with 0s)
                    if self.data[i - 1][j].top != 0:
                        self.data[i - 1][j].height += row_height
                        self.data[i - 1][j].text += " " + self.data[i][j].text
                self.data.pop(i)
            else:
                i += 1
            last_row_top = row_top

    def __str__(self):
        output = f"TabulaTable(extraction_method={self.extraction_method}, " \
                 f"top={self.top}, bottom={self.bottom}, left={self.left}, " \
                 f"right={self.right}, width={self.width}, height={self.height}, " \
                 f"data=\n"

        # Find the width of the widest cell in each column
        max_row_lengths: list[int] = [0] * len(self.data[0])
        for row in self.data:
            for i in range(len(row)):
                max_row_lengths[i] = max(max_row_lengths[i], len(row[i].text))
        # Generate the horizontal divider
        divider: str = ""
        for max_row_length in max_row_lengths:
            divider += f"+{'-' * max_row_length}"
        divider += "+\n"
        # Generate the table
        output += divider
        for row in self.data:
            for i in range(len(row)):
                output += f"|{row[i].text.ljust(max_row_lengths[i])}"
            output += "|\n"
            output += divider
        output += ")"
        return output


class TabulaTableCell:
    """Represents a cell in a :class:`TabulaTable`."""
    top: float  # Distance of top of cell from top of page, in points
    left: float  # Distance of left of cell from left of page, in points
    width: float  # Width of cell, in points
    height: float  # Height of cell, in points
    text: str  # Text in cell

    def __init__(self, json_dict: dict):
        self.top = json_dict["top"]
        self.left = json_dict["left"]
        self.width = json_dict["width"]
        self.height = json_dict["height"]
        self.text = json_dict["text"]

    def __str__(self):
        return self.text
