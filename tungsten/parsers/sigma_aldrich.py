from __future__ import annotations

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTText
from pdfminer.layout import LTItem

from dataclasses import dataclass
from enum import Enum


def parse_sigma_aldrich(filename: str) -> HierarchyNode:
    # Currently this program does not catch these edge cases:
    # - An element will be further to the left than the first element, this triggers a stack underflow

    parsing_elements = import_parsing_elements(filename)

    # Data Structures
    hierarchy = HierarchyNode(is_root=True)  # root node. the tree represents the parsing hierarchy
    node_stack = []  # stack of dictionaries, used to remember higher level dictionaries
    x_stack = []  # stack of x coordinates

    # Push root node to stack
    node_stack.append(hierarchy)

    # Push initial node to datastructures
    held_element = parsing_elements.pop()
    new_node = HierarchyNode(held_element)
    hierarchy.add_child(new_node)
    x_stack.append(held_element.x0)
    node_stack.append(new_node)

    while len(parsing_elements) > 0:
        # Pop all stacks, get next element
        held_element = parsing_elements.pop()
        held_node = node_stack.pop()
        held_x = x_stack.pop()
        print(40 * "=" + "\nTesting Element:", held_element.name.strip())

        # If the element is further to the right, push what we just popped back on the stack
        # Create a new node as a child of the node we popped
        if held_element.x0 > held_x:
            print("Decision: push dict")
            # Push stuff back onto stack
            node_stack.append(held_node)
            x_stack.append(held_x)

            # Add new node as a child
            new_node = HierarchyNode(held_element)
            held_node.add_child(new_node)
            node_stack.append(new_node)
            # Push new x level, which is further to the right
            x_stack.append(held_element.x0)
        # If the element is at the same level,
        # create a new child of the top node on the node stack (same level from root)
        elif held_element.x0 == held_x:
            print("Decision: push element")
            # The x level remains the same, so push back
            x_stack.append(held_x)

            # Add new node at the same level
            new_node = HierarchyNode(held_element)
            node_stack[-1].add_child(new_node)
            node_stack.append(new_node)
        # If the element is further to the left,
        # then we just hold off on doing anything until the x level is equal to that of a previous level
        elif held_element.x0 < held_x:
            print("Decision: pop and wait")
            parsing_elements.append(held_element)
        # Should never happen
        else:
            raise Exception
        print("X coordinate stack:", x_stack)

    return hierarchy


def import_parsing_elements(filename: str):
    # Use pdfminer.six to parse out pdf items
    pdf_items = []
    for elements in extract_pages(filename):
        for element in elements:
            pdf_items.append(element)
    # Push converted elements in reverse, such that they are popped in order (maybe use a deque for clarity?)
    parsing_elements = []
    for i in range(len(pdf_items) - 1, -1, -1):
        parsing_elements.append(convert_to_parsing_element(pdf_items[i]))
    return parsing_elements


def convert_to_parsing_element(lt_item: LTItem):
    """Bare-bones converter from LTItem to parsing element.
    TODO Maybe wrap this into the ParsingElement constructor later
    TODO Implement PDF item classification to aid figure extraction"""
    return ParsingElement(lt_item.x0, lt_item.y0, lt_item.x1, lt_item.y1,
                          None,
                          lt_item,
                          lt_item.get_text() if isinstance(lt_item,
                                                           LTText) and lt_item.get_text().strip() != "" else type(
                              lt_item).__name__)


class HierarchyNode:
    """Represents a node in the hierarchy of ParsingElements, may have multiple ordered children."""
    data: ParsingElement
    children: list
    is_root: bool

    def add_child(self, new_child: HierarchyNode):
        if new_child.is_root:
            raise ValueError("The child of a hierarchy node cannot be a root node.")
        self.children.append(new_child)

    def __init__(self, data: ParsingElement = None, is_root: bool = False):
        self.data = data
        self.children = []
        self.is_root = is_root

    def __str__(self):
        indent = "| "  # The general indent to denote child elements
        direct_child_indent = "|-"  # The indent used on the first line of a direct child of the node
        direct_child_flag = True

        # The first line should always be string representation of data, unless it's the root node.
        output = ("<ROOT>" if self.is_root else str(self.data).strip()) + ":\n"

        # Recursively generate the string representation of the hierarchy
        for child in self.children:
            for line in str(child).splitlines():
                if direct_child_flag:
                    direct_child_flag = False
                    output += direct_child_indent + line + "\n"
                else:
                    output += indent + line + "\n"
            direct_child_flag = True
        return output


@dataclass
class ParsingElement:
    """Class used to abstract PDF objects into parsing objects"""
    x0: float
    y0: float
    x1: float
    y1: float
    type: ParsingElementType  # TODO Currently not implemented
    element: LTItem
    name: str

    def __lt__(self, other):
        return self.y0 < other.y0  # TODO replace with canon y sorting after implementation of canon y

    def __str__(self):
        return self.name


class ParsingElementType(Enum):
    """TODO currently unused, enums are placeholders (FIX!), planned for use during figure extraction"""
    TEXT = 1
    VECTOR = 2
    RASTER = 3
