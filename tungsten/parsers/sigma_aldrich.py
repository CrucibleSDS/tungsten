from __future__ import annotations

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTText, LAParams
from pdfminer.layout import LTComponent

from dataclasses import dataclass
from enum import Enum

from tungsten.parsers.globally_harmonized_system import GhsSafetyDataSheet

from io import IOBase


def parse_sigma_aldrich(file: IOBase) -> GhsSafetyDataSheet:
    parsing_elements = import_parsing_elements(file)
    hierarchy = generate_initial_hierarchy(parsing_elements)


def generate_initial_hierarchy(parsing_elements: list[ParsingElement]) -> HierarchyNode:
    """Returns a HierarchyNode representing the initial text parse pass hierarchy based on x values.
    Currently, this function does not catch these edge cases:
     - An element will be further to the left than the first element, this triggers a stack underflow"""

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
    x_stack.append(held_element.page_x0)
    node_stack.append(new_node)

    while len(parsing_elements) > 0:
        # Get next element
        held_element = parsing_elements.pop()
        print(40 * "=" + "\nTesting Element:", held_element.text_content.strip())
        if should_skip_element(held_element):
            print("Decision: skip")
            continue

        # Element is worthy, Pop all stacks
        held_node = node_stack.pop()
        held_x = x_stack.pop()

        # If the element is further to the right, push what we just popped back on the stack
        # Create a new node as a child of the node we popped
        if held_element.page_x0 > held_x:
            print("Decision: push dict")
            # Push stuff back onto stack
            node_stack.append(held_node)
            x_stack.append(held_x)

            # Add new node as a child
            new_node = HierarchyNode(held_element)
            held_node.add_child(new_node)
            node_stack.append(new_node)
            # Push new x level, which is further to the right
            x_stack.append(held_element.page_x0)
        # If the element is at the same level,
        # create a new child of the top node on the node stack (same level from root)
        elif held_element.page_x0 == held_x:
            print("Decision: push element")
            # The x level remains the same, so push back
            x_stack.append(held_x)

            # Add new node at the same level
            new_node = HierarchyNode(held_element)
            node_stack[-1].add_child(new_node)
            node_stack.append(new_node)
        # If the element is further to the left,
        # then we just hold off on doing anything until the x level is equal to that of a previous level
        elif held_element.page_x0 < held_x:
            print("Decision: pop and wait")
            parsing_elements.append(held_element)
        # Should never happen
        else:
            raise Exception
        print("X coordinate stack:", x_stack)

    return hierarchy


def should_skip_element(element: ParsingElement) -> bool:
    """Returns whether this parsing element should not be added to initial hierarchy"""
    return element.text_content.strip() == ""


def import_parsing_elements(file: IOBase):
    # Use pdfminer.six to parse out pdf components, to then convert and add to a list
    parsing_elements = []
    page_y_offset = 0  # Amount to add to ensure y values for subsequent pages are increasingly larger
    # set line_margin=0 to separate fields
    # note that we may need to programmatically join together paragraphs later
    for page in extract_pages(file, laparams=LAParams(line_margin=0)):
        page_length = page.y1 - page.y0
        for component in page:
            parsing_elements.append(ParsingElement(
                component.x0, component.y0, component.x1, component.y1,
                component.x0, page_y_offset + (page_length - component.y0) if component.y0 >= 0 else component.y0,
                component.x1, page_y_offset + (page_length - component.y1) if component.y1 >= 0 else component.y1,
                None,  # TODO Implement PDF item classification to aid figure extraction
                component,
                component.get_text() if isinstance(component, LTText) else "",
                type(component).__name__
            ))
        page_y_offset += page_length  # Add the length of the page to the offset

    parsing_elements.sort(reverse=True)

    return parsing_elements


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
    page_x0: float
    page_y0: float
    page_x1: float
    page_y1: float
    document_x0: float
    document_y0: float
    document_x1: float
    document_y1: float
    type: ParsingElementType  # TODO Currently not implemented
    element: LTComponent
    text_content: str
    class_name: str

    def __lt__(self, other: ParsingElement):
        if self.document_y0 != other.document_y0:
            return self.document_y0 < other.document_y0
        else:
            return self.document_x0 < other.document_x0

    def __str__(self):
        return self.text_content if self.text_content.strip() != "" else self.class_name


class ParsingElementType(Enum):
    """TODO currently unused, enums are placeholders (FIX!), planned for use during figure extraction"""
    TEXT = 1
    VECTOR = 2
    RASTER = 3
