import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Iterable

from displacy.defaults import (
    DEFAULT_DIR,
    DEFAULT_ENTITY_COLOR,
    DEFAULT_LABEL_COLORS,
    DEFAULT_LANG,
)
from displacy.html import (  # get_span_line2,
    get_div,
    get_span_line,
    get_span_start,
    get_token_span,
    get_unann_span,
    get_wrapper,
)
from displacy.model import Entity, TokenInfo

Doc = dict[str, Any]


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

    # pylint: disable-next=dangerous-default-value
    def __init__(self, options: dict[str, Any] = {}) -> None:
        # Set up the colors and overall look
        colors = dict(DEFAULT_LABEL_COLORS)
        colors.update(options.get("colors", {}))
        self.default_color = DEFAULT_ENTITY_COLOR
        self.colors = {label.upper(): color for label, color in colors.items()}

        # These values are in px
        self.top_offset = options.get("top_offset", 40)
        # This is how far under the top offset the span labels appear
        self.span_label_offset = options.get("span_label_offset", 20)
        self.offset_step = options.get("top_offset_step", 17)

    def render_dom(self, docs: Iterable[Doc]) -> ET.Element:
        # render each parse
        rendered = list(map(self.render_doc, docs))
        html, body = get_wrapper()
        body.extend(rendered)
        return html

    def render_html(self, parsed: Iterable[Doc]) -> str:
        dom = self.render_dom(parsed)
        return ET.tostring(dom, encoding="utf-8", method="html").decode("utf-8")

    def render_doc(self, doc: Doc) -> ET.Element:
        per_token_info = self._assemble_per_token_info(doc["tokens"], doc["spans"])
        et_tokens = self._render_markup(per_token_info)
        div = get_div()
        div.extend(et_tokens)
        return div

    @staticmethod
    def _assemble_per_token_info(
        tokens: list[str], spans: list[dict[str, Any]]
    ) -> list[TokenInfo]:
        """Assembles token info used to generate markup in render_spans()."""
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
                        sublabel=span.get("sublabel"),
                        tags=span.get("tags"),
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
                # token_span = get_token_span(escape_html(token.text), total_height)
                token_span = get_token_span(token.text, total_height)
                # token_span.tail = " "
                token_span.extend(slices)
                token_span.extend(starts)
                tokens.append(token_span)
            else:
                # span = get_unann_span(escape_html(token.text))
                if token.text == "\n":
                    span = ET.Element("br")
                elif token.text == " ":
                    span = ET.Element("span", attrib={"class": "space"})
                else:
                    span = get_unann_span(token.text)
                # span.tail = " "
                tokens.append(span)

        return tokens

    def _get_span_lines(self, entities: list[Entity]) -> list[ET.Element]:
        """Get the rendered markup of all Span slices"""
        span_lines = []
        for entity in entities:
            color = self.colors.get(entity.label.upper(), self.default_color)
            top_offset = self.top_offset + (self.offset_step * (entity.render_slot - 1))
            span_line = get_span_line(color, top_offset)
            # span_line = get_span_line2(entity.render_slot, top_offset)
            span_lines.append(span_line)
        return span_lines

    def _get_span_starts(self, entities: list[Entity]) -> list[ET.Element]:
        """Get the rendered markup of all Span start tokens"""
        span_starts = []
        for entity in entities:
            color = self.colors.get(entity.label.upper(), self.default_color)
            top_offset = self.top_offset + (self.offset_step * (entity.render_slot - 1))
            if entity.is_start:
                label_elt = get_span_start(entity.label, color, top_offset)
                if entity.sublabel:
                    sublabel = ET.Element("span", attrib={"class": "sublabel"})
                    sublabel.text = entity.sublabel
                    # this seems to work
                    label_elt[0].append(sublabel)
                if entity.tags:
                    label_elt.attrib["title"] = ", ".join(entity.tags)
                span_starts.append(label_elt)
        return span_starts
