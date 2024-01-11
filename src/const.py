import re

STYLE_PATH = "./glossary/styles.md"
OUT_STYLE_PATH = "./glossary/styles_formatted.md"
JSON_STYLE_PATH = "./src/style_json.json"
OUT_CHARTS_PATH = "./references/charts"

HEADER_REGEX = re.compile(r"#\s*(\w[\w\s]+)\n?")
FIRST_LINE_REGEX = re.compile(r"[\*-] \*\*(.+)(?:\*\*:|:\*\*)(.*)\n?")
GLOSSARY_LINE_REGEX = re.compile(r"(\t*)(?:[\*-]|\d+\.)\s?(.*)\n?")
BULLET_REGEX = re.compile(r"(\s*)[\*-]\s*([\w ]+)(\:\s*\w?[^\n]*)\n?")
NON_BULLET_REGEX = re.compile(r"(\s*)[\*-]\s*(\w[^\n]*)\n?")

COLOR_PROFILE_REGEX = re.compile(r"([\w\- ]+) *\((\d+(?:\.\d+)?) *- *(\d+(?:\.\d+)?) *SRM\)")
ALCOHOL_PROFILE_REGEX = re.compile(r"([\w\- ]+) *\((\d+(?:\.\d+)?) *- *(\d+(?:\.\d+)?)% *ABV\)")
BITTERNESS_PROFILE_REGEX = re.compile(r"([\w\- ]+) *\((\d+(?:\.\d+)?) *- *(\d+(?:\.\d+)?) *IBUs\)")
FILENAME_DATE_REGEX = re.compile(r"evaluate_value_(\d+\_\d+)\.csv")

STYLE_CAT__HISTORICAL = "historical"
STYLE_CAT__SPECIALTY = "specialty"


TERMS_FILE_NAME__BREWERIES = "./glossary/breweries.md"
TERMS_FILE_NAME__BREWING = "./glossary/brewing/terms.md"
TERMS_FILE_NAME__ORGANIZATIONS = "./glossary/organizations.md"
TERMS_FILE_NAME__PEOPLE = "./glossary/people.md"
TERMS_FILE_NAME__PLACES = "./glossary/places.md"
TERMS_FILE_NAME__SERVING = "./glossary/serving.md"

GLOSSARY_FILE_NAMES = [
    TERMS_FILE_NAME__BREWERIES,
    TERMS_FILE_NAME__BREWING,
    TERMS_FILE_NAME__ORGANIZATIONS,
    TERMS_FILE_NAME__PEOPLE,
    TERMS_FILE_NAME__PLACES,
    TERMS_FILE_NAME__SERVING,
]

CHART_CATEGORIES = [
    "British Dark Ales",
    "British Pale Ales",
    "British Strong Ales",
    "German Dark Lagers",
    "Flanders Ales and Lambic Beers",
    "French and Belgian Beers",
    "German Hybrid Ales",
    "German Wheat Ales",
    "German Pale Lagers",
    "Secular and Trappist Strong Ales",
]

RESULT_DIR = "./evaluate_results/evaluate_value"
