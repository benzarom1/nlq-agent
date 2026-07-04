import json
from typing import Any

import gradio as gr
import pandas as pd
from langchain_core.messages import HumanMessage

from src.graph import build_graph


graph_app = build_graph()


def format_state(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2, default=str)


def results_to_dataframe(state: dict[str, Any]) -> pd.DataFrame:
    rows = state.get("query_results") or []
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def run_graph(message: str, history: list[dict[str, str]]):
    if not message or not message.strip():
        yield "", history, "Please enter a question.", "", pd.DataFrame()
        return

    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": "Thinking..."})

    latest_state: dict[str, Any] = {}

    initial_state = {
        "question": message,
        "messages": [HumanMessage(content=message)],
        "retry_count": 0,
    }

    yield "", history, "Starting graph...", "", pd.DataFrame()

    try:
        for event in graph_app.stream(initial_state, stream_mode="updates"):
            for node_name, update in event.items():
                if isinstance(update, dict):
                    latest_state.update(update)

                history[-1] = {
                    "role": "assistant",
                    "content": f"Working... ({node_name})",
                }

                yield (
                    "",
                    history,
                    format_state(latest_state),
                    latest_state.get("generated_sql", ""),
                    results_to_dataframe(latest_state),
                )

        final_answer = latest_state.get(
            "final_answer",
            "I could not generate a final answer.",
        )

        history[-1] = {
            "role": "assistant",
            "content": final_answer,
        }

        yield (
            "",
            history,
            format_state(latest_state),
            latest_state.get("generated_sql", ""),
            results_to_dataframe(latest_state),
        )

    except Exception as e:
        history[-1] = {
            "role": "assistant",
            "content": f"Something went wrong: {e}",
        }

        yield "", history, f"Error: {e}", "", pd.DataFrame()


def clear_chat():
    return [], "State cleared.", "", pd.DataFrame()


with gr.Blocks(title="NBA NLQ Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # NBA NLQ Agent

        Ask a question about the NBA data and watch the current graph state update as the workflow runs.
        """
    )
    with gr.Tab("About"):
        instructions = gr.Markdown(label = "Instructions", value= """
This app allows you to ask analytic questions about **NBA player box scores (2010–2024)** in natural language.

The assistant will:
- Classify your question
- Generate the appropriate SQL query
- Execute the query
- Return a clear answer
- Display the generated SQL and raw query results
---

## Example Questions

Questions the agent can answer:

- Who scored the most points in a single game during the 2023 season?
- What was LeBron James' average points per game in 2022?
- Which Warriors players had 30+ points in a game?

---

## Questions That Will Fail Gracefully

The app will reject unsupported questions and explain why.

### Missing data
**Question:**  
Which players scored the most points in 2007?

**Reason:**  
Data is only from 2010 to 2024 NBA season.

---

### Unsupported database changes
**Question:**  
Update Chris Paul's points in game 12345 to 50.

**Reason:**  
Only SELECT queries are allowed.

---

### Subjective questions
**Question:**  
Who is the greatest NBA player of all time?

**Reason:**  
The question is opinion-based and cannot be answered from box score data.

---

### Non-NBA questions
**Question:**  
What is the weather in Los Angeles tonight?

**Reason:**  
The question is unrelated to NBA statistics.

---


## Tip

Stick to questions about **players, teams, games, seasons, and box-score statistics**.

Check the **Full State**, **Generated SQL**, and **SQL Results** tabs to understand how the agent processed your question.
"""
        )
    with gr.Tab("Chatbot"):
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                chatbot = gr.Chatbot(
                    label="NBA Assistant", height=560
                )
                user_input = gr.Textbox(
                    label="Ask a question",
                    placeholder="Who averaged the most points in March 2024?",
                )
                with gr.Row():
                    submit_btn = gr.Button("Ask", variant="primary")
                    clear_btn = gr.Button("Clear")
            with gr.Column(scale=1):
                with gr.Tab("State"):
                    state_viewer = gr.Code(
                        label="Current Graph State",
                        value="State cleared.",
                        language="json",
                        lines=25,
                    )
                with gr.Tab("SQL"):
                    sql_viewer = gr.Code(
                        label="Generated SQL Query",
                        value="",
                        language="sql",
                        lines=12,
                    )
                with gr.Tab("Results"):
                    results_viewer = gr.Dataframe(
                        label="SQL Query Results",
                        value=pd.DataFrame(),
                        interactive=False,
                        wrap=True,
                    )

    submit_btn.click(
        fn=run_graph,
        inputs=[user_input, chatbot],
        outputs=[
            user_input,
            chatbot,
            state_viewer,
            sql_viewer,
            results_viewer,
        ],
    )

    user_input.submit(
        fn=run_graph,
        inputs=[user_input, chatbot],
        outputs=[
            user_input,
            chatbot,
            state_viewer,
            sql_viewer,
            results_viewer,
        ],
    )

    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[
            chatbot,
            state_viewer,
            sql_viewer,
            results_viewer,
        ],
    )


if __name__ == "__main__":
    demo.launch()