from __future__ import annotations


class HierarchyNode:
    """Represents a node in the hierarchy of ParsingElements,
    may have multiple ordered children."""
    data: HierarchyElement
    children: list[HierarchyNode]
    is_root: bool

    def add_child(self, new_child: HierarchyNode):
        if new_child.is_root:
            raise ValueError("The child of a hierarchy node cannot be a root node.")
        self.children.append(new_child)

    def __init__(self, data: HierarchyElement = None, is_root: bool = False):
        self.data = data
        self.children = []
        self.is_root = is_root

    def __str__(self):
        # The general indent to denote child elements
        indent = "| "
        # The indent used on the first line of a direct child of the node
        direct_child_indent = "|-"
        # Flag for whether the current line is the first line of a child element
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


class HierarchyElement:
    """Class used to abstract PDF objects into parsing objects"""
    page_num: int
    page_x0: float
    page_y0: float
    page_x1: float
    page_y1: float
    document_x0: float
    document_y0: float
    document_x1: float
    document_y1: float
    element: any
    text_content: str
    class_name: str
    to_delete: bool

    def set_delete(self):
        self.to_delete = True

    def __init__(self, page_num: int, page_x0: float, page_y0: float, page_x1: float,
                 page_y1: float, document_x0: float, document_y0: float, document_x1: float,
                 document_y1: float, element: any, text_content: str, class_name: str):
        self.page_num = page_num
        self.page_x0 = page_x0
        self.page_y0 = page_y0
        self.page_x1 = page_x1
        self.page_y1 = page_y1
        self.document_x0 = document_x0
        self.document_y0 = document_y0
        self.document_x1 = document_x1
        self.document_y1 = document_y1
        self.element = element
        self.text_content = text_content
        self.class_name = class_name
        self.to_delete = False

    def __lt__(self, other: HierarchyElement):
        if self.document_y0 != other.document_y0:
            return self.document_y0 < other.document_y0
        else:
            return self.document_x0 < other.document_x0

    def __str__(self):
        s = f"{self.text_content.strip() if self.text_content.strip() != '' else self.class_name}"\
            # f"(x{self.page_x0},y{self.page_y0}),(x{self.page_x1},y{self.page_y1})"
        return s
