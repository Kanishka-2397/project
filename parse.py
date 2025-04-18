# selectolax_parser.py
from selectolax.parser import Node

def parse_raw_attributes(node: Node, selectors: list):
    parsed = {}

    for s in selectors:
        match = s.get("match")
        type_ = s.get("type")
        selector = s.get("selector")
        name = s.get("name")

        if match == "all":
            matched = node.css(selector)
            parsed[name] = [m.text(strip=True) for m in matched] if type_ == "text" else matched
        elif match == "first":
            matched = node.css_first(selector)
            if matched:
                parsed[name] = matched.text(strip=True) if type_ == "text" else matched

    return parsed
