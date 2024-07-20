from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from .search_replace import SearchReplaceParser
from .system_prompts import system_prompt


def main():
    parser = SearchReplaceParser()
    model = ChatOpenAI(model="gpt-4")
    chain = model | parser

    messages = [
        SystemMessage(system_prompt),
    ]

    response = chain.invoke(messages)
    print(response)
