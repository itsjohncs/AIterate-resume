import argparse
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .search_replace import SearchReplaceParser
from .system_prompts import system_prompt


def main():
    # Set up argument parser
    arg_parser = argparse.ArgumentParser(description="Process a file and send its contents to the AI model.")
    arg_parser.add_argument("file_path", type=str, help="Path to the file to be processed")
    args = arg_parser.parse_args()

    # Read the contents of the specified file
    file_path = Path(args.file_path)
    with file_path.open('r') as file:
        file_contents = file.read()

    parser = SearchReplaceParser()
    model = ChatOpenAI(model="gpt-4")
    chain = model | parser

    messages = [
        SystemMessage(system_prompt),
        HumanMessage(content=file_contents)
    ]

    response = chain.invoke(messages)
    print(response)
