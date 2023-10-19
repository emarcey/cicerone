from pydantic import validator
from pydantic.generics import GenericModel
import json
import re
from typing import Any, Dict, Tuple, TypedDict, List, Optional
from collections import OrderedDict, defaultdict, namedtuple

style_path = "/Users/evanmarcey/notes/cicerone/glossary/styles.md"
lines = []
with open(style_path, "r") as f:
    for line in f.readlines():
        if len(line.strip()) > 0:
            lines.append(line)

curr_header = None
parsed_header = defaultdict(list)

HEADER_REGEX = re.compile(r"#\s*(\w[\w\s]+)\n?")
BULLET_REGEX = re.compile(r"(\s*)\*\s*([\w ]+)(\:\s*\w?[^\n]*)\n?")
NON_BULLET_REGEX = re.compile(r"(\s*)\*\s*(\w[^\n]*)\n?")

for line in lines:
    if HEADER_REGEX.match(line):
        curr_header = HEADER_REGEX.findall(line)[0].strip()
        continue

    parsed_header[curr_header].append(line)


def parse_depth_name_value(l: str) -> Tuple[int, str, str]:
    depth = ""
    name = ""
    value = ""
    vals = BULLET_REGEX.findall(l)
    if vals:
        depth, name, value = vals[0]
        value = value.replace(":", "", -1).strip()
    else:
        vals = NON_BULLET_REGEX.findall(header_line)
        if vals:
            depth, value = vals[0]
    return len(depth), name, value


class DictItem:
    value: str
    children: OrderedDict

    def __init__(self, value, children) -> None:
        self.value = value
        self.children = children

    def __json__(self):
        return {}


def to_snake_case(s: str) -> str:
    """
    Converts a PascalCase or camelCase string to snake_case

    Args:
        s: string to convert

    Returns:
        converted string
    """
    return s.lower().replace(" ", "_", -1)


def validate_string_input(cls, v: DictItem) -> str:
    """
    Cleans up an argument that could either be a string or UUID or not set

    Args:
        cls: data model class
        v: str, UUID, or None

    Returns:
        formatted string
    """
    if v.children:
        raise ValueError(f"Does not expect children!!")
    return v.value


def validate_optional_string_to_list(cls, v: Optional[DictItem]) -> List[str]:
    """
    Cleans up an argument that could either be a string or UUID or not set

    Args:
        cls: data model class
        v: str, UUID, or None

    Returns:
        formatted string
    """
    if not v:
        return []
    if v.children:
        raise ValueError(f"Does not expect children!!")
    if v.value:
        return [x.strip() for x in v.value.split(",")]
    return []


class BeerStyle(GenericModel):
    name: str
    region: str
    categories: List[str]
    malt: Any
    hops: Any
    other_names: Optional[List[str]]
    glassware: Any
    color: Any
    alcohol: Any
    mouthfeel: Any
    bitterness: Any
    flavors: Any
    commercial_examples: List[str]
    Notes: Any

    _validate_string_input = validator("region", pre=True, allow_reuse=True)(validate_string_input)
    _validate_optional_string_to_list_input = validator(
        "categories", "other_names", "commercial_examples", pre=True, allow_reuse=True
    )(validate_optional_string_to_list)


parsed_dict = {}

for header, header_lines in parsed_header.items():
    if header != "Saison":
        continue
    stack = [DictItem(value=header, children=OrderedDict())]
    depth = 0
    dummy_idx = 0
    tmp_header_lines = []
    for idx in range(len(header_lines)):
        header_line = header_lines[idx].replace("**", "", -1)
        indent, name, value = parse_depth_name_value(header_line)
        if not (name or value):
            continue
        if not name:
            name = str(idx)
        tmp_header_lines.append([indent, to_snake_case(name), value])

    num_lines = len(tmp_header_lines)
    for idx in range(len(tmp_header_lines)):
        indent, name, value = tmp_header_lines[idx]
        print(f"indent {indent}, name {name}, value {value}")
        if idx > 0 and indent < tmp_header_lines[idx - 1][0]:
            stack.pop()
        stack[-1].children[name] = DictItem(value=value, children=OrderedDict())
        if idx < num_lines - 1 and indent < tmp_header_lines[idx + 1][0]:
            stack.append(stack[-1].children[name])

    parsed_dict[header] = stack[0].children
    print(parsed_dict[header])


styles = {}
for style, body in parsed_dict.items():
    try:
        styles[style] = BeerStyle(name=style, **body)
    except Exception as e:
        print(style)
        print(body)
        raise e

print(styles["Faro"])
