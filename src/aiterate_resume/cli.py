import argparse
import os
from pathlib import Path
from openai import OpenAI

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from aiterate_resume.search_replace import execute_search_replace
from .search_replace_format import (
    parse_search_replace_text,
    UnexpectedFenceError,
    UnexpectedEndOfInput,
)
from .system_prompts import system_prompt
from . import search_replace_prompts


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

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": search_replace_prompts.format_prompt},
        *search_replace_prompts.examples,
        {
            "role": "user",
            "content": f"Provide changes to improve the following resume:\n\n{resume_contents}",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    max_retries = 3
    parsed_suggestions = []
    for attempt in range(max_retries):
        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        raw_text = response.choices[0].message.content
        if not raw_text:
            raise ValueError("Got empty response.")

        print(raw_text)
        print("=" * 5)

        try:
            parsed_suggestions = parse_search_replace_text(raw_text)
            break
        except (UnexpectedFenceError, UnexpectedEndOfInput) as e:
            if attempt == max_retries - 1:
                print(f"Failed to parse suggestions after {max_retries} attempts.")
                raise

            error_message = f"Your response was not in the correct *SEARCH/REPLACE block* format. Trying to parse it gave the error: {str(e)}. Please try again, ensuring your response follows the correct format."
            messages.append({"role": "system", "content": error_message})
            print(f"Failed to parse response...\n\t{error_message}")

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )

    if not parsed_suggestions:
        print("No valid suggestions were parsed.")
        return

    # Print the parsed suggestions
    for suggestion in parsed_suggestions:
        print(f"Search:\n{suggestion.search}\n")
        print(f"Replace:\n{suggestion.replace}\n")
        print(f"Reason:\n{suggestion.reason}\n")
        print("-" * 5)

    changed_contents = resume_contents
    for suggestion in parsed_suggestions:
        changed_contents = execute_search_replace(suggestion, changed_contents)
        print(f"Applied {suggestion}")

    print("=" * 5)
    print(changed_contents)
