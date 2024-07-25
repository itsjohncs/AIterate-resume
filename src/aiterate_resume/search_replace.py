from typing import NamedTuple


class MultipleReplacementsError(Exception):
    """Raised when more than one replacement occurs."""

    def __init__(self, count: int):
        self.count = count
        super().__init__(f"Multiple replacements occurred: {count}")


class NoReplacementError(Exception):
    """Raised when no replacement occurs."""

    def __init__(self):
        super().__init__("No replacement occurred")


class SearchReplaceResult(NamedTuple):
    search: str
    replace: str
    reason: str


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
