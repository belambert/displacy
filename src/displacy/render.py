import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

from spacy.errors import Errors
from spacy.util import escape_html, registry

from displacy.makehtml import (
    get_div,
    get_span_line,
    get_span_start,
    get_token_span,
    get_unann_span,
    get_wrapper,
)
from displacy.model import Entity, TokenInfo

DEFAULT_LANG = "en"
DEFAULT_DIR = "ltr"
DEFAULT_ENTITY_COLOR = "#ddd"
DEFAULT_LABEL_COLORS = {
    "ORG": "#7aecec",
    "PRODUCT": "#bfeeb7",
    "GPE": "#feca74",
    "LOC": "#ff9561",
    "PERSON": "#aa9cfc",
    "NORP": "#c887fb",
    "FAC": "#9cc9cc",
    "EVENT": "#ffeb80",
    "LAW": "#ff8197",
    "LANGUAGE": "#ff8197",
    "WORK_OF_ART": "#f0d0ff",
    "DATE": "#bfe1d9",
    "TIME": "#bfe1d9",
    "MONEY": "#e4e7d2",
    "QUANTITY": "#e4e7d2",
    "ORDINAL": "#e4e7d2",
    "CARDINAL": "#e4e7d2",
    "PERCENT": "#e4e7d2",
}


@dataclass
# pylint: disable-next=too-many-instance-attributes
class SpanRenderer:
    """Render Spans as HTML."""

    colors: dict
    top_offset: int
    span_label_offset: int
    offset_step: int
    default_color: str = DEFAULT_ENTITY_COLOR
    direction: str = DEFAULT_DIR
    lang: str = DEFAULT_LANG
    # span_template: str = TPL_SPAN
    # span_slice_template: str = TPL_SPAN_SLICE
    # span_start_template: str = TPL_SPAN_START

    # pylint: disable-next=dangerous-default-value
    def __init__(self, options: dict[str, Any] = {}) -> None:
        """Initialise span renderer

        options (dict): Visualiser-specific options (colors, spans)
        """
        # Set up the colors and overall look
        colors = dict(DEFAULT_LABEL_COLORS)
        user_colors = registry.displacy_colors.get_all()
        for user_color in user_colors.values():
            if callable(user_color):
                # Since this comes from the function registry, we want to make
                # sure we support functions that *return* a dict of colors
                user_color = user_color()
            if not isinstance(user_color, dict):
                raise ValueError(Errors.E925.format(obj=type(user_color)))
            colors.update(user_color)
        colors.update(options.get("colors", {}))
        self.default_color = DEFAULT_ENTITY_COLOR
        self.colors = {label.upper(): color for label, color in colors.items()}

        # These values are in px
        self.top_offset = options.get("top_offset", 40)
        # This is how far under the top offset the span labels appear
        self.span_label_offset = options.get("span_label_offset", 20)
        self.offset_step = options.get("top_offset_step", 17)

        # Set up which templates will be used
        # template = options.get("template")
        # if template:
        #     self.span_template = template["span"]
        #     self.span_slice_template = template["slice"]
        #     self.span_start_template = template["start"]
        # elif self.direction == "rtl":
        #     self.span_template = TPL_SPAN_RTL
        #     self.span_slice_template = TPL_SPAN_SLICE_RTL
        #     self.span_start_template = TPL_SPAN_START_RTL

    def render(
        self,
        parsed: list[dict[str, Any]],
        # page: bool = False,
        # minify: bool = False,
    ) -> str:
        """Render complete markup.

        parsed (list): Dependency parses to render.
        page (bool): Render parses wrapped as full HTML page.
        minify (bool): Minify HTML markup.
        RETURNS (str): Rendered SVG or HTML markup.
        """
        # render each parse
        rendered = []
        for i, p in enumerate(parsed):
            if i == 0:
                settings = p.get("settings", {})
                self.direction = settings.get("direction", DEFAULT_DIR)
                self.lang = settings.get("lang", DEFAULT_LANG)
            rendered.append(
                self.render_spans(p["tokens"], p["spans"])
            )  # , p.get("title")))

        html, body = get_wrapper()
        body.extend(rendered)
        html_str = ET.tostring(html, encoding="utf-8", method="html").decode("utf-8")

        # if minify:
        #     return minify_html(markup)
        return html_str

    def render_spans(
        self,
        tokens: list[str],
        spans: list[dict[str, Any]],
        # title: Optional[str],
    ) -> str:
        """Render span types in text.

        Spans are rendered per-token, this means that for each token, we check if it's part
        of a span slice (a member of a span type) or a span start (the starting token of a
        given span type).

        tokens (list): Individual tokens in the text
        spans (list): Individual entity spans and their start, end, label, kb_id and kb_url.
        title (str / None): Document title set in Doc.user_data['title'].
        """
        per_token_info = self._assemble_per_token_info(tokens, spans)
        et_tokens = self._render_markup(per_token_info)
        div = get_div()
        div.extend(et_tokens)
        return div

    @staticmethod
    def _assemble_per_token_info(
        tokens: list[str], spans: list[dict[str, Any]]
    ) -> list[TokenInfo]:
        """Assembles token info used to generate markup in render_spans().
        tokens (List[str]): Tokens in text.
        spans (List[Dict[str, Any]]): Spans in text.
        RETURNS (List[Dict[str, List[Dict, str, Any]]]): Per token info needed
            to render HTML markup for given tokens and spans.
        """
        per_token_info = []

        # we must sort so that we can correctly describe when spans need to "stack"
        # which is determined by their start token, then span length (longer spans on top),
        # then break any remaining ties with the span label
        spans = sorted(
            spans,
            key=lambda s: (
                s["start_token"],
                -(s["end_token"] - s["start_token"]),
                s["label"],
            ),
        )

        for s in spans:
            # this is the vertical 'slot' that the span will be rendered in
            # vertical_position = span_label_offset + (offset_step * (slot - 1))
            s["render_slot"] = 0

        # loops over the token
        for idx, token in enumerate(tokens):
            # Identify if a token belongs to a Span (and which) and if it's a
            # start token of said Span. We'll use this for the final HTML render
            intersecting_spans: list[dict[str, Any]] = []
            entities = []
            for span in spans:
                if span["start_token"] <= idx < span["end_token"]:
                    span_start = idx == span["start_token"]

                    if span_start:
                        # When the span starts, we need to know how many other
                        # spans are on the 'span stack' and will be rendered.
                        # This value becomes the vertical render slot for this entire span
                        span["render_slot"] = (
                            intersecting_spans[-1]["render_slot"]
                            # pylint: disable-next=use-implicit-booleaness-not-len
                            if len(intersecting_spans)
                            else 0
                        ) + 1
                    intersecting_spans.append(span)
                    ent = Entity(
                        label=span["label"],
                        is_start=span_start,
                        render_slot=span["render_slot"],
                        kb_id=span.get("kb_id", ""),
                        kb_url=span.get("kb_url", "#"),
                        kb_link="",
                    )
                    entities.append(ent)
                else:
                    # We don't specifically need to do this since we loop
                    # over tokens and spans sorted by their start_token,
                    # so we'll never use a span again after the last token it appears in,
                    # but if we were to use these spans again we'd want to make sure
                    # this value was reset correctly.
                    span["render_slot"] = 0
            token_markup = TokenInfo(text=token, entities=entities)
            per_token_info.append(token_markup)
        return per_token_info

    def _render_markup(self, per_token_info: list[TokenInfo]) -> list[ET.Element]:
        """Render the markup from per-token information"""
        tokens = []
        for token in per_token_info:
            # entities = sorted(token.entities, key=Entity.render_slot)
            entities = sorted(token.entities, key=lambda x: x.render_slot)
            # Whitespace tokens disrupt the vertical space (no line height) so that the
            # span indicators get misaligned. We don't render them as individual
            # tokens anyway, so we'll just not display a span indicator either.
            is_whitespace = token.text.strip() == ""
            if entities and not is_whitespace:
                slices = self._get_span_lines(token.entities)
                starts = self._get_span_starts(token.entities)
                total_height = (
                    self.top_offset
                    + self.span_label_offset
                    + (self.offset_step * (len(entities) - 1))
                )
                token_span = get_token_span(escape_html(token.text), total_height)
                token_span.tail = " "
                token_span.extend(slices)
                token_span.extend(starts)
                tokens.append(token_span)
            else:
                span = get_unann_span(escape_html(token.text))
                span.tail = " "
                tokens.append(span)

        return tokens

    def _get_span_lines(self, entities: list[Entity]) -> list[ET.Element]:
        """Get the rendered markup of all Span slices"""
        span_lines = []
        for entity in entities:
            color = self.colors.get(entity.label.upper(), self.default_color)
            top_offset = self.top_offset + (self.offset_step * (entity.render_slot - 1))
            span_line = get_span_line(color, top_offset)
            span_lines.append(span_line)
        return span_lines

    def _get_span_starts(self, entities: list[Entity]) -> list[ET.Element]:
        """Get the rendered markup of all Span start tokens"""
        span_starts = []
        for entity in entities:
            color = self.colors.get(entity.label.upper(), self.default_color)
            top_offset = self.top_offset + (self.offset_step * (entity.render_slot - 1))
            if entity.is_start:
                span_starts.append(get_span_start(entity.label, color, top_offset))
        return span_starts
