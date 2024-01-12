import click
from collections import OrderedDict, defaultdict
import colorcet as cc
import json
import matplotlib.pyplot as plt
import os
from rich import print
import seaborn as sns
from typing import Any, Dict, List, Tuple


from src.analyze import analyze_historical_results
from src.const import (
    BULLET_REGEX,
    CHART_CATEGORIES,
    FIRST_LINE_REGEX,
    GLOSSARY_FILE_NAMES,
    GLOSSARY_LINE_REGEX,
    HEADER_REGEX,
    JSON_STYLE_PATH,
    NON_BULLET_REGEX,
    OUT_CHARTS_PATH,
    OUT_STYLE_PATH,
    RESULT_DIR,
    STYLE_PATH,
)
from src.data_models import BeerStyle, BeerStyleMap, BeerStyleTestParams, GlossaryHeader, GlossaryLine
from src.generics import DictItem
from src.utils import to_snake_case


def parse_depth_name_value(li: str) -> Tuple[int, str, str]:
    depth = ""
    name = ""
    value = ""
    vals = BULLET_REGEX.findall(li)
    if vals:
        depth, name, value = vals[0]
        value = value.replace(":", "", -1).strip()
    else:
        vals = NON_BULLET_REGEX.findall(li)
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


def parse_glossary_file(lines: List[str]) -> Dict[str, GlossaryHeader]:
    curr_header = None
    parsed_lines = {}

    for line in lines:
        first_line_match = FIRST_LINE_REGEX.match(line)
        if first_line_match is not None:
            name, value = FIRST_LINE_REGEX.findall(line)[0]
            curr_header = name
            parsed_lines[name] = GlossaryHeader(name=name.strip(), value=value.strip())
            continue

        glossary_line_match = GLOSSARY_LINE_REGEX.match(line)
        if not glossary_line_match:
            raise Exception(f"Line did not match glossary format! {line}")

        indents, line_value = GLOSSARY_LINE_REGEX.findall(line)[0]
        parsed_lines[curr_header].lines.append(GlossaryLine(value=line_value.strip(), indent=len(indents)))
    return parsed_lines


def parse_file(lines: List[str]) -> Dict[str, Dict[Any, Any]]:
    curr_header = None
    parsed_header = defaultdict(list)

    for line in lines:
        header_line_match = HEADER_REGEX.match(line)
        if header_line_match is not None:
            curr_header = HEADER_REGEX.findall(line)[0].strip()
            continue

        parsed_header[curr_header].append(line)

    parsed_dict: Dict[str, Dict[Any, Any]] = {}

    for header, header_lines in parsed_header.items():
        stack = [DictItem(value=header, children=OrderedDict(), indent=0)]
        tmp_header_lines: List[Tuple[int, str, str]] = []
        for idx in range(len(header_lines)):
            header_line = header_lines[idx].replace("**", "", -1)
            indent, name, value = parse_depth_name_value(header_line)
            if not (name or value):
                continue
            if not name:
                name = str(idx)
            tmp_header_lines.append((indent, to_snake_case(name), value))

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


def parse_dict_items_to_styles(parsed_dict: Dict[str, Dict[Any, Any]]) -> BeerStyleMap:
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
        json.dump(
            styles.model_dump(
                include={
                    "styles",
                },
                mode="json",
            ),
            f,
            indent=4,
        )
    with open(o_md_filename, "w") as f:
        f.write(str(styles))
    return styles


def load_styles(filename: str) -> BeerStyleMap:
    with open(filename, "r") as f:
        return BeerStyleMap(**json.load(f))


def evaluate(filename: str) -> None:
    styles = load_styles(filename)
    styles.evaluate(BeerStyleTestParams())


def evaluate_values(filename: str) -> None:
    styles = load_styles(filename)
    styles.evaluate_values(BeerStyleTestParams())


def gen_glossary(glossary_file_names: List[str]) -> None:
    for file_name in glossary_file_names:
        lines = load_file(file_name)
        glossary_file = parse_glossary_file(lines)
        glossary_items = sorted(list(glossary_file.values()), key=lambda x: x.name)
        glossary_str = "\n\n".join(list(map(str, glossary_items)))
        o_file_name = file_name.replace(".md", ".clean.md")
        with open(o_file_name, "w") as f:
            f.write(glossary_str)


def make_chart(target_dir: str, chart_groups: List[BeerStyle], style_cat: str, metric_cat: str) -> None:
    vals = [
        {
            "label": style.name,
            "xmin": getattr(style, metric_cat).value_low,
            "xmax": getattr(style, metric_cat).value_high,
        }
        for style in chart_groups
        if getattr(style, metric_cat)
    ]
    sorted_vals = sorted(vals, key=lambda x: (x["xmin"], x["xmax"], x["label"]))
    palette = sns.color_palette(cc.glasbey, n_colors=len(chart_groups))
    title = f"{style_cat}: {metric_cat.title()}"

    for i in range(len(sorted_vals)):
        val = sorted_vals[i]
        y = i + 1
        plt.hlines(y=y, xmin=val["xmin"], xmax=val["xmax"], colors=palette[i])
        plt.text((val["xmin"] + val["xmax"]) / 2, y, val["label"], color=palette[i], ha="center", va="bottom")
        plt.text(val["xmin"], y, val["xmin"], color="black", ha="right", va="top", size="smaller")
        plt.text(val["xmax"], y, val["xmax"], color="black", va="top", size="smaller")

    plt.yticks([])
    plt.title(title)
    plt.savefig(f"{target_dir}/{title}.png")
    plt.cla()


def gen_charts(target_dir: str, styles: BeerStyleMap) -> None:
    output_directory = f"{target_dir}"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    all_chart_groups = defaultdict(list)
    for cat in CHART_CATEGORIES:
        for k, v in styles.styles.items():
            if cat in v.categories:
                all_chart_groups[cat].append(v)

    for style_cat, chart_groups in all_chart_groups.items():
        for metric_cat in ["alcohol", "color", "bitterness"]:
            make_chart(target_dir, chart_groups, style_cat, metric_cat)


@click.command()
@click.option("--file_mode", type=click.Choice(["gen", "test", "test-values", "analyze"]))
def main(file_mode: str) -> None:
    if file_mode == "gen":
        styles = gen_styles(STYLE_PATH, OUT_STYLE_PATH, JSON_STYLE_PATH)
        gen_glossary(GLOSSARY_FILE_NAMES)
        gen_charts(OUT_CHARTS_PATH, styles)
    elif file_mode == "test":
        evaluate(JSON_STYLE_PATH)
    elif file_mode == "test-values":
        evaluate_values(JSON_STYLE_PATH)
    elif file_mode == "analyze":
        analyze_historical_results(RESULT_DIR)
    else:
        raise ValueError(f"Invalid file mode: {file_mode}")


if __name__ == "__main__":
    main()
