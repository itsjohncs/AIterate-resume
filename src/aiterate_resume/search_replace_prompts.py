format_prompt = """Once you understand the request you MUST describe each change with a *SEARCH/REPLACE block* per the examples below. All changes must use this *SEARCH/REPLACE block* format. ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!"""

example_messages = [
    dict(
        role="user",
        content="Suggest two general improvements to my resume. Keep each suggested improvement small.",
    ),
    dict(
        role="assistant",
        content="""```
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
```
This change provides a clearer picture of the technologies used and emphasizes the impact on user engagement and collaboration.

```
<<<<<<< SEARCH
        <summary>
          Built Unity simulations and editor extensions for their YouTube
          channel with 1.7M subscribers.
        </summary>
=======
        <summary>
          Developed Unity simulations and editor extensions, enhancing
          educational content for a YouTube channel with 1.7M subscribers.
        </summary>
>>>>>>> REPLACE
```
This change emphasizes the role in improving educational content and provides a clearer context for the impact.
""",
    ),
]
