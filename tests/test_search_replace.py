import pytest
from aiterate_resume.search_replace import (
    UnexpectedEndOfInput,
    parse_search_replace_text,
    SearchReplaceResult,
    UnexpectedFenceError,
)


def test_single_result():
    input_text = """<<<<<<< SEARCH
old text
=======
new text
>>>>>>> REPLACE
This is the reason for the change."""

    expected_result = [
        SearchReplaceResult(
            search="old text",
            replace="new text",
            reason="This is the reason for the change.",
        )
    ]

    assert parse_search_replace_text(input_text) == expected_result


def test_multiple_results():
    input_text = """<<<<<<< SEARCH
old text 1
=======
new text 1
>>>>>>> REPLACE
Reason 1

<<<<<<< SEARCH
old text 2
=======
new text 2
>>>>>>> REPLACE
Reason 2"""

    expected_result = [
        SearchReplaceResult(
            search="old text 1", replace="new text 1", reason="Reason 1"
        ),
        SearchReplaceResult(
            search="old text 2", replace="new text 2", reason="Reason 2"
        ),
    ]

    assert parse_search_replace_text(input_text) == expected_result


def test_multiline():
    input_text = """<<<<<<< SEARCH
old text
with multiple
lines
=======
new text
also with
multiple lines
>>>>>>> REPLACE
This is the reason
for the change."""

    expected_result = [
        SearchReplaceResult(
            search="old text\nwith multiple\nlines",
            replace="new text\nalso with\nmultiple lines",
            reason="This is the reason\nfor the change.",
        )
    ]

    assert parse_search_replace_text(input_text) == expected_result


def test_empty_sections():
    input_text = """<<<<<<< SEARCH
=======
>>>>>>> REPLACE
No change needed."""

    expected_result = [
        SearchReplaceResult(search="", replace="", reason="No change needed.")
    ]

    assert parse_search_replace_text(input_text) == expected_result


def test_unexpected_fence():
    input_text = """<<<<<<< SEARCH
old text
>>>>>>> REPLACE
This is invalid."""

    with pytest.raises(UnexpectedFenceError) as excinfo:
        parse_search_replace_text(input_text)

    assert excinfo.value.expected_fence == "======="
    assert excinfo.value.found_fence == ">>>>>>> REPLACE"


def test_missing_fence():
    input_text = """<<<<<<< SEARCH
old text
=======
new text
This is invalid."""

    with pytest.raises(UnexpectedEndOfInput) as excinfo:
        parse_search_replace_text(input_text)

    assert excinfo.value.expected_fence == ">>>>>>> REPLACE"


def test_wrong_format():
    input_text = """old text
new text
This is invalid."""

    with pytest.raises(UnexpectedEndOfInput) as excinfo:
        parse_search_replace_text(input_text)

    assert excinfo.value.expected_fence == "<<<<<<< SEARCH"
