import argparse
import os
from pathlib import Path
from openai import OpenAI

from .search_replace import SearchReplaceResult, MultipleReplacementsError, NoReplacementError
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


def send_messages(client: OpenAI, messages: list[ChatCompletionMessageParam], max_requests) -> (int, list[SearchReplaceResult]):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    parsed_suggestions: list[SearchReplaceResult] = []
    for attempt in range(max_requests):
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
            if attempt == max_requests - 1:
                print(f"Failed to parse suggestions after {max_requests} attempts.")
                raise

            error_message = f"Your response was not in the correct *SEARCH/REPLACE block* format. Trying to parse it gave the error: {str(e)}. Please try again, ensuring your response follows the correct format."
            messages.append({"role": "system", "content": error_message})
            print(f"Failed to parse response...\n\t{error_message}")

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )

    if not parsed_suggestions:
        raise ValueError("No valid suggestions were parsed.")
        return
    
    return (attempt + 1, parsed_suggestions)


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

    remaining_requests = 4

    num_requests_made, parsed_suggestions = send_messages(client, messages, remaining_requests)
    remaining_requests -= num_requests_made

    # Print the parsed suggestions
    for suggestion in parsed_suggestions:
        print(f"Search:\n{suggestion.search}\n")
        print(f"Replace:\n{suggestion.replace}\n")
        print(f"Reason:\n{suggestion.reason}\n")
        print("-" * 5)

    changed_contents = resume_contents
    while True:
        errors: list[(SearchReplaceResult, MultipleReplacementsError | NoReplacementError)] = []
        for suggestion in parsed_suggestions:
            try:
                changed_contents = execute_search_replace(suggestion, changed_contents)
                print(f"Applied {suggestion}")
            except (MultipleReplacementsError, NoReplacementError) as e:
                errors.append((suggestion, e))
        
        if errors:
            if remaining_requests <= 0:
                raise RuntimeError("Out of attempts.")

            for suggestion, error in errors:
                messages.append({"role": "system", "content": f"There was an error applying the following *SEARCH/REPLACE block* {error}\n\n{suggestion.to_block()}"})
            
            num_requests_made, parsed_suggestions = send_messages(client, messages, remaining_requests)
            remaining_requests -= num_requests_made

    print("=" * 5)
    print(changed_contents)
