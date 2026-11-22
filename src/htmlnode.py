class HTMLNode:
    def __init__(self, tag: str = None, value: str = None, children: [HTMLNode] = None, props: {} = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        return f"Tag: {self.tag}; Value: {self.value}; Children: {self.children}; Props: {self.props}"

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self) -> str:
        if self.props == None or len(self.props) == 0:
            return ""

        output_html = ""

        for prop in self.props:
            output_html += f" {prop}=\"{self.props[prop]}\""

        return output_html

class LeafNode(HTMLNode):
    def __init__(self, tag: str, value: str, props: {} = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value == "":
            raise ValueError("All leaf nodes must have a value")

        if self.tag == None:
            return self.value
        
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"Tag: {self.tag}; Value: {self.value}; Props: {self.props}"

class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: [HTMLNode], props: {} = None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag == None or self.tag == "":
            raise ValueError("All parent nodes must have a tag")

        if self.children == [] or self.children == None:
            raise ValueError("All parent nodes must have children")

        result = ""
        for child in self.children:
            result += child.to_html()
        
        return f"<{self.tag}>{self.props_to_html()}{result}</{self.tag}>"