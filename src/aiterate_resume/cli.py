import argparse
import os
from pathlib import Path
from openai import OpenAI

from aiterate_resume.reflection import modify_resume
from .system_prompts import system_prompt
from . import search_replace_prompts
from .chat import Console, ChatSession


def parse_args():
    # Set up argument parser
    arg_parser = argparse.ArgumentParser(description="Iterate on a resume with an AI.")
    arg_parser.add_argument("resume", type=str, help="Path to the file to be processed")
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = arg_parser.parse_args()

    # Read the contents of the specified file
    resume = Path(args.resume)
    with resume.open("r") as file:
        resume_contents = file.read()

    return args, resume_contents


def main():
    args, resume_contents = parse_args()
    console = Console(verbose=args.verbose)

    if "OPENAI_API_KEY" not in os.environ:
        console.quit("OPENAI_API_KEY environment variable is not set")

    session = ChatSession(OpenAI(api_key=os.environ["OPENAI_API_KEY"]), console)

    changed_contents = modify_resume(
        session,
        resume_contents,
        [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": search_replace_prompts.format_prompt},
            *search_replace_prompts.examples,
            {
                "role": "user",
                "content": f"Provide changes to improve the following resume:\n\n{resume_contents}",
            },
        ],
    )

    print(changed_contents)
