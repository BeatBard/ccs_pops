# CCS POPS - Sales Coaching Assistant Implementation Plan

**Project:** Sales Insights and Coaching Assistant POC
**Focus DSR:** Nalin Perera
**Target Platform:** WhatsApp via Twilio
**Architecture:** LangGraph + LangChain + Tool Calling
**Version:** 2.0
**Date:** 2026-01-11

---

## 1. Architecture Overview

### High-Level Architecture with LangGraph

```
┌─────────────────┐
│   Nalin Perera  │
│  (WhatsApp User)│
└────────┬────────┘
         │
         │ WhatsApp Messages
         ▼
┌─────────────────────────────────┐
│      Twilio WhatsApp API        │
│  (Message Gateway & Routing)    │
└────────────┬────────────────────┘
             │
             │ HTTP POST Webhook
             ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend                          │
│  ┌────────────────────────────────────────────────┐  │
│  │           Webhook Handler                      │  │
│  │  - Receive Twilio POST                         │  │
│  │  - Extract message & user                      │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│  ┌────────────────▼───────────────────────────────┐  │
│  │         LangGraph State Machine                │  │
│  │  ┌──────────────────────────────────────────┐ │  │
│  │  │  State: IDLE → GREETING → AT_OUTLET →   │ │  │
│  │  │         COACHING → END_DAY → IDLE       │ │  │
│  │  └──────────────────────────────────────────┘ │  │
│  │                                                │  │
│  │  Nodes (Processing Steps):                    │  │
│  │  ┌─────────────────────────────────────────┐ │  │
│  │  │ • morning_checkin_node                  │ │  │
│  │  │ • outlet_arrival_node                   │ │  │
│  │  │ • coaching_request_node                 │ │  │
│  │  │ • visit_tracking_node                   │ │  │
│  │  │ • end_of_day_node                       │ │  │
│  │  │ • error_handler_node                    │ │  │
│  │  └─────────────────────────────────────────┘ │  │
│  │                                                │  │
│  │  Edges (State Transitions):                   │  │
│  │  • Conditional routing based on user input    │  │
│  │  • Intent classification → Node selection     │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│  ┌────────────────▼───────────────────────────────┐  │
│  │         LangChain Agent Layer                  │  │
│  │  ┌──────────────────────────────────────────┐ │  │
│  │  │  Agent Executor                          │ │  │
│  │  │  - Receives user message                 │ │  │
│  │  │  - Determines which tools to call        │ │  │
│  │  │  - Executes tools                        │ │  │
│  │  │  - Formats response                      │ │  │
│  │  └──────────────────────────────────────────┘ │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│  ┌────────────────▼───────────────────────────────┐  │
│  │         LangChain Tools (Tool Calling)         │  │
│  │  ┌──────────────────────────────────────────┐ │  │
│  │  │ • get_daily_plan_tool                    │ │  │
│  │  │ • get_outlet_info_tool                   │ │  │
│  │  │ • get_lipb_tracking_tool                 │ │  │
│  │  │ • get_top_skus_tool                      │ │  │
│  │  │ • calculate_metrics_tool                 │ │  │
│  │  │ • get_coaching_tips_tool                 │ │  │
│  │  │ • mark_visit_tool                        │ │  │
│  │  │ • generate_ai_coaching_tool (Gemini)     │ │  │
│  │  └──────────────────────────────────────────┘ │  │
│  └────────────────┬───────────────────────────────┘  │
└───────────────────┼────────────────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌─────────────┐
│   Data   │  │  Gemini  │  │   Memory    │
│   Layer  │  │    AI    │  │   Store     │
│  (CSV)   │  │ (via tool)│ │(Conversation)│
└──────────┘  └──────────┘  └─────────────┘
```

### Component Stack

**Frontend:**
- WhatsApp (Mobile App - User Interface)
- Interactive buttons and quick replies

**Communication Layer:**
- Twilio WhatsApp Business API
- TwiML (Twilio Markup Language) for responses

**Backend Application:**
- FastAPI (Python web framework)
- Async/await for concurrent handling
- Pydantic for data validation

**Agent Framework (NEW):**
- **LangGraph** - State machine and conversation flow orchestration
- **LangChain** - Agent framework and tool calling
- **LangChain Tools** - Custom tools for data access and operations
- **Memory** - Conversation history and context management

**AI/ML Layer:**
- Google Gemini 3 Flash Preview (via LangChain tool)
- Vertex AI for model access
- Custom prompts for coaching
- Tool calling for structured outputs

**Data Layer:**
- CSV files (POC phase)
- Pandas for data manipulation
- In-memory caching for performance
- LangGraph checkpointer for state persistence

**Infrastructure:**
- ngrok for local tunnel (development)
- Environment variable management (.env)
- Logging and error tracking

---

## 2. Data Flow with LangGraph

### 2.1 Morning Check-in Flow

```
User sends: "Good morning" or clicks button
    │
    ▼
Twilio receives WhatsApp message
    │
    ▼
POST to /webhook with Form data:
    - From: whatsapp:+94772057878
    - Body: "Good morning"
    │
    ▼
FastAPI webhook handler:
    1. Extract sender phone number
    2. Load or create LangGraph thread
    3. Pass message to LangGraph
    │
    ▼
LangGraph State Machine:
    1. Current state: IDLE
    2. User input: "Good morning"
    3. Intent classification → MORNING_GREETING
    4. Transition: IDLE → GREETING
    5. Route to: morning_checkin_node
    │
    ▼
morning_checkin_node executes:
    1. Update state to GREETING
    2. Invoke LangChain Agent
    │
    ▼
LangChain Agent decides:
    "I need to get today's plan for Nalin"
    → Calls get_daily_plan_tool(dsr="Nalin Perera", date="2026-01-11")
    │
    ▼
get_daily_plan_tool:
    1. Query daily_plan.csv
    2. Return: 3 outlets, 2 priority, breakdown
    │
    ▼
LangChain Agent receives tool result:
    "I have the data, now I'll generate greeting"
    → Uses Gemini to format Sinhala message
    → Calls generate_ai_coaching_tool with context
    │
    ▼
generate_ai_coaching_tool:
    1. Build prompt with daily plan data
    2. Call Gemini API
    3. Return formatted Sinhala greeting
    │
    ▼
LangChain Agent formats final response:
    - Message: "සුභ උදෑසනක්..."
    - Buttons: [OW, NA, ADA LEAVE]
    │
    ▼
LangGraph updates state:
    - Current state: AWAITING_RESPONSE
    - Context: {plan_data, greeting_sent}
    - Save checkpoint
    │
    ▼
FastAPI returns TwiML to Twilio
    │
    ▼
Twilio sends to WhatsApp
    │
    ▼
User receives message with buttons
    │
    ▼
User clicks "OW" button
    │
    ▼
LangGraph receives button payload:
    - Load checkpoint
    - Current state: AWAITING_RESPONSE
    - Button: "OW"
    - Transition: GREETING → ACTIVE
    - Display full day plan
```

### 2.2 Visit Coaching Flow with Tool Calling

```
User sends: "At SD0002"
    │
    ▼
LangGraph State Machine:
    - Current state: ACTIVE
    - Intent: AT_OUTLET
    - Route to: outlet_arrival_node
    │
    ▼
outlet_arrival_node executes:
    1. Parse outlet_id from message
    2. Update state: AT_OUTLET
    3. Store context: {current_outlet: "SD0002"}
    4. Invoke LangChain Agent
    │
    ▼
LangChain Agent reasoning:
    "User is at outlet SD0002. I need to:
    1. Get outlet information
    2. Check LIPB performance
    3. Get top SKUs
    4. Generate coaching tips"
    │
    ▼
Agent calls multiple tools in sequence:

Tool Call 1: get_outlet_info_tool("SD0002")
    → Returns: {
        name: "City Bites Cafe",
        type: "Eatery",
        poi: ["Schools", "Hospital"],
        visibility_issues: True
    }

Tool Call 2: get_lipb_tracking_tool("Nalin Perera", "SD0002")
    → Returns: {
        avg_lipb: 1.3,
        target: 3.0,
        last_lipb: 1,
        trend: "Declining"
    }

Tool Call 3: get_top_skus_tool("SD0002", top_n=5)
    → Returns: [
        "Coca-Cola 500ml (25 units)",
        "Kinley Water 500ml (22 units)",
        "Sprite 500ml (18 units - LOW STOCK)",
        "Fanta Orange 500ml (15 units - OUT OF STOCK)",
        "Minute Maid Orange 500ml (12 units)"
    ]

Tool Call 4: get_coaching_tips_tool(
    category="Upselling",
    situation="Low LIPB",
    dsr_strength="Customer Handling"
)
    → Returns: [
        "ඔබ අවසන් වතාවේ SKU 1ක් විතරයි..."
    ]

Tool Call 5: generate_ai_coaching_tool({
    dsr_profile: {
        name: "Nalin Perera",
        strengths: ["Customer Handling"],
        dev_areas: ["Route Planning"]
    },
    outlet_context: {
        type: "Eatery",
        lipb: 1.3,
        target: 3.0,
        issues: ["visibility"]
    },
    top_skus: [...],
    rule_tips: [...]
})
    → Gemini generates personalized coaching
    │
    ▼
LangChain Agent combines all tool results:
    - Formats comprehensive coaching message
    - Includes LIPB data
    - Lists top SKUs
    - Adds AI coaching + rule-based tips
    - Suggests specific actions
    │
    ▼
LangGraph updates state:
    - State: COACHING_PROVIDED
    - Context: {outlet: "SD0002", coaching_sent: True}
    - Save checkpoint
    │
    ▼
Response sent to WhatsApp via Twilio
```

### 2.3 End of Day Flow with Parallel Tool Calls

```
System timer triggers at 6:00 PM
OR User sends: "End day"
    │
    ▼
LangGraph routes to: end_of_day_node
    │
    ▼
LangChain Agent planning:
    "I need to calculate daily summary. I can call
    multiple tools in parallel to speed this up."
    │
    ▼
Agent executes parallel tool calls:

Parallel Call Group 1:
├─ get_daily_plan_tool("Nalin Perera", "2026-01-11")
├─ calculate_metrics_tool("Nalin Perera", "2026-01-11")
└─ get_visit_progress_tool("Nalin Perera", "2026-01-11")

    → All execute simultaneously
    │
    ▼
Tool Results:
- Daily Plan: 3 outlets planned
- Metrics: {
    adherence: 100%,
    productive_visits: 3/3,
    target_achievement: 96%
  }
- Visit Progress: {
    SD0001: completed (ahead),
    SD0002: completed (behind),
    SD0003: completed (ahead)
  }
    │
    ▼
Agent synthesizes results:
    "Nalin had an excellent day!"
    → Calls generate_ai_coaching_tool for summary
    │
    ▼
generate_ai_coaching_tool generates:
    - Congratulations message
    - Performance highlights
    - Areas for improvement (SD0002)
    - Motivational closing
    │
    ▼
LangGraph updates state:
    - State: DAY_COMPLETE → IDLE
    - Clear daily context
    - Save checkpoint
    │
    ▼
Response sent to user
```

---

## 3. Implementation Phases

### Phase 1: LangGraph & LangChain Setup (Week 1)
**Goal:** Set up LangGraph state machine and LangChain agent framework

**Tasks:**
1. Install dependencies (langgraph, langchain, langchain-google-vertexai)
2. Design LangGraph state schema
3. Define all conversation states
4. Create state machine nodes
5. Define state transitions (edges)
6. Set up checkpointer for state persistence
7. Configure LangChain agent with Gemini

**Deliverables:**
- LangGraph state machine definition
- Basic nodes for each conversation stage
- State transition logic
- LangChain agent configuration

**Success Criteria:**
- State machine can transition between states
- Checkpointer saves/loads state correctly
- LangChain agent responds to basic prompts

**Code Structure:**
```
src/
├── graph/
│   ├── state.py          # State schema definition
│   ├── nodes.py          # All node implementations
│   ├── edges.py          # Conditional edge logic
│   └── graph.py          # LangGraph compilation
├── agent/
│   ├── agent.py          # LangChain agent setup
│   └── prompts.py        # Agent system prompts
└── tools/
    └── __init__.py       # Tool registry
```

---

### Phase 2: Tool Development (Week 2)
**Goal:** Create all LangChain tools for data access and operations

**Tasks:**
1. Create base tool class with error handling
2. Implement data access tools:
   - get_daily_plan_tool
   - get_outlet_info_tool
   - get_lipb_tracking_tool
   - get_top_skus_tool
   - get_coaching_tips_tool
3. Implement operation tools:
   - mark_visit_tool
   - calculate_metrics_tool
   - get_visit_progress_tool
4. Implement AI tool:
   - generate_ai_coaching_tool
5. Add tool descriptions for agent reasoning
6. Test each tool independently

**Deliverables:**
- 9+ LangChain tools
- Tool descriptions and schemas
- Unit tests for all tools

**Success Criteria:**
- All tools execute successfully
- Tools return properly formatted data
- Agent can call tools correctly
- Tool descriptions are clear

**Tool Structure:**
```python
from langchain.tools import BaseTool

class GetDailyPlanTool(BaseTool):
    name = "get_daily_plan"
    description = """
    Get the daily outlet visit plan for a DSR.
    Input: {"dsr_name": str, "date": str}
    Returns: List of outlets with targets
    """

    def _run(self, dsr_name: str, date: str):
        # Load from CSV
        # Return structured data
        pass
```

---

### Phase 3: Morning Check-in Graph Flow (Week 3)
**Goal:** Implement complete morning check-in using LangGraph

**Tasks:**
1. Implement morning_checkin_node
2. Create intent classification logic
3. Build morning greeting prompt template
4. Configure tool calling sequence
5. Implement button handling
6. Add state transitions for user responses
7. Create Sinhala message formatting
8. Test full morning flow

**Deliverables:**
- Working morning check-in node
- Intent classifier
- Complete conversation flow
- Sinhala templates

**Success Criteria:**
- Agent detects "good morning" intent
- Calls get_daily_plan_tool automatically
- Generates Sinhala greeting
- Buttons work correctly
- State persists between messages

**LangGraph Node Example:**
```python
def morning_checkin_node(state: ConversationState):
    """Handle morning check-in flow"""
    # Get user message
    user_msg = state["messages"][-1]

    # Invoke agent with tools
    response = agent.invoke({
        "messages": state["messages"],
        "tools": [get_daily_plan_tool],
        "dsr_profile": state["dsr_profile"]
    })

    # Update state
    return {
        "messages": response["messages"],
        "current_state": "AWAITING_RESPONSE",
        "context": {"plan_sent": True}
    }
```

---

### Phase 4: Outlet Visit & Coaching Node (Week 4)
**Goal:** Implement visit tracking and AI coaching

**Tasks:**
1. Implement outlet_arrival_node
2. Configure multi-tool calling for outlet context
3. Build coaching generation logic
4. Integrate rule-based + AI coaching
5. Implement LIPB analysis
6. Add SKU recommendation logic
7. Create coaching message templates
8. Test coaching quality

**Deliverables:**
- outlet_arrival_node
- Multi-tool orchestration
- Coaching generation pipeline
- Quality coaching messages

**Success Criteria:**
- Agent automatically calls 4-5 tools
- Coaching is contextual and relevant
- LIPB insights are accurate
- SKU recommendations make sense
- Messages are in Sinhala

**Multi-Tool Calling:**
```python
# Agent automatically determines tool sequence
agent_response = agent.invoke({
    "messages": [
        HumanMessage(content="At SD0002")
    ],
    "tools": [
        get_outlet_info_tool,
        get_lipb_tracking_tool,
        get_top_skus_tool,
        get_coaching_tips_tool,
        generate_ai_coaching_tool
    ]
})
# Agent executes tools in optimal order
```

---

### Phase 5: Visit Tracking & Real-time Updates (Week 5)
**Goal:** Implement real-time visit tracking

**Tasks:**
1. Implement visit_tracking_node
2. Create mark_visit_tool
3. Add progress calculation logic
4. Implement status query handling
5. Add real-time metrics updates
6. Create progress visualization
7. Test tracking accuracy

**Deliverables:**
- Visit tracking system
- Real-time progress updates
- Status query capability

**Success Criteria:**
- Visits are tracked accurately
- Progress updates in real-time
- Can query status anytime
- Metrics are calculated correctly

---

### Phase 6: End of Day Node (Week 6)
**Goal:** Implement end-of-day summary

**Tasks:**
1. Implement end_of_day_node
2. Configure parallel tool calling
3. Create summary generation logic
4. Add achievement recognition
5. Implement improvement suggestions
6. Create tomorrow preview
7. Test summary accuracy

**Deliverables:**
- end_of_day_node
- Parallel tool execution
- Comprehensive summaries

**Success Criteria:**
- Summary is accurate
- All metrics calculated correctly
- Recognizes achievements
- Provides actionable feedback

**Parallel Tool Calling:**
```python
# Agent calls multiple tools in parallel
from langchain.agents import AgentExecutor

response = agent.invoke({
    "messages": [HumanMessage(content="End day")],
    "tools": [
        get_daily_plan_tool,
        calculate_metrics_tool,
        get_visit_progress_tool
    ],
    "parallel": True  # Execute in parallel
})
```

---

### Phase 7: Error Handling & Edge Cases (Week 7)
**Goal:** Robust error handling and edge cases

**Tasks:**
1. Implement error_handler_node
2. Add tool failure handling
3. Create fallback responses
4. Handle unknown intents
5. Add timeout handling
6. Implement retry logic
7. Test error scenarios

**Deliverables:**
- Error handling system
- Fallback mechanisms
- Graceful degradation

**Success Criteria:**
- No crashes on errors
- User always gets a response
- Errors are logged properly
- Fallbacks work correctly

---

### Phase 8: Testing & Optimization (Week 8)
**Goal:** End-to-end testing and optimization

**Tasks:**
1. Test all conversation flows
2. Optimize tool calling sequences
3. Reduce latency
4. Test concurrent users
5. Optimize Gemini API usage
6. Refine Sinhala language
7. Load testing

**Deliverables:**
- Test suite
- Performance optimizations
- Final POC demo

**Success Criteria:**
- All flows work smoothly
- Response time < 3 seconds
- No critical bugs
- Agent reasoning is sound

---

## 4. Component Breakdown

### 4.1 LangGraph State Schema

**Purpose:** Define conversation state structure

**State Schema:**
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class ConversationState(TypedDict):
    # Messages
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # User context
    dsr_name: str
    dsr_phone: str
    dsr_profile: dict

    # Conversation state
    current_state: str  # IDLE, GREETING, AT_OUTLET, etc.
    previous_state: str

    # Session context
    current_outlet: str | None
    outlets_visited_today: list[str]
    daily_plan: dict

    # Flags
    morning_checkin_done: bool
    end_of_day_done: bool

    # Metadata
    conversation_id: str
    created_at: str
    updated_at: str
```

**State Transitions:**
```
IDLE ──(good morning)──> GREETING ──(button:OW)──> ACTIVE
  │                                                    │
  └─────────────(end day)─────────────────────────────┘
                          │
                          ▼
                      DAY_COMPLETE ──> IDLE

ACTIVE ──(at outlet)──> AT_OUTLET ──(coaching)──> COACHING
  │                          │                        │
  └──────────────────────────┴────────────────────────┘
                             │
                   (visit complete)
                             │
                             ▼
                          ACTIVE
```

---

### 4.2 LangGraph Nodes

**Node 1: morning_checkin_node**
- Handles morning greeting
- Calls get_daily_plan_tool
- Generates Sinhala greeting
- Returns buttons

**Node 2: outlet_arrival_node**
- Handles "at outlet" message
- Calls multiple tools (outlet info, LIPB, SKUs)
- Updates visit tracking
- Returns outlet context

**Node 3: coaching_request_node**
- Handles coaching requests
- Calls get_coaching_tips_tool
- Calls generate_ai_coaching_tool
- Returns personalized coaching

**Node 4: visit_tracking_node**
- Handles visit completion
- Calls mark_visit_tool
- Updates progress
- Returns confirmation

**Node 5: end_of_day_node**
- Handles end of day
- Calls parallel tools
- Generates summary
- Returns recap

**Node 6: error_handler_node**
- Handles errors
- Provides fallback responses
- Logs errors

---

### 4.3 LangChain Tools

**Tool Registry:**

1. **get_daily_plan_tool**
   - Input: dsr_name, date
   - Output: List of outlets with targets
   - Data source: daily_plan.csv

2. **get_outlet_info_tool**
   - Input: outlet_id
   - Output: Outlet details (type, POI, etc.)
   - Data source: outlet_details.csv

3. **get_lipb_tracking_tool**
   - Input: dsr_name, outlet_id
   - Output: LIPB metrics and trend
   - Data source: lipb_tracking.csv

4. **get_top_skus_tool**
   - Input: outlet_id, top_n
   - Output: Top selling SKUs
   - Data source: sku_performance_by_outlet.csv

5. **get_coaching_tips_tool**
   - Input: category, situation, dsr_strength
   - Output: Rule-based coaching tips
   - Data source: coaching_tips.csv

6. **calculate_metrics_tool**
   - Input: dsr_name, date
   - Output: Performance metrics
   - Calculation: route adherence, target achievement

7. **mark_visit_tool**
   - Input: dsr_name, outlet_id, sales_value
   - Output: Confirmation
   - Side effect: Update in-memory tracking

8. **get_visit_progress_tool**
   - Input: dsr_name, date
   - Output: Visit progress data
   - Data source: In-memory tracking

9. **generate_ai_coaching_tool**
   - Input: context (DSR profile, outlet, LIPB, SKUs)
   - Output: AI-generated coaching in Sinhala
   - External: Gemini API

---

### 4.4 LangChain Agent Configuration

**Agent Type:** Tool-calling agent with Gemini

**System Prompt:**
```python
SYSTEM_PROMPT = """
You are a sales coaching assistant for beverage DSRs in Sri Lanka.

Your role:
- Help DSRs plan their day
- Provide outlet-specific coaching
- Suggest SKUs to upsell
- Encourage positive behavior
- Track visit progress

Guidelines:
- Always respond in Sinhala
- Be encouraging and positive
- Provide specific, actionable tips
- Use data to support recommendations
- Keep messages concise (< 500 characters)

You have access to tools to:
- Get daily outlet plans
- Retrieve outlet information
- Check LIPB performance
- Find top-selling SKUs
- Get coaching tips
- Track visits
- Calculate metrics

Use tools when needed to provide accurate, contextual coaching.
"""
```

**Agent Configuration:**
```python
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent

# Initialize Gemini model
llm = ChatVertexAI(
    model_name="gemini-3-flash-preview",
    project="amiable-catfish-433412-d9",
    location="global"
)

# Create agent with tools
agent = create_react_agent(
    model=llm,
    tools=all_tools,
    state_schema=ConversationState,
    checkpointer=checkpointer
)
```

---

### 4.5 Message Formatter with LangChain

**Purpose:** Format agent responses for WhatsApp/TwiML

**Responsibilities:**
- Parse agent output
- Extract final answer
- Format for WhatsApp
- Add buttons if needed
- Generate TwiML

**Integration with Agent:**
```python
def format_agent_response(agent_output):
    """Format LangChain agent output for WhatsApp"""
    # Extract final message
    final_message = agent_output["messages"][-1].content

    # Check for button indicators in message
    if "[BUTTONS:" in final_message:
        message, buttons = parse_buttons(final_message)
    else:
        message = final_message
        buttons = []

    # Generate TwiML
    return create_twiml_response(message, buttons)
```

---

## 5. Integration Points

### 5.1 LangGraph Integration

**Setup:**
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# Create graph
graph = StateGraph(ConversationState)

# Add nodes
graph.add_node("morning_checkin", morning_checkin_node)
graph.add_node("outlet_arrival", outlet_arrival_node)
graph.add_node("coaching", coaching_request_node)
graph.add_node("end_of_day", end_of_day_node)

# Add edges
graph.add_conditional_edges(
    "morning_checkin",
    route_after_morning,  # Function to determine next node
    {
        "active": "outlet_arrival",
        "leave": "end_of_day",
        "idle": END
    }
)

# Set entry point
graph.set_entry_point("morning_checkin")

# Compile with checkpointer
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

**Execution:**
```python
# In webhook handler
config = {"configurable": {"thread_id": user_phone}}
result = app.invoke(
    {"messages": [HumanMessage(content=user_message)]},
    config
)
```

---

### 5.2 LangChain Tool Calling Integration

**Tool Creation:**
```python
from langchain.tools import tool

@tool
def get_daily_plan(dsr_name: str, date: str) -> dict:
    """Get the daily outlet visit plan for a DSR.

    Args:
        dsr_name: Name of the DSR (e.g., "Nalin Perera")
        date: Date in YYYY-MM-DD format

    Returns:
        Dictionary with outlet plan details
    """
    # Load from CSV
    plan_df = pd.read_csv("data/daily_plan.csv")
    plan = plan_df[
        (plan_df["dsr_name"] == dsr_name) &
        (plan_df["date"] == date)
    ]

    return {
        "outlets": plan.to_dict("records"),
        "total_count": len(plan),
        "priority_count": len(plan[plan["priority"] == "Yes"])
    }
```

**Tool Usage by Agent:**
- Agent automatically determines when to call tools
- Agent can call multiple tools in sequence or parallel
- Agent synthesizes tool results into response

---

### 5.3 Gemini Integration via LangChain

**LangChain Gemini Setup:**
```python
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(
    model_name="gemini-3-flash-preview",
    project="amiable-catfish-433412-d9",
    location="global",
    temperature=0.7,
    max_output_tokens=500
)
```

**Gemini as a Tool:**
```python
@tool
def generate_ai_coaching(context: dict) -> str:
    """Generate AI coaching using Gemini.

    Args:
        context: Dictionary with DSR profile, outlet info, LIPB data, etc.

    Returns:
        Coaching message in Sinhala
    """
    prompt = f"""
    Generate coaching tips in Sinhala for:

    DSR: {context['dsr_name']}
    Strengths: {context['strengths']}

    Outlet: {context['outlet_type']}
    LIPB: {context['lipb']} (Target: {context['target_lipb']})
    Issues: {context['issues']}

    Provide 3-5 short, actionable tips.
    """

    response = llm.invoke(prompt)
    return response.content
```

---

### 5.4 State Persistence with Checkpointers

**Memory Checkpointer (POC):**
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
```

**Redis Checkpointer (Production):**
```python
from langgraph.checkpoint.redis import RedisSaver
import redis

redis_client = redis.Redis(host='localhost', port=6379)
checkpointer = RedisSaver(redis_client)
```

**Benefits:**
- Conversation history persists
- Can resume conversations
- Multi-turn context maintained
- State survives restarts (with Redis)

---

### 5.5 Twilio Integration (Unchanged)

**Webhook Handler with LangGraph:**
```python
@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(), From: str = Form()):
    """Handle incoming WhatsApp messages"""

    # Configure thread
    config = {"configurable": {"thread_id": From}}

    # Invoke graph
    result = graph_app.invoke(
        {"messages": [HumanMessage(content=Body)]},
        config
    )

    # Extract response
    agent_response = result["messages"][-1].content

    # Format for WhatsApp
    twiml = format_for_whatsapp(agent_response)

    return Response(content=twiml, media_type="application/xml")
```

---

## 6. Success Criteria & KPIs

### Technical Success Criteria:
- ✅ LangGraph state machine transitions correctly
- ✅ Tools are called in optimal sequence
- ✅ Agent reasoning is logical and contextual
- ✅ Response time < 5 seconds (including tool calls)
- ✅ State persists across messages
- ✅ Gemini API success rate > 95%

### Functional Success Criteria:
- ✅ Agent automatically determines which tools to call
- ✅ Multi-tool orchestration works smoothly
- ✅ Coaching is contextual and personalized
- ✅ All conversation flows work end-to-end
- ✅ State management is robust

### Agent Quality Criteria:
- ✅ Agent doesn't hallucinate data (uses tools)
- ✅ Tool calling is efficient (not redundant)
- ✅ Responses are relevant and helpful
- ✅ Language quality is natural in Sinhala
- ✅ Agent handles errors gracefully

---

## 7. Risks & Mitigation

### Risk 1: Agent Tool Calling Inefficiency
**Issue:** Agent calls too many tools or wrong tools
**Mitigation:**
- Clear tool descriptions
- Few-shot examples in prompts
- Monitor tool usage patterns
- Optimize prompts based on logs

### Risk 2: LangGraph Complexity
**Issue:** State machine becomes too complex
**Mitigation:**
- Keep state schema simple
- Limit number of states
- Clear state transition rules
- Good documentation

### Risk 3: Latency from Tool Calling
**Issue:** Multiple tool calls increase response time
**Mitigation:**
- Use parallel tool calling where possible
- Cache tool results
- Optimize tool implementations
- Use Gemini Flash (faster model)

### Risk 4: Gemini API Costs
**Issue:** Every agent invocation costs money
**Mitigation:**
- Use Gemini Flash (cheaper)
- Implement response caching
- Set max_tokens limits
- Monitor costs daily

---

## 8. Required Dependencies

**New Packages:**
```txt
# LangGraph & LangChain
langgraph>=0.0.50
langchain>=0.1.0
langchain-core>=0.1.0
langchain-google-vertexai>=0.1.0

# Existing
fastapi==0.109.0
uvicorn[standard]==0.27.0
twilio==8.11.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
pandas>=2.0.0
google-genai

# Optional for production
redis>=5.0.0  # For Redis checkpointer
```

---

## 9. Next Steps After POC

### Immediate (Post-POC):
1. Analyze agent tool calling patterns
2. Optimize prompt engineering
3. Measure tool usage efficiency
4. Gather feedback from Nalin

### Short-term (1-2 months):
1. Migrate checkpointer to Redis
2. Add more sophisticated tools
3. Implement tool result caching
4. Add agent tracing/observability (LangSmith)
5. Optimize for multiple concurrent users

### Long-term (3-6 months):
1. Scale to all DSRs
2. Add memory summarization for long conversations
3. Implement advanced routing (multiple sub-graphs)
4. Add human-in-the-loop for critical decisions
5. Build manager dashboard with agent analytics

---

**Document Version:** 2.0 (LangGraph/LangChain Edition)
**Last Updated:** 2026-01-11
**Author:** CCS POPS Team
**Status:** Ready for Implementation with LangGraph
