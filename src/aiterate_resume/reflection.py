from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from .search_replace import (
    MultipleReplacementsError,
    NoReplacementError,
    SearchReplaceResult,
    execute_search_replace,
)

from .chat import ChatSession
from .search_replace_format import (
    UnexpectedEndOfInput,
    UnexpectedFenceError,
    parse_search_replace_text,
)


class FormatMiddleware:
    """Handles parsing, retry counting, and format reflection."""

    def __init__(self, session: ChatSession, max_requests: int):
        self.session = session
        self.remaining_requests = max_requests

    def send_messages(
        self, messages: list[ChatCompletionMessageParam]
    ) -> list[SearchReplaceResult]:
        """Send messages and parse the result.

        This will send reflection messages if the response is not in the
        correct format, and error if we've run out of request attempts.
        """
        # This may get set to reflection messages (ie: messages telling the
        # model to try again due to a parsing error).
        to_send: list[ChatCompletionMessageParam] = messages

        while True:
            if self.remaining_requests == 0:
                raise RuntimeError("Out of attempts.")

            self.remaining_requests -= 1

            response = self.session.send_messages(to_send)
            raw_text = response.choices[0].message.content
            if not raw_text:
                raise ValueError("Got empty response.")

            try:
                return parse_search_replace_text(raw_text)
            except (UnexpectedFenceError, UnexpectedEndOfInput) as e:
                to_send = [
                    {
                        "role": "system",
                        "content": f"Your response was not in the correct *SEARCH/REPLACE block* format. Trying to parse it gave the error: {str(e)}. Please try again, ensuring your response follows the correct format.",
                    }
                ]


def execute_changes(
    changes: list[SearchReplaceResult], src: str
) -> tuple[list[ChatCompletionMessageParam], str]:
    """Try to apply `changes` to `src`.

    Will return a list of reflection messages if there were any failures.
    """
    changed_src = src
    error_messages: list[ChatCompletionMessageParam] = []
    for suggestion in changes:
        try:
            changed_src = execute_search_replace(suggestion, changed_src)
        except (MultipleReplacementsError, NoReplacementError) as e:
            error_messages.append(
                {
                    "role": "system",
                    "content": f"There was an error applying the following *SEARCH/REPLACE block* {e}\n\n{suggestion.to_block()}",
                }
            )

    return error_messages, changed_src


def modify_resume(
    session: ChatSession,
    resume_contents: str,
    messages: list[ChatCompletionMessageParam],
) -> str:
    middleware = FormatMiddleware(session, max_requests=4)
    changes = middleware.send_messages(messages)

    changed_contents = resume_contents

    error_messages, changed_contents = execute_changes(changes, changed_contents)
    while error_messages:
        changes = middleware.send_messages(error_messages)
        error_messages, changed_contents = execute_changes(changes, changed_contents)

    return changed_contents
