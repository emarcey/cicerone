import os
from string import punctuation
from typing import Any, Dict, List, Optional, Union
from unidecode import unidecode

from src.const import ALCOHOL_PROFILE_REGEX, BITTERNESS_PROFILE_REGEX, CARBONATION_PROFILE_REGEX, COLOR_PROFILE_REGEX
from src.generics import OPTIONAL_DICT_OR_DICT_ITEM, OPTIONAL_DICT_OR_LIST, DictItem

str_translator = str.maketrans("", "", punctuation)


def clear_screen():
    os.system("clear")


def clean_string(s: str) -> str:
    return unidecode(s.strip().lower().translate(str_translator))


def to_snake_case(s: str) -> str:
    """
    Converts a PascalCase or camelCase string to snake_case

    Args:
        s: string to convert

    Returns:
        converted string
    """
    return s.lower().replace(" ", "_", -1)


def snake_to_sentence_case(s: str) -> str:
    """
    Converts  snake_case string to "Sentence case"

    Args:
        s: string to convert

    Returns:
        converted string
    """
    tmp_s = s.lower().replace("_", " ", -1)
    if len(tmp_s) < 1:
        return tmp_s
    return tmp_s[0].upper() + tmp_s[1:]


def validate_string_input(cls, v: Union[str, DictItem]) -> str:
    """
    Cleans up an argument that could either be a string or UUID or not set

    Args:
        cls: data model class
        v: str, UUID, or None

    Returns:
        formatted string
    """
    # if v.children:
    # raise ValueError(f"Does not expect children!!")
    if isinstance(v, str):
        return v.strip()
    return v.value.strip()


def validate_optional_string_input(cls, v: Optional[Union[str, DictItem]]) -> Optional[str]:
    """
    Cleans up an argument that could either be a string or UUID or not set

    Args:
        cls: data model class
        v: str, UUID, or None

    Returns:
        formatted string
    """
    if not v:
        return None
    if isinstance(v, str):
        return v
    return v.value


def validate_optional_string_to_list(cls, v: OPTIONAL_DICT_OR_LIST) -> List[str]:
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
    if isinstance(v, list):
        return v
    return v.to_list()


def validate_optional_string_to_list_no_split(cls, v: OPTIONAL_DICT_OR_LIST) -> List[str]:
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
    if isinstance(v, list):
        return v
    return v.to_list(split_value=False)


def validate_color_profile(cls, v: OPTIONAL_DICT_OR_DICT_ITEM) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    if isinstance(v, dict):
        return v
    range, value_low, value_high = COLOR_PROFILE_REGEX.findall(v.value)[0]
    return {
        "color_range": [x.strip() for x in range.split("-")],
        "value_low": float(value_low),
        "value_high": float(value_high),
    }


def validate_alcohol_profile(cls, v: OPTIONAL_DICT_OR_DICT_ITEM) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    if isinstance(v, dict):
        return v
    range, value_low, value_high = ALCOHOL_PROFILE_REGEX.findall(v.value)[0]

    return {
        "alcohol_range": [x.strip() for x in range.split("-")],
        "value_low": float(value_low),
        "value_high": float(value_high),
        "notes": v.to_list(include_value=False),
    }


def validate_bitterness_profile(cls, v: OPTIONAL_DICT_OR_DICT_ITEM) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    if isinstance(v, dict):
        return v
    range, value_low, value_high = BITTERNESS_PROFILE_REGEX.findall(v.value)[0]
    return {
        "bitterness_range": [x.strip() for x in range.split("-")],
        "value_low": float(value_low),
        "value_high": float(value_high),
    }


def validate_carbonation_profile(cls, v: OPTIONAL_DICT_OR_DICT_ITEM) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    if isinstance(v, dict):
        return v
    value_low, value_high = CARBONATION_PROFILE_REGEX.findall(v.value)[0]
    return {
        "value_low": float(value_low),
        "value_high": float(value_high),
    }
