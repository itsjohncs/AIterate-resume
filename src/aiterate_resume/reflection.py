from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from .search_replace import (
    MultipleReplacementsError,
    NoReplacementError,
    execute_search_replace,
)

from .chat import ChatSession
from .search_replace_format import (
    UnexpectedEndOfInput,
    UnexpectedFenceError,
    parse_search_replace_text,
)


def modify_resume(
    session: ChatSession,
    resume_contents: str,
    messages: list[ChatCompletionMessageParam],
) -> str:
    response = session.send_messages(messages)

    changed_contents = resume_contents
    max_retries = 3
    parsed_suggestions = []
    for attempt in range(max_retries):
        raw_text = response.choices[0].message.content
        if not raw_text:
            raise ValueError("Got empty response.")

        try:
            parsed_suggestions = parse_search_replace_text(raw_text)
        except (UnexpectedFenceError, UnexpectedEndOfInput) as e:
            if attempt == max_retries - 1:
                session.console.quit(
                    f"Failed to parse suggestions after {max_retries} attempt: {e}"
                )

            response = session.send_messages(
                [
                    {
                        "role": "system",
                        "content": f"Your response was not in the correct *SEARCH/REPLACE block* format. Trying to parse it gave the error: {str(e)}. Please try again, ensuring your response follows the correct format.",
                    }
                ]
            )
            continue

        error_messages: list[ChatCompletionMessageParam] = []
        for suggestion in parsed_suggestions:
            try:
                changed_contents = execute_search_replace(suggestion, changed_contents)
            except (MultipleReplacementsError, NoReplacementError) as e:
                error_messages.append(
                    {
                        "role": "system",
                        "content": f"There was an error applying the following *SEARCH/REPLACE block* {e}\n\n{suggestion.to_block()}",
                    }
                )

        if error_messages:
            response = session.send_messages(error_messages)
            continue
        else:
            break
    else:
        session.console.quit("Ran out of reflection attempts.")

    return changed_contents
