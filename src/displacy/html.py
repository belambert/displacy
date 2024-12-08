# pylint: disable=line-too-long

import xml.etree.ElementTree as ET
from wsgiref import simple_server

from .util import find_available_port

# see here:
# https://docs.python.org/3/library/xml.html

# the color could be specified with a class... (e.g. class=color-api-key, color-password)
# the top offset could also be done with a class (e.g. class=level1, level2, etc.)
# but we still need to set the ID based on other info


CSS = """
body {
    font-size: 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
    padding: 4rem 2rem;
    direction: ltr;
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
def get_span_line(color: str = "#7aecec", top=40):
    span = ET.Element("span", attrib={"class": "span_line"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg=color, top_offset=top),
    )
    return span


def get_span_start(label: str, color: str = "#7aecec", top=40):
    span = ET.Element("span", attrib={"class": "span_start1"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg=color, top_offset=top),
    )
    subspan = ET.SubElement(span, "span", attrib={"class": "span_start2"})
    subspan.set("style", "background: {bg};".format(bg=color))
    subspan.text = label
    return span


def get_div():
    div = ET.Element("div")
    # div.set("style", "line-height: 2.5; direction: {dir}")
    div.set("style", "line-height: 2.5; direction: ltr")
    div.set("class", "spans")
    return div


# 3 tokens with one annotation...
def get_token_spans() -> list[ET.Element]:
    tokens = []
    for i in range(3):
        token = get_token_span("token")
        token.append(get_span_line())
        if i == 0:
            token.append(get_span_start("label"))
        token.tail = " "
        tokens.append(token)
    return tokens


def get_wrapper():
    html = ET.Element("html")
    head = ET.SubElement(html, "head")
    style = ET.SubElement(head, "style")
    style.text = CSS
    body = ET.SubElement(html, "body")
    return html, body


def main():

    div = get_div()
    # token_spans = list(get_token_spans() + get_token_spans())
    token_spans = get_token_spans()
    print(token_spans)
    # div.extend(token_spans)
    for token in token_spans:
        div.append(token)

    print(div)
    print(list(div))

    html, body = get_wrapper()
    body.append(div)

    html_str = ET.tostring(html, encoding="utf-8", method="html").decode("utf-8")

    print(html_str)

    host = "0.0.0.0"

    port = find_available_port(5000, host, True)
    httpd = simple_server.make_server(host, port, get_app(html_str))
    print(f"Serving on http://{host}:{port} ...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"Shutting down server on port {port}.")
    finally:
        httpd.server_close()


def get_app(html: str):

    def app(_environ, start_response):
        headers = [("Content-type", "text/html; charset=utf-8")]
        start_response("200 OK", headers)
        res = html.encode(encoding="utf-8")
        return [res]

    return app


# def getDOM() -> Document:
#     impl = getDOMImplementation()
#     dt = impl.createDocumentType(
#         "html",
#         "-//W3C//DTD XHTML 1.0 Strict//EN",
#         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
#     )
#     return impl.createDocument("http://www.w3.org/1999/xhtml", "html", dt)


if __name__ == "__main__":
    main()
