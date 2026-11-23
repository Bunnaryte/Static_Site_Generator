from textnode import TextType, TextNode
import re

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

def extract_markdown_images(text: str):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text: str):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    result = []

    for node in old_nodes:
        if node.text == "":
            continue
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue

        extracted = extract_markdown_images(node.text)
        if len(extracted) == 0:
            result.append(node)
            continue

        alt_text, source = extracted[0]
        split_text = node.text.split(f"![{alt_text}]({source})", 1)

        if split_text[0] != "":
            result.append(TextNode(split_text[0], TextType.TEXT))

        result.append(TextNode(alt_text, TextType.IMAGE, source))
        if split_text[1] != "":
           result.extend(split_nodes_image([TextNode(split_text[1], TextType.TEXT)]))

    return result

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    result = []

    for node in old_nodes:
        if node.text == "":
            continue
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue

        extracted = extract_markdown_links(node.text)
        if len(extracted) == 0:
            result.append(node)
            continue

        link_text, source = extracted[0]
        split_text = node.text.split(f"[{link_text}]({source})", 1)

        if split_text[0] != "":
            result.append(TextNode(split_text[0], TextType.TEXT))
            
        result.append(TextNode(link_text, TextType.LINK, source))
        if split_text[1] != "":
           result.extend(split_nodes_link([TextNode(split_text[1], TextType.TEXT)]))

    return result