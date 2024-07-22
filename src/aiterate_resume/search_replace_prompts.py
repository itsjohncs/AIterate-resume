format_prompt: str = """Once you understand the request you MUST describe each change with a reason followed by a *SEARCH/REPLACE block* per the examples below. All changes must use this *SEARCH/REPLACE block* format. All changes must be preceded by a reason.

This change provides a clearer picture of the technologies used and emphasizes the impact on user engagement and collaboration.

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
"""
