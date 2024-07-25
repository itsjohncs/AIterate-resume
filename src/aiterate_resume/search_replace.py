from typing import NamedTuple


class MultipleReplacementsError(Exception):
    """Raised when more than one replacement occurs."""

    def __init__(self, count: int):
        self.count = count
        super().__init__(
            "The text in the SEARCH section was found multiple times in the resume. Make sure to include enough context lines to uniquely match the lines to change."
        )


class NoReplacementError(Exception):
    """Raised when no replacement occurs."""

    def __init__(self):
        super().__init__(
            "Could not find text in the SEARCH section in the resume. Make sure it matches the contents of the resume exactly, including whitespace, comments, tags, etc."
        )


class SearchReplaceResult(NamedTuple):
    search: str
    replace: str
    reason: str

    def to_block(self) -> str:
        return f"<<<<<<< SEARCH\n{self.search}\n=======\n{self.replace}\n>>>>>>> REPLACE\n\n{self.reason}\n"


def execute_search_replace(result: SearchReplaceResult, source: str) -> str:
    """
    Execute a SearchReplaceResult on the given source text.

    Args:
        result (SearchReplaceResult): The search and replace instructions.
        source (str): The source text to modify.

    Returns:
        str: The modified source text.

    Raises:
        MultipleReplacementsError: If more than one replacement would occur.
        NoReplacementError: If no replacement occurs.
    """
    count = source.count(result.search)
    if count > 1:
        raise MultipleReplacementsError(count)
    elif count == 0:
        raise NoReplacementError()
    return source.replace(result.search, result.replace)
