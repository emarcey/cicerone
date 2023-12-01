import random
from pydantic import BaseModel, Field, validator
from rich import print
from typing import Dict, List, Optional, Set, Tuple
from src.const import STYLE_CAT__HISTORICAL

from src.utils import (
    snake_to_sentence_case,
    validate_alcohol_profile,
    validate_bitterness_profile,
    validate_color_profile,
    validate_optional_string_input,
    validate_optional_string_to_list,
    validate_optional_string_to_list_no_split,
    validate_string_input,
)


class BeerStyleTestParams(BaseModel):
    exclude_categories: Set[str] = Field(
        default_factory=lambda: {
            STYLE_CAT__HISTORICAL,
        }
    )


class MouthFeelProfile(BaseModel):
    body: str
    carbonation: str
    alcohol_warmth: Optional[str] = None

    _validate_string_input = validator("body", "carbonation", pre=True, allow_reuse=True)(validate_string_input)
    _validate_optional_string_input = validator("alcohol_warmth", pre=True, allow_reuse=True)(
        validate_optional_string_input
    )

    def __str__(self) -> str:
        vals = []
        for k, v in self.__dict__.items():
            vals.append([k, v])
        return "\n" + "\n".join(map(lambda x: f"\t- {x[0]}: {x[1]}", vals))


class FlavorProfile(BaseModel):
    malt: List[str]
    fermentation: List[str]
    hop: List[str]
    _validate_string_input = validator("malt", "fermentation", "hop", pre=True, allow_reuse=True)(
        validate_optional_string_to_list
    )

    def __str__(self) -> str:
        vals = []
        for k, v in self.__dict__.items():
            vals.append([k, ", ".join(v)])
        return "\n" + "\n".join(map(lambda x: f"\t- {x[0]}: {x[1]}", vals))


class ColorProfile(BaseModel):
    color_range: List[str]
    srm_low: float
    srm_high: float

    def __str__(self) -> str:
        return f"{' - '.join(self.color_range)} ({self.srm_low} - {self.srm_high} SRM)"


class AlcoholProfile(BaseModel):
    alcohol_range: List[str]
    abv_low: float
    abv_high: float
    notes: List[str] = Field(default_factory=lambda: [])

    def __str__(self) -> str:
        vals = [f"{' - '.join(self.alcohol_range)} ({self.abv_low} - {self.abv_high}% ABV)"]
        for note in self.notes:
            vals.append(f"\t- {note}")
        return "\n".join(vals)


class BitternessProfile(BaseModel):
    bitterness_range: List[str]
    ibu_low: float
    ibu_high: float

    def __str__(self) -> str:
        return f"{' - '.join(self.bitterness_range)} ({self.ibu_low} - {self.ibu_high} IBU)"


class BeerStyle(BaseModel):
    name: str
    region: str
    categories: List[str]
    malt: List[str]
    hops: List[str]
    other_names: List[str] = Field(default_factory=lambda: [])
    glassware: List[str] = Field(default_factory=lambda: [])
    color: Optional[ColorProfile] = None
    alcohol: AlcoholProfile
    mouthfeel: Optional[MouthFeelProfile]
    bitterness: Optional[BitternessProfile] = None
    flavors: FlavorProfile
    commercial_examples: List[str] = Field(default_factory=lambda: [])
    notes: List[str] = Field(default_factory=lambda: [])

    _validate_string_input = validator("region", pre=True, allow_reuse=True)(validate_string_input)
    _validate_optional_string_to_list_input = validator(
        "categories",
        "other_names",
        "glassware",
        "commercial_examples",
        "hops",
        "malt",
        pre=True,
        allow_reuse=True,
    )(validate_optional_string_to_list)

    _validate_notes = validator("notes", pre=True, allow_reuse=True)(validate_optional_string_to_list_no_split)
    _validate_color_profile = validator("color", pre=True, allow_reuse=True)(validate_color_profile)
    _validate_alcohol_profile = validator("alcohol", pre=True, allow_reuse=True)(validate_alcohol_profile)
    _validate_bitterness_profile = validator("bitterness", pre=True, allow_reuse=True)(validate_bitterness_profile)

    def __str__(self) -> str:
        vals = []
        for k, v in self.__dict__.items():
            if not v:
                continue
            if k in ["name"]:
                continue
            delimiter = ", "
            sep = ": "
            if k == "notes":
                sep = ": \n"
                delimiter = "\n"
            tmp_v = v
            if isinstance(tmp_v, list):
                tmp_v = delimiter.join(tmp_v)
            vals.append([snake_to_sentence_case(k), sep, tmp_v])

        serialized_vals = "\n".join(map(lambda x: f"- {x[0]}{x[1]}{x[2]}", vals))
        return f"# {self.name}\n\n{serialized_vals}"

    def print_test(self) -> str:
        vals = []
        for k in ["region", "color", "alcohol", "bitterness"]:
            v = self.__dict__[k]
            if not v:
                continue
            if k in ["name"]:
                continue
            delimiter = ", "
            sep = ": "
            if k == "notes":
                sep = ": \n"
                delimiter = "\n"
            tmp_v = v
            if isinstance(tmp_v, list):
                tmp_v = delimiter.join(tmp_v)
            vals.append([snake_to_sentence_case(k), sep, tmp_v])

        return "\n".join(map(lambda x: f"- {x[0]}{x[1]}{x[2]}", vals))


class BeerStyleMap(BaseModel):
    styles: Dict[str, BeerStyle]

    def __str__(self) -> str:
        sorted_styles = sorted(list(self.styles.values()), key=lambda x: x.name)
        return "\n\n".join(map(str, sorted_styles))

    def test_evaluate_style(self, styles: Dict[str, BeerStyle]) -> Tuple[bool, str, str, str]:
        style = random.choice(list(styles))
        all_lower_style_names = [s.lower() for s in styles.keys()]
        print("\n" + self.styles[style].print_test())
        print("[magenta]Enter style: [/magenta]")
        guess = input("")
        while guess not in all_lower_style_names and guess.lower() != "exit":
            tmp_guess = input("Not a valid style. Try again or type 'exit' to quit:\n")
            if tmp_guess == "exit":
                break
            guess = tmp_guess
        return guess.lower().strip() == style.lower().strip(), style, guess, self.styles[style].print_test()

    def _select_eligible_styles(self, params: BeerStyleTestParams) -> Dict[str, BeerStyle]:
        eligible_styles: Dict[str, BeerStyle] = {}
        for name, style in self.styles.items():
            if len(set([cat.lower() for cat in style.categories]).intersection(params.exclude_categories)) > 0:
                print(f"Excluding style: {name}")
                continue
            eligible_styles[name] = style
        return eligible_styles

    def evaluate(self, params: BeerStyleTestParams) -> None:
        total = 0
        correct = 0
        mistakes = []
        eligible_styles = self._select_eligible_styles(params)
        try:
            while True:
                is_correct, style, guess, printed = self.test_evaluate_style(eligible_styles)
                total += 1
                if is_correct:
                    print(f"[green]Correct![/green]")
                    correct += 1
                else:
                    print(f"[red]Incorrect![/red] Guess: {guess}, Actual: {style}\n")
                    if guess in self.styles:
                        print("*** Your Guess ***")
                        print(self.styles[style].print_test())
                        print("***           ***")
                    mistakes.append([style, guess, printed])
        except KeyboardInterrupt:
            print(f"Results: {total} Attempted; {correct} Correct\n")
            idx = 0
            for mistake in mistakes:
                print(f"Mistake {idx}")
                print(f"Guess: {mistake[1]}, Actual: {mistake[0]}")
                print(f"Prompt:\n{mistake[2]}\n")
