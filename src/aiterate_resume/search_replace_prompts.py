from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


format_prompt: str = """Once you understand the request you MUST provide each change as a *SEARCH/REPLACE block* per the examples below. All changes must use this exact *SEARCH/REPLACE block* format. DO NOT PROVIDE CHANGES OUTSIDE OF THIS *SEARCH/REPLACE block* FORMAT.

You MUST provide a reason why each change is needed. Reference specific resume-writing guidelines in each reason. Provide that reason after each *SEARCH/REPLACE block*. Do not write `Reason:` or any other markup to denote that the text is is the reason.

Do not provide any other text or formatting outside of the *SEARCH/REPLACE* blocks and reasons. Do not break the changes into sections. DO NOT PROVIDE ANY OTHER TEXT OR FORMATTING OUTSIDE OF THE *SEARCH/REPLACE* BLOCKS AND REASONS.
"""

examples: list[ChatCompletionMessageParam] = [
    {
        "role": "user",
        "content": "Please provide two improvements to the resume I provided earlier.",
    },
    {
        "role": "assistant",
        "content": """<<<<<<< SEARCH
Proposed designed, and co-built a
<a href="https://www.selenium.dev">Selenium</a>
end-to-end testing system.
=======
Proposed, designed, and co-built a
<a href="https://www.selenium.dev">Selenium</a>
end-to-end testing system.
>>>>>>> REPLACE

Missing a comma between "proposed" and "designed." Make sure your writing is grammatically correct.

<<<<<<< SEARCH
  <li>
    Built a feature-rich map editor using React, TypeScript, and the
    Canvas API with multi-user collaboration supported via the
    <a
      href="https://en.wikipedia.org/wiki/Operational_transformation"
      >operational transformation</a
    >
    algorithm and WebSockets.
  </li>
=======
  <li>
    Developed a collaborative map editor using React, TypeScript, and
    Canvas API, enabling real-time multi-user interactions via
    <a
      href="https://en.wikipedia.org/wiki/Operational_transformation"
      >operational transformation</a
    >
    and WebSockets, resulting in improved user engagement and
    collaboration.
  </li>
>>>>>>> REPLACE

This change provides a clearer picture of the technologies used and emphasizes the impact on user engagement and collaboration.
""",
    },
    {
        "role": "user",
        "content": "Thank you. I'm done with that resume now. Please don't give any more improvements regarding that resume.",
    },
]
