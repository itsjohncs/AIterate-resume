from typing import NamedTuple
from enum import Enum
from langchain_core.output_parsers.base import BaseOutputParser
from .search_replace_prompts import format_prompt


class SearchReplaceResult(NamedTuple):
    search: str
    replace: str
    reason: str


class ParserState(Enum):
    LOOKING_FOR_SEARCH = 1
    IN_SEARCH = 2
    IN_REPLACE = 3
    IN_REASON = 4


class UnexpectedFenceError(Exception):
    def __init__(self, expected_fence: str, found_fence: str):
        self.expected_fence = expected_fence
        self.found_fence = found_fence
        super().__init__(
            f"Expected fence '{expected_fence}', but found '{found_fence}'."
        )


class UnexpectedEndOfInput(Exception):
    def __init__(self, expected_fence: str):
        self.expected_fence = expected_fence
        super().__init__(f"Unexpected end of input. Expected fence '{expected_fence}'.")


class FenceStateSpec(NamedTuple):
    allowed_in: set[ParserState]
    "The state the parser is allowed to be in."

    next_state: ParserState
    "The state to put the parser into after."


FENCE_STATE_SPECS = {
    "<<<<<<< SEARCH": FenceStateSpec(
        {ParserState.LOOKING_FOR_SEARCH, ParserState.IN_REASON}, ParserState.IN_SEARCH
    ),
    "=======": FenceStateSpec({ParserState.IN_SEARCH}, ParserState.IN_REPLACE),
    ">>>>>>> REPLACE": FenceStateSpec({ParserState.IN_REPLACE}, ParserState.IN_REASON),
}

STATE_TO_FENCE: dict[ParserState, str] = {}
for state in ParserState:
    for fence, spec in FENCE_STATE_SPECS.items():
        if state in spec.allowed_in:
            STATE_TO_FENCE[state] = fence
            break
    else:
        raise ValueError(f"Could not find expected fence for {state}.")


def parse_search_replace_text(text: str) -> list[SearchReplaceResult]:
    results = []
    state = ParserState.LOOKING_FOR_SEARCH

    current_search = []
    current_replace = []
    current_reason = []

    for line in text.split("\n"):
        spec = FENCE_STATE_SPECS.get(line.rstrip())
        if spec:
            if state not in spec.allowed_in:
                raise UnexpectedFenceError(STATE_TO_FENCE[state], line.rstrip())

            # If we're moving _out of_ the reason state
            if state == ParserState.IN_REASON:
                results.append(
                    SearchReplaceResult(
                        search="\n".join(current_search).strip(),
                        replace="\n".join(current_replace).strip(),
                        reason="\n".join(current_reason).strip(),
                    )
                )
                current_search = []
                current_replace = []
                current_reason = []

            state = spec.next_state
        else:
            if state == ParserState.IN_SEARCH:
                current_search.append(line)
            elif state == ParserState.IN_REPLACE:
                current_replace.append(line)
            elif state == ParserState.IN_REASON:
                current_reason.append(line)

    if current_search or current_replace or current_reason:
        if state != ParserState.IN_REASON:
            raise UnexpectedEndOfInput(STATE_TO_FENCE[state])

        results.append(
            SearchReplaceResult(
                search="\n".join(current_search).strip(),
                replace="\n".join(current_replace).strip(),
                reason="\n".join(current_reason).strip(),
            )
        )

    if state == ParserState.LOOKING_FOR_SEARCH:
        raise UnexpectedEndOfInput(STATE_TO_FENCE[state])

    return results


class SearchReplaceParser(BaseOutputParser[list[SearchReplaceResult]]):
    def parse(self, text: str) -> list[SearchReplaceResult]:
        return parse_search_replace_text(text)

    @property
    def _type(self) -> str:
        return "search_replace_parser"

    def get_format_instructions(self) -> str:
        return format_prompt
