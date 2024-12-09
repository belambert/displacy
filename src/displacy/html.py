# pylint: disable=line-too-long

import xml.etree.ElementTree as ET

# see here:
# https://docs.python.org/3/library/xml.html

# the color could be specified with a class... (e.g. class=color-api-key, color-password)
# the top offset could also be done with a class (e.g. class=level1, level2, etc.)
# but we still need to set the ID based on other info


# counter-reset: ex-counter 0;
# counter-increment: ex-counter 1;
# direction: ltr;

CSS = """
body {
    font-size: 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
    padding: 4rem 2rem;
}
.spans {
    line-height: 1.5 !important;
    font-family: monospace !important;
    list-style-type: none;
}
.label {
    white-space: nowrap;
}
.token_span {
    font-weight: bold;
    display: inline-block;
    position: relative;
}
/* this is the line for non-first tokens */
.span_line {
    height: 4px;
    left: -1px;
    width: calc(100% + 2px);
    position: absolute;
}
/* this is the line for the first token? */
.span_start1 {
    height: 4px;
    border-top-left-radius: 3px;
    border-bottom-left-radius: 3px;
    left: -1px;
    width: calc(100% + 2px);
    position: absolute;
}
/* this is where we put the label */
.span_start2 {
    z-index: 10;
    color: #000;
    top: -0.5em;
    padding: 2px 3px;
    position: absolute;
    font-size: 0.6em;
    font-weight: bold;
    line-height: 1;
    border-radius: 3px
}
.sublabel {
    text-decoration: none;
    color: inherit;
    font-weight: normal
}
.space {
    display: inline-block;
    width: 1em;
}
.unselectable {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
figure {
    margin-bottom: 6rem;
    border-bottom: 1px solid #ccc;
}
"""


def get_unann_span(token: str) -> ET.Element:
    span = ET.Element("span")
    span.text = token
    return span


def get_token_span(token: str, height: int = 60) -> ET.Element:
    span = ET.Element("span", attrib={"class": "token_span"})
    span.set("style", "height: {height};".format(height=height))
    span.text = token
    return span


# this one is just for the line
def get_span_line(color: str, top: int):
    span = ET.Element("span", attrib={"class": "span_line"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg=color, top_offset=top),
    )
    return span


def get_span_start(label: str, color: str, top: int):
    span = ET.Element("span", attrib={"class": "span_start1"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg=color, top_offset=top),
    )
    subspan = ET.SubElement(span, "span", attrib={"class": "span_start2"})
    subspan.set("style", "background: {bg};".format(bg=color))
    subspan.text = label
    return span


# these two for class version
def get_span_line2(tag: str, top: int):
    span = ET.Element("span", attrib={"class": f"span_line {tag}"})
    span.set("style", "top: {top_offset}px;".format(top_offset=top))
    return span


def get_span_start2(label: str, color: str, top: int):
    span = ET.Element("span", attrib={"class": "span_start1"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg=color, top_offset=top),
    )
    subspan = ET.SubElement(span, "span", attrib={"class": "span_start2"})
    subspan.set("style", "background: {bg};".format(bg=color))
    subspan.text = label
    return span


def get_figure():
    figure = ET.Element("figure")
    div = ET.SubElement(figure, "div", attrib={"class": "spans"})
    return figure, div


def get_wrapper():
    html = ET.Element("html")
    head = ET.SubElement(html, "head")
    style = ET.SubElement(head, "style")
    style.text = CSS
    body = ET.SubElement(html, "body")
    return html, body


# def getDOM() -> Document:
#     impl = getDOMImplementation()
#     dt = impl.createDocumentType(
#         "html",
#         "-//W3C//DTD XHTML 1.0 Strict//EN",
#         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
#     )
#     return impl.createDocument("http://www.w3.org/1999/xhtml", "html", dt)
