"""
These are similar to the public SpaCy functions.
"""

from typing import Any, Iterable, Union
from wsgiref import simple_server

from .render import SpanRenderer
from .util import find_available_port

Doc = dict[str, Any]


# pylint: disable-next=dangerous-default-value
def render(
    docs: Union[Iterable[Doc], Doc],
    options: dict[str, Any] = {},
) -> str:
    """Render displaCy visualisation.

    docs (Union[Iterable[Union[Doc, Span, dict]], Doc, Span, dict]]): Document(s) to visualise.
        a 'dict' is only allowed here when 'manual' is set to True
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    options (dict): Visualiser-specific options, e.g. colors.
    RETURNS (str): Rendered HTML markup.
    """
    if isinstance(docs, dict):
        docs = [docs]
    if not all(isinstance(obj, dict) for obj in docs):
        raise ValueError("bad input")
    renderer = SpanRenderer(options=options)
    for doc in docs:
        if isinstance(doc, dict) and "ents" in doc:
            doc["ents"] = sorted(doc["ents"], key=lambda x: (x["start"], x["end"]))
    return renderer.render_html(docs)


# pylint: disable-next=dangerous-default-value
def serve(
    docs: Union[Iterable[Doc], Doc],
    options: dict[str, Any] = {},
    port: int = 5000,
    host: str = "0.0.0.0",
    auto_select_port: bool = False,
) -> None:
    """Serve displaCy visualisation.

    docs (list or Doc): Document(s) to visualise.
    options (dict): Visualiser-specific options, e.g. colors.
    port (int): Port to serve visualisation.
    host (str): Host to serve visualisation.
    auto_select_port (bool): Automatically select a port if the specified port is in use.
    """
    port = find_available_port(port, host, auto_select_port)
    html = render(docs, options=options)
    httpd = simple_server.make_server(host, port, get_app(html))
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
