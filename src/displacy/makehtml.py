# pylint: disable=line-too-long

import xml.etree.ElementTree as ET

# from xml.dom.minidom import Document, getDOMImplementation

# see here:
# https://docs.python.org/3/library/xml.html


def get_token_span():
    span = ET.Element("span")
    span.set(
        "style",
        "font-weight: bold; display: inline-block; position: relative; height: 20px;",
    )
    return span


def get_span_slice():
    span = ET.Element("span")
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;",
    )
    return span


def get_span_start(label: str):
    span = ET.Element("span")
    span.set(
        "style",
        "background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;",
    )
    subspan = ET.SubElement(span, "span")
    subspan.set(
        "style",
        "background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px",
    )
    subspan.text = label
    return span


def main():

    # span1 = ET.Element('span')
    # span1.set("style", "font-weight: bold; display: inline-block; position: relative; height: 20px;")
    # span2 = ET.SubElement(span1, 'span')
    # print(ET.dump(span1))

    ET.dump(get_token_span())
    print("\n")
    ET.dump(get_span_slice())
    print("\n")
    ET.dump(get_span_start("APIKEY"))

    # print(ul(["first item", "second item", "third item"]))


# def getDOM() -> Document:
#     impl = getDOMImplementation()
#     dt = impl.createDocumentType(
#         "html",
#         "-//W3C//DTD XHTML 1.0 Strict//EN",
#         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
#     )
#     return impl.createDocument("http://www.w3.org/1999/xhtml", "html", dt)


# def ul(items: List[str]) -> str:
#     dom = getDOM()
#     html = dom.documentElement
#     ul = dom.createElement("ul")
#     for item in items:
#         li = dom.createElement("li")
#         li.appendChild(dom.createTextNode(item))
#         ul.appendChild(li)
#     html.appendChild(ul)
#     return dom.toxml()


if __name__ == "__main__":
    main()
