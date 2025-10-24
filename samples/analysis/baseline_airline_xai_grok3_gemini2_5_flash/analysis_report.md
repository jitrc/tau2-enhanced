# Enhanced Tau2 Execution Analysis Report

**Source File:** `baseline_airline_xai_grok3_gemini2_5_flash_reduced.json`
**Generated:** 2025-10-23 11:48:07
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | 200 |
| **Successful Simulations** | 115 |
| **Task Success Rate** | 57.5% |
| **Total Tool Calls** | 1162 |
| **Tool Success Rate** | 65.3% |
| **Tool Error Rate** | 34.7% |
| **State Changing Calls** | 139 |
| **Average Execution Time** | 0.27ms |
| **Success Metric Source** | action_checks |

---

## 🛠️ Tool Performance Analysis

### Performance Overview

| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |
|-----------|-------|--------------|---------------|----------|
| get_reservation_details | 488 | 44.5% | 0.10 | Poor |
| search_direct_flight | 164 | 10.4% | 0.24 | Poor |
| get_user_details | 158 | 35.4% | 0.82 | Poor |
| search_onestop_flight | 100 | 100.0% | 0.68 | Excellent |
| update_reservation_flights | 62 | 61.3% | 0.13 | Poor |
| get_flight_status | 56 | 100.0% | 0.06 | Excellent |
| transfer_to_human_agents | 56 | 0.0% | 0.06 | Poor |
| cancel_reservation | 39 | 74.4% | 0.15 | Poor |
| update_reservation_baggages | 16 | 56.2% | 0.08 | Poor |
| book_reservation | 9 | 55.6% | 0.22 | Poor |
| update_reservation_passengers | 9 | 100.0% | 0.12 | Excellent |
| send_certificate | 4 | 100.0% | 0.16 | Excellent |
| calculate | 1 | 0.0% | 0.11 | Poor |

### Performance Distribution

- **Poor**: 9 tools
- **Excellent**: 4 tools

---

## 🔥 Failure Analysis

### Failure Overview

**Note:** Failure rates below are calculated against **action-checked calls only**, not total calls. See Performance Overview for overall success rates against all calls.

**Impact Score Formula:** `failure_rate × simulations_affected / total_simulations × 100`

| Tool Name | Failure Type | Count | Failure Rate | Simulations | Impact Score | Checked Calls |
|-----------|--------------|-------|--------------|-------------|--------------|---------------|
| book_reservation | Never Called | 28 | 84.8% | 22 | 9.3 | 33 |
| update_reservation_flights | Never Called | 46 | 54.8% | 29 | 7.9 | 84 |
| search_direct_flight | Never Called | 63 | 78.8% | 19 | 7.5 | 80 |
| update_reservation_baggages | Never Called | 15 | 62.5% | 15 | 4.7 | 24 |
| cancel_reservation | Never Called | 22 | 43.1% | 15 | 3.2 | 51 |
| send_certificate | Never Called | 8 | 66.7% | 8 | 2.7 | 12 |
| calculate | Never Called | 4 | 100.0% | 4 | 2.0 | 4 |
| transfer_to_human_agents | Never Called | 4 | 100.0% | 4 | 2.0 | 4 |
| update_reservation_passengers | Never Called | 3 | 25.0% | 3 | 0.4 | 12 |
| get_reservation_details | Called But No Match | 11 | 4.8% | 5 | 0.1 | 228 |

**Key Failure Metrics:**
- Total failures: **204**
- Affected tools: **10**
- Total action checks performed: **588**
- Total tool calls (see Performance Overview): **1162**

**Failure Type Breakdown:**
- **Never Called**: 163 failures (79.9%)
  - Affected tools: update_reservation_flights, transfer_to_human_agents, search_direct_flight, calculate, book_reservation, ... (4 more)
- **Called With Wrong Args**: 27 failures (13.2%)
  - Affected tools: update_reservation_flights, update_reservation_baggages, book_reservation, search_direct_flight
- **Called But No Match**: 14 failures (6.9%)
  - Affected tools: cancel_reservation, get_reservation_details

---

## 📊 Action Sequence Accuracy

This section compares actual tool call sequences against expected action sequences from ground truth task definitions.

### Overview Metrics

| Metric | Value |
|--------|-------|
| **Precision** | 33.39% |
| **Recall** | 61.15% |
| **F1 Score** | 43.20% |
| **Total Tasks Analyzed** | 172 |
| **Matched Actions** | 362/592 |

### Task Distribution

- ✅ **Success + Ordered:** 75 tasks (correct sequence, task succeeded)
- ⚠️  **Success + Unordered:** 12 tasks (wrong order, but task succeeded)
- ❌ **Failed + Ordered:** 78 tasks (correct sequence, but task failed)
- 🔴 **Failed + Unordered:** 7 tasks (wrong sequence, task failed)

### Action-Level Metrics

- **Expected actions:** 592
- **Actual actions executed:** 1084
- **Correctly matched:** 362
- **Missing (omitted):** 184
- **Extra (unexpected):** 676
- **Argument mismatches:** 46

### Per-Tool Sequence Accuracy

| Tool | Expected | ✅ Matched | ❌ Missing | 🔧 Arg Err | ⚠️ Extra | Precision | Recall |
|------|----------|-----------|-----------|-----------|---------|-----------|--------|
| get_reservation_details | 228 | 203 | 11 | 14 | 246 | 45.2% | 89.0% |
| update_reservation_flights | 84 | 32 | 37 | 15 | 15 | 68.1% | 38.1% |
| search_direct_flight | 80 | 17 | 60 | 3 | 136 | 11.1% | 21.2% |
| get_user_details | 56 | 56 | 0 | 0 | 86 | 39.4% | 100.0% |
| cancel_reservation | 52 | 27 | 22 | 3 | 9 | 75.0% | 51.9% |
| book_reservation | 36 | 5 | 27 | 4 | 0 | 100.0% | 13.9% |
| update_reservation_baggages | 24 | 9 | 8 | 7 | 0 | 100.0% | 37.5% |
| send_certificate | 12 | 4 | 8 | 0 | 0 | 100.0% | 33.3% |
| update_reservation_passengers | 12 | 9 | 3 | 0 | 0 | 100.0% | 75.0% |
| transfer_to_human_agents | 4 | 0 | 4 | 0 | 44 | 0.0% | 0.0% |

*Showing top 10 of 13 tools. See detailed reports for complete data.*

---

## 🔄 State Change Analysis

### State-Changing Tools (6 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| update_reservation_flights | 62 | 61.3% | 0.13 |
| cancel_reservation | 39 | 74.4% | 0.15 |
| update_reservation_baggages | 16 | 56.2% | 0.08 |
| book_reservation | 9 | 55.6% | 0.22 |
| update_reservation_passengers | 9 | 100.0% | 0.12 |
| send_certificate | 4 | 100.0% | 0.16 |

### Read-Only Tools (7 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 488 | 44.5% | 0.10 |
| search_direct_flight | 164 | 10.4% | 0.24 |
| get_user_details | 158 | 35.4% | 0.82 |
| search_onestop_flight | 100 | 100.0% | 0.68 |
| get_flight_status | 56 | 100.0% | 0.06 |
| transfer_to_human_agents | 56 | 0.0% | 0.06 |
| calculate | 1 | 0.0% | 0.11 |

---

## 🔗 Tool Sequence Patterns

### Most Common Tool Transitions

| From Tool | To Tool | Count |
|-----------|---------|-------|
| get_reservation_details | get_reservation_details | 287 |
| get_user_details | get_reservation_details | 134 |
| search_direct_flight | search_onestop_flight | 68 |
| search_direct_flight | search_direct_flight | 66 |
| search_onestop_flight | search_direct_flight | 45 |
| get_reservation_details | transfer_to_human_agents | 40 |
| get_reservation_details | search_direct_flight | 38 |
| get_reservation_details | get_user_details | 33 |
| transfer_to_human_agents | get_user_details | 30 |
| get_reservation_details | cancel_reservation | 29 |

---

## 🔍 Key Insights

- **4** out of 13 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 488 calls
- Overall system reliability: **65.3%**
- **9** tools showing poor performance require attention
- **17.6%** error rate across all tool executions
- **Highest impact:** book_reservation (Never Called) - impact score 9.3, affecting 22 simulations
- **Most frequent failure:** search_direct_flight (Never Called) with 63 failures
- **Failure type breakdown:** 80% Never Called (critical), 13% Called With Wrong Args (medium), 7% Called But No Match (high)
- Tool distribution: **6** state-changing, **7** read-only
- High self-loop rate (37.3%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (287 times)

---

## 💡 Recommendations

- **High Impact Pattern**: High-usage poor performers identified: get_reservation_details, search_direct_flight, get_user_details, update_reservation_flights, transfer_to_human_agents, cancel_reservation, update_reservation_baggages
- **Performance Pattern**: 9 tools categorized as poor performers based on execution metrics
- **High-Impact Failures:** book_reservation (Never Called, critical severity): impact 9.3, 22 simulations, update_reservation_flights (Never Called, critical severity): impact 7.9, 29 simulations, search_direct_flight (Never Called, critical severity): impact 7.5, 19 simulations
- **Critical: Tools Never Executed:** 9 tools with 'never_called' failures (critical severity): update_reservation_flights, transfer_to_human_agents, search_direct_flight, calculate, book_reservation
- **High Failure Rate:** Tools with >50% failure rate: search_direct_flight, update_reservation_flights, book_reservation, update_reservation_baggages, send_certificate, calculate, transfer_to_human_agents

---

## 🎯 Detailed Failure Analysis

### 📊 Failure Statistics

- **Total failures:** 204
- **Overall error rate:** 17.6%
- **Affected tools:** 10
- **Error categories:** 1

### 🚨 Root Cause Analysis

#### Action Check Failures

**10 tools** failed action validation checks:

- **search_direct_flight**: 63 failures (78.8% failure rate)
  - Affected 19 simulation(s)
  - Example args: `{'origin': 'BOS', 'destination': 'MCO', 'date': '2024-05-18'}`
- **update_reservation_flights**: 46 failures (54.8% failure rate)
  - Affected 29 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT005', 'date': '20...`
- **book_reservation**: 28 failures (84.8% failure rate)
  - Affected 22 simulation(s)
  - Example args: `{'user_id': 'mohamed_silva_9265', 'origin': 'JFK', 'destination': 'SFO', 'flight_type': 'round_trip'...`
- **cancel_reservation**: 22 failures (43.1% failure rate)
  - Affected 15 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B'}`
- **update_reservation_baggages**: 15 failures (62.5% failure rate)
  - Affected 15 simulation(s)
  - Example args: `{'reservation_id': 'FQ8APE', 'total_baggages': 3, 'nonfree_baggages': 0, 'payment_id': 'gift_card_81...`
- **get_reservation_details**: 11 failures (4.8% failure rate)
  - Affected 5 simulation(s)
  - Example args: `{'reservation_id': 'SDZQKO'}`
- **send_certificate**: 8 failures (66.7% failure rate)
  - Affected 8 simulation(s)
  - Example args: `{'user_id': 'noah_muller_9847', 'amount': 50}`
- **calculate**: 4 failures (100.0% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'expression': '2 * ((350 - 122) + (499 - 127))'}`
- **transfer_to_human_agents**: 4 failures (100.0% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'summary': 'User wants to change my upcoming one stop flight from ATL to LAX within reservation XEW...`
- **update_reservation_passengers**: 3 failures (25.0% failure rate)
  - Affected 3 simulation(s)
  - Example args: `{'reservation_id': '3RK2T9', 'passengers': [{'first_name': 'Anya', 'last_name': 'Garcia', 'dob': '19...`

### ⚡ Performance Impact

**High-usage tools with poor performance:**

- **get_reservation_details**: 488 calls, 44.5% success rate
- **search_direct_flight**: 164 calls, 10.4% success rate
- **get_user_details**: 158 calls, 35.4% success rate
- **update_reservation_flights**: 62 calls, 61.3% success rate
- **transfer_to_human_agents**: 56 calls, 0.0% success rate
- **cancel_reservation**: 39 calls, 74.4% success rate
- **update_reservation_baggages**: 16 calls, 56.2% success rate
- **book_reservation**: 9 calls, 55.6% success rate

**Slowest tools by execution time:**

- **get_user_details**: 0.82ms average
- **search_onestop_flight**: 0.68ms average
- **search_direct_flight**: 0.24ms average
- **book_reservation**: 0.22ms average
- **send_certificate**: 0.16ms average

### 💡 Failure Insights

- **Most problematic tool:** search_direct_flight (63 failures)
- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic
- **Average tool success rate:** 56.7%

### 🔍 Failure Type Comparison

Side-by-side comparison of failure types and their characteristics:

| Failure Type | Severity | Total Failures | Affected Tools | Top Failing Tools |
|--------------|----------|----------------|----------------|-------------------|
| **Never Called** | Critical | 163 | 9 | search_direct_flight (60), update_reservation_flights (37), book_reservation (20) |
| **Called But No Match** | High | 14 | 2 | get_reservation_details (11), cancel_reservation (3) |
| **Called With Wrong Args** | Medium | 27 | 4 | update_reservation_flights (9), book_reservation (8), update_reservation_baggages (7) |

**Key Insights:**

- **Never Called (79.9%):** Critical severity - These tools were never executed at all, indicating the agent failed to recognize when to use them.
- **Called But No Match (6.9%):** High severity - Tools were called but didn't produce expected results, suggesting execution logic issues.
- **Called With Wrong Args (13.2%):** Medium severity - Tools were called with incorrect parameters, indicating parameter validation or reasoning issues.

---

## 🎯 Performance Issues Analysis

### Performance Metrics

- **Overall success rate: 65.3%**
- **State-changing actions: 74.6% success rate**
- **Read-only actions: 41.5% success rate**

### 🔍 Failure Patterns

- **18% of operations result in failures**
- **Most failed operations:**
  - search_direct_flight: 79% failure rate
  - update_reservation_flights: 55% failure rate
  - book_reservation: 85% failure rate
- **Action validation failures in 10 different tools**
- **100%% of failures involve validation mismatches**

### 📊 Action Complexity Impact

- **0 state changes: 41.5% success**
- **Tools with state changes: 74.6% success**

---

## 📋 Task & Simulation Analysis

### Simulation Success Patterns

- **Total simulations: 200**
- **Successful simulations: 115**
- **Task success rate: 57.5%**
- **Moderate task completion rate** - Significant improvement needed

### 📈 Trial Performance Patterns

- **Success evaluation method: action_checks**
- **Action-based evaluation** - Success determined by correct action execution

### 🎲 Complexity vs Success Correlation

- **Average tools per simulation: 0.1**
- **Average calls per simulation: 5.8**
- **State-changing operations: 12.0% of all calls**

---

## 💬 Communication vs Tool Call Analysis

### Transfer to Human Analysis

- **Transfer calls: 56 (4.8% of total calls)**
- **Transfer success rate: 0.0%**

### Communication Tool Usage

- **Communication calls: 4 (0.3% of total calls)**
- **Communication success rate: 100.0%**

### 🛑 Task Termination Analysis

- **Execution efficiency: 0.0%** (time spent in actual tool execution)
- **Low efficiency suggests high wait times** or communication delays
- **9 tools used extensively** (10+ calls each)
- **Possible indication of retry patterns** or complex multi-step operations

---

## ⚡ Performance Deep Dive

### 🏆 Performance Tier Analysis

**Excellent Performance (4 tools)** - Success rate ≥95%:
- `search_onestop_flight`: 100.0% success, 100 calls
- `get_flight_status`: 100.0% success, 56 calls
- `update_reservation_passengers`: 100.0% success, 9 calls
- `send_certificate`: 100.0% success, 4 calls

**Poor Performance (9 tools)** - Success rate <75%:
- `get_reservation_details`: 44.5% success, 488 calls
- `search_direct_flight`: 10.4% success, 164 calls
- `get_user_details`: 35.4% success, 158 calls
- `update_reservation_flights`: 61.3% success, 62 calls
- `transfer_to_human_agents`: 0.0% success, 56 calls
- `cancel_reservation`: 74.4% success, 39 calls
- `update_reservation_baggages`: 56.2% success, 16 calls
- `book_reservation`: 55.6% success, 9 calls
- `calculate`: 0.0% success, 1 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`** (Called But No Match, high severity):
  - Success rate: 44.5%
  - Total calls: 488
  - Failed calls: 271
  - Impact score: 0.1
  - Simulations affected: 5
  - State changing: No
- **`search_direct_flight`** (Never Called, critical severity):
  - Success rate: 10.4%
  - Total calls: 164
  - Failed calls: 147
  - Impact score: 7.5
  - Simulations affected: 19
  - State changing: No
- **`get_user_details`**:
  - Success rate: 35.4%
  - Total calls: 158
  - Failed calls: 102
  - Impact score: 0.0
  - Simulations affected: N/A
  - State changing: No
- **`update_reservation_flights`** (Never Called, critical severity):
  - Success rate: 61.3%
  - Total calls: 62
  - Failed calls: 24
  - Impact score: 7.9
  - Simulations affected: 29
  - State changing: Yes
- **`transfer_to_human_agents`** (Never Called, critical severity):
  - Success rate: 0.0%
  - Total calls: 56
  - Failed calls: 56
  - Impact score: 2.0
  - Simulations affected: 4
  - State changing: No
- **`cancel_reservation`** (Never Called, critical severity):
  - Success rate: 74.4%
  - Total calls: 39
  - Failed calls: 10
  - Impact score: 3.2
  - Simulations affected: 15
  - State changing: Yes
- **`update_reservation_baggages`** (Never Called, critical severity):
  - Success rate: 56.2%
  - Total calls: 16
  - Failed calls: 7
  - Impact score: 4.7
  - Simulations affected: 15
  - State changing: Yes
- **`book_reservation`** (Never Called, critical severity):
  - Success rate: 55.6%
  - Total calls: 9
  - Failed calls: 4
  - Impact score: 9.3
  - Simulations affected: 22
  - State changing: Yes

### ⏱️ Execution Time Analysis

- **Average execution time across all tools:** 0.23ms
- **Median execution time:** 0.13ms
- **Slowest tool:** `get_user_details` (0.82ms)
- **Fastest tool:** `transfer_to_human_agents` (0.06ms)

**Performance vs Usage Correlation:**
- High-usage tools (≥10 calls) average success rate: 53.6%
- Low-usage tools (<10 calls) average success rate: 63.9%
- **Usage-performance correlation:** High-usage tools perform 10.3% worse

**State-Changing vs Read-Only Performance:**
- State-changing tools: 74.6% success, 0.0001s avg time (6 tools)
- Read-only tools: 41.5% success, 0.0003s avg time (7 tools)

---

## 🔄 Execution Patterns & Workflow Analysis

### ⏰ Execution Timeline

- **Total execution timespan:** 7286.3 seconds
- **Actual tool execution time:** 0.3121 seconds
- **Execution efficiency:** 0.00% (time spent in tool execution)
- **Average call rate:** 0.16 calls/second
- **Low call rate** may indicate thinking/processing time between calls

### 🔗 Tool Usage Patterns

**Most Common Tool Transitions:**

- **`get_reservation_details` → `get_reservation_details`** (287x): Self-loops indicate repeated calls to same tool
- **`get_user_details` → `get_reservation_details`** (134x): Common workflow pattern
- **`search_direct_flight` → `search_onestop_flight`** (68x): Common workflow pattern
- **`search_direct_flight` → `search_direct_flight`** (66x): Self-loops indicate repeated calls to same tool
- **`search_onestop_flight` → `search_direct_flight`** (45x): Common workflow pattern

**Pattern Analysis:**
- **Most common transition:** 24.7% of all transitions
- **Moderately concentrated** workflow with some preferred patterns
- **Self-loop rate:** 37.3% of transitions are repeated calls to same tool
- **High self-loop rate** may indicate retry logic or iterative processing

### 🧠 Workflow Intelligence

- **Tool diversity:** 13 unique tools used
- **Average calls per tool:** 89.4
- **Usage concentration:** 42.0% of calls go to most-used tool

### 🎯 Success Pattern Analysis

- **Moderate success pattern** (57.5%): Mixed results requiring investigation
- **Failure distribution:** 85 failed simulations out of 200 total
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
