
# nlq-agent

**Natural Language Query Agent for NBA Player Box Score Analytics**

---

## Introduction

`nlq-agent` is a modular, LLM-powered analytics agent that lets users query over a decade of NBA player box score data with natural language. You can ask basketball questions in plain English, and the agent generates, validates, and executes SQL on your local DuckDB to retrieve and summarize player stats and team information. The web app leverages a graph-based agent architecture for interpretability and robust error handling, exposing an intuitive chatbot UI for end users and full execution state for developers.

---

## Table of Contents

- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [Startup Guide](#startup-guide)
- [Dataset Choice](#dataset-choice)
- [Foundational Model Choice](#foundational-model-choice)
- [Code Quality and Architecture](#code-quality-and-architecture)
  - [Architecture Layout](#high-level-architecture)
  - [Directory Responsibilities](#directory-responsibilities)
  - [Agent Responsibilities](#agent-responsibilities)
  - [Node Responsibilities](#node-responsibilities)
  - [Graph Architecture](#graph-architecture)
  - [NLQState](#nlqstate)
- [Future Next Steps](#future-next-steps)

---

## Startup Guide

### 1. Prerequisites

- Python 3.9+
- OpenAI API key (in `.env`)
- game_data_enriched.csv (in `data/`)
- A DuckDB database file already available (no need to initialize)

### 2. Installation

Clone the repository and install Python dependencies:

```bash
git clone <repo_url>
cd nlq-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Add .env file:

```
OPENAI_API_KEY= <KEY HERE>
```

### 4. Launch the Application
```
python app.py
```

Visit the Gradio web UI at:
http://localhost:7860/
## Dataset Choice

This project uses an NBA player box score dataset covering the 2010-2024 seasons. The dataset is stored locally in DuckDB for fast analytical querying and simple setup.

### Dataset Schema

```text
season_year,
normalized_season_year,
normalized_game_date
game_date,
gameId,
matchup,
teamId,
teamCity,
teamName,
teamTricode,
teamSlug,
personId,
personName,
position,
comment,
jerseyNum,
minutes,
fieldGoalsMade,
fieldGoalsAttempted,
fieldGoalsPercentage,
threePointersMade,
threePointersAttempted,
threePointersPercentage,
freeThrowsMade,
freeThrowsAttempted,
freeThrowsPercentage,
reboundsOffensive,
reboundsDefensive,
reboundsTotal,
assists,
steals,
blocks,
turnovers,
foulsPersonal,
points,
plusMinusPoints,
matchup_team_tricode,
opponent_team_tricode,
team_side_from_matchup,
rowTeamIdFromTricode,
opponentTeamId,
homeTeamId,
awayTeamId
```

### Storage Choice

The dataset is loaded into a local DuckDB database.

DuckDB was chosen because it is lightweight, fast for analytical workloads, easy to run locally, and does not require database server infrastructure. This makes it a good fit for a focused natural language analytics prototype.

### Reason for Dataset Selection

I chose NBA player box score data because it is an expansive sports dataset with rich statistical fields. It allows the agent to answer questions about player performance, team trends, scoring, efficiency, three-point shooting, assists, rebounds, home/away performance, and changes in play style over time.

Because the dataset spans 2011-2024, it can support analysis across a meaningful 14-year window. This makes it possible to explore larger basketball trends, such as:

- Growth in three-point volume
- Increases in high-scoring games
- Changes in shooting efficiency
- More playmaking responsibility from centers and forwards
- Differences between home and away performance
- Player and team trends across multiple seasons

The dataset also covers the full period of the Nets' move to Barclays Center, making it relevant for team-specific business analysis if future arena, attendance, and ticketing datasets are added.

### Future Data Extensions

The next step would be to append richer business datasets, including:

- Attendance data
- Jersey sales
- Ticket sales
- Concession sales
- Promotional event data
- Internal arena sales tools
- Team popularity and player popularity indicators

These additions would enable questions such as:



```text
Which players drive the largest attendance lift at Barclays Center, regardless of their current team?
```

```text
Which promotional events drive the highest ticket sales?
```

```text
Which player appearances correlate with higher jersey sales?
```

```text
Do star players increase concession sales when they play at Barclays Center?
```

```text
Which opposing teams or players create the largest revenue impact over time?
```

The current dataset provides the player-performance foundation needed for this future business analytics layer.

---

## Foundational Model Choice

This project uses OpenAI chat models as the foundational model provider.

### Reason for Choosing OpenAI

OpenAI was selected because it provides a reliable inference endpoint, strong structured-output support, and high-quality reasoning for natural language to SQL workflows. The project benefits from consistent API behavior, mature LangChain integration, and the ability to choose different models for different levels of task complexity.


## Code Quality and Architecture

The project is organized around a graph-based agent architecture. Each major responsibility is separated into a dedicated agent or node, making the system easier to understand, debug, and extend.

### High-Level Architecture

```text
nlq-agent/
│
├── app.py
│   └── Gradio interface with chatbot and state viewer
│
├── src/
│   ├── graph.py
│   │   └── LangGraph workflow definition and routing
│   │
│   ├── state.py
│   │   └── Shared NLQState structure
│   │
│   ├── llm.py
│   │   └── OpenAI model configuration
│   │
│   ├── database.py
│   │   └── DuckDB connection and schema/query helpers
│   │
│   ├── agents/
│   │   ├── intent_agent.py
│   │   ├── sql_agent.py
│   │   └── insight_agent.py
│   │
│   ├── nodes/
│   │   ├── sql_validate_node.py
│   │   ├── sql_execute_node.py
│   │   ├── non_database_response_node.py
│   │   └── error_node.py
│   │
│   └── prompts/
│       └── Prompt templates for agents
│
├── scripts/
│   └── Data loading and preprocessing scripts
│
├── data/
│   └── CSV files and local DuckDB database
│
└── tests/
    └── Agent and workflow tests
```

---

## Directory Responsibilities

### `agents/`

The `agents/` directory contains LLM-powered components. These are responsible for reasoning tasks that benefit from language understanding.

Agents include:

- Intent classification
- SQL generation
- Insight summarization

Each agent accepts the shared `NLQState`, performs one responsibility, and returns state updates.

### `nodes/`

The `nodes/` directory contains deterministic workflow steps. These are not primarily reasoning tasks and should be predictable.

Nodes include:

- SQL validation
- SQL execution
- Error handling
- Non-database response handling

These nodes are separated from agents so that safety and execution logic remain explicit and testable.

### `prompts/`

The `prompts/` directory stores reusable prompt templates. Keeping prompts outside agent implementation files improves readability and makes prompt iteration easier.

This also makes it easier to add prompt versioning, few-shot examples, and evaluation-specific prompt variants in the future.

---

## Agent Responsibilities

### Intent Agent

The intent agent determines whether a user message should be answered through the database or handled another way.

It classifies the request into one of the supported intent categories:

```text
database_query
general_conversation
unsupported_query
ambiguous_query
unsafe_query
```

This agent exists so that unsafe, irrelevant, or unclear requests do not proceed to SQL generation.

The intent agent uses a lower-cost model because classification is constrained and structured.

**LLM configuration:**  
- Uses a lower-cost OpenAI model (`gpt-4.1-mini`)
- Temperature: `0` (deterministic output)
- This task is strictly classification, with a limited structured output space. It does not require the depth or reasoning power of a larger model, so using a lightweight/cheaper LLM reduces cost and latency without sacrificing accuracy.


### SQL Agent

The SQL agent converts a valid natural language analytics question into a DuckDB-compatible `SELECT` query.

It receives the current database schema as context and is instructed to:

- Generate only `SELECT` statements
- Use only available tables and columns
- Prefer clear aliases
- Limit result sizes unless the user asks otherwise
- Avoid explanation text inside the SQL field

This agent uses a stronger model because SQL generation is the highest-risk reasoning step in the workflow.

**LLM configuration:**  
- Uses a higher-accuracy OpenAI model (`gpt-4.1`)
- Temperature: `0` (deterministic for correctness)
- Injects full schema for context
- NLQ-to-SQL translation is the system's most complex and error-sensitive step. The agent must correctly map user intent to database fields, handle aggregation, filtering, and ordering, and produce safe queries. Using a more capable model with zero temperature provides the best chance of correctness and lowers the risk of invalid/misdirected queries, which could lead to failure or the wrong analysis.




### Insight Agent

The insight agent converts raw SQL results into a concise answer for the user.

It receives:

- Original user question
- Generated SQL
- Query results
- Row count

Its prompt instructs it to answer only from the provided results and avoid inventing unsupported facts.

This agent exists to separate analytical execution from user-facing communication.

**LLM configuration:**  
- Uses the high-accuracy model (`gpt-4.1`)
- Temperature: `0.3` (helps with helpful, non-repetitive language for user-facing explanations)
- Summarizing query results into a natural, readable, and relevant answer may require some creativity of phrasing—e.g., handling empty results, ranking, or explaining outliers. A slightly higher temperature encourages the LLM to produce diverse and explanatory language, while still grounding in the facts from the SQL output.

---


### Configuration Strategy

- **Intent agent:** Use small, cheap LLMs for structured classification.
- **SQL agent:** Use strong models for precise SQL translation from NLQ (zero temperature).
- **Insight agent:** Use strong models (possibly with slightly raised temperature) for creative, readable final answers, accepting more LLM "voice" as it only summarizes SQL results.

**Tradeoff:**  
This split improves cost-efficiency (cheaper models for easy tasks, powerful models for hard tasks) while ensuring SQL correctness and user-friendly answers where they matter most.
## Node Responsibilities

### SQL Validation Node

Validates generated SQL before execution.

It blocks:

- Non-`SELECT` statements
- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- `TRUNCATE`
- Multiple SQL statements

This node provides a safety layer between LLM-generated SQL and the database.

### SQL Execution Node

Executes validated SQL against DuckDB and stores the results in `NLQState`.

It catches execution failures and returns an `execution_error` instead of crashing the workflow.

### Non-Database Response Node

Handles supported non-SQL paths such as greetings, help requests, unsupported questions, ambiguous requests, and unsafe requests.

This keeps the agent from trying to force every user message into SQL.

### Error Node

Produces a clear final response when validation or execution fails.

This node exists so that failures are communicated clearly instead of surfacing raw exceptions to the user.

---

## Graph Architecture

The workflow is defined in graph.py using LangGraph.

### ASCII Diagram

```text
                ┌──────────────┐
                │ Intent Agent │
                └──────┬───────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
 database_query              non-database / unsafe /
        │                    unsupported / ambiguous
        │                             │
        v                             v
┌────────────────┐          ┌──────────────────────┐
│   SQL Agent    │          │ Non-Database Response │
└───────┬────────┘          └──────────┬───────────┘
        │                              │
        v                              v
┌────────────────┐                    END
│ SQL Validator  │
└───────┬────────┘
        │
   valid│invalid
        │
        v
┌────────────────┐
│ SQL Executor   │
└───────┬────────┘
        │
 success│failure
        │
        v
┌────────────────┐
│ Insight Agent  │
└───────┬────────┘
        │
        v
       END

Invalid SQL or execution failure routes to:

┌────────────────┐
│   Error Node   │
└───────┬────────┘
        │
        v
       END
```

### Architectural Decisions

The graph separates reasoning, validation, execution, and response generation into distinct steps.

This design was chosen because it improves:

- Debuggability
- Safety
- Observability
- Testability
- Extensibility

The SQL is not executed immediately after generation. It first passes through a validation node, which reduces the risk of unsafe or malformed queries.

The graph also routes non-database requests away from SQL generation, which prevents unnecessary LLM calls and improves user experience.

### Tradeoffs

This graph is more verbose than a single-chain implementation, but the added structure makes the workflow easier to reason about.

Potential tradeoffs include:

- More files and functions to maintain
- Slightly higher latency because each step is separate
- More state management complexity
- Requires careful consistency between agent outputs and graph routing keys

I wanted to demonstrate a slightly more complex agent workflow while still keeping the function and focus of the application concise. This is why I went with a multi agent orchestration.

---

## NLQState

The graph passes a shared `NLQState` between nodes.

### State Fields

```text
question
messages
intent
intent_reason
schema_context
generated_sql
sql_reasoning
is_valid_sql
validation_error
retry_count
query_results
row_count
execution_error
final_answer
```

### Why This State Was Chosen

`NLQState` was designed to capture the complete lifecycle of a natural language analytics request.

It includes:

- The original user input
- Conversation messages
- Intent classification
- SQL generation output
- Validation status
- Execution results
- Error information
- Final answer

This structure makes the workflow transparent and easy to debug. Each node only needs to read the fields relevant to its responsibility and return updates for the fields it owns.

The state also supports the Gradio state viewer, where developers can inspect the full graph execution in real time.

---

## Future Next Steps

The current implementation is intentionally focused to demonstrate natural language into sql back into natural language, while having error handling/validation steps.

To make this a production application, the following areas would be expanded.

---

## Production Data Expansion

The current dataset focuses on NBA player box scores. A production analytics system should incorporate additional internal and external business datasets.

Potential additions include:

- Attendance data
- Ticket sales
- Jersey sales
- Concession sales
- Promotional events
- Arena event calendars
- Opponent popularity data
- Player popularity metrics
- Injury reports and availability
- Broadcast and media exposure
- Internal CRM or sales tooling

These additions would allow the system to answer business questions such as:

```text
Which players perform the best during the biggest games of the year?
```

```text
Which players drive ticket sales regardless of the team they currently play for?
```

```text
Which promotional events drive the highest ticket sales?
```

```text
How do bobblehead nights compare to discounted ticket promotions?
```


```text
Which games generate the highest combined revenue from tickets, concessions, and merchandise?
```

```text
Do nationally televised games produce higher attendance or merchandise sales?
```

```text
How does the attendance change in games after a major trade or player signing?
```


This would shift the system from player performance analytics toward broader sports business intelligence.

---

## Production Architecture Improvements

### BaseAgent Abstraction

A production version should introduce a `BaseAgent` class that all agents extend.

This would provide a shared framework for:

- LLM configuration
- Prompt loading
- Structured output parsing
- Retry behavior
- Error handling
- Logging
- Token usage tracking
- Latency tracking
- Agent-level validation

Example structure:

```text
BaseAgent
├── IntentAgent
├── SQLAgent
├── InsightAgent
├── ClarificationAgent
├── DataCatalogAgent
└── BusinessMetricsAgent
```

This would make it easier to add new agents consistently and reduce duplicated implementation patterns.

### Stronger Agent Validation

Each agent should define the exact structured fields it is responsible for producing.

For example:

```text
IntentAgent
- intent
- intent_reason
- confidence

SQLAgent
- generated_sql
- sql_reasoning
- referenced_tables
- referenced_columns

InsightAgent
- final_answer
- caveats
- supporting_metrics
```

The workflow should distinguish between required and optional fields. If a required field is missing, the graph should fail gracefully. If an optional field is missing, the graph may continue with a warning.

This makes the system more reliable and easier to debug.

### Improved Error Recovery

A production system should support partial failure handling.

Examples:

- If SQL generation fails, ask a clarifying question.
- If validation fails, retry SQL generation with the validation error.
- If execution fails due to a missing column, regenerate SQL using the schema.
- If query results are empty, produce a helpful explanation instead of a generic failure.
- If the LLM output fails parsing, retry with a stricter format instruction.

### Clarification Agent

A clarification agent could be added for ambiguous questions.

For example:

```text
User: Who was the best player last season?
```

The system could ask:

```text
Do you mean highest points, best plus-minus, most efficient shooter, or another metric?
```

This would improve NLQ accuracy without requiring multi-turn memory.

---

## Testing Infrastructure

A production-ready version should include a larger pytest suite organized around agents, nodes, graph routing, and SQL behavior.

Recommended test structure:

```text
tests/
├── agents/
│   ├── test_intent_agent.py
│   ├── test_sql_agent.py
│   └── test_insight_agent.py
│
├── nodes/
│   ├── test_sql_validate_node.py
│   ├── test_sql_execute_node.py
│   ├── test_error_node.py
│   └── test_non_database_response_node.py
│
├── graph/
│   ├── test_graph_routing.py
│   └── test_end_to_end_queries.py
│
├── data/
│   └── test_schema_contract.py
│
└── evals/
    ├── golden_questions.yaml
    └── test_golden_sql_outputs.py
```

Recommended test categories:

- Intent classification tests
- Unsafe query blocking tests
- SQL validation tests
- SQL execution tests
- End-to-end graph tests
- Empty result handling tests
- Ambiguous question tests
- Schema compatibility tests
- Golden answer regression tests

### Golden Evaluation Set

A golden evaluation set should include representative natural language questions, expected SQL patterns, and expected answer properties.

Example:

```yaml
- question: "Who scored the most points in a game in 2023?"
  expected_tables:
    - player_game_stats
  expected_columns:
    - personName
    - points
    - game_date
  expected_order_by:
    - points DESC
  expected_limit: true
```

This would make it easier to evaluate model changes and prevent prompt regressions.

---

## Foundational Model Evaluation

A production version should include a model evaluation strategy.

### Amazon Bedrock Integration

Amazon Bedrock could be incorporated to manage and compare multiple model deployments. This would allow the system to evaluate different models for each agent role while tracking cost and performance.

### A/B Testing

Different models should be tested per agent:

```text
Intent Agent:
- lower-cost classification models
- compare accuracy and latency

SQL Agent:
- stronger reasoning models
- compare SQL correctness and execution success

Insight Agent:
- summarization-focused models
- compare clarity, factuality, and conciseness
```

### Metrics to Track

Production model monitoring should include:

- Token usage
- Cost per request
- Latency per agent
- SQL execution success rate
- SQL validation failure rate
- Empty result rate
- LLM parsing failure rate
- User-facing error rate
- Intent classification accuracy
- Golden test pass rate

### Cost Optimization

Golden answer responses should be used to compare cheaper models against stronger models. If a lower-cost model performs well for a specific agent, it can be promoted for that role.

This would allow the application to reduce cost without sacrificing quality.

---

## Production Observability

Explicit logging should be added throughout the system.

Recommended logs include:

- User question
- Classified intent
- Generated SQL
- SQL validation result
- SQL execution time
- Row count
- LLM model used per agent
- Token usage
- Final answer
- Errors and retries

Logs should be structured so they can be searched and analyzed in production systems.

A production deployment should also include:

- Request tracing
- Agent-level timing
- User feedback collection
- Alerting on failure rates
- Dashboards for model cost and latency

---

## Additional Production Requirements
- Mult-Turn Conversation Memoery
- Authentication and authorization
- Secrets management
- Automated database refresh process
- Data quality checks
- Prompt versioning
- Model versioning
- Monitoring and alerting
- User feedback loop
