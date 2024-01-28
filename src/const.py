import re
import seaborn as sns

STYLE_PATH = "./glossary/styles.md"
OUT_STYLE_PATH = "./glossary/styles.clean.md"
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
    "American Dark Ales",
    "American Hoppy Ales",
    "American Pale Lagers and Ales",
    "American Strong Ales",
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


# SRM value == index of list
SRM_TO_HEX = [
    "#f0efb5",
    "#e9d76c",
    "#e1c336",
    "#dab700",
    "#d5ad00",
    "#cfa200",
    "#c99800",
    "#c38e0d",
    "#bd841a",
    "#b87b1c",
    "#b2731e",
    "#ad6a20",
    "#a86222",
    "#a35b20",
    "#9d531f",
    "#984c1d",
    "#94461c",
    "#8f3f1c",
    "#8a391d",
    "#85341d",
    "#812f1e",
    "#7c2a1f",
    "#78251c",
    "#74211a",
    "#701e18",
    "#6b1a16",
    "#671714",
    "#641413",
    "#601213",
    "#5c1012",
    "#580e12",
    "#550d11",
    "#510c11",
    "#4e0c11",
    "#4b0c11",
    "#470c11",
    "#440c11",
    "#410c11",
    "#3e0c11",
    "#3c0c11",
]

IBU_TO_RGB = sns.color_palette("Greens", n_colors=100)
ABV_TO_RGB = sns.color_palette("magma_r", n_colors=18)
