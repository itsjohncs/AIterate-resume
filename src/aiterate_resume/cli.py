import argparse
import os
import sys
from pathlib import Path
from openai import OpenAI
from rich import print as rprint
from rich.markup import escape

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from aiterate_resume.search_replace import execute_search_replace
from .search_replace_format import (
    parse_search_replace_text,
    UnexpectedFenceError,
    UnexpectedEndOfInput,
)
from .system_prompts import system_prompt
from . import search_replace_prompts


class Console:
    def __init__(self, verbose: bool = False):
        self.seen_messages: set[int] = set()
        self.verbose = verbose

    def print_message(self, message: ChatCompletionMessageParam):
        if not self.verbose or id(message) in self.seen_messages:
            return

        self.seen_messages.add(id(message))

        role = message["role"]
        content = message.get("content")
        if isinstance(content, str):
            rprint(f"[underline]{role}[/underline]")

            color = "green" if role == "assistant" else "blue"
            for line in content.splitlines():
                rprint(f"[{color}]> {escape(line)}[/{color}]")

    def expected_fatal_error(self, exception: Exception) -> None:
        rprint(f"[red]{exception}[/red]")
        sys.exit(1)


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
        console.expected_fatal_error(
            ValueError("OPENAI_API_KEY environment variable is not set")
        )

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

    for message in messages:
        console.print_message(message)

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

        try:
            parsed_suggestions = parse_search_replace_text(raw_text)
            break
        except (UnexpectedFenceError, UnexpectedEndOfInput) as e:
            if attempt == max_retries - 1:
                console.expected_fatal_error(
                    RuntimeError(
                        f"Failed to parse suggestions after {max_retries} attempts."
                    )
                )
                raise

            error_message = f"Your response was not in the correct *SEARCH/REPLACE block* format. Trying to parse it gave the error: {str(e)}. Please try again, ensuring your response follows the correct format."
            messages.append({"role": "system", "content": error_message})
            print(f"Failed to parse response...\n\t{error_message}")

            for message in messages:
                console.print_message(message)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )

    if not parsed_suggestions:
        console.expected_fatal_error(ValueError("No valid suggestions were parsed."))
        return

    changed_contents = resume_contents
    for suggestion in parsed_suggestions:
        changed_contents = execute_search_replace(suggestion, changed_contents)

    print(changed_contents)
