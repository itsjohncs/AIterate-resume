from langchain_core.output_parsers.base import BaseOutputParser


class SearchReplaceParser(BaseOutputParser[str]):
    def parse(self, text: str) -> str:
        return text

    @property
    def _type(self) -> str:
        return "search_replace_parser"
