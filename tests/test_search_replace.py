import pytest
from aiterate_resume.search_replace import (
    SearchReplaceResult,
    execute_search_replace,
    MultipleReplacementsError,
    NoReplacementError,
)


def test_success():
    result = SearchReplaceResult("old", "new", "Test replacement")
    source = "This is an old text."
    expected = "This is an new text."
    assert execute_search_replace(result, source) == expected


def test_multiple_replacements():
    result = SearchReplaceResult("old", "new", "Test multiple replacements")
    source = "This old text has old words."
    with pytest.raises(MultipleReplacementsError) as exc_info:
        execute_search_replace(result, source)
    assert exc_info.value.count == 2


def test_no_replacement():
    result = SearchReplaceResult("nonexistent", "new", "Test no replacement")
    source = "This text doesn't contain the search term."
    with pytest.raises(NoReplacementError):
        execute_search_replace(result, source)


def test_empty_source():
    result = SearchReplaceResult("old", "new", "Test empty source")
    source = ""
    with pytest.raises(NoReplacementError):
        execute_search_replace(result, source)


def test_empty_search():
    result = SearchReplaceResult("", "new", "Test empty search")
    source = "This is some text."
    with pytest.raises(MultipleReplacementsError) as exc_info:
        execute_search_replace(result, source)
    assert exc_info.value.count == len(source) + 1
