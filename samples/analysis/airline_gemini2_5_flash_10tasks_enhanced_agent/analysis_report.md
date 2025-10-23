# Enhanced Tau2 Execution Analysis Report

**Source File:** `airline_gemini2_5_flash_10tasks_2t_enhanced_agent_enhanced_logs.json`
**Generated:** 2025-10-23 02:59:20
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | 20 |
| **Successful Simulations** | 11 |
| **Task Success Rate** | 55.0% |
| **Total Tool Calls** | 240 |
| **Tool Success Rate** | 70.4% |
| **Tool Error Rate** | 29.6% |
| **State Changing Calls** | 20 |
| **Average Execution Time** | 0.08ms |
| **Success Metric Source** | action_checks |

---

## 🛠️ Tool Performance Analysis

### Performance Overview

| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |
|-----------|-------|--------------|---------------|----------|
| get_reservation_details | 128 | 20.3% | 0.04 | Poor |
| get_user_details | 34 | 23.5% | 0.04 | Poor |
| transfer_to_human_agents | 24 | 100.0% | 0.03 | Excellent |
| search_direct_flight | 16 | 18.8% | 0.19 | Poor |
| book_reservation | 14 | 0.0% | 0.11 | Poor |
| cancel_reservation | 8 | 12.5% | 0.11 | Poor |
| get_flight_status | 8 | 100.0% | 0.04 | Excellent |
| update_reservation_flights | 4 | 0.0% | 0.10 | Poor |
| search_onestop_flight | 2 | 100.0% | 2.86 | Excellent |
| send_certificate | 2 | 0.0% | 0.05 | Poor |

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
| cancel_reservation | Never Called | 5 | 83.3% | 4 | 16.7 | 6 |
| book_reservation | Called With Wrong Args | 2 | 100.0% | 2 | 10.0 | 2 |
| send_certificate | Never Called | 2 | 100.0% | 2 | 10.0 | 2 |
| update_reservation_flights | Called With Wrong Args | 2 | 100.0% | 2 | 10.0 | 2 |
| get_user_details | Never Called | 4 | 33.3% | 4 | 6.7 | 12 |
| search_direct_flight | Never Called | 1 | 25.0% | 1 | 1.2 | 4 |

**Key Failure Metrics:**
- Total failures: **16**
- Affected tools: **6**
- Total action checks performed: **54**
- Total tool calls (see Performance Overview): **240**

**Failure Type Breakdown:**
- **Never Called**: 12 failures (75.0%)
  - Affected tools: send_certificate, get_user_details, cancel_reservation, search_direct_flight, update_reservation_flights
- **Called With Wrong Args**: 3 failures (18.8%)
  - Affected tools: update_reservation_flights, book_reservation
- **Called But No Match**: 1 failures (6.2%)
  - Affected tools: cancel_reservation

---

## 📊 Action Sequence Accuracy

This section compares actual tool call sequences against expected action sequences from ground truth task definitions.

### Overview Metrics

| Metric | Value |
|--------|-------|
| **Precision** | 0.00% |
| **Recall** | 0.00% |
| **F1 Score** | 0.00% |
| **Total Tasks Analyzed** | 18 |
| **Matched Actions** | 0/54 |

### Task Distribution

- ✅ **Success + Ordered:** 9 tasks (correct sequence, task succeeded)
- ⚠️  **Success + Unordered:** 0 tasks (wrong order, but task succeeded)
- ❌ **Failed + Ordered:** 9 tasks (correct sequence, but task failed)
- 🔴 **Failed + Unordered:** 0 tasks (wrong sequence, task failed)

### Action-Level Metrics

- **Expected actions:** 54
- **Actual actions executed:** 0
- **Correctly matched:** 0
- **Missing (omitted):** 54
- **Extra (unexpected):** 0
- **Argument mismatches:** 0

### Per-Tool Sequence Accuracy

| Tool | Expected | ✅ Matched | ❌ Missing | 🔧 Arg Err | ⚠️ Extra | Precision | Recall |
|------|----------|-----------|-----------|-----------|---------|-----------|--------|
| get_reservation_details | 26 | 0 | 26 | 0 | 0 | 0.0% | 0.0% |
| get_user_details | 12 | 0 | 12 | 0 | 0 | 0.0% | 0.0% |
| cancel_reservation | 6 | 0 | 6 | 0 | 0 | 0.0% | 0.0% |
| search_direct_flight | 4 | 0 | 4 | 0 | 0 | 0.0% | 0.0% |
| send_certificate | 2 | 0 | 2 | 0 | 0 | 0.0% | 0.0% |
| update_reservation_flights | 2 | 0 | 2 | 0 | 0 | 0.0% | 0.0% |
| book_reservation | 2 | 0 | 2 | 0 | 0 | 0.0% | 0.0% |

---

## 🔄 State Change Analysis

### State-Changing Tools (4 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| cancel_reservation | 8 | 12.5% | 0.11 |
| book_reservation | 6 | 0.0% | 0.16 |
| update_reservation_flights | 4 | 0.0% | 0.10 |
| send_certificate | 2 | 0.0% | 0.05 |

### Read-Only Tools (7 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 128 | 20.3% | 0.04 |
| get_user_details | 34 | 23.5% | 0.04 |
| transfer_to_human_agents | 24 | 100.0% | 0.03 |
| search_direct_flight | 16 | 18.8% | 0.19 |
| book_reservation | 8 | 0.0% | 0.08 |
| get_flight_status | 8 | 100.0% | 0.04 |
| search_onestop_flight | 2 | 100.0% | 2.86 |

---

## 🔗 Tool Sequence Patterns

### Most Common Tool Transitions

| From Tool | To Tool | Count |
|-----------|---------|-------|
| get_reservation_details | get_reservation_details | 82 |
| get_user_details | get_reservation_details | 30 |
| get_reservation_details | transfer_to_human_agents | 20 |
| transfer_to_human_agents | get_user_details | 12 |
| transfer_to_human_agents | get_reservation_details | 9 |
| get_reservation_details | get_user_details | 9 |
| get_reservation_details | search_direct_flight | 9 |
| book_reservation | book_reservation | 8 |
| get_flight_status | get_flight_status | 6 |
| search_direct_flight | book_reservation | 6 |

---

## 🔍 Key Insights

- **3** out of 10 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 128 calls
- Overall system reliability: **70.4%**
- **7** tools showing poor performance require attention
- **6.7%** error rate across all tool executions
- **Highest impact:** cancel_reservation (Never Called) - impact score 16.7, affecting 4 simulations
- **Most frequent failure:** cancel_reservation (Never Called) with 5 failures
- **Failure type breakdown:** 75% Never Called (critical), 19% Called With Wrong Args (medium), 6% Called But No Match (high)
- Tool distribution: **4** state-changing, **7** read-only
- State-changing tools underperform read-only tools (3.1% vs 51.8%)
- High self-loop rate (42.7%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (82 times)

---

## 💡 Recommendations

- **High Impact Pattern**: High-usage poor performers identified: get_reservation_details, get_user_details, search_direct_flight, book_reservation
- **Performance Pattern**: 7 tools categorized as poor performers based on execution metrics
- **High-Impact Failures:** cancel_reservation (Never Called, critical severity): impact 16.7, 4 simulations, book_reservation (Called With Wrong Args, medium severity): impact 10.0, 2 simulations, send_certificate (Never Called, critical severity): impact 10.0, 2 simulations, update_reservation_flights (Called With Wrong Args, medium severity): impact 10.0, 2 simulations, get_user_details (Never Called, critical severity): impact 6.7, 4 simulations
- **Critical: Tools Never Executed:** 5 tools with 'never_called' failures (critical severity): send_certificate, get_user_details, cancel_reservation, search_direct_flight, update_reservation_flights
- **High Failure Rate:** Tools with >50% failure rate: cancel_reservation, book_reservation, send_certificate, update_reservation_flights

---

## 🎯 Detailed Failure Analysis

### 📊 Failure Statistics

- **Total failures:** 16
- **Overall error rate:** 6.7%
- **Affected tools:** 6
- **Error categories:** 1

### 🚨 Root Cause Analysis

#### Action Check Failures

**6 tools** failed action validation checks:

- **cancel_reservation**: 5 failures (83.3% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B'}`
- **get_user_details**: 4 failures (33.3% failure rate)
  - Affected 4 simulation(s)
  - Example args: `{'user_id': 'anya_garcia_5901'}`
- **book_reservation**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'sophia_silva_7557', 'origin': 'ORD', 'destination': 'PHL', 'flight_type': 'one_way', 'c...`
- **send_certificate**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'noah_muller_9847', 'amount': 50}`
- **update_reservation_flights**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT005', 'date': '20...`
- **search_direct_flight**: 1 failures (25.0% failure rate)
  - Affected 1 simulation(s)
  - Example args: `{'origin': 'JFK', 'destination': 'MCO', 'date': '2024-05-22'}`

### ⚡ Performance Impact

**High-usage tools with poor performance:**

- **get_reservation_details**: 128 calls, 20.3% success rate
- **get_user_details**: 34 calls, 23.5% success rate
- **search_direct_flight**: 16 calls, 18.8% success rate
- **book_reservation**: 14 calls, 0.0% success rate
- **cancel_reservation**: 8 calls, 12.5% success rate

**Slowest tools by execution time:**

- **search_onestop_flight**: 2.86ms average
- **search_direct_flight**: 0.19ms average
- **book_reservation**: 0.11ms average
- **cancel_reservation**: 0.11ms average
- **update_reservation_flights**: 0.10ms average

### 💡 Failure Insights

- **Most problematic tool:** cancel_reservation (5 failures)
- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic
- **Average tool success rate:** 37.5%

### 🔍 Failure Type Comparison

Side-by-side comparison of failure types and their characteristics:

| Failure Type | Severity | Total Failures | Affected Tools | Top Failing Tools |
|--------------|----------|----------------|----------------|-------------------|
| **Never Called** | Critical | 12 | 5 | get_user_details (4), cancel_reservation (4), send_certificate (2) |
| **Called But No Match** | High | 1 | 1 | cancel_reservation (1) |
| **Called With Wrong Args** | Medium | 3 | 2 | book_reservation (2), update_reservation_flights (1) |

**Key Insights:**

- **Never Called (75.0%):** Critical severity - These tools were never executed at all, indicating the agent failed to recognize when to use them.
- **Called But No Match (6.2%):** High severity - Tools were called but didn't produce expected results, suggesting execution logic issues.
- **Called With Wrong Args (18.8%):** Medium severity - Tools were called with incorrect parameters, indicating parameter validation or reasoning issues.

---

## 🎯 Performance Issues Analysis

### Performance Metrics

- **Overall success rate: 70.4%**
- **State-changing actions: 3.1% success rate**
- **Read-only actions: 60.4% success rate**
- **57%pp performance drop when actions are required** (60.4% → 3.1% success)

### 🔍 Failure Patterns

- **7% of operations result in failures**
- **Most failed operations:**
  - cancel_reservation: 83% failure rate
  - get_user_details: 33% failure rate
  - book_reservation: 100% failure rate
- **Action validation failures in 6 different tools**
- **100%% of failures involve validation mismatches**

### 📊 Action Complexity Impact

- **0 state changes: 60.4% success**
- **Tools with state changes: 3.1% success**
- **Clear correlation between complexity and failure**

---

## 📋 Task & Simulation Analysis

### Simulation Success Patterns

- **Total simulations: 20**
- **Successful simulations: 11**
- **Task success rate: 55.0%**
- **Moderate task completion rate** - Significant improvement needed

### 📈 Trial Performance Patterns

- **Success evaluation method: action_checks**
- **Action-based evaluation** - Success determined by correct action execution

### 🎲 Complexity vs Success Correlation

- **Average tools per simulation: 0.5**
- **Average calls per simulation: 12.0**
- **State-changing operations: 8.3% of all calls**

---

## 💬 Communication vs Tool Call Analysis

### Transfer to Human Analysis

- **Transfer calls: 24 (10.0% of total calls)**
- **Transfer success rate: 100.0%**

### Communication Tool Usage

- **Communication calls: 2 (0.8% of total calls)**
- **Communication success rate: 0.0%**

### 🛑 Task Termination Analysis

- **Execution efficiency: 0.0%** (time spent in actual tool execution)
- **Low efficiency suggests high wait times** or communication delays
- **5 tools used extensively** (10+ calls each)
- **Possible indication of retry patterns** or complex multi-step operations

---

## ⚡ Performance Deep Dive

### 🏆 Performance Tier Analysis

**Excellent Performance (3 tools)** - Success rate ≥95%:
- `transfer_to_human_agents`: 100.0% success, 24 calls
- `get_flight_status`: 100.0% success, 8 calls
- `search_onestop_flight`: 100.0% success, 2 calls

**Poor Performance (7 tools)** - Success rate <75%:
- `get_reservation_details`: 20.3% success, 128 calls
- `get_user_details`: 23.5% success, 34 calls
- `search_direct_flight`: 18.8% success, 16 calls
- `book_reservation`: 0.0% success, 14 calls
- `cancel_reservation`: 12.5% success, 8 calls
- `update_reservation_flights`: 0.0% success, 4 calls
- `send_certificate`: 0.0% success, 2 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`**:
  - Success rate: 20.3%
  - Total calls: 128
  - Failed calls: 102
  - Impact score: 0.0
  - Simulations affected: N/A
  - State changing: No
- **`get_user_details`** (Never Called, critical severity):
  - Success rate: 23.5%
  - Total calls: 34
  - Failed calls: 26
  - Impact score: 6.7
  - Simulations affected: 4
  - State changing: No
- **`search_direct_flight`** (Never Called, critical severity):
  - Success rate: 18.8%
  - Total calls: 16
  - Failed calls: 13
  - Impact score: 1.2
  - Simulations affected: 1
  - State changing: No
- **`book_reservation`** (Called With Wrong Args, medium severity):
  - Success rate: 0.0%
  - Total calls: 14
  - Failed calls: 14
  - Impact score: 10.0
  - Simulations affected: 2
  - State changing: Yes
- **`cancel_reservation`** (Never Called, critical severity):
  - Success rate: 12.5%
  - Total calls: 8
  - Failed calls: 7
  - Impact score: 16.7
  - Simulations affected: 4
  - State changing: Yes

### ⏱️ Execution Time Analysis

- **Average execution time across all tools:** 0.36ms
- **Median execution time:** 0.08ms
- **Slowest tool:** `search_onestop_flight` (2.86ms)
- **Fastest tool:** `transfer_to_human_agents` (0.03ms)

**Performance vs Usage Correlation:**
- High-usage tools (≥10 calls) average success rate: 32.5%
- Low-usage tools (<10 calls) average success rate: 42.5%

**State-Changing vs Read-Only Performance:**
- State-changing tools: 3.1% success, 0.0001s avg time (4 tools)
- Read-only tools: 60.4% success, 0.0005s avg time (6 tools)

---

## 🔄 Execution Patterns & Workflow Analysis

### ⏰ Execution Timeline

- **Total execution timespan:** 214.5 seconds
- **Actual tool execution time:** 0.0189 seconds
- **Execution efficiency:** 0.01% (time spent in tool execution)
- **Average call rate:** 1.12 calls/second

### 🔗 Tool Usage Patterns

**Most Common Tool Transitions:**

- **`get_reservation_details` → `get_reservation_details`** (82x): Self-loops indicate repeated calls to same tool
- **`get_user_details` → `get_reservation_details`** (30x): Common workflow pattern
- **`get_reservation_details` → `transfer_to_human_agents`** (20x): Common workflow pattern
- **`transfer_to_human_agents` → `get_user_details`** (12x): Common workflow pattern
- **`transfer_to_human_agents` → `get_reservation_details`** (9x): Common workflow pattern

**Pattern Analysis:**
- **Most common transition:** 34.3% of all transitions
- **Moderately concentrated** workflow with some preferred patterns
- **Self-loop rate:** 42.7% of transitions are repeated calls to same tool
- **High self-loop rate** may indicate retry logic or iterative processing

### 🧠 Workflow Intelligence

- **Tool diversity:** 10 unique tools used
- **Average calls per tool:** 24.0
- **Usage concentration:** 53.3% of calls go to most-used tool

### 🎯 Success Pattern Analysis

- **Moderate success pattern** (55.0%): Mixed results requiring investigation
- **Failure distribution:** 9 failed simulations out of 20 total
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
