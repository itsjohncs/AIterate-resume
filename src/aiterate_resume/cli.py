import argparse
from pathlib import Path
from langchain_openai import ChatOpenAI
from .search_replace import SearchReplaceParser
from .system_prompts import system_prompt
from langchain_core.prompts import ChatPromptTemplate


def parse_args():
    # Set up argument parser
    arg_parser = argparse.ArgumentParser(description="Iterate on a resume with an AI.")
    arg_parser.add_argument("resume", type=str, help="Path to the file to be processed")
    args = arg_parser.parse_args()

    # Read the contents of the specified file
    resume = Path(args.resume)
    with resume.open("r") as file:
        resume_contents = file.read()

    return resume_contents


def main():
    resume_contents = parse_args()

    parser = SearchReplaceParser()
    model = ChatOpenAI(model="gpt-4o")
    chain = model | parser

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                "Give suggestions to improve the following resume:\n\n{resume_contents}",
            ),
        ]
    )

    print(
        chain.invoke(
            prompt.format_messages(
                resume_contents=resume_contents,
                format_prompt=parser.get_format_instructions(),
            )
        )
    )
