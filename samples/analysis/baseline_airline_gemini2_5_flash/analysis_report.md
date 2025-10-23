# Enhanced Tau2 Execution Analysis Report

**Source File:** `baseline_airline_gemini2_5_flash_reduced.json`
**Generated:** 2025-10-23 11:48:10
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | 200 |
| **Successful Simulations** | 94 |
| **Task Success Rate** | 47.0% |
| **Total Tool Calls** | 1094 |
| **Tool Success Rate** | 48.5% |
| **Tool Error Rate** | 51.5% |
| **State Changing Calls** | 151 |
| **Average Execution Time** | 0.20ms |
| **Success Metric Source** | action_checks |

---

## 🛠️ Tool Performance Analysis

### Performance Overview

| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |
|-----------|-------|--------------|---------------|----------|
| get_reservation_details | 429 | 38.0% | 0.05 | Poor |
| get_user_details | 156 | 28.8% | 0.06 | Poor |
| search_direct_flight | 143 | 25.9% | 0.28 | Poor |
| transfer_to_human_agents | 98 | 0.0% | 0.06 | Poor |
| get_flight_status | 68 | 100.0% | 0.05 | Excellent |
| update_reservation_flights | 49 | 0.0% | 0.15 | Poor |
| cancel_reservation | 41 | 65.9% | 0.15 | Poor |
| book_reservation | 39 | 0.0% | 0.13 | Poor |
| search_onestop_flight | 39 | 100.0% | 2.76 | Excellent |
| update_reservation_baggages | 13 | 53.8% | 0.07 | Poor |
| calculate | 10 | 0.0% | 0.66 | Poor |
| update_reservation_passengers | 7 | 100.0% | 0.11 | Excellent |
| send_certificate | 2 | 50.0% | 0.08 | Poor |

### Performance Distribution

- **Poor**: 10 tools
- **Excellent**: 3 tools

---

## 🔥 Failure Analysis

### Failure Overview

**Note:** Failure rates below are calculated against **action-checked calls only**, not total calls. See Performance Overview for overall success rates against all calls.

**Impact Score Formula:** `failure_rate × simulations_affected / total_simulations × 100`

| Tool Name | Failure Type | Count | Failure Rate | Simulations | Impact Score | Checked Calls |
|-----------|--------------|-------|--------------|-------------|--------------|---------------|
| update_reservation_flights | Called With Wrong Args | 84 | 100.0% | 56 | 28.0 | 84 |
| book_reservation | Never Called | 36 | 100.0% | 28 | 14.0 | 36 |
| update_reservation_baggages | Never Called | 17 | 70.8% | 17 | 6.0 | 24 |
| send_certificate | Never Called | 11 | 91.7% | 11 | 5.0 | 12 |
| search_direct_flight | Never Called | 43 | 53.8% | 18 | 4.8 | 80 |
| cancel_reservation | Never Called | 25 | 48.1% | 18 | 4.3 | 52 |
| get_reservation_details | Called But No Match | 65 | 28.5% | 21 | 3.0 | 228 |
| calculate | Never Called | 4 | 100.0% | 4 | 2.0 | 4 |
| transfer_to_human_agents | Never Called | 4 | 100.0% | 4 | 2.0 | 4 |
| get_user_details | Never Called | 11 | 19.6% | 11 | 1.1 | 56 |
| update_reservation_passengers | Never Called | 5 | 41.7% | 5 | 1.0 | 12 |

**Key Failure Metrics:**
- Total failures: **305**
- Affected tools: **11**
- Total action checks performed: **592**
- Total tool calls (see Performance Overview): **1094**

**Failure Type Breakdown:**
- **Never Called**: 198 failures (64.9%)
  - Affected tools: get_user_details, send_certificate, update_reservation_flights, cancel_reservation, search_direct_flight, ... (6 more)
- **Called With Wrong Args**: 63 failures (20.7%)
  - Affected tools: book_reservation, update_reservation_flights, update_reservation_baggages, search_direct_flight
- **Called But No Match**: 44 failures (14.4%)
  - Affected tools: get_reservation_details, search_direct_flight, cancel_reservation

---

## 📊 Action Sequence Accuracy

This section compares actual tool call sequences against expected action sequences from ground truth task definitions.

### Overview Metrics

| Metric | Value |
|--------|-------|
| **Precision** | 27.88% |
| **Recall** | 45.78% |
| **F1 Score** | 34.65% |
| **Total Tasks Analyzed** | 172 |
| **Matched Actions** | 271/592 |

### Task Distribution

- ✅ **Success + Ordered:** 71 tasks (correct sequence, task succeeded)
- ⚠️  **Success + Unordered:** 0 tasks (wrong order, but task succeeded)
- ❌ **Failed + Ordered:** 94 tasks (correct sequence, but task failed)
- 🔴 **Failed + Unordered:** 7 tasks (wrong sequence, task failed)

### Action-Level Metrics

- **Expected actions:** 592
- **Actual actions executed:** 972
- **Correctly matched:** 271
- **Missing (omitted):** 237
- **Extra (unexpected):** 617
- **Argument mismatches:** 84

### Per-Tool Sequence Accuracy

| Tool | Expected | ✅ Matched | ❌ Missing | 🔧 Arg Err | ⚠️ Extra | Precision | Recall |
|------|----------|-----------|-----------|-----------|---------|-----------|--------|
| get_reservation_details | 228 | 151 | 57 | 20 | 213 | 41.5% | 66.2% |
| update_reservation_flights | 84 | 0 | 46 | 38 | 8 | 0.0% | 0.0% |
| search_direct_flight | 80 | 37 | 41 | 2 | 78 | 32.2% | 46.2% |
| get_user_details | 56 | 45 | 11 | 0 | 93 | 32.6% | 80.4% |
| cancel_reservation | 52 | 23 | 23 | 6 | 10 | 69.7% | 44.2% |
| book_reservation | 36 | 0 | 23 | 13 | 26 | 0.0% | 0.0% |
| update_reservation_baggages | 24 | 7 | 12 | 5 | 0 | 100.0% | 29.2% |
| send_certificate | 12 | 1 | 11 | 0 | 1 | 50.0% | 8.3% |
| update_reservation_passengers | 12 | 7 | 5 | 0 | 0 | 100.0% | 58.3% |
| transfer_to_human_agents | 4 | 0 | 4 | 0 | 83 | 0.0% | 0.0% |

*Showing top 10 of 13 tools. See detailed reports for complete data.*

---

## 🔄 State Change Analysis

### State-Changing Tools (6 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| update_reservation_flights | 49 | 0.0% | 0.15 |
| cancel_reservation | 41 | 65.9% | 0.15 |
| book_reservation | 39 | 0.0% | 0.13 |
| update_reservation_baggages | 13 | 53.8% | 0.07 |
| update_reservation_passengers | 7 | 100.0% | 0.11 |
| send_certificate | 2 | 50.0% | 0.08 |

### Read-Only Tools (7 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 429 | 38.0% | 0.05 |
| get_user_details | 156 | 28.8% | 0.06 |
| search_direct_flight | 143 | 25.9% | 0.28 |
| transfer_to_human_agents | 98 | 0.0% | 0.06 |
| get_flight_status | 68 | 100.0% | 0.05 |
| search_onestop_flight | 39 | 100.0% | 2.76 |
| calculate | 10 | 0.0% | 0.66 |

---

## 🔗 Tool Sequence Patterns

### Most Common Tool Transitions

| From Tool | To Tool | Count |
|-----------|---------|-------|
| get_reservation_details | get_reservation_details | 233 |
| get_user_details | get_reservation_details | 122 |
| search_direct_flight | search_direct_flight | 57 |
| get_reservation_details | transfer_to_human_agents | 49 |
| transfer_to_human_agents | get_user_details | 45 |
| get_reservation_details | search_direct_flight | 40 |
| search_direct_flight | search_onestop_flight | 33 |
| get_reservation_details | get_user_details | 33 |
| transfer_to_human_agents | get_reservation_details | 30 |
| get_reservation_details | get_flight_status | 29 |

---

## 🔍 Key Insights

- **3** out of 13 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 429 calls
- Overall system reliability: **48.5%**
- **10** tools showing poor performance require attention
- **27.9%** error rate across all tool executions
- **Highest impact:** update_reservation_flights (Called With Wrong Args) - impact score 28.0, affecting 56 simulations
- **Most frequent failure:** update_reservation_flights (Called With Wrong Args) with 84 failures
- **Failure type breakdown:** 65% Never Called (critical), 21% Called With Wrong Args (medium), 14% Called But No Match (high)
- Tool distribution: **6** state-changing, **7** read-only
- High self-loop rate (36.2%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (233 times)

---

## 💡 Recommendations

- **High Impact Pattern**: High-usage poor performers identified: get_reservation_details, get_user_details, search_direct_flight, transfer_to_human_agents, update_reservation_flights, cancel_reservation, book_reservation, update_reservation_baggages, calculate
- **Performance Pattern**: 10 tools categorized as poor performers based on execution metrics
- **High-Impact Failures:** update_reservation_flights (Called With Wrong Args, medium severity): impact 28.0, 56 simulations, book_reservation (Never Called, critical severity): impact 14.0, 28 simulations, update_reservation_baggages (Never Called, critical severity): impact 6.0, 17 simulations, send_certificate (Never Called, critical severity): impact 5.0, 11 simulations
- **Critical: Tools Never Executed:** 11 tools with 'never_called' failures (critical severity): get_user_details, send_certificate, update_reservation_flights, cancel_reservation, search_direct_flight
- **High Failure Rate:** Tools with >50% failure rate: update_reservation_flights, search_direct_flight, book_reservation, update_reservation_baggages, send_certificate, calculate, transfer_to_human_agents

---

## 🎯 Detailed Failure Analysis

### 📊 Failure Statistics

- **Total failures:** 305
- **Overall error rate:** 27.9%
- **Affected tools:** 11
- **Error categories:** 1

### 🚨 Root Cause Analysis

#### Action Check Failures

**11 tools** failed action validation checks:

- **update_reservation_flights**: 84 failures (100.0% failure rate)
  - Affected 56 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT005', 'date': '20...`
- **get_reservation_details**: 65 failures (28.5% failure rate)
  - Affected 21 simulation(s)
  - Example args: `{'reservation_id': 'S61CZX'}`
- **search_direct_flight**: 43 failures (53.8% failure rate)
  - Affected 18 simulation(s)
  - Example args: `{'origin': 'JFK', 'destination': 'MCO', 'date': '2024-05-22'}`
- **book_reservation**: 36 failures (100.0% failure rate)
  - Affected 28 simulation(s)
  - Example args: `{'user_id': 'sophia_silva_7557', 'origin': 'ORD', 'destination': 'PHL', 'flight_type': 'one_way', 'c...`
- **cancel_reservation**: 25 failures (48.1% failure rate)
  - Affected 18 simulation(s)
  - Example args: `{'reservation_id': 'NQNU5R'}`
- **update_reservation_baggages**: 17 failures (70.8% failure rate)
  - Affected 17 simulation(s)
  - Example args: `{'reservation_id': 'YAX4DR', 'total_baggages': 2, 'nonfree_baggages': 0, 'payment_id': 'credit_card_...`
- **get_user_details**: 11 failures (19.6% failure rate)
  - Affected 11 simulation(s)
  - Example args: `{'user_id': 'mei_brown_7075'}`
- **send_certificate**: 11 failures (91.7% failure rate)
  - Affected 11 simulation(s)
  - Example args: `{'user_id': 'noah_muller_9847', 'amount': 50}`
- **update_reservation_passengers**: 5 failures (41.7% failure rate)
  - Affected 5 simulation(s)
  - Example args: `{'reservation_id': 'FQ8APE', 'passengers': [{'first_name': 'Omar', 'last_name': 'Rossi', 'dob': '197...`
- **calculate**: 4 failures (100.0% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'expression': '2 * ((350 - 122) + (499 - 127))'}`
- **transfer_to_human_agents**: 4 failures (100.0% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'summary': 'User wants to change my upcoming one stop flight from ATL to LAX within reservation XEW...`

### ⚡ Performance Impact

**High-usage tools with poor performance:**

- **get_reservation_details**: 429 calls, 38.0% success rate
- **get_user_details**: 156 calls, 28.8% success rate
- **search_direct_flight**: 143 calls, 25.9% success rate
- **transfer_to_human_agents**: 98 calls, 0.0% success rate
- **update_reservation_flights**: 49 calls, 0.0% success rate
- **cancel_reservation**: 41 calls, 65.9% success rate
- **book_reservation**: 39 calls, 0.0% success rate
- **update_reservation_baggages**: 13 calls, 53.8% success rate
- **calculate**: 10 calls, 0.0% success rate

**Slowest tools by execution time:**

- **search_onestop_flight**: 2.76ms average
- **calculate**: 0.66ms average
- **search_direct_flight**: 0.28ms average
- **cancel_reservation**: 0.15ms average
- **update_reservation_flights**: 0.15ms average

### 💡 Failure Insights

- **Most problematic tool:** update_reservation_flights (84 failures)
- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic
- **Average tool success rate:** 43.3%

### 🔍 Failure Type Comparison

Side-by-side comparison of failure types and their characteristics:

| Failure Type | Severity | Total Failures | Affected Tools | Top Failing Tools |
|--------------|----------|----------------|----------------|-------------------|
| **Never Called** | Critical | 198 | 11 | update_reservation_flights (42), search_direct_flight (39), get_reservation_details (29) |
| **Called But No Match** | High | 44 | 3 | get_reservation_details (36), cancel_reservation (6), search_direct_flight (2) |
| **Called With Wrong Args** | Medium | 63 | 4 | update_reservation_flights (42), book_reservation (14), update_reservation_baggages (5) |

**Key Insights:**

- **Never Called (64.9%):** Critical severity - These tools were never executed at all, indicating the agent failed to recognize when to use them.
- **Called But No Match (14.4%):** High severity - Tools were called but didn't produce expected results, suggesting execution logic issues.
- **Called With Wrong Args (20.7%):** Medium severity - Tools were called with incorrect parameters, indicating parameter validation or reasoning issues.

---

## 🎯 Performance Issues Analysis

### Performance Metrics

- **Overall success rate: 48.5%**
- **State-changing actions: 44.9% success rate**
- **Read-only actions: 41.8% success rate**

### 🔍 Failure Patterns

- **28% of operations result in failures**
- **Most failed operations:**
  - update_reservation_flights: 100% failure rate
  - get_reservation_details: 29% failure rate
  - search_direct_flight: 54% failure rate
- **Action validation failures in 11 different tools**
- **100%% of failures involve validation mismatches**

### 📊 Action Complexity Impact

- **0 state changes: 41.8% success**
- **Tools with state changes: 44.9% success**

---

## 📋 Task & Simulation Analysis

### Simulation Success Patterns

- **Total simulations: 200**
- **Successful simulations: 94**
- **Task success rate: 47.0%**
- **Moderate task completion rate** - Significant improvement needed

### 📈 Trial Performance Patterns

- **Success evaluation method: action_checks**
- **Action-based evaluation** - Success determined by correct action execution

### 🎲 Complexity vs Success Correlation

- **Average tools per simulation: 0.1**
- **Average calls per simulation: 5.5**
- **State-changing operations: 13.8% of all calls**

---

## 💬 Communication vs Tool Call Analysis

### Transfer to Human Analysis

- **Transfer calls: 98 (9.0% of total calls)**
- **Transfer success rate: 0.0%**

### Communication Tool Usage

- **Communication calls: 2 (0.2% of total calls)**
- **Communication success rate: 50.0%**

### 🛑 Task Termination Analysis

- **Execution efficiency: 0.0%** (time spent in actual tool execution)
- **Low efficiency suggests high wait times** or communication delays
- **11 tools used extensively** (10+ calls each)
- **Possible indication of retry patterns** or complex multi-step operations

---

## ⚡ Performance Deep Dive

### 🏆 Performance Tier Analysis

**Excellent Performance (3 tools)** - Success rate ≥95%:
- `get_flight_status`: 100.0% success, 68 calls
- `search_onestop_flight`: 100.0% success, 39 calls
- `update_reservation_passengers`: 100.0% success, 7 calls

**Poor Performance (10 tools)** - Success rate <75%:
- `get_reservation_details`: 38.0% success, 429 calls
- `get_user_details`: 28.8% success, 156 calls
- `search_direct_flight`: 25.9% success, 143 calls
- `transfer_to_human_agents`: 0.0% success, 98 calls
- `update_reservation_flights`: 0.0% success, 49 calls
- `cancel_reservation`: 65.9% success, 41 calls
- `book_reservation`: 0.0% success, 39 calls
- `update_reservation_baggages`: 53.8% success, 13 calls
- `calculate`: 0.0% success, 10 calls
- `send_certificate`: 50.0% success, 2 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`** (Called But No Match, high severity):
  - Success rate: 38.0%
  - Total calls: 429
  - Failed calls: 266
  - Impact score: 3.0
  - Simulations affected: 21
  - State changing: No
- **`get_user_details`** (Never Called, critical severity):
  - Success rate: 28.8%
  - Total calls: 156
  - Failed calls: 111
  - Impact score: 1.1
  - Simulations affected: 11
  - State changing: No
- **`search_direct_flight`** (Never Called, critical severity):
  - Success rate: 25.9%
  - Total calls: 143
  - Failed calls: 106
  - Impact score: 4.8
  - Simulations affected: 18
  - State changing: No
- **`transfer_to_human_agents`** (Never Called, critical severity):
  - Success rate: 0.0%
  - Total calls: 98
  - Failed calls: 98
  - Impact score: 2.0
  - Simulations affected: 4
  - State changing: No
- **`update_reservation_flights`** (Called With Wrong Args, medium severity):
  - Success rate: 0.0%
  - Total calls: 49
  - Failed calls: 49
  - Impact score: 28.0
  - Simulations affected: 56
  - State changing: Yes
- **`cancel_reservation`** (Never Called, critical severity):
  - Success rate: 65.9%
  - Total calls: 41
  - Failed calls: 13
  - Impact score: 4.3
  - Simulations affected: 18
  - State changing: Yes
- **`book_reservation`** (Never Called, critical severity):
  - Success rate: 0.0%
  - Total calls: 39
  - Failed calls: 39
  - Impact score: 14.0
  - Simulations affected: 28
  - State changing: Yes
- **`update_reservation_baggages`** (Never Called, critical severity):
  - Success rate: 53.8%
  - Total calls: 13
  - Failed calls: 6
  - Impact score: 6.0
  - Simulations affected: 17
  - State changing: Yes
- **`calculate`** (Never Called, critical severity):
  - Success rate: 0.0%
  - Total calls: 10
  - Failed calls: 10
  - Impact score: 2.0
  - Simulations affected: 4
  - State changing: No

### ⏱️ Execution Time Analysis

- **Average execution time across all tools:** 0.35ms
- **Median execution time:** 0.11ms
- **Slowest tool:** `search_onestop_flight` (2.76ms)
- **Fastest tool:** `get_flight_status` (0.05ms)

**Performance vs Usage Correlation:**
- High-usage tools (≥10 calls) average success rate: 37.5%
- Low-usage tools (<10 calls) average success rate: 75.0%
- **Usage-performance correlation:** High-usage tools perform 37.5% worse

**State-Changing vs Read-Only Performance:**
- State-changing tools: 44.9% success, 0.0001s avg time (6 tools)
- Read-only tools: 41.8% success, 0.0006s avg time (7 tools)

---

## 🔄 Execution Patterns & Workflow Analysis

### ⏰ Execution Timeline

- **Total execution timespan:** 5504.8 seconds
- **Actual tool execution time:** 0.2156 seconds
- **Execution efficiency:** 0.00% (time spent in tool execution)
- **Average call rate:** 0.20 calls/second
- **Low call rate** may indicate thinking/processing time between calls

### 🔗 Tool Usage Patterns

**Most Common Tool Transitions:**

- **`get_reservation_details` → `get_reservation_details`** (233x): Self-loops indicate repeated calls to same tool
- **`get_user_details` → `get_reservation_details`** (122x): Common workflow pattern
- **`search_direct_flight` → `search_direct_flight`** (57x): Self-loops indicate repeated calls to same tool
- **`get_reservation_details` → `transfer_to_human_agents`** (49x): Common workflow pattern
- **`transfer_to_human_agents` → `get_user_details`** (45x): Common workflow pattern

**Pattern Analysis:**
- **Most common transition:** 21.3% of all transitions
- **Moderately concentrated** workflow with some preferred patterns
- **Self-loop rate:** 36.2% of transitions are repeated calls to same tool
- **High self-loop rate** may indicate retry logic or iterative processing

### 🧠 Workflow Intelligence

- **Tool diversity:** 13 unique tools used
- **Average calls per tool:** 84.2
- **Usage concentration:** 39.2% of calls go to most-used tool

### 🎯 Success Pattern Analysis

- **Low success pattern** (47.0%): Systematic issues affecting most executions
- **Failure distribution:** 106 failed simulations out of 200 total
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
