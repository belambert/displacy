"""
spaCy's built in visualization suite for dependencies and named entities.

DOCS: https://spacy.io/api/top-level#displacy
USAGE: https://spacy.io/usage/visualizers
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments

import warnings
from typing import Any, Iterable, Union

from spacy.errors import Errors, Warnings
from spacy.tokens import Doc, Span
from spacy.util import find_available_port, is_in_jupyter

from .render import SpanRenderer

_html = {}


# pylint: disable-next=dangerous-default-value
def render(
    docs: Union[Iterable[Union[Doc, Span, dict]], Doc, Span, dict],
    style: str = "dep",
    page: bool = False,
    minify: bool = False,
    options: dict[str, Any] = {},
    manual: bool = False,
) -> str:
    """Render displaCy visualisation.

    docs (Union[Iterable[Union[Doc, Span, dict]], Doc, Span, dict]]): Document(s) to visualise.
        a 'dict' is only allowed here when 'manual' is set to True
    style (str): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    jupyter (bool): Override Jupyter auto-detection.
    options (dict): Visualiser-specific options, e.g. colors.
    manual (bool): Don't parse `Doc` and instead expect a dict/list of dicts.
    RETURNS (str): Rendered SVG or HTML markup.

    DOCS: https://spacy.io/api/top-level#displacy.render
    USAGE: https://spacy.io/usage/visualizers
    """
    factories = {
        "span": (SpanRenderer, parse_spans),
    }
    if style not in factories:
        raise ValueError(Errors.E087.format(style=style))
    if isinstance(docs, (Doc, Span, dict)):
        docs = [docs]
    docs = [obj if not isinstance(obj, Span) else obj.as_doc() for obj in docs]
    if not all(isinstance(obj, (Doc, Span, dict)) for obj in docs):
        raise ValueError(Errors.E096)
    renderer_func, converter = factories[style]
    renderer = renderer_func(options=options)
    parsed = [converter(doc, options) for doc in docs] if not manual else docs  # type: ignore
    if manual:
        for doc in docs:
            if isinstance(doc, dict) and "ents" in doc:
                doc["ents"] = sorted(doc["ents"], key=lambda x: (x["start"], x["end"]))
    _html["parsed"] = renderer.render(parsed, page=page, minify=minify).strip()  # type: ignore
    html = _html["parsed"]
    return html


# pylint: disable-next=dangerous-default-value
def serve(
    docs: Union[Iterable[Doc], Doc],
    style: str = "dep",
    page: bool = True,
    minify: bool = False,
    options: dict[str, Any] = {},
    manual: bool = False,
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

    DOCS: https://spacy.io/api/top-level#displacy.serve
    USAGE: https://spacy.io/usage/visualizers
    """
    # pylint: disable-next=import-outside-toplevel
    from wsgiref import simple_server

    port = find_available_port(port, host, auto_select_port)

    if is_in_jupyter():
        warnings.warn(Warnings.W011)
    render(docs, style=style, page=page, minify=minify, options=options, manual=manual)
    httpd = simple_server.make_server(host, port, app)
    print(f"\nUsing the '{style}' visualizer")
    print(f"Serving on http://{host}:{port} ...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"Shutting down server on port {port}.")
    finally:
        httpd.server_close()


def app(_environ, start_response):
    headers = [("Content-type", "text/html; charset=utf-8")]
    start_response("200 OK", headers)
    res = _html["parsed"].encode(encoding="utf-8")
    return [res]


# pylint: disable-next=dangerous-default-value,too-many-locals
def parse_deps(
    orig_doc: Union[Doc, Span], options: dict[str, Any] = {}
) -> dict[str, Any]:
    """Generate dependency parse in {'words': [], 'arcs': []} format.

    orig_doc (Union[Doc, Span]): Document to parse.
    options (Dict[str, Any]): Dependency parse specific visualisation options.
    RETURNS (dict): Generated dependency parse keyed by words and arcs.
    """
    if isinstance(orig_doc, Span):
        orig_doc = orig_doc.as_doc()
    doc = Doc(orig_doc.vocab).from_bytes(
        orig_doc.to_bytes(exclude=["user_data", "user_hooks"])
    )
    if not doc.has_annotation("DEP"):
        warnings.warn(Warnings.W005)
    if options.get("collapse_phrases", False):
        with doc.retokenize() as retokenizer:
            for np in list(doc.noun_chunks):
                attrs = {
                    "tag": np.root.tag_,
                    "lemma": np.root.lemma_,
                    "ent_type": np.root.ent_type_,
                }
                retokenizer.merge(np, attrs=attrs)  # type: ignore[arg-type]
    if options.get("collapse_punct", True):
        spans = []
        for word in doc[:-1]:
            if word.is_punct or not word.nbor(1).is_punct:
                continue
            start = word.i
            end = word.i + 1
            while end < len(doc) and doc[end].is_punct:
                end += 1
            span = doc[start:end]
            spans.append((span, word.tag_, word.lemma_, word.ent_type_))
        with doc.retokenize() as retokenizer:
            for span, tag, lemma, ent_type in spans:
                attrs = {"tag": tag, "lemma": lemma, "ent_type": ent_type}
                retokenizer.merge(span, attrs=attrs)  # type: ignore[arg-type]
    fine_grained = options.get("fine_grained")
    add_lemma = options.get("add_lemma")
    words = [
        {
            "text": w.text,
            "tag": w.tag_ if fine_grained else w.pos_,
            "lemma": w.lemma_ if add_lemma else None,
        }
        for w in doc
    ]
    arcs = []
    for word in doc:
        if word.i < word.head.i:
            arcs.append(
                {"start": word.i, "end": word.head.i, "label": word.dep_, "dir": "left"}
            )
        elif word.i > word.head.i:
            arcs.append(
                {
                    "start": word.head.i,
                    "end": word.i,
                    "label": word.dep_,
                    "dir": "right",
                }
            )
    return {"words": words, "arcs": arcs, "settings": get_doc_settings(orig_doc)}


# pylint: disable-next=dangerous-default-value
def parse_ents(doc: Doc, options: dict[str, Any] = {}) -> dict[str, Any]:
    """Generate named entities in [{start: i, end: i, label: 'label'}] format.

    doc (Doc): Document to parse.
    options (Dict[str, Any]): NER-specific visualisation options.
    RETURNS (dict): Generated entities keyed by text (original text) and ents.
    """
    kb_url_template = options.get("kb_url_template", None)
    ents = [
        {
            "start": ent.start_char,
            "end": ent.end_char,
            "label": ent.label_,
            "kb_id": ent.kb_id_ if ent.kb_id_ else "",
            "kb_url": kb_url_template.format(ent.kb_id_) if kb_url_template else "#",
        }
        for ent in doc.ents
    ]
    if not ents:
        warnings.warn(Warnings.W006)
    title = doc.user_data.get("title", None) if hasattr(doc, "user_data") else None
    settings = get_doc_settings(doc)
    return {"text": doc.text, "ents": ents, "title": title, "settings": settings}


# pylint: disable-next=dangerous-default-value
def parse_spans(doc: Doc, options: dict[str, Any] = {}) -> dict[str, Any]:
    """Generate spans in [{start_token: i, end_token: i, label: 'label'}] format.

    doc (Doc): Document to parse.
    options (Dict[str, any]): Span-specific visualisation options.
    RETURNS (dict): Generated span types keyed by text (original text) and spans.
    """
    kb_url_template = options.get("kb_url_template", None)
    spans_key = options.get("spans_key", "sc")
    spans = [
        {
            "start": span.start_char,
            "end": span.end_char,
            "start_token": span.start,
            "end_token": span.end,
            "label": span.label_,
            "kb_id": span.kb_id_ if span.kb_id_ else "",
            "kb_url": kb_url_template.format(span.kb_id_) if kb_url_template else "#",
        }
        for span in doc.spans.get(spans_key, [])
    ]
    tokens = [token.text for token in doc]

    if not spans:
        keys = list(doc.spans.keys())
        warnings.warn(Warnings.W117.format(spans_key=spans_key, keys=keys))
    title = doc.user_data.get("title", None) if hasattr(doc, "user_data") else None
    settings = get_doc_settings(doc)
    return {
        "text": doc.text,
        "spans": spans,
        "title": title,
        "settings": settings,
        "tokens": tokens,
    }


def get_doc_settings(doc: Doc) -> dict[str, Any]:
    return {
        "lang": doc.lang_,
        "direction": doc.vocab.writing_system.get("direction", "ltr"),
    }