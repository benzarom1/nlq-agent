## Introduction

`nlq-agent` is a modular, LLM-powered analytics agent that lets users query NBA player box score and synthetic game attendance data with natural language. Users can ask basketball questions in plain English, and the agent generates, validates, and executes SQL on a local DuckDB database to retrieve and summarize player statistics, team information, game attendance, and combined player-attendance analysis.

The application uses a graph-based agent architecture for interpretability, SQL safety, and robust error handling. It exposes an intuitive chatbot UI for end users and a full execution state viewer for developers.

---

## Startup Guide

### 1. Prerequisites

Before running the application, ensure you have:

- Python 3.12 or higher
- OpenAI API key configured in `.env`
- DuckDB database initialized locally

Verify your Python version:

```bash
python3 --version
```

Expected:

```text
Python 3.12+
```

If your Python version is below 3.12, install a newer version before continuing.

---

### 2. Create Virtual Environment

Create a virtual environment using Python 3.12 or higher:

```bash
python3.12 -m venv .venv
```

Activate the environment:

Mac/Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Verify the virtual environment is using Python 3.12+:

```bash
python --version
```

Expected:

```text
Python 3.12+
```

---

### 3. Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### 4. Ensure .env file is initialized:

- In directory: nlq-agent create .env file.
- Initialize .env file with OPENAI_API_KEY
- Example is given in .env.template
```
OPENAI_API_KEY=<API-KEY>
```


### 5. Launch Application

Run:

```bash
python app.py
```

Open:

```text
http://localhost:7860/
```

## Dataset Choice

This project uses an NBA player box score dataset covering the 2010-2023 seasons, along with a synthetic attendance dataset generated for each game.

The data is stored locally in DuckDB for fast analytical querying and simple setup.

### Dataset Tables

The database currently uses two main tables:

```text
player_game_stats
game_attendance
```

These tables are intentionally kept separate.

The reason for not merging the player statistics and attendance data into one table is to demonstrate multi-table SQL query generation. This allows the SQL agent to reason about when joins are necessary and generate queries that combine player-level and game-level data correctly.

---

## Player Game Stats Table
=======
### 3. Add .env file:

```
OPENAI_API_KEY= <KEY HERE>
```

### 4. Launch the Application
```
python app.py
```

The `player_game_stats` table stores player box score data at the player-game level.

Each row represents one player's performance in one NBA game.

Example fields include:

```text
season_year,
normalized_season_year,
game_date,
normalized_game_date,
player_stats_gameId,
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
plusMinusPoints
```

---

## Game Attendance Table

The `game_attendance` table stores synthetic game-level attendance data.

Each row represents one NBA game.

Example fields include:

```text
attendance_gameId,
attendance,
homeTeam,
awayTeam,
gameDate,
normalizedGameDate,
normalizedGameDatetime,
teamTricode,
homeCity,
awayCity,
homeTeamId,
awayTeamId
```

The join relationship between the tables is:

```sql
player_game_stats.player_stats_gameId = game_attendance.attendance_gameId
```

---

## Synthetic Attendance Data

The attendance data used in this project is synthetic. It was generated to simulate realistic NBA attendance numbers based on team and game information.

The synthetic attendance table includes:

- Game ID
- Attendance number
- Home team
- Away team
- Game date
- Home city
- Away city
- Team identifiers

Synthetic attendance was added so the system could support business-style questions such as:

```text
Which teams had the highest average attendance?
```

```text
What games had the largest crowds?
```

```text
Did players score more in higher-attendance games?
```

```text
What was the average attendance for games Stephen Curry played in?
```

Because attendance is game-level data and player statistics are player-game-level data, the system must generate joins when a question requires both datasets.

---

## Reason for Dataset Selection

I chose NBA player box score data because it is an expansive sports dataset with rich statistical fields. It allows the agent to answer questions about player performance, team trends, scoring, efficiency, three-point shooting, assists, rebounds, home/away performance, attendance patterns, and changes in play style over time.

Because the dataset spans 2010-2023, it can support analysis across a meaningful multi-year window.

The synthetic attendance layer expands the project from pure player performance analytics into early sports business analytics. It allows the agent to answer questions that combine basketball performance with game-level demand indicators.

Examples include:

```text
Which players scored the most points in the highest-attendance games?
```

```text
Which home teams had the highest average attendance?
```

```text
How did attendance vary by season?
```



---

## Future Data Extensions

The current attendance data is synthetic. In a production version, this would be replaced or supplemented with live or regularly refreshed attendance data from official or internal data sources.

Future attendance improvements would include:

- Live attendance data ingestion
- Automated attendance refresh jobs
- Official arena attendance records
- Ticket sales data
- Paid attendance vs scanned attendance
- Sell-through percentage
- Arena capacity data
- Promotional event metadata

Additional business datasets could include:

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


---

## SQL Agent

The SQL agent converts a valid natural language analytics question into a DuckDB-compatible `SELECT` query.

It receives the current database schema as context and is instructed to:

- Generate only `SELECT` statements
- Use only available tables and columns
- Prefer clear aliases
- Limit result sizes unless the user asks otherwise
- Join tables only when needed
- Avoid double-counting game-level attendance data

The SQL agent understands that the database contains two separate analytical tables:

```text
player_game_stats
game_attendance
```

For player-only questions, it queries `player_game_stats`.

For attendance-only questions, it queries `game_attendance`.

For questions involving both player performance and attendance, it joins the tables using:

```sql
player_game_stats.player_stats_gameId = game_attendance.attendance_gameId
```

This design intentionally demonstrates multi-table natural language to SQL generation.

---

## High-Level Architecture

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
│       └── Prompt templates for intent, SQL, and insight agents
│
├── data/
│   └── local DuckDB database
```

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

I wanted to demonstrate a slightly more complex agent workflow while still keeping the function and focus of the application concise.

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

---

## Production Data Expansion

The current implementation includes synthetic attendance data to demonstrate how the agent handles game-level business metrics alongside player-level basketball statistics.

A production system would replace synthetic attendance with live or regularly refreshed attendance data.

Potential production data additions include:

- Official attendance feeds
- Ticketing system data
- Ticket scans
- Arena capacity data
- Revenue data
- Concession sales
- Merchandise sales
- Promotional event calendars
- Opponent popularity indicators
- Player popularity metrics

This would shift the system from player performance analytics toward broader sports business intelligence.

Example future questions:

```text
Which players drive the largest attendance lift?
```

```text
Which games generate the highest combined revenue from tickets, concessions, and merchandise?
```

```text
Do nationally televised games produce higher attendance or merchandise sales?
```

```text
How does attendance change after a major trade or player signing?
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



## Ai Tool Usage

- GitHub Copilot: OpenAi Gpt-4.1, Gpt-5.4
=======
