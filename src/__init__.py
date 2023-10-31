import click
from collections import OrderedDict, defaultdict
import json
from typing import Dict, List, Tuple

from src.const import BULLET_REGEX, HEADER_REGEX, JSON_STYLE_PATH, NON_BULLET_REGEX, OUT_STYLE_PATH, STYLE_PATH
from src.data_models import BeerStyle, BeerStyleMap
from src.generics import DictItem
from src.utils import to_snake_case


def parse_depth_name_value(l: str) -> Tuple[int, str, str]:
    depth = ""
    name = ""
    value = ""
    vals = BULLET_REGEX.findall(l)
    if vals:
        depth, name, value = vals[0]
        value = value.replace(":", "", -1).strip()
    else:
        vals = NON_BULLET_REGEX.findall(l)
        if vals:
            depth, value = vals[0]
    return len(depth), name, value


def load_file(filename: str) -> List[str]:
    lines = []
    with open(filename, "r") as f:
        for line in f.readlines():
            if len(line.strip()) > 0:
                lines.append(line)
    return lines


def parse_file(lines: List[str]) -> Dict[str, BeerStyle]:
    curr_header = None
    parsed_header = defaultdict(list)

    for line in lines:
        if HEADER_REGEX.match(line):
            curr_header = HEADER_REGEX.findall(line)[0].strip()
            continue

        parsed_header[curr_header].append(line)

    parsed_dict = {}

    for header, header_lines in parsed_header.items():
        stack = [DictItem(value=header, children=OrderedDict(), indent=0)]
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
            if idx > 0 and indent < tmp_header_lines[idx - 1][0]:
                diff = tmp_header_lines[idx - 1][0] - indent
                for i in range(diff):
                    stack.pop()
            stack[-1].children[name] = DictItem(value=value, children=OrderedDict(), indent=indent)
            if idx < num_lines - 1 and indent < tmp_header_lines[idx + 1][0]:
                stack.append(stack[-1].children[name])

        parsed_dict[header] = stack[0].children
    return parsed_dict


def parse_dict_items_to_styles(parsed_dict: Dict[str, DictItem]) -> BeerStyleMap:
    styles = {}
    for style, body in parsed_dict.items():
        try:
            styles[style] = BeerStyle(
                name=style,
                mouthfeel=body["mouthfeel"].children if body.get("mouthfeel") else None,
                flavors=body["flavors"].children if body.get("flavors") else None,
                **{k: v for k, v in body.items() if k not in ["mouthfeel", "flavors"]},
            )
        except Exception as e:
            print(style)
            print(body)
            raise e
    return BeerStyleMap(styles=styles)


def gen_styles(in_filename: str, o_md_filename: str, o_filename: str):
    lines = load_file(in_filename)
    parsed_dict = parse_file(lines)
    styles = parse_dict_items_to_styles(parsed_dict)
    with open(o_filename, "w") as f:
        json.dump(styles.model_dump(mode="json"), f, indent=4)
    with open(o_md_filename, "w") as f:
        f.write(str(styles))
    return styles


@click.command()
@click.option("--file_mode", type=click.Choice(["gen", "test"]))
def main(file_mode: str) -> None:
    if file_mode == "gen":
        gen_styles(STYLE_PATH, OUT_STYLE_PATH, JSON_STYLE_PATH)
    elif file_mode == "test":
        pass
    else:
        raise ValueError(f"Invalid file mode: {file_mode}")


if __name__ == "__main__":
    main()
