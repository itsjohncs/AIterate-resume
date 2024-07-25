from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai import OpenAI
import sys

from rich import print as rprint
from rich.markup import escape


class Console:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def print_message(self, message: ChatCompletionMessageParam, verbose_level=False):
        if verbose_level and not self.verbose:
            return

        role = message["role"]
        content = message.get("content")
        if isinstance(content, str):
            rprint(f"[underline]{role}[/underline]")

            color = "green" if role == "assistant" else "blue"
            for line in content.splitlines():
                rprint(f"[{color}]> {escape(line)}[/{color}]")

    def print_messages(
        self, messages: list[ChatCompletionMessageParam], verbose_level=False
    ) -> None:
        for message in messages:
            self.print_message(message, verbose_level)

    def expected_fatal_error(self, exception: Exception) -> None:
        rprint(f"[red]{exception}[/red]")
        sys.exit(1)


class ChatSession:
    def __init__(self, client: OpenAI, console: Console):
        self.client = client
        self.console = console
        self.messages: list[ChatCompletionMessageParam] = []

    def send_messages(self, messages: list[ChatCompletionMessageParam]):
        self.messages.extend(messages)
        self.console.print_messages(messages)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
        )

        response_message: ChatCompletionMessageParam = {
            "role": "assistant",
            "content": response.choices[0].message.content,
        }
        self.messages.append(response_message)
        self.console.print_message(response_message)

        return response
