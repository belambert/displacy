
TPL_FIGURE = """
<figure style="margin-bottom: 6rem">{content}</figure>
"""

TPL_TITLE = """
<h2 style="margin: 0">{title}</h2>
"""


TPL_SPANS = """
<div class="spans" style="line-height: 2.5; direction: {dir}">{content}</div>
"""

TPL_SPAN = """
<span style="font-weight: bold; display: inline-block; position: relative; height: {total_height}px;">
    {text}
    {span_slices}
    {span_starts}
</span>
"""

TPL_SPAN_SLICE = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;">
</span>
"""


TPL_SPAN_START = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">
    <span style="background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px">
        {label}{kb_link}
    </span>
</span>

"""

TPL_SPAN_RTL = """
<span style="font-weight: bold; display: inline-block; position: relative;">
    {text}
    {span_slices}
    {span_starts}
</span>
"""

TPL_SPAN_SLICE_RTL = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;">
</span>
"""

TPL_SPAN_START_RTL = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">
    <span style="background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px">
        {label}{kb_link}
    </span>
</span>
"""


# Important: this needs to start with a space!
TPL_KB_LINK = """
 <a style="text-decoration: none; color: inherit; font-weight: normal" href="{kb_url}">{kb_id}</a>
"""


TPL_PAGE = """
<!DOCTYPE html>
<html lang="{lang}">
    <head>
        <title>displaCy</title>
    </head>

    <body style="font-size: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; padding: 4rem 2rem; direction: {dir}">{content}</body>
</html>
"""