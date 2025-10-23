# Enhanced Tau2 Execution Analysis Report

**Source File:** `airline_gemini2_5_flash_10tasks_2t_retry_agent_enhanced_logs.json`
**Generated:** 2025-10-22 23:57:37
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | 20 |
| **Successful Simulations** | 12 |
| **Task Success Rate** | 60.0% |
| **Total Tool Calls** | 230 |
| **Tool Success Rate** | 68.5% |
| **Tool Error Rate** | 31.5% |
| **State Changing Calls** | 24 |
| **Average Execution Time** | 0.33ms |
| **Success Metric Source** | action_checks |

---

## 🛠️ Tool Performance Analysis

### Performance Overview

| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |
|-----------|-------|--------------|---------------|----------|
| get_reservation_details | 116 | 18.1% | 0.04 | Poor |
| get_user_details | 36 | 25.0% | 0.04 | Poor |
| transfer_to_human_agents | 24 | 100.0% | 0.03 | Excellent |
| cancel_reservation | 14 | 28.6% | 0.10 | Poor |
| get_flight_status | 12 | 100.0% | 0.04 | Excellent |
| book_reservation | 10 | 0.0% | 6.62 | Poor |
| search_direct_flight | 10 | 20.0% | 0.18 | Poor |
| send_certificate | 4 | 25.0% | 0.05 | Poor |
| search_onestop_flight | 2 | 100.0% | 0.17 | Excellent |
| update_reservation_flights | 2 | 0.0% | 0.12 | Poor |

### Performance Distribution

- **Poor**: 7 tools
- **Excellent**: 3 tools

---

## 🔥 Failure Analysis

### Failure Overview

**Note:** Failure rates below are calculated against **action-checked calls only**, not total calls. See Performance Overview for overall success rates against all calls.

**Impact Score Formula:** `failure_rate × simulations_affected / total_simulations × 100`

| Tool Name | Failure Type | Count | Failure Rate | Simulations | Impact Score | Checked Calls |
|-----------|--------------|-------|--------------|-------------|--------------|---------------|
| book_reservation | Called With Wrong Args | 2 | 100.0% | 2 | 10.0 | 2 |
| update_reservation_flights | Never Called | 2 | 100.0% | 2 | 10.0 | 2 |
| search_direct_flight | Never Called | 2 | 50.0% | 2 | 5.0 | 4 |
| get_reservation_details | Called But No Match | 5 | 19.2% | 4 | 3.8 | 26 |
| get_user_details | Never Called | 3 | 25.0% | 3 | 3.8 | 12 |
| cancel_reservation | Never Called | 2 | 33.3% | 2 | 3.3 | 6 |
| send_certificate | Never Called | 1 | 50.0% | 1 | 2.5 | 2 |

**Key Failure Metrics:**
- Total failures: **17**
- Affected tools: **7**
- Total action checks performed: **54**
- Total tool calls (see Performance Overview): **230**

**Failure Type Breakdown:**
- **Never Called**: 10 failures (58.8%)
  - Affected tools: send_certificate, get_user_details, update_reservation_flights, cancel_reservation, search_direct_flight
- **Called But No Match**: 5 failures (29.4%)
  - Affected tools: get_reservation_details
- **Called With Wrong Args**: 2 failures (11.8%)
  - Affected tools: book_reservation

---

## 🔄 State Change Analysis

### State-Changing Tools (4 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| cancel_reservation | 14 | 28.6% | 0.10 |
| book_reservation | 4 | 0.0% | 16.43 |
| send_certificate | 4 | 25.0% | 0.05 |
| update_reservation_flights | 2 | 0.0% | 0.12 |

### Read-Only Tools (7 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 116 | 18.1% | 0.04 |
| get_user_details | 36 | 25.0% | 0.04 |
| transfer_to_human_agents | 24 | 100.0% | 0.03 |
| get_flight_status | 12 | 100.0% | 0.04 |
| search_direct_flight | 10 | 20.0% | 0.18 |
| book_reservation | 6 | 0.0% | 0.08 |
| search_onestop_flight | 2 | 100.0% | 0.17 |

---

## 🔗 Tool Sequence Patterns

### Most Common Tool Transitions

| From Tool | To Tool | Count |
|-----------|---------|-------|
| get_reservation_details | get_reservation_details | 69 |
| get_user_details | get_reservation_details | 32 |
| get_reservation_details | transfer_to_human_agents | 16 |
| transfer_to_human_agents | get_user_details | 12 |
| get_reservation_details | get_user_details | 10 |
| transfer_to_human_agents | get_reservation_details | 9 |
| get_reservation_details | get_flight_status | 6 |
| get_flight_status | get_flight_status | 6 |
| search_direct_flight | book_reservation | 6 |
| get_reservation_details | search_direct_flight | 6 |

---

## 🔍 Key Insights

- **3** out of 10 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 116 calls
- Overall system reliability: **68.5%**
- **7** tools showing poor performance require attention
- **7.4%** error rate across all tool executions
- **Highest impact:** book_reservation (Called With Wrong Args) - impact score 10.0, affecting 2 simulations
- **Most frequent failure:** get_reservation_details (Called But No Match) with 5 failures
- **Failure type breakdown:** 59% Never Called (critical), 29% Called But No Match (high), 12% Called With Wrong Args (medium)
- Tool distribution: **4** state-changing, **7** read-only
- State-changing tools underperform read-only tools (13.4% vs 51.9%)
- High self-loop rate (37.1%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (69 times)

---

## 💡 Recommendations

- **High Impact Pattern**: High-usage poor performers identified: get_reservation_details, get_user_details, cancel_reservation, book_reservation, search_direct_flight
- **Performance Pattern**: 7 tools categorized as poor performers based on execution metrics
- **High-Impact Failures:** book_reservation (Called With Wrong Args, medium severity): impact 10.0, 2 simulations, update_reservation_flights (Never Called, critical severity): impact 10.0, 2 simulations
- **Critical: Tools Never Executed:** 5 tools with 'never_called' failures (critical severity): send_certificate, get_user_details, update_reservation_flights, cancel_reservation, search_direct_flight
- **High Failure Rate:** Tools with >50% failure rate: book_reservation, update_reservation_flights

---

## 🎯 Detailed Failure Analysis

### 📊 Failure Statistics

- **Total failures:** 17
- **Overall error rate:** 7.4%
- **Affected tools:** 7
- **Error categories:** 1

### 🚨 Root Cause Analysis

#### Action Check Failures

**7 tools** failed action validation checks:

- **get_reservation_details**: 5 failures (19.2% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'reservation_id': '4OG6T3'}`
- **get_user_details**: 3 failures (25.0% failure rate)
  - Affected 3 simulation(s)
  - Example args: `{'user_id': 'anya_garcia_5901'}`
- **book_reservation**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'sophia_silva_7557', 'origin': 'ORD', 'destination': 'PHL', 'flight_type': 'one_way', 'c...`
- **cancel_reservation**: 2 failures (33.3% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'reservation_id': 'NQNU5R'}`
- **search_direct_flight**: 2 failures (50.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'origin': 'JFK', 'destination': 'MCO', 'date': '2024-05-22'}`
- **update_reservation_flights**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT005', 'date': '20...`
- **send_certificate**: 1 failures (50.0% failure rate)
  - Affected 1 simulation(s)
  - Example args: `{'user_id': 'noah_muller_9847', 'amount': 50}`

### ⚡ Performance Impact

**High-usage tools with poor performance:**

- **get_reservation_details**: 116 calls, 18.1% success rate
- **get_user_details**: 36 calls, 25.0% success rate
- **cancel_reservation**: 14 calls, 28.6% success rate
- **book_reservation**: 10 calls, 0.0% success rate
- **search_direct_flight**: 10 calls, 20.0% success rate

**Slowest tools by execution time:**

- **book_reservation**: 6.62ms average
- **search_direct_flight**: 0.18ms average
- **search_onestop_flight**: 0.17ms average
- **update_reservation_flights**: 0.12ms average
- **cancel_reservation**: 0.10ms average

### 💡 Failure Insights

- **Most problematic tool:** get_reservation_details (5 failures)
- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic
- **Average tool success rate:** 41.7%

### 🔍 Failure Type Comparison

Side-by-side comparison of failure types and their characteristics:

| Failure Type | Severity | Total Failures | Affected Tools | Top Failing Tools |
|--------------|----------|----------------|----------------|-------------------|
| **Never Called** | Critical | 10 | 5 | get_user_details (3), update_reservation_flights (2), cancel_reservation (2) |
| **Called But No Match** | High | 5 | 1 | get_reservation_details (5) |
| **Called With Wrong Args** | Medium | 2 | 1 | book_reservation (2) |

**Key Insights:**

- **Never Called (58.8%):** Critical severity - These tools were never executed at all, indicating the agent failed to recognize when to use them.
- **Called But No Match (29.4%):** High severity - Tools were called but didn't produce expected results, suggesting execution logic issues.
- **Called With Wrong Args (11.8%):** Medium severity - Tools were called with incorrect parameters, indicating parameter validation or reasoning issues.

---

## 🎯 Performance Issues Analysis

### Performance Metrics

- **Overall success rate: 68.5%**
- **State-changing actions: 13.4% success rate**
- **Read-only actions: 60.5% success rate**
- **47%pp performance drop when actions are required** (60.5% → 13.4% success)

### 🔍 Failure Patterns

- **7% of operations result in failures**
- **Most failed operations:**
  - get_reservation_details: 19% failure rate
  - get_user_details: 25% failure rate
  - book_reservation: 100% failure rate
- **Action validation failures in 7 different tools**
- **100%% of failures involve validation mismatches**

### 📊 Action Complexity Impact

- **0 state changes: 60.5% success**
- **Tools with state changes: 13.4% success**
- **Clear correlation between complexity and failure**

---

## 📋 Task & Simulation Analysis

### Simulation Success Patterns

- **Total simulations: 20**
- **Successful simulations: 12**
- **Task success rate: 60.0%**
- **Good task completion rate** - Some optimization opportunities

### 📈 Trial Performance Patterns

- **Success evaluation method: action_checks**
- **Action-based evaluation** - Success determined by correct action execution

### 🎲 Complexity vs Success Correlation

- **Average tools per simulation: 0.5**
- **Average calls per simulation: 11.5**
- **State-changing operations: 10.4% of all calls**

---

## 💬 Communication vs Tool Call Analysis

### Transfer to Human Analysis

- **Transfer calls: 24 (10.4% of total calls)**
- **Transfer success rate: 100.0%**

### Communication Tool Usage

- **Communication calls: 4 (1.7% of total calls)**
- **Communication success rate: 25.0%**

### 🛑 Task Termination Analysis

- **Execution efficiency: 0.0%** (time spent in actual tool execution)
- **Low efficiency suggests high wait times** or communication delays
- **7 tools used extensively** (10+ calls each)
- **Possible indication of retry patterns** or complex multi-step operations

---

## ⚡ Performance Deep Dive

### 🏆 Performance Tier Analysis

**Excellent Performance (3 tools)** - Success rate ≥95%:
- `transfer_to_human_agents`: 100.0% success, 24 calls
- `get_flight_status`: 100.0% success, 12 calls
- `search_onestop_flight`: 100.0% success, 2 calls

**Poor Performance (7 tools)** - Success rate <75%:
- `get_reservation_details`: 18.1% success, 116 calls
- `get_user_details`: 25.0% success, 36 calls
- `cancel_reservation`: 28.6% success, 14 calls
- `book_reservation`: 0.0% success, 10 calls
- `search_direct_flight`: 20.0% success, 10 calls
- `send_certificate`: 25.0% success, 4 calls
- `update_reservation_flights`: 0.0% success, 2 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`** (Called But No Match, high severity):
  - Success rate: 18.1%
  - Total calls: 116
  - Failed calls: 95
  - Impact score: 3.8
  - Simulations affected: 4
  - State changing: No
- **`get_user_details`** (Never Called, critical severity):
  - Success rate: 25.0%
  - Total calls: 36
  - Failed calls: 27
  - Impact score: 3.8
  - Simulations affected: 3
  - State changing: No
- **`cancel_reservation`** (Never Called, critical severity):
  - Success rate: 28.6%
  - Total calls: 14
  - Failed calls: 10
  - Impact score: 3.3
  - Simulations affected: 2
  - State changing: Yes
- **`book_reservation`** (Called With Wrong Args, medium severity):
  - Success rate: 0.0%
  - Total calls: 10
  - Failed calls: 10
  - Impact score: 10.0
  - Simulations affected: 2
  - State changing: Yes
- **`search_direct_flight`** (Never Called, critical severity):
  - Success rate: 20.0%
  - Total calls: 10
  - Failed calls: 8
  - Impact score: 5.0
  - Simulations affected: 2
  - State changing: No

### ⏱️ Execution Time Analysis

- **Average execution time across all tools:** 0.74ms
- **Median execution time:** 0.08ms
- **Slowest tool:** `book_reservation` (6.62ms)
- **Fastest tool:** `transfer_to_human_agents` (0.03ms)

**Performance vs Usage Correlation:**
- High-usage tools (≥10 calls) average success rate: 41.7%
- Low-usage tools (<10 calls) average success rate: 41.7%

**State-Changing vs Read-Only Performance:**
- State-changing tools: 13.4% success, 0.0017s avg time (4 tools)
- Read-only tools: 60.5% success, 0.0001s avg time (6 tools)

---

## 🔄 Execution Patterns & Workflow Analysis

### ⏰ Execution Timeline

- **Total execution timespan:** 182.3 seconds
- **Actual tool execution time:** 0.0769 seconds
- **Execution efficiency:** 0.04% (time spent in tool execution)
- **Average call rate:** 1.26 calls/second

### 🔗 Tool Usage Patterns

**Most Common Tool Transitions:**

- **`get_reservation_details` → `get_reservation_details`** (69x): Self-loops indicate repeated calls to same tool
- **`get_user_details` → `get_reservation_details`** (32x): Common workflow pattern
- **`get_reservation_details` → `transfer_to_human_agents`** (16x): Common workflow pattern
- **`transfer_to_human_agents` → `get_user_details`** (12x): Common workflow pattern
- **`get_reservation_details` → `get_user_details`** (10x): Common workflow pattern

**Pattern Analysis:**
- **Most common transition:** 30.1% of all transitions
- **Moderately concentrated** workflow with some preferred patterns
- **Self-loop rate:** 37.1% of transitions are repeated calls to same tool
- **High self-loop rate** may indicate retry logic or iterative processing

### 🧠 Workflow Intelligence

- **Tool diversity:** 10 unique tools used
- **Average calls per tool:** 23.0
- **Usage concentration:** 50.4% of calls go to most-used tool

### 🎯 Success Pattern Analysis

- **Moderate success pattern** (60.0%): Mixed results requiring investigation
- **Failure distribution:** 8 failed simulations out of 20 total
- **Mixed pattern:** Both successes and failures indicate inconsistent behavior

---

## 📈 Visualization Files

The following core visualizations are generated by default:

- `analysis_report.md` - This markdown summary report
- `tool_report.html` - Comprehensive HTML tool analysis report
- `enhanced_analysis_report.html` - Enhanced analysis report with interactive plots

**Additional visualizations available** (enable by uncommenting in analysis script):

- `summary_dashboard.html` - Executive dashboard with key metrics
- `failure_analysis.html` - Detailed failure analysis charts
- `state_change_analysis.html` - State change patterns and performance
- `tool_flow_sankey.html` - Tool usage flow diagram
- `performance_bottlenecks.html` - Performance analysis scatter plot
- `simulation_report.html` - Comprehensive HTML simulation report

---

*Report generated by Enhanced Tau2 Analytics Framework*
