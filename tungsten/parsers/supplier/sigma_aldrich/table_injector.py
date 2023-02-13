from __future__ import annotations

import logging as logging
import time
from dataclasses import dataclass
from typing import IO

import tabula

from tungsten.parsers.parsing_hierarchy import HierarchyElement
from tungsten.parsers.sds_parser import (
    CoordinateType,
    Injection,
    InjectionBox,
    InjectionOverwriteBoundaryMode,
    SdsParserInjector
)


class SigmaAldrichTableInjector(SdsParserInjector):
    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(f"tungsten:{self.__class__.__name__}")

    def generate_injections(self, io: IO[bytes]) -> list[Injection]:
        start_time = time.perf_counter()
        self.logger.info("Received request to generate table injections")

        # noinspection PyTypeChecker
        json_list: list[dict] = tabula.read_pdf(
            io,
            "json",
            multiple_tables=True,
            pages="all",
            guess=True,
            stream=True,
            silent=False
        )
        tables: list[TabulaTable] = []
        for json_dict in json_list:
            tabula_table = TabulaTable(json_dict)
            if len(tabula_table.data) > 1:
                tables.append(tabula_table)
        for table in tables:
            self.logger.debug(f"Found: {table}")
            # Strip all cells, just in case
            table.strip_text()
            # Tables seem to have dividers between rows when line spacing >12.5 pt.
            table.merge_rows(line_threshold=12.5)
            # Extract remarks to not mess with other tabled data
            table.extract_remarks()
            # Assume that empty cells are references to above cells
            table.pull_down_to_empty()
            # Remove rows with remaining empty cells
            # table.delete_rows_with_empty()
            self.logger.debug(f"Cleaned: {table}")
        self.logger.info(f"Found {len(tables)} tables in "
                         f"{time.perf_counter() - start_time} seconds.")

        i: int = 0
        while i < len(tables):
            if self.reject_table(tables[i]):
                self.logger.debug(f"Rejected: {tables[i]}")
                tables.pop(i)
            else:
                i += 1

        injections: list[Injection] = []
        hardcoded_page_len_ltr: float = 841.92  # TODO do not do this this is bad this is temporary
        # hardcoded_page_wid_ltr: float = 595.32  TODO do not do this this is bad this is temporary
        for table in tables:
            injections.append(Injection(
                boxes=[InjectionBox(
                    page_num=table.page_number,
                    x0=table.left,
                    y0=hardcoded_page_len_ltr - table.bottom,
                    x1=table.left + table.width,
                    y1=hardcoded_page_len_ltr - table.top,
                    coord_type=CoordinateType.PAGE
                )],
                mode=InjectionOverwriteBoundaryMode.INTERSECTS,
                payload=HierarchyElement(
                    page_num=table.page_number,
                    page_x0=table.left,
                    page_y0=hardcoded_page_len_ltr - table.bottom,
                    page_x1=table.left + table.width,
                    page_y1=hardcoded_page_len_ltr - table.top,
                    document_x0=table.page_number * hardcoded_page_len_ltr + table.left,
                    document_y0=table.page_number * hardcoded_page_len_ltr + table.bottom,
                    document_x1=table.page_number * hardcoded_page_len_ltr + table.left +
                    table.width,
                    document_y1=table.page_number * hardcoded_page_len_ltr + table.top,
                    class_name=TabulaTable.__name__,
                    element=table,
                    text_content=str(table)
                )
            ))

        return injections

    @staticmethod
    def reject_table(table: TabulaTable) -> bool:
        # TODO this is a temporary solution
        # TODO reject more tables that are false positives
        try:
            return table.data[1][0].text.strip()[1] == ")"
        except IndexError:
            return True


@dataclass
class TabulaTable:
    """Represents an auto-detected table by Tabula in a PDF."""
    extraction_method: str  # "lattice" or "stream"
    page_number: int  # Page number that the table is on
    top: float  # Distance of top of table from top of page, in points
    bottom: float  # Distance of bottom of table from top of page, in points
    left: float  # Distance of left of table from left of page, in points
    right: float  # Distance of right of table from left of page, in points
    width: float  # Width of table, in points
    height: float  # Height of table, in points
    data: list[list[TabulaTableCell]]  # Double-dimensioned in rows[columns[cell]]
    remarks: dict[int, str]  # Dictionary of "Remarks" rows and a reference to the row # above
    additional_ops: list[str]  # Log of additional post-processing operations after Tabula export

    def __init__(self, json_dict: dict):
        self.extraction_method = json_dict["extraction_method"]
        self.page_number = json_dict["page_number"]
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
        self.remarks = {}
        self.additional_ops = []

    def strip_text(self):
        """Strips whitespace from the text of each cell."""
        for row in self.data:
            for cell in row:
                cell.text = cell.text.strip()
        self.additional_ops.append("strip_text")

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
                    # Above cell is not an empty cell
                    if self.data[i - 1][j].text != "":
                        self.data[i - 1][j].height += row_height
                        self.data[i - 1][j].text += " " + self.data[i][j].text
                self.data.pop(i)
            else:
                i += 1
            last_row_top = row_top
        self.additional_ops.append("merge_rows")

    def extract_remarks(self):
        """Removes rows containing remarks and places then into the remarks dictionary"""
        i: int = 1
        while i < len(self.data):
            is_remark: bool = False
            for j in range(len(self.data[i])):
                if "Remarks" in self.data[i][j].text:
                    is_remark = True
                    remark = " ".join(
                        [self.data[i][k].text for k in range(j + 1, len(self.data[i]))])
                    self.remarks[i - 1] = remark
                    self.data.pop(i)
                    break
            if not is_remark:
                i += 1

    def pull_down_to_empty(self):
        """Pulls down the value of the cell above if the current cell is empty. Does not pull down
        the first row after headers (to not pull down headers)."""
        if len(self.data) < 3:
            return
        for i in range(2, len(self.data)):
            for j in range(len(self.data[i])):
                if self.data[i][j].text == "":
                    self.data[i][j].text = self.data[i - 1][j].text
        self.additional_ops.append("pull_down_to_empty")

    def delete_rows_with_empty(self):
        """Deletes rows with empty cells. Should usually be applied after pull_down_to_empty."""
        i: int = 0
        while i < len(self.data):
            if any([cell.text == "" for cell in self.data[i]]):
                self.data.pop(i)
            else:
                i += 1
        self.additional_ops.append("delete_rows_with_empty")

    def __str__(self):
        output = f"TabulaTable(extraction_method={self.extraction_method}, " \
                 f"page_number={self.page_number}, top={self.top}, bottom={self.bottom}, " \
                 f"left={self.left}, right={self.right}, width={self.width}, " \
                 f"height={self.height}, data="
        if len(self.data) == 0:
            output += "Empty"
        else:
            output += "\n"
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
            for i in range(len(self.data)):
                for j in range(len(self.data[i])):
                    output += f"|{self.data[i][j].text.ljust(max_row_lengths[j])}"
                output += f"|{'Remarks: ' + self.remarks[i] if i in self.remarks else ''}\n"
                output += divider
        output += f", additional_ops={str(self.additional_ops)})"
        return output


@dataclass
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
