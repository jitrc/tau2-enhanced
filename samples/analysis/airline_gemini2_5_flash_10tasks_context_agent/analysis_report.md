# Enhanced Tau2 Execution Analysis Report

**Source File:** `airline_gemini2_5_flash_10tasks_2t_context_agent_enhanced_logs.json`
**Generated:** 2025-10-23 03:17:41
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | 20 |
| **Successful Simulations** | 12 |
| **Task Success Rate** | 60.0% |
| **Total Tool Calls** | 220 |
| **Tool Success Rate** | 59.3% |
| **Tool Error Rate** | 40.7% |
| **State Changing Calls** | 20 |
| **Average Execution Time** | 0.06ms |
| **Success Metric Source** | action_checks |

---

## 🛠️ Tool Performance Analysis

### Performance Overview

| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |
|-----------|-------|--------------|---------------|----------|
| get_reservation_details | 120 | 15.0% | 0.04 | Poor |
| get_user_details | 36 | 25.0% | 0.12 | Poor |
| transfer_to_human_agents | 20 | 100.0% | 0.03 | Excellent |
| book_reservation | 12 | 0.0% | 0.10 | Poor |
| cancel_reservation | 12 | 25.0% | 0.10 | Poor |
| get_flight_status | 8 | 100.0% | 0.04 | Excellent |
| search_direct_flight | 8 | 25.0% | 0.20 | Poor |
| send_certificate | 2 | 0.0% | 0.06 | Poor |
| update_reservation_flights | 2 | 0.0% | 0.11 | Poor |

### Performance Distribution

- **Poor**: 7 tools
- **Excellent**: 2 tools

---

## 🔥 Failure Analysis

### Failure Overview

**Note:** Failure rates below are calculated against **action-checked calls only**, not total calls. See Performance Overview for overall success rates against all calls.

**Impact Score Formula:** `failure_rate × simulations_affected / total_simulations × 100`

| Tool Name | Failure Type | Count | Failure Rate | Simulations | Impact Score | Checked Calls |
|-----------|--------------|-------|--------------|-------------|--------------|---------------|
| book_reservation | Called With Wrong Args | 2 | 100.0% | 2 | 10.0 | 2 |
| send_certificate | Never Called | 2 | 100.0% | 2 | 10.0 | 2 |
| update_reservation_flights | Never Called | 2 | 100.0% | 2 | 10.0 | 2 |
| cancel_reservation | Never Called | 3 | 50.0% | 2 | 5.0 | 6 |
| search_direct_flight | Never Called | 2 | 50.0% | 2 | 5.0 | 4 |
| get_reservation_details | Called But No Match | 8 | 30.8% | 3 | 4.6 | 26 |
| get_user_details | Never Called | 3 | 25.0% | 3 | 3.8 | 12 |

**Key Failure Metrics:**
- Total failures: **22**
- Affected tools: **7**
- Total action checks performed: **54**
- Total tool calls (see Performance Overview): **220**

**Failure Type Breakdown:**
- **Never Called**: 12 failures (54.5%)
  - Affected tools: send_certificate, get_user_details, update_reservation_flights, cancel_reservation, search_direct_flight
- **Called But No Match**: 8 failures (36.4%)
  - Affected tools: get_reservation_details
- **Called With Wrong Args**: 2 failures (9.1%)
  - Affected tools: book_reservation

---

## 📊 Action Sequence Accuracy

This section compares actual tool call sequences against expected action sequences from ground truth task definitions.

### Overview Metrics

| Metric | Value |
|--------|-------|
| **Precision** | 3.12% |
| **Recall** | 25.93% |
| **F1 Score** | 5.58% |
| **Total Tasks Analyzed** | 18 |
| **Matched Actions** | 14/54 |

### Task Distribution

- ✅ **Success + Ordered:** 10 tasks (correct sequence, task succeeded)
- ⚠️  **Success + Unordered:** 0 tasks (wrong order, but task succeeded)
- ❌ **Failed + Ordered:** 8 tasks (correct sequence, but task failed)
- 🔴 **Failed + Unordered:** 0 tasks (wrong sequence, task failed)

### Action-Level Metrics

- **Expected actions:** 54
- **Actual actions executed:** 448
- **Correctly matched:** 14
- **Missing (omitted):** 7
- **Extra (unexpected):** 401
- **Argument mismatches:** 33

### Per-Tool Sequence Accuracy

| Tool | Expected | ✅ Matched | ❌ Missing | 🔧 Arg Err | ⚠️ Extra | Precision | Recall |
|------|----------|-----------|-----------|-----------|---------|-----------|--------|
| get_reservation_details | 26 | 2 | 0 | 24 | 214 | 0.9% | 7.7% |
| get_user_details | 12 | 7 | 2 | 3 | 60 | 10.4% | 58.3% |
| cancel_reservation | 6 | 3 | 0 | 3 | 18 | 14.3% | 50.0% |
| search_direct_flight | 4 | 2 | 1 | 1 | 5 | 28.6% | 50.0% |
| send_certificate | 2 | 0 | 2 | 0 | 4 | 0.0% | 0.0% |
| update_reservation_flights | 2 | 0 | 2 | 0 | 3 | 0.0% | 0.0% |
| book_reservation | 2 | 0 | 0 | 2 | 9 | 0.0% | 0.0% |
| transfer_to_human_agents | 0 | 0 | 0 | 0 | 44 | 0.0% | 0.0% |
| None | 0 | 0 | 0 | 0 | 32 | 0.0% | 0.0% |
| get_flight_status | 0 | 0 | 0 | 0 | 12 | 0.0% | 0.0% |

---

## 🔄 State Change Analysis

### State-Changing Tools (4 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| cancel_reservation | 12 | 25.0% | 0.10 |
| book_reservation | 4 | 0.0% | 0.16 |
| send_certificate | 2 | 0.0% | 0.06 |
| update_reservation_flights | 2 | 0.0% | 0.11 |

### Read-Only Tools (6 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 120 | 15.0% | 0.04 |
| get_user_details | 36 | 25.0% | 0.12 |
| transfer_to_human_agents | 20 | 100.0% | 0.03 |
| book_reservation | 8 | 0.0% | 0.08 |
| get_flight_status | 8 | 100.0% | 0.04 |
| search_direct_flight | 8 | 25.0% | 0.20 |

---

## 🔗 Tool Sequence Patterns

### Most Common Tool Transitions

| From Tool | To Tool | Count |
|-----------|---------|-------|
| get_reservation_details | get_reservation_details | 76 |
| get_user_details | get_reservation_details | 31 |
| get_reservation_details | transfer_to_human_agents | 16 |
| get_reservation_details | get_user_details | 12 |
| transfer_to_human_agents | get_user_details | 10 |
| transfer_to_human_agents | get_reservation_details | 8 |
| get_reservation_details | search_direct_flight | 6 |
| book_reservation | book_reservation | 6 |
| search_direct_flight | book_reservation | 6 |
| cancel_reservation | cancel_reservation | 5 |

---

## 🔍 Key Insights

- **2** out of 9 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 120 calls
- Overall system reliability: **59.3%**
- **7** tools showing poor performance require attention
- **10.0%** error rate across all tool executions
- **Highest impact:** book_reservation (Called With Wrong Args) - impact score 10.0, affecting 2 simulations
- **Most frequent failure:** get_reservation_details (Called But No Match) with 8 failures
- **Failure type breakdown:** 55% Never Called (critical), 36% Called But No Match (high), 9% Called With Wrong Args (medium)
- Tool distribution: **4** state-changing, **6** read-only
- State-changing tools underperform read-only tools (6.2% vs 44.2%)
- High self-loop rate (42.9%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (76 times)

---

## 💡 Recommendations

- **High Impact Pattern**: High-usage poor performers identified: get_reservation_details, get_user_details, book_reservation, cancel_reservation
- **Performance Pattern**: 7 tools categorized as poor performers based on execution metrics
- **High-Impact Failures:** book_reservation (Called With Wrong Args, medium severity): impact 10.0, 2 simulations, send_certificate (Never Called, critical severity): impact 10.0, 2 simulations, update_reservation_flights (Never Called, critical severity): impact 10.0, 2 simulations
- **Critical: Tools Never Executed:** 5 tools with 'never_called' failures (critical severity): send_certificate, get_user_details, update_reservation_flights, cancel_reservation, search_direct_flight
- **High Failure Rate:** Tools with >50% failure rate: book_reservation, send_certificate, update_reservation_flights

---

## 🎯 Detailed Failure Analysis

### 📊 Failure Statistics

- **Total failures:** 22
- **Overall error rate:** 10.0%
- **Affected tools:** 7
- **Error categories:** 1

### 🚨 Root Cause Analysis

#### Action Check Failures

**7 tools** failed action validation checks:

- **get_reservation_details**: 8 failures (30.8% failure rate)
  - Affected 3 simulation(s)
  - Example args: `{'reservation_id': 'KC18K6'}`
- **cancel_reservation**: 3 failures (50.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'reservation_id': 'NQNU5R'}`
- **get_user_details**: 3 failures (25.0% failure rate)
  - Affected 3 simulation(s)
  - Example args: `{'user_id': 'mei_brown_7075'}`
- **book_reservation**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'sophia_silva_7557', 'origin': 'ORD', 'destination': 'PHL', 'flight_type': 'one_way', 'c...`
- **search_direct_flight**: 2 failures (50.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'origin': 'JFK', 'destination': 'MCO', 'date': '2024-05-22'}`
- **send_certificate**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'noah_muller_9847', 'amount': 50}`
- **update_reservation_flights**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT005', 'date': '20...`

### ⚡ Performance Impact

**High-usage tools with poor performance:**

- **get_reservation_details**: 120 calls, 15.0% success rate
- **get_user_details**: 36 calls, 25.0% success rate
- **book_reservation**: 12 calls, 0.0% success rate
- **cancel_reservation**: 12 calls, 25.0% success rate
- **search_direct_flight**: 8 calls, 25.0% success rate

**Slowest tools by execution time:**

- **search_direct_flight**: 0.20ms average
- **get_user_details**: 0.12ms average
- **update_reservation_flights**: 0.11ms average
- **cancel_reservation**: 0.10ms average
- **book_reservation**: 0.10ms average

### 💡 Failure Insights

- **Most problematic tool:** get_reservation_details (8 failures)
- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic
- **Average tool success rate:** 32.2%

### 🔍 Failure Type Comparison

Side-by-side comparison of failure types and their characteristics:

| Failure Type | Severity | Total Failures | Affected Tools | Top Failing Tools |
|--------------|----------|----------------|----------------|-------------------|
| **Never Called** | Critical | 12 | 5 | get_user_details (3), cancel_reservation (3), send_certificate (2) |
| **Called But No Match** | High | 8 | 1 | get_reservation_details (8) |
| **Called With Wrong Args** | Medium | 2 | 1 | book_reservation (2) |

**Key Insights:**

- **Never Called (54.5%):** Critical severity - These tools were never executed at all, indicating the agent failed to recognize when to use them.
- **Called But No Match (36.4%):** High severity - Tools were called but didn't produce expected results, suggesting execution logic issues.
- **Called With Wrong Args (9.1%):** Medium severity - Tools were called with incorrect parameters, indicating parameter validation or reasoning issues.

---

## 🎯 Performance Issues Analysis

### Performance Metrics

- **Overall success rate: 59.3%**
- **State-changing actions: 6.2% success rate**
- **Read-only actions: 53.0% success rate**
- **47%pp performance drop when actions are required** (53.0% → 6.2% success)

### 🔍 Failure Patterns

- **10% of operations result in failures**
- **Most failed operations:**
  - get_reservation_details: 31% failure rate
  - cancel_reservation: 50% failure rate
  - get_user_details: 25% failure rate
- **Action validation failures in 7 different tools**
- **100%% of failures involve validation mismatches**

### 📊 Action Complexity Impact

- **0 state changes: 53.0% success**
- **Tools with state changes: 6.2% success**
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
- **Average calls per simulation: 11.0**
- **State-changing operations: 9.1% of all calls**

---

## 💬 Communication vs Tool Call Analysis

### Transfer to Human Analysis

- **Transfer calls: 20 (9.1% of total calls)**
- **Transfer success rate: 100.0%**

### Communication Tool Usage

- **Communication calls: 2 (0.9% of total calls)**
- **Communication success rate: 0.0%**

### 🛑 Task Termination Analysis

- **Execution efficiency: 0.0%** (time spent in actual tool execution)
- **Low efficiency suggests high wait times** or communication delays
- **5 tools used extensively** (10+ calls each)
- **Possible indication of retry patterns** or complex multi-step operations

---

## ⚡ Performance Deep Dive

### 🏆 Performance Tier Analysis

**Excellent Performance (2 tools)** - Success rate ≥95%:
- `transfer_to_human_agents`: 100.0% success, 20 calls
- `get_flight_status`: 100.0% success, 8 calls

**Poor Performance (7 tools)** - Success rate <75%:
- `get_reservation_details`: 15.0% success, 120 calls
- `get_user_details`: 25.0% success, 36 calls
- `book_reservation`: 0.0% success, 12 calls
- `cancel_reservation`: 25.0% success, 12 calls
- `search_direct_flight`: 25.0% success, 8 calls
- `send_certificate`: 0.0% success, 2 calls
- `update_reservation_flights`: 0.0% success, 2 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`** (Called But No Match, high severity):
  - Success rate: 15.0%
  - Total calls: 120
  - Failed calls: 102
  - Impact score: 4.6
  - Simulations affected: 3
  - State changing: No
- **`get_user_details`** (Never Called, critical severity):
  - Success rate: 25.0%
  - Total calls: 36
  - Failed calls: 27
  - Impact score: 3.8
  - Simulations affected: 3
  - State changing: No
- **`book_reservation`** (Called With Wrong Args, medium severity):
  - Success rate: 0.0%
  - Total calls: 12
  - Failed calls: 12
  - Impact score: 10.0
  - Simulations affected: 2
  - State changing: Yes
- **`cancel_reservation`** (Never Called, critical severity):
  - Success rate: 25.0%
  - Total calls: 12
  - Failed calls: 9
  - Impact score: 5.0
  - Simulations affected: 2
  - State changing: Yes
- **`search_direct_flight`** (Never Called, critical severity):
  - Success rate: 25.0%
  - Total calls: 8
  - Failed calls: 6
  - Impact score: 5.0
  - Simulations affected: 2
  - State changing: No

### ⏱️ Execution Time Analysis

- **Average execution time across all tools:** 0.09ms
- **Median execution time:** 0.10ms
- **Slowest tool:** `search_direct_flight` (0.20ms)
- **Fastest tool:** `transfer_to_human_agents` (0.03ms)

**Performance vs Usage Correlation:**
- High-usage tools (≥10 calls) average success rate: 33.0%
- Low-usage tools (<10 calls) average success rate: 31.2%

**State-Changing vs Read-Only Performance:**
- State-changing tools: 6.2% success, 0.0001s avg time (4 tools)
- Read-only tools: 53.0% success, 0.0001s avg time (5 tools)

---

## 🔄 Execution Patterns & Workflow Analysis

### ⏰ Execution Timeline

- **Total execution timespan:** 211.5 seconds
- **Actual tool execution time:** 0.0139 seconds
- **Execution efficiency:** 0.01% (time spent in tool execution)
- **Average call rate:** 1.04 calls/second

### 🔗 Tool Usage Patterns

**Most Common Tool Transitions:**

- **`get_reservation_details` → `get_reservation_details`** (76x): Self-loops indicate repeated calls to same tool
- **`get_user_details` → `get_reservation_details`** (31x): Common workflow pattern
- **`get_reservation_details` → `transfer_to_human_agents`** (16x): Common workflow pattern
- **`get_reservation_details` → `get_user_details`** (12x): Common workflow pattern
- **`transfer_to_human_agents` → `get_user_details`** (10x): Common workflow pattern

**Pattern Analysis:**
- **Most common transition:** 34.7% of all transitions
- **Moderately concentrated** workflow with some preferred patterns
- **Self-loop rate:** 42.9% of transitions are repeated calls to same tool
- **High self-loop rate** may indicate retry logic or iterative processing

### 🧠 Workflow Intelligence

- **Tool diversity:** 9 unique tools used
- **Average calls per tool:** 24.4
- **Usage concentration:** 54.5% of calls go to most-used tool

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
