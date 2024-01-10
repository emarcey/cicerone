from collections import Counter
from datetime import datetime
from enum import Enum
import os
import random
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from string import capwords
from typing import Dict, List, Optional, Set, Tuple

from src.const import STYLE_CAT__HISTORICAL, STYLE_CAT__SPECIALTY
from src.utils import (
    clear_screen,
    snake_to_sentence_case,
    validate_alcohol_profile,
    validate_bitterness_profile,
    validate_color_profile,
    validate_optional_string_input,
    validate_optional_string_to_list,
    validate_optional_string_to_list_no_split,
    validate_string_input,
)

console = Console()


class GuessProximity(Enum):
    miss = 0
    close = 1
    very_close = 2
    exact = 3

    def _to_output_color(self) -> str:
        if self.value == 0:
            return "red"
        elif self.value == 1 or self.value == 2:
            return "cyan"
        return "green"

    def _to_output_message(self) -> str:
        color = self._to_output_color()
        message = "Correct"
        if self.value == 0:
            message = "Incorrect"
        elif self.value == 1:
            message = "Close"
        elif self.value == 2:
            message = "Almost Correct"
        return f"[{color}]{message}[/{color}]"


class GlossaryLine(BaseModel):
    value: str
    indent: int

    _validate_string_input = field_validator("value", mode="before")(validate_string_input)

    def __str__(self) -> str:
        indent = "\t" * (self.indent - 1)
        return f"{indent}-  {self.value}"


class GlossaryHeader(BaseModel):
    name: str
    value: str
    lines: List[GlossaryLine] = Field(default_factory=lambda: [])
    _validate_string_input = field_validator("name", "value", mode="before")(validate_string_input)

    def __str__(self) -> str:
        lines = [f"# {capwords(self.name)}"]
        if self.value:
            lines.append(f"-  {self.value}")

        return "\n".join(lines + list(map(str, self.lines)))


class BeerStyleTestParams(BaseModel):
    exclude_categories: Set[str] = Field(default_factory=lambda: {STYLE_CAT__HISTORICAL, STYLE_CAT__SPECIALTY})
    proximity_threshold_default: float = 2.5
    proximity_threshold_abv: float = 0.25


class MouthFeelProfile(BaseModel):
    body: str
    carbonation: str
    alcohol_warmth: Optional[str] = None

    _validate_string_input = field_validator("body", "carbonation", mode="before")(validate_string_input)
    _validate_optional_string_input = field_validator("alcohol_warmth", mode="before")(validate_optional_string_input)

    def __str__(self) -> str:
        vals = []
        for k, v in self.__dict__.items():
            vals.append([k, v])
        return "\n" + "\n".join(map(lambda x: f"\t- {x[0]}: {x[1]}", vals))


class FlavorProfile(BaseModel):
    malt: List[str]
    fermentation: List[str]
    hop: List[str]
    _validate_string_input = field_validator("malt", "fermentation", "hop", mode="before")(
        validate_optional_string_to_list
    )

    def __str__(self) -> str:
        vals = []
        for k, v in self.__dict__.items():
            vals.append([k, ", ".join(v)])
        return "\n" + "\n".join(map(lambda x: f"\t- {x[0]}: {x[1]}", vals))


class ColorProfile(BaseModel):
    color_range: List[str]
    value_low: float
    value_high: float

    def __str__(self) -> str:
        return f"{' - '.join(self.color_range)} ({self.value_low} - {self.value_high} SRM)"


class AlcoholProfile(BaseModel):
    alcohol_range: List[str]
    value_low: float
    value_high: float
    notes: List[str] = Field(default_factory=lambda: [])

    def __str__(self) -> str:
        vals = [f"{' - '.join(self.alcohol_range)} ({self.value_low} - {self.value_high}% ABV)"]
        for note in self.notes:
            vals.append(f"\t- {note}")
        return "\n".join(vals)


class BitternessProfile(BaseModel):
    bitterness_range: List[str]
    value_low: float
    value_high: float

    def __str__(self) -> str:
        return f"{' - '.join(self.bitterness_range)} ({self.value_low} - {self.value_high} IBU)"


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

    _validate_string_input = field_validator("region", mode="before")(validate_string_input)
    _validate_optional_string_to_list_input = field_validator(
        "categories",
        "other_names",
        "glassware",
        "commercial_examples",
        "hops",
        "malt",
        mode="before",
    )(validate_optional_string_to_list)

    _validate_notes = field_validator("notes", mode="before")(validate_optional_string_to_list_no_split)
    _validate_color_profile = field_validator("color", mode="before")(validate_color_profile)
    _validate_alcohol_profile = field_validator("alcohol", mode="before")(validate_alcohol_profile)
    _validate_bitterness_profile = field_validator("bitterness", mode="before")(validate_bitterness_profile)

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

    def _evaluate_match_proximity(
        self,
        name: str,
        value_lower: float,
        value_upper: float,
        guess_lower: float,
        guess_upper: float,
        params: BeerStyleTestParams,
    ) -> Tuple[GuessProximity, GuessProximity, GuessProximity]:
        proximity_threshold = params.proximity_threshold_default
        if name == "alcohol":
            proximity_threshold = params.proximity_threshold_abv
        lower_proximity = GuessProximity.miss
        if value_lower == guess_lower:
            lower_proximity = GuessProximity.exact
        elif abs(value_lower - guess_lower) <= proximity_threshold:
            lower_proximity = GuessProximity.close

        upper_proximity = GuessProximity.miss
        if value_upper == guess_upper:
            upper_proximity = GuessProximity.exact
        elif abs(value_upper - guess_upper) <= proximity_threshold:
            upper_proximity = GuessProximity.close

        overall_proximity = GuessProximity.miss
        if lower_proximity == GuessProximity.exact and upper_proximity == GuessProximity.exact:
            overall_proximity = GuessProximity.exact
        elif (lower_proximity == GuessProximity.exact and upper_proximity == GuessProximity.close) or (
            lower_proximity == GuessProximity.close and upper_proximity == GuessProximity.exact
        ):
            overall_proximity = GuessProximity.very_close
        elif (lower_proximity == GuessProximity.exact or upper_proximity == GuessProximity.exact) or (
            lower_proximity != GuessProximity.miss and upper_proximity != GuessProximity.miss
        ):
            overall_proximity = GuessProximity.close

        return overall_proximity, lower_proximity, upper_proximity

    def evaluate_value(self, params: BeerStyleTestParams) -> Tuple[str, str, float, float, float, float]:
        value = random.choice(["alcohol", "bitterness", "color"])
        console.print("*" * 20)
        console.print(self.name, style="bold")
        console.print("*" * 20)

        value_lower = getattr(self, value).value_low
        value_upper = getattr(self, value).value_high

        guess_lower = None
        guess_upper = None
        while not guess_upper and not guess_lower:
            try:
                guess_lower = float(console.input(f"Enter the lower bound for {value}: "))
                guess_upper = float(console.input(f"Enter the upper bound for {value}: "))
            except ValueError as e:
                console.print(e)
                console.print("Try again")
        lower_color = "cyan"
        upper_color = "cyan"

        overall_proximity, lower_proximity, upper_proximity = self._evaluate_match_proximity(
            value, float(value_lower), float(value_upper), float(guess_lower), float(guess_upper), params
        )

        console.print(overall_proximity._to_output_message(), style="bold")
        if overall_proximity != GuessProximity.exact:
            lower_color = lower_proximity._to_output_color()
            upper_color = upper_proximity._to_output_color()
            console.print(
                f"Actual Value: [{lower_color}]{value_lower}[/{lower_color}] - [{upper_color}]{value_upper}[/{upper_color}]; "
                + f"Your Guess: {guess_lower} - {guess_upper}",
                style="bold",
            )
        return (
            overall_proximity.name,
            value,
            float(value_lower),
            float(value_upper),
            float(guess_lower),
            float(guess_upper),
        )

    def print_test(self) -> str:
        vals = []
        for k in ["region", "color", "alcohol", "bitterness"]:
            v = self.__dict__[k]
            if not v:
                continue
            if k in ["region"]:
                v = v.split(", ")[-1]
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
    output_directory: str = "./evaluate_results"
    start_time: datetime = Field(default_factory=lambda: datetime.now())

    def __str__(self) -> str:
        sorted_styles = sorted(list(self.styles.values()), key=lambda x: x.name)
        return "\n\n".join(map(str, sorted_styles))

    def test_evaluate_style(
        self, style_name: str, style_value: BeerStyle, all_lower_style_names: Set[str]
    ) -> Tuple[bool, str, str, str]:
        console.print("*" * 20)
        console.print("\n" + style_value.print_test())
        console.print("*" * 20)
        console.print("Enter style: ", style="magenta")
        guess = input("")
        while guess.lower() not in all_lower_style_names and guess.lower() != "exit":
            tmp_guess = input("Not a valid style. Try again or type 'exit' to quit:\n")
            if tmp_guess == "exit":
                break
            guess = tmp_guess
        return (
            guess.lower().strip() == style_name.lower().strip(),
            all_lower_style_names.get(guess.lower(), guess),
            style_value.print_test(),
        )

    def _select_eligible_styles(self, params: BeerStyleTestParams) -> Dict[str, BeerStyle]:
        eligible_styles: Dict[str, BeerStyle] = {}
        for name, style in self.styles.items():
            if len(set([cat.lower() for cat in style.categories]).intersection(params.exclude_categories)) > 0:
                console.print(f"Excluding style: {name}")
                continue
            eligible_styles[name] = style
        return eligible_styles

    def output_results(
        self, total: int, correct: int, mistakes: List[Tuple[str, str, str]], all_results: List[Tuple[str, str, bool]]
    ) -> None:
        if total <= 0:
            return
        clear_screen()
        console.print("")
        console.print("*" * 20)
        console.print(f"Results:")
        console.print("*" * 20)
        console.print(f"{total} Attempted")
        console.print(f"{correct} Correct")
        accuracy = round(correct / total, 2) * 100
        console.print(f"{accuracy}% Accuracy")
        console.print("*" * 20)
        idx = 1
        if mistakes:
            console.print(f"Mistakes: \n")
        for mistake in mistakes:
            console.print(f"Mistake {idx}")
            console.print(f"Guess: {mistake[1]}, Actual: {mistake[0]}")
            console.print(f"Prompt:\n{mistake[2]}\n")
            idx += 1

        output_directory = self.output_directory + "/evaluate"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        start_time = self.start_time.strftime("%Y%m%d_%H%M%S")
        all_lines = [["style", "guess", "is_correct"]] + all_results

        with open(f"{output_directory}/evaluate_{start_time}.csv", "w") as f:
            for line in all_lines:
                line_to_write = ",".join(map(str, line)) + "\n"
                f.write(line_to_write)

    def output_evaluate_values_results(
        self, result_count: Counter, all_results: List[Tuple[str, str, float, float, float, float]]
    ) -> None:
        total = sum(result_count.values())
        if total <= 0:
            return
        clear_screen()
        console.print("")
        console.print("*" * 20)
        console.print(f"Results:")
        console.print("*" * 20)
        console.print(f"{total} Attempted")
        for guess_proximity_type in GuessProximity:
            num_of_type = result_count.get(guess_proximity_type.name, 0)
            accuracy = round(round(num_of_type / total, 4) * 100, 2)
            console.print(f"{num_of_type} {guess_proximity_type._to_output_message()}: {accuracy}%")
        console.print("*" * 20)

        output_directory = self.output_directory + "/evaluate_value"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        start_time = self.start_time.strftime("%Y%m%d_%H%M%S")
        all_lines = [
            ["style", "value_name", "result", "value_lower", "value_upper", "guess_low", "guess_upper"]
        ] + all_results
        with open(f"{output_directory}/evaluate_value_{start_time}.csv", "w") as f:
            for line in all_lines:
                line_to_write = ",".join(map(str, line)) + "\n"
                f.write(line_to_write)

    def evaluate_values(self, params: BeerStyleTestParams) -> None:
        total = 0
        correct = 0
        close = 0
        eligible_styles = self._select_eligible_styles(params)
        all_results = []
        result_count = Counter()
        clear_screen()
        try:
            while True:
                style = random.choice(list(eligible_styles))
                result, value_name, value_lower, value_upper, guess_low, guess_upper = self.styles[
                    style
                ].evaluate_value(params)
                result_count.update([result])
                total += 1
                if result == GuessProximity.exact.name:
                    correct += 1
                elif result != GuessProximity.miss.name:
                    close += 1
                all_results.append((style, value_name, result, value_lower, value_upper, guess_low, guess_upper))
        except KeyboardInterrupt:
            self.output_evaluate_values_results(result_count, all_results)

    def evaluate(self, params: BeerStyleTestParams) -> None:
        total = 0
        correct = 0
        mistakes = []
        eligible_styles = self._select_eligible_styles(params)
        # tmp_eligible_styles = list(eligible_styles)
        tmp_eligible_styles = []
        all_results = []
        clear_screen()
        try:
            while True:
                if not tmp_eligible_styles:
                    console.print(
                        "Wow! You finished everything! Let's roll it back and start over!", style="bold green"
                    )
                    tmp_eligible_styles = list(eligible_styles)
                style = random.choice(tmp_eligible_styles)
                tmp_eligible_styles.remove(style)
                all_lower_style_names = {s.lower(): s for s in eligible_styles.keys()}
                is_correct, guess, printed = self.test_evaluate_style(
                    style, eligible_styles[style], all_lower_style_names
                )
                total += 1
                all_results.append((style, guess, is_correct))
                if is_correct:
                    console.print(f"Correct!", style="bold green")
                    correct += 1
                else:
                    console.print(f"[bold][red]Incorrect![/red][/bold] Guess: {guess}, Actual: {style}\n")
                    if guess in self.styles:
                        console.print("**** Your Guess ****")
                        console.print(self.styles[guess].print_test())
                        console.print("********************")
                    mistakes.append((style, guess, printed))
        except KeyboardInterrupt:
            self.output_results(total, correct, mistakes, all_results)
