import argparse
import os
from pathlib import Path
from openai import OpenAI
from .search_replace import SearchReplaceParser
from .system_prompts import system_prompt


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

    # Ensure OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Prepare the messages for the API call
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Give suggestions to improve the following resume:\n\n{resume_contents}",
        },
        {
            "role": "user",
            "content": f"Format your response according to these instructions:\n\n{parser.get_format_instructions()}",
        },
    ]

    # Make the API call
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)

    # Extract the content from the response
    ai_suggestions = response.choices[0].message.content

    # Parse the suggestions using the existing SearchReplaceParser
    parsed_suggestions = parser.parse(ai_suggestions)

    # Print the parsed suggestions
    for suggestion in parsed_suggestions:
        print(f"Search:\n{suggestion.search}\n")
        print(f"Replace:\n{suggestion.replace}\n")
        print(f"Reason:\n{suggestion.reason}\n")
        print("-" * 50)
