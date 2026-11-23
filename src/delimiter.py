from textnode import TextType, TextNode
import re
from enum import Enum

class DelimiterEnum(Enum):
    BOLD = "**"
    ITALIC = "_"
    CODE = "`"

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERD = "unordered_list"
    ORDERED = "ordered_list"

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


def text_to_textnodes(text) -> list[TextNode]:
    text_node = TextNode(text, TextType.TEXT)
    result = [text_node]

    result = split_nodes_delimiter(result, "**", TextType.BOLD)
    result = split_nodes_delimiter(result, "`", TextType.CODE)
    result = split_nodes_delimiter(result, "_", TextType.ITALIC)
    result = split_nodes_image(result)
    result = split_nodes_link(result)
    return result

def markdown_to_blocks(markdown) -> list[str]:
    result = []
    blocks = markdown.split("\n\n")
    for block in blocks:
        clean_block = block.strip()
        if clean_block != "":
            result.append(clean_block)

    return result

def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH