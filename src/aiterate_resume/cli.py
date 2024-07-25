import argparse
import os
from pathlib import Path
from openai import OpenAI
from .search_replace import parse_search_replace_text
from .system_prompts import system_prompt
from .search_replace_prompts import format_prompt


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

    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": format_prompt},
            {
                "role": "user",
                "content": f"Provide changes to improve the following resume:\n\n{resume_contents}",
            },
        ],
    )

    raw_text = response.choices[0].message.content
    if not raw_text:
        raise ValueError("Got empty response.")

    print(raw_text)
    print("=" * 5)

    parsed_suggestions = parse_search_replace_text(raw_text)

    # Print the parsed suggestions
    for suggestion in parsed_suggestions:
        print(f"Search:\n{suggestion.search}\n")
        print(f"Replace:\n{suggestion.replace}\n")
        print(f"Reason:\n{suggestion.reason}\n")
        print("-" * 5)
