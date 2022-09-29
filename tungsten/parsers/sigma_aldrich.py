from collections import deque
from pprint import pprint
import json

import pdfminer.layout
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdfminer.layout import LTComponent
from pdfminer.layout import LTText
from pdfminer.layout import LTItem

from dataclasses import dataclass
from enum import Enum


class ParsingElementType(Enum):
    TEXT = 1
    VECTOR = 2
    RASTER = 3


@dataclass
class ParsingElement:
    """Class used to abstract PDF objects into parsing objects"""
    x0: float
    y0: float
    x1: float
    y1: float
    type: ParsingElementType
    element: LTItem
    name: str

    def __lt__(self, other):
        return self.y0 < other.y0


def convert_to_parsing_element(lt_item: LTItem):
    return ParsingElement(lt_item.x0, lt_item.y0, lt_item.x1, lt_item.y1,
                          None,
                          lt_item,
                          lt_item.get_text() if isinstance(lt_item, LTText) else type(lt_item).__name__)


def generateUniqueName(proposedName: str, nameSet: set):
    if proposedName in nameSet:
        return proposedName + "'"
    else:
        return proposedName


def parse_sigma_aldrich(filename) -> None:
    # Currently this program does not catch these edge cases:
    # - An element will be further to the left than the first element, this triggers a stack underflow

    elements = [element for elements in extract_pages(filename) for element in elements]

    parsingelements = [convert_to_parsing_element(element) for element in elements]
    parsingelements.reverse()
    print(parsingelements)

    # Data Structures
    docudata = {}  # nested dictionaries, represents the parsing structure
    levelstack = []  # stack of dictionaries, used to remember higher level dictionaries
    existingnames = []  # stack of sets, used to remember reused names in each scope
    xstack = []  # stack of x coordinates

    # Append and update base dictionary
    levelstack.append(docudata)
    existingnames.append(set())

    # Append and update initial dictionary
    heldelement = parsingelements.pop()
    xstack.append(heldelement.x0)
    levelstack.append({})
    existingnames.append(set())
    docudata[generateUniqueName(heldelement.name, existingnames[-1])] = levelstack[-1]

    while len(parsingelements) > 0:
        # Pop all stacks, get next element
        heldDictionary = levelstack.pop()
        heldElement = parsingelements.pop()
        heldNames = existingnames.pop()
        heldX = xstack.pop()
        print("======================================\nTesting Element:", heldElement.name.strip())
        # If the element is further to the right, push what we just popped back on the stack
        # Create a new dictionary underneath the dictionary we popped
        if heldElement.x0 > heldX:
            print("Decision: push dict")
            # Push stuff back onto stack
            levelstack.append(heldDictionary)
            existingnames.append(heldNames)
            xstack.append(heldX)

            # Add new dictionary one level down
            newDictionary = {}
            heldDictionary[generateUniqueName(heldElement.name, existingnames[-1])] = newDictionary
            levelstack.append(newDictionary)
            existingnames.append(set())
            # Push new x level, which is further to the right
            xstack.append(heldElement.x0)
        # If the element is at the same level,
        # create a new dictionary at the same level as the dictionary we popped
        elif heldElement.x0 == heldX:
            print("Decision: push element")
            # The x level remains the same
            xstack.append(heldX)

            # Add new dictionary at the same level
            newDictionary = {}
            levelstack[-1][generateUniqueName(heldElement.name, existingnames[-1])] = newDictionary
            levelstack.append(newDictionary)
            existingnames.append(set())
        # If the element is further to the left,
        # then we just hold off on doing anything until the x level is equal to that of a previous level
        elif heldElement.x0 < heldX:
            print("Decision: pop and wait")
            parsingelements.append(heldElement)
        # Should never happen
        else:
            raise Exception
        print("X coordinate stack:", xstack)

    myFile = open("output.json", "w")
    myFile.write(json.dumps(docudata, sort_keys=False, indent=2))
    myFile.close()
