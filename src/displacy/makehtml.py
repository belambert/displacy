# pylint: disable=line-too-long

import xml.etree.ElementTree as ET
from wsgiref import simple_server

from spacy.util import find_available_port

# see here:
# https://docs.python.org/3/library/xml.html


def get_token_span(token: str) -> ET.Element:
    span = ET.Element("span", attrib={"class": "token_span"})
    span.text = token
    return span

# this one is just for the line
def get_span_slice():
    span = ET.Element("span", attrib={"class": "span_slice"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg="#7aecec", top_offset=40),
    )
    return span


def get_span_start(label: str):
    span = ET.Element("span", attrib={"class": "span_start1"})
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px;".format(bg="#7aecec", top_offset=40),
    )
    subspan = ET.SubElement(span, "span", attrib={"class": "span_start2"})
    subspan.set("style", "background: {bg};".format(bg="#7aecec"))
    subspan.text = label
    return span


def get_div():
    div = ET.Element("div")
    div.set("style", "line-height: 2.5; direction: {dir}")
    div.set("class", "spans")
    return div


# each token annotated...
# def get_token_spans() -> list[ET.Element]:
#     tokens =[]
#     for i in range(5):
#         token = get_token_span("token")
#         token.append(get_span_start("label"))
#         token.tail = " "
#         tokens.append(token)
#     return tokens


# 3 tokens with one annotation...
def get_token_spans() -> list[ET.Element]:
    tokens = []
    for i in range(3):
        token = get_token_span("token")
        if i == 0:
            token.append(get_span_start("label"))
        else:
            token.append(get_span_slice())
        token.tail = " "
        tokens.append(token)
    return tokens


CSS = """
.token_span {
    font-weight: bold;
    display: inline-block;
    position: relative;
    height: 20px;
}
.span_slice {
    height: 4px;
    left: -1px;
    width: calc(100% + 2px);
    position: absolute;
}
.span_start1 {
    height: 4px;
    border-top-left-radius: 3px;
    border-bottom-left-radius: 3px;
    left: -1px; width: calc(100% + 2px);
    position: absolute;
}
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


def get_wrapper():
    html = ET.Element("html")
    head = ET.SubElement(html, "head")
    style = ET.SubElement(head, "style")
    style.text = CSS
    body = ET.SubElement(html, "body")
    return html, body


def main():

    div = get_div()
    div.extend(get_token_spans() + get_token_spans())

    html, body = get_wrapper()
    body.append(div)

    html_str = ET.tostring(html, encoding="utf-8").decode("utf-8")

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
