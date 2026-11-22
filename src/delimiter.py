from textnode import TextType, TextNode

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    result = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue

        split_text = node.text.split(delimiter)
        if len(split_text) % 2 == 0:
            raise ValueError(f"No closing delimiter {delimiter!r} found")

        for i, text in enumerate(split_text):
            if text == "":
                continue
            if i % 2 == 1:
                result.append(TextNode(text, text_type))
            else:
                result.append(TextNode(text, TextType.TEXT))

    return result