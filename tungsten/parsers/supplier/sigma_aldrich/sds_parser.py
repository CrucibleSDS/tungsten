from __future__ import annotations

from io import IOBase
from typing import IO

import pdfminer.high_level as pdfm
from pdfminer.layout import LAParams, LTText

from tungsten.globally_harmonized_system.safety_data_sheet import (
    GhsSafetyDataSheet,
    GhsSdsItem,
    GhsSdsItemType,
    GhsSdsSection,
    GhsSdsSectionTitle,
    GhsSdsSubsection
)
from tungsten.parsers.parsing_hierarchy import HierarchyElement, HierarchyNode
from tungsten.parsers.sds_parser import SdsParser
from tungsten.parsers.supplier.sigma_aldrich.safety_data_sheet_rules import (
    SigmaAldrichGhsSdsRules
)
from tungsten.parsers.supplier.sigma_aldrich.table_injector import (
    SigmaAldrichTableInjector
)


class SigmaAldrichSdsParser(SdsParser):
    sds_rules: SigmaAldrichGhsSdsRules

    def __init__(self):
        super().__init__()
        self.sds_rules = SigmaAldrichGhsSdsRules()
        self.register_injector(SigmaAldrichTableInjector())

    def _parse_to_hierarchy(self, io: IO[bytes]) -> HierarchyNode:
        # noinspection PyTypeChecker
        parsing_elements = self.import_parsing_elements(io)
        hierarchy = self.generate_initial_hierarchy(parsing_elements)
        section_node = self.generate_section_hierarchy(hierarchy)
        return section_node

    def _hierarchy_to_ghs_sds(self, root: HierarchyNode) -> GhsSafetyDataSheet:
        ghs_sds = GhsSafetyDataSheet(
            name="default",  # TODO figure out what to do with names
            sections=self.identify_ghs_sections(root.children)
        )
        return ghs_sds

    def generate_section_hierarchy(self, hierarchy: HierarchyNode) -> HierarchyNode:
        """In a Sigma-Aldrich SDS, the sections are at the same x-level as the subsections.
        It's useful to have subsection nodes underneath the section nodes, so this method fulfills
        this purpose."""
        # We assume that the GHS SDS sections are children of the root node.
        # This may node always be the case. TODO implement level search of GHS SDS sections
        sds_root_node = HierarchyNode(is_root=True)
        for child in hierarchy.children:
            if self.sds_rules.is_section(child.data.text_content):
                sds_root_node.add_child(child)
            else:
                if len(sds_root_node.children):
                    sds_root_node.children[-1].add_child(child)
        return sds_root_node

    def identify_ghs_sections(self, sds_children: list[HierarchyNode]) -> list[GhsSdsSection]:
        """Applies the rules specified in :class:`SigmaAldrichGhsSdsRules` to create list of
        :class:`GhsSdsSection` objects from :class:`HierarchyNode` objects."""
        ghs_sections: list[GhsSdsSection] = []
        for child in sds_children:
            if self.sds_rules.is_section(child.data.text_content):
                section_title = self.sds_rules.discriminate_section(child.data.text_content)
                assert section_title is not None
                ghs_sections.append(GhsSdsSection(
                    section_title,
                    self.identify_ghs_subsections(child.children, section_title)
                ))
        return ghs_sections

    def identify_ghs_subsections(
            self,
            section_children: list[HierarchyNode],
            context: GhsSdsSectionTitle,
    ) -> list[GhsSdsSubsection]:
        """Applies the rules specified in :class:`SigmaAldrichGhsSdsRules` to create list of
        :class:`GhsSdsSubection` objects from :class:`HierarchyNode` objects.
        Note that this method requires a `context` :class:`GhsSdsSectionTitle`, as the ruleset
        requires this to be able to identify subsections. (This is to prevent incorrectly matching
        a subsection of another section,)"""
        # TODO detect/assume section type more thoroughly.
        # Currently, it is assumed that all items are LIST
        ghs_subsections: list[GhsSdsSubsection] = []
        for child in section_children:
            subsection_title = self.sds_rules \
                .discriminate_subsection(child.data.text_content, context)
            ghs_subsections.append(GhsSdsSubsection(
                subsection_title,
                [GhsSdsItem(
                    type=GhsSdsItemType.FIELD,
                    name=str(subchild.data),
                    data=self.flatten_to_children_str(subchild)) for subchild in child.children],
                child.data.text_content
            ))
        return ghs_subsections

    @staticmethod
    def flatten_to_children_str(head: HierarchyNode) -> list[str]:
        """Flattens an entire tree of HierarchyNodes to a list of strings (DFS)"""
        names: list[str] = []
        stack: list[HierarchyNode] = head.children
        while len(stack):
            # Pop
            hand = stack.pop()

            # Process
            names.append(str(hand.data))

            # Push
            for child in hand.children:
                stack.append(child)
        return names

    def generate_initial_hierarchy(self,
                                   parsing_elements: list[HierarchyElement]) -> HierarchyNode:
        """Returns a HierarchyNode representing the initial text parse pass hierarchy based on x
        Currently, this function does not catch these edge cases:
         - An element will be further to the left than the first element,
         this triggers a stack underflow"""

        # Data Structures
        hierarchy = HierarchyNode(
            is_root=True)  # root node. the tree represents the parsing hierarchy
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
            if self.should_skip_element(held_element):
                continue

            # Element is worthy, Pop all stacks
            held_node = node_stack.pop()
            held_x = x_stack.pop()

            # If the element is further to the right, push what we just popped back on the stack
            # Create a new node as a child of the node we popped
            if held_element.page_x0 > held_x:
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
                parsing_elements.append(held_element)
            # Should never happen
            else:
                raise Exception

        return hierarchy

    @staticmethod
    def should_skip_element(element: HierarchyElement) -> bool:
        """Returns whether this parsing element should not be added to initial hierarchy.
        Currently, all elements which are non-text data, or within the footer are removed."""
        should_skip = False
        # Skip if the text entry is empty
        should_skip = should_skip or element.text_content.strip() == ""
        # Skip if element is in footer
        should_skip = should_skip or element.page_y0 < 125
        return should_skip

    @staticmethod
    def import_parsing_elements(io: IOBase) -> list[HierarchyElement]:
        """Given an IOBase, returns a list of :class:`ParsingElement` objects that represent
        elements within the PDF of the Sigma-Aldrich SDS."""
        # Use pdfminer.six to parse out pdf components, to then convert and add to a list
        parsing_elements = []
        # Amount to add to ensure y values for subsequent pages are increasingly larger
        page_y_offset = 0
        # Keep track of page number
        page_number = 1
        # set line_margin=0 to separate fields
        # note that we may need to programmatically join together paragraphs later
        for page in pdfm.extract_pages(io, laparams=LAParams(line_margin=0)):
            page_length = page.y1 - page.y0
            for component in page:
                parsing_elements.append(HierarchyElement(
                    page_num=page_number,
                    page_x0=component.x0,
                    page_y0=component.y0,
                    page_x1=component.x1,
                    page_y1=component.y1,
                    document_x0=component.x0,
                    document_y0=page_y_offset + (page_length - component.y0)
                    if component.y0 >= 0 else component.y0,
                    document_x1=component.x1,
                    document_y1=page_y_offset + (page_length - component.y1)
                    if component.y1 >= 0 else component.y1,
                    element=component,
                    text_content=component.get_text() if isinstance(component, LTText) else "",
                    class_name=type(component).__name__
                ))
            page_y_offset += page_length  # Add the length of the page to the offset
            page_number += 1

        parsing_elements.sort(reverse=True)

        return parsing_elements
