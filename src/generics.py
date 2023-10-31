from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union


class DictItem:
    value: str
    children: OrderedDict
    indent: int

    def __init__(self, value, children, indent) -> None:
        self.value = value
        self.children = children
        self.indent = indent

    def __str__(self):
        children = {k: str(v) for k, v in self.children.items()}
        return f"""("value": {self.value},"children": {children})"""

    def to_list(self, include_value=True, split_value=True):
        output = []
        if self.value and include_value:
            if split_value:
                output = [x.strip() for x in self.value.split(",")]
            else:
                output = ["\t" * self.indent + "- " + self.value.strip()]
        for child_key, child_value in self.children.items():
            if not child_key.isnumeric():
                output.append(child_key)
            if isinstance(child_value, DictItem):
                output.extend(child_value.to_list(split_value=split_value))
            else:
                output.append(child_value)

        return output


DICT_STR_ANY = Dict[str, Any]
OPTIONAL_DICT_OR_DICT_ITEM = Optional[Union[DICT_STR_ANY, DictItem]]
OPTIONAL_DICT_OR_LIST = Optional[Union[List[str], DictItem]]
