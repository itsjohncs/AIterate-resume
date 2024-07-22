from typing import List, NamedTuple
import re
from langchain_core.output_parsers.base import BaseOutputParser
from .search_replace_prompts import format_prompt


class SearchReplaceResult(NamedTuple):
    search: str
    replace: str
    reason: str


class SearchReplaceParser(BaseOutputParser[List[SearchReplaceResult]]):
    def parse(self, text: str) -> List[SearchReplaceResult]:
        results = []
        pattern = r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE\n\n(.*?)\n\n"
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            search_text, replace_text, reason = match
            results.append(
                SearchReplaceResult(
                    search=search_text.strip(),
                    replace=replace_text.strip(),
                    reason=reason.strip(),
                )
            )

        return results

    @property
    def _type(self) -> str:
        return "search_replace_parser"

    def get_format_instructions(self) -> str:
        return format_prompt
