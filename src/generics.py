from collections import OrderedDict


class DictItem:
    value: str
    children: OrderedDict

    def __init__(self, value, children) -> None:
        self.value = value
        self.children = children

    def __str__(self):
        children = {k: str(v) for k, v in self.children.items()}
        return f"""("value": {self.value},"children": {children})"""

    def to_list(self, include_value=True, split_value=True):
        output = []
        if self.value and include_value:
            if split_value:
                output = [x.strip() for x in self.value.split(",")]
            else:
                output = [self.value]
        for child_key, child_value in self.children.items():
            if not child_key.isnumeric():
                output.append(child_key)
            if isinstance(child_value, DictItem):
                output.extend(child_value.to_list(split_value=split_value))
            else:
                output.append(child_value)

        return output
