import re

STYLE_PATH = "/Users/evanmarcey/notes/cicerone/glossary/styles.md"
OUT_STYLE_PATH = "/Users/evanmarcey/notes/cicerone/glossary/styles_formatted.md"
JSON_STYLE_PATH = "/Users/evanmarcey/notes/cicerone/src/style_json.json"

HEADER_REGEX = re.compile(r"#\s*(\w[\w\s]+)\n?")
BULLET_REGEX = re.compile(r"(\s*)\*\s*([\w ]+)(\:\s*\w?[^\n]*)\n?")
NON_BULLET_REGEX = re.compile(r"(\s*)\*\s*(\w[^\n]*)\n?")

COLOR_PROFILE_REGEX = re.compile(r"([\w\- ]+) *\((\d+(?:\.\d+)?) *- *(\d+(?:\.\d+)?) *SRM\)")
ALCOHOL_PROFILE_REGEX = re.compile(r"([\w\- ]+) *\((\d+(?:\.\d+)?) *- *(\d+(?:\.\d+)?)% *ABV\)")
BITTERNESS_PROFILE_REGEX = re.compile(r"([\w\- ]+) *\((\d+(?:\.\d+)?) *- *(\d+(?:\.\d+)?) *IBUs\)")

STYLE_CAT__HISTORICAL = "historical"
STYLE_CAT__SPECIALTY = "specialty"
