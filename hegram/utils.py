from dash import html
from xml.etree import ElementTree
import re


def htmlify(a):
    depth = [s.count("\t") for s in a.split("\n")]
    lines = [re.sub(r"^\d. ", "", s.strip()) for s in a.split("\n")]
    previous_depth = 0
    html = ["<ol>"]
    for d, l in zip(depth, lines):
        delta = d - previous_depth
        if delta == 1:
            html.append("<ol>")
        if delta < 0:
            for _ in range(abs(delta)):
                html.append("</ol>")
        previous_depth = d
        html.append(f"<li>{l}</li>")
    remaining = html.count("<ol>") - html.count(r"</ol>")
    for _ in range(remaining):
        html.append("</ol>")

    return "\n".join(html)


def convert_html_to_dash(html_code):
    """Convert standard html to Dash components"""

    def parse_css(css):
        """Convert a style in ccs format to dictionary accepted by Dash"""
        return {k: v for style in css.strip(";").split(";") for k, v in [style.split(":")]}

    def _convert(elem):
        comp = getattr(html, elem.tag.capitalize())
        children = [_convert(child) for child in elem]
        if not children:
            children = elem.text
        attribs = elem.attrib.copy()
        if "class" in attribs:
            attribs["className"] = attribs.pop("class")
        attribs = {k: (parse_css(v) if k == "style" else v) for k, v in attribs.items()}

        return comp(children=children, **attribs)

    et = ElementTree.fromstring(html_code)

    return _convert(et)
