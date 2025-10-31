# --- Main Prompt Template ---
MAIN_PROMPT_TEMPLATE = '''
You are an expert system that converts natural language descriptions of processes into a structured GRAPH JSON format.
Your response MUST be a single, valid JSON object and nothing else. Do not include any explanatory text, markdown, or comments.

The JSON object must conform to the following schema:
{{
  "nodes": [
    {{"id": "string", "label": "string", "group": "string", "shape": "string"}},
    ...
  ],
  "edges": [
    {{"source": "string", "target": "string", "label": "string"}},
    ...
  ],
  "layout": {{"direction": "string"}}
}}

RULES:
1.  `nodes.id`: Must be a short, unique string (e.g., "A", "B", "C1").
2.  `nodes.label`: Keep it concise, ideally under 6 words.
3.  `nodes.shape`: Must be one of: "box", "ellipse", "diamond", "circle". Use "diamond" for decisions/questions.
4.  `edges`: Connect nodes using their `id` values in `source` and `target`.
5.  `layout.direction`: Must be either "TB" (Top-to-Bottom) or "LR" (Left-to-Right). Choose the one that best fits the flow.
6.  Generate a maximum of 40 nodes unless the user's text clearly implies a larger process.
7.  Do NOT add any extra keys or properties to the objects.

Here is the user's description of the process:
---
{user_text}
---

Now, generate the GRAPH JSON based on this description.
'''

# --- Repair Prompt Template ---
REPAIR_PROMPT_TEMPLATE = '''
You previously generated JSON that failed validation. You must correct it.
Your response MUST be a single, valid JSON object and nothing else. Do not include any explanatory text, markdown, or comments.

Here was the original user request:
---
{user_text}
---

Here is the invalid JSON you generated:
---
{invalid_json}
---

And here is the validation error message:
---
{error_message}
---

Please analyze the error and the original request, then generate a new, valid GRAPH JSON that fixes the problem.
'''
