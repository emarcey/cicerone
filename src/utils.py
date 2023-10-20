from typing import Any, Dict, List, Optional
from src.const import ALCOHOL_PROFILE_REGEX, BITTERNESS_PROFILE_REGEX, COLOR_PROFILE_REGEX
from src.generics import DictItem


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


def validate_string_input(cls, v: DictItem) -> str:
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
    return v.value


def validate_optional_string_input(cls, v: Optional[DictItem]) -> Optional[str]:
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
    return v.to_list()


def validate_optional_string_to_list_no_split(cls, v: Optional[DictItem]) -> List[str]:
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
    return v.to_list(split_value=False)


def validate_color_profile(cls, v: Optional[DictItem]) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    range, srm_low, srm_high = COLOR_PROFILE_REGEX.findall(v.value)[0]
    return {
        "color_range": [x.strip() for x in range.split("-")],
        "srm_low": float(srm_low),
        "srm_high": float(srm_high),
    }


def validate_alcohol_profile(cls, v: Optional[DictItem]) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    range, abv_low, abv_high = ALCOHOL_PROFILE_REGEX.findall(v.value)[0]

    return {
        "alcohol_range": [x.strip() for x in range.split("-")],
        "abv_low": float(abv_low),
        "abv_high": float(abv_high),
        "notes": v.to_list(include_value=False),
    }


def validate_bitterness_profile(cls, v: Optional[DictItem]) -> Optional[Dict[str, Any]]:
    if not v:
        return None
    range, ibu_low, ibu_high = BITTERNESS_PROFILE_REGEX.findall(v.value)[0]
    return {
        "bitterness_range": [x.strip() for x in range.split("-")],
        "ibu_low": float(ibu_low),
        "ibu_high": float(ibu_high),
    }
