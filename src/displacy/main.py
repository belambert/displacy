# pylint: disable=too-many-arguments,too-many-positional-arguments

from typing import Any, Iterable, Union

from .render import SpanRenderer
from .util import find_available_port

Doc = dict[str, Any]


# pylint: disable-next=dangerous-default-value
def render(
    docs: Union[Iterable[Doc], Doc],
    # page: bool = False,
    # minify: bool = False,
    options: dict[str, Any] = {},
) -> str:
    """Render displaCy visualisation.

    docs (Union[Iterable[Union[Doc, Span, dict]], Doc, Span, dict]]): Document(s) to visualise.
        a 'dict' is only allowed here when 'manual' is set to True
    style (str): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    options (dict): Visualiser-specific options, e.g. colors.
    manual (bool): Don't parse `Doc` and instead expect a dict/list of dicts.
    RETURNS (str): Rendered SVG or HTML markup.
    """
    if isinstance(docs, dict):
        docs = [docs]
    if not all(isinstance(obj, dict) for obj in docs):
        raise ValueError("bad input")
    renderer = SpanRenderer(options=options)
    for doc in docs:
        if isinstance(doc, dict) and "ents" in doc:
            doc["ents"] = sorted(doc["ents"], key=lambda x: (x["start"], x["end"]))
    return renderer.render(docs)


# pylint: disable-next=dangerous-default-value
def serve(
    docs: Union[Iterable[Doc], Doc],
    style: str = "dep",
    # page: bool = True,
    # minify: bool = False,
    options: dict[str, Any] = {},
    port: int = 5000,
    host: str = "0.0.0.0",
    auto_select_port: bool = False,
) -> None:
    """Serve displaCy visualisation.

    docs (list or Doc): Document(s) to visualise.
    style (str): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    options (dict): Visualiser-specific options, e.g. colors.
    manual (bool): Don't parse `Doc` and instead expect a dict/list of dicts.
    port (int): Port to serve visualisation.
    host (str): Host to serve visualisation.
    auto_select_port (bool): Automatically select a port if the specified port is in use.

    """
    # pylint: disable-next=import-outside-toplevel
    from wsgiref import simple_server

    port = find_available_port(port, host, auto_select_port)
    # render(docs, style=style, page=page, minify=minify, options=options, manual=manual)
    # render(docs, style=style, options=options, manual=manual)
    html = render(docs, options=options)
    httpd = simple_server.make_server(host, port, get_app(html))
    print(f"\nUsing the '{style}' visualizer")
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
