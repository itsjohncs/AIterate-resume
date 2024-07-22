from langchain_core.output_parsers.base import BaseOutputParser
from .search_replace_prompts import format_prompt


class SearchReplaceParser(BaseOutputParser[str]):
    def parse(self, text: str) -> str:
        return text

    @property
    def _type(self) -> str:
        return "search_replace_parser"

    def get_format_instructions(self) -> str:
        return format_prompt
