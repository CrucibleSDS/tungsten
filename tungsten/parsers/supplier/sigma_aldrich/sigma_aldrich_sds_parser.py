from __future__ import annotations

import re
from io import IOBase

import pdfminer.high_level as pdfm
from pdfminer.layout import LAParams, LTText

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSafetyDataSheet, GhsSdsItem, GhsSdsItemType, GhsSdsSection,
    GhsSdsSectionTitle, GhsSdsSubsection, GhsSdsSubsectionTitle)
from tungsten.parsers.parsing_hierarchy import HierarchyNode, ParsingElement
from tungsten.parsers.sds_parser import SdsParser


class SigmaAldrichSdsParser(SdsParser):
    def parse(self, io: IOBase) -> GhsSafetyDataSheet:
        parsing_elements = import_parsing_elements(io)
        hierarchy = generate_initial_hierarchy(parsing_elements)
        section_nodes = generate_section_hierarchy(hierarchy)

        ghs_sections: list[GhsSdsSection] = []
        for i in range(13):
            ghs_sections.append(GhsSdsSection(
                GhsSdsSectionTitle(i + 1),
                identify_ghs_subsections(section_nodes.children[i].children)
            ))

        for i in range(13, 16, 1):
            ghs_sections.append(GhsSdsSection(
                GhsSdsSectionTitle(i + 1),
                [GhsSdsSubsection(
                    GhsSdsSubsectionTitle(str(i + 1) + ".1"),
                    [GhsSdsItem(GhsSdsItemType.LIST, subchild)
                     for subchild in section_nodes.children[i].children]
                )]
            ))

        ghs: GhsSafetyDataSheet = GhsSafetyDataSheet("placeholder", ghs_sections)
        return ghs


def generate_section_hierarchy(hierarchy: HierarchyNode) -> HierarchyNode:
    # We assume that the GHS SDS sections are children of the root node.
    # This may node always be the case. TODO implement level search of GHS SDS sections
    regex_section = re.compile(r"([A-Z])+\s+\d?\d?:\s+[\w\s]+")
    sds_root_node = HierarchyNode(is_root=True)
    for child in hierarchy.children:
        if regex_section.match(child.data.text_content) is not None:
            sds_root_node.add_child(child)
        else:
            if len(sds_root_node.children):
                sds_root_node.children[-1].add_child(child)

    assert len(sds_root_node.children) == 16

    return sds_root_node


def identify_ghs_subsections(section_children: list[HierarchyNode]) -> list[GhsSdsSubsection]:
    # TODO detect/assume section type more thoroughly.
    # Currently it is assumed that all items are LIST
    regex_subsection = re.compile(r"(^\d?\d\.\d)\s+[\w\s]+$")
    subsection_ghs: list[GhsSdsSubsection] = []
    for child in section_children:
        match = regex_subsection.match(child.data.text_content)
        if match is not None:
            subsection_ghs.append(GhsSdsSubsection(
                GhsSdsSubsectionTitle(match.group(1)),
                [GhsSdsItem(GhsSdsItemType.LIST, subchild) for subchild in child.children]
            ))
    return subsection_ghs


def generate_initial_hierarchy(parsing_elements: list[ParsingElement]) -> HierarchyNode:
    """Returns a HierarchyNode representing the initial text parse pass hierarchy based on x values
    Currently, this function does not catch these edge cases:
     - An element will be further to the left than the first element,
     this triggers a stack underflow"""

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
        #  print(40 * "=" + "\nTesting Element:", held_element.text_content.strip())
        if should_skip_element(held_element):
            #  print("Decision: skip")
            continue

        # Element is worthy, Pop all stacks
        held_node = node_stack.pop()
        held_x = x_stack.pop()

        # If the element is further to the right, push what we just popped back on the stack
        # Create a new node as a child of the node we popped
        if held_element.page_x0 > held_x:
            #  print("Decision: push dict")
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
            #  print("Decision: push element")
            # The x level remains the same, so push back
            x_stack.append(held_x)

            # Add new node at the same level
            new_node = HierarchyNode(held_element)
            node_stack[-1].add_child(new_node)
            node_stack.append(new_node)
        # If the element is further to the left,
        # then we just hold off on doing anything
        # until the x level is equal to that of a previous level
        elif held_element.page_x0 < held_x:
            #  print("Decision: pop and wait")
            parsing_elements.append(held_element)
        # Should never happen
        else:
            raise Exception
        #  print("X coordinate stack:", x_stack)

    return hierarchy


def should_skip_element(element: ParsingElement) -> bool:
    """Returns whether this parsing element should not be added to initial hierarchy"""
    should_skip = False
    # Skip if the text entry is empty
    should_skip = should_skip or element.text_content.strip() == ""
    # Skip if element is in footer
    should_skip = should_skip or element.page_y0 < 125
    return should_skip


def import_parsing_elements(file: IOBase):
    # Use pdfminer.six to parse out pdf components, to then convert and add to a list
    parsing_elements = []
    # Amount to add to ensure y values for subsequent pages are increasingly larger
    page_y_offset = 0
    # set line_margin=0 to separate fields
    # note that we may need to programmatically join together paragraphs later
    for page in pdfm.extract_pages(file, laparams=LAParams(line_margin=0)):
        page_length = page.y1 - page.y0
        for component in page:
            parsing_elements.append(ParsingElement(
                component.x0, component.y0, component.x1, component.y1,
                component.x0, page_y_offset + (page_length - component.y0)
                if component.y0 >= 0 else component.y0,
                component.x1, page_y_offset + (page_length - component.y1)
                if component.y1 >= 0 else component.y1,
                None,  # TODO Implement PDF item classification to aid figure extraction
                component,
                component.get_text() if isinstance(component, LTText) else "",
                type(component).__name__
            ))
        page_y_offset += page_length  # Add the length of the page to the offset

    parsing_elements.sort(reverse=True)

    return parsing_elements
