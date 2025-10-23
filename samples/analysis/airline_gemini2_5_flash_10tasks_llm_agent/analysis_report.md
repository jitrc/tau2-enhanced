# Enhanced Tau2 Execution Analysis Report

**Source File:** `airline_gemini2_5_flash_10tasks_2t_enhanced_logs.json`
**Generated:** 2025-10-22 23:57:30
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | 20 |
| **Successful Simulations** | 12 |
| **Task Success Rate** | 60.0% |
| **Total Tool Calls** | 212 |
| **Tool Success Rate** | 57.4% |
| **Tool Error Rate** | 42.6% |
| **State Changing Calls** | 20 |
| **Average Execution Time** | 0.27ms |
| **Success Metric Source** | action_checks |

---

## 🛠️ Tool Performance Analysis

### Performance Overview

| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |
|-----------|-------|--------------|---------------|----------|
| get_reservation_details | 104 | 14.4% | 0.04 | Poor |
| get_user_details | 34 | 29.4% | 0.04 | Poor |
| transfer_to_human_agents | 26 | 100.0% | 1.80 | Excellent |
| book_reservation | 12 | 8.3% | 0.13 | Poor |
| cancel_reservation | 10 | 20.0% | 0.10 | Poor |
| get_flight_status | 10 | 100.0% | 0.04 | Excellent |
| search_direct_flight | 10 | 30.0% | 0.18 | Poor |
| calculate | 2 | 100.0% | 0.08 | Excellent |
| send_certificate | 2 | 0.0% | 0.06 | Poor |
| update_reservation_flights | 2 | 0.0% | 0.11 | Poor |

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
| get_reservation_details | Never Called | 11 | 42.3% | 5 | 10.6 | 26 |
| cancel_reservation | Never Called | 4 | 66.7% | 3 | 10.0 | 6 |
| send_certificate | Never Called | 2 | 100.0% | 2 | 10.0 | 2 |
| update_reservation_flights | Never Called | 2 | 100.0% | 2 | 10.0 | 2 |
| book_reservation | Called With Wrong Args | 1 | 50.0% | 1 | 2.5 | 2 |
| get_user_details | Never Called | 2 | 16.7% | 2 | 1.7 | 12 |
| search_direct_flight | Never Called | 1 | 25.0% | 1 | 1.2 | 4 |

**Key Failure Metrics:**
- Total failures: **23**
- Affected tools: **7**
- Total action checks performed: **54**
- Total tool calls (see Performance Overview): **212**

**Failure Type Breakdown:**
- **Never Called**: 18 failures (78.3%)
  - Affected tools: get_reservation_details, send_certificate, get_user_details, update_reservation_flights, cancel_reservation, ... (1 more)
- **Called But No Match**: 4 failures (17.4%)
  - Affected tools: get_reservation_details
- **Called With Wrong Args**: 1 failures (4.3%)
  - Affected tools: book_reservation

---

## 🔄 State Change Analysis

### State-Changing Tools (4 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| cancel_reservation | 10 | 20.0% | 0.10 |
| book_reservation | 6 | 16.7% | 0.18 |
| send_certificate | 2 | 0.0% | 0.06 |
| update_reservation_flights | 2 | 0.0% | 0.11 |

### Read-Only Tools (7 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 104 | 14.4% | 0.04 |
| get_user_details | 34 | 29.4% | 0.04 |
| transfer_to_human_agents | 26 | 100.0% | 1.80 |
| get_flight_status | 10 | 100.0% | 0.04 |
| search_direct_flight | 10 | 30.0% | 0.18 |
| book_reservation | 6 | 16.7% | 0.08 |
| calculate | 2 | 100.0% | 0.08 |

---

## 🔗 Tool Sequence Patterns

### Most Common Tool Transitions

| From Tool | To Tool | Count |
|-----------|---------|-------|
| get_reservation_details | get_reservation_details | 59 |
| get_user_details | get_reservation_details | 26 |
| get_reservation_details | transfer_to_human_agents | 16 |
| transfer_to_human_agents | get_user_details | 15 |
| transfer_to_human_agents | get_reservation_details | 9 |
| get_reservation_details | get_user_details | 8 |
| get_reservation_details | search_direct_flight | 8 |
| book_reservation | book_reservation | 6 |
| get_reservation_details | get_flight_status | 6 |
| get_user_details | transfer_to_human_agents | 6 |

---

## 🔍 Key Insights

- **3** out of 10 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 104 calls
- Overall system reliability: **57.4%**
- **7** tools showing poor performance require attention
- **10.8%** error rate across all tool executions
- **Highest impact:** get_reservation_details (Never Called) - impact score 10.6, affecting 5 simulations
- **Most frequent failure:** get_reservation_details (Never Called) with 11 failures
- **Failure type breakdown:** 78% Never Called (critical), 17% Called But No Match (high), 4% Called With Wrong Args (medium)
- Tool distribution: **4** state-changing, **7** read-only
- State-changing tools underperform read-only tools (9.2% vs 55.8%)
- High self-loop rate (35.5%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (59 times)

---

## 💡 Recommendations

- **High Impact Pattern**: High-usage poor performers identified: get_reservation_details, get_user_details, book_reservation, cancel_reservation, search_direct_flight
- **Performance Pattern**: 7 tools categorized as poor performers based on execution metrics
- **High-Impact Failures:** get_reservation_details (Never Called, critical severity): impact 10.6, 5 simulations, cancel_reservation (Never Called, critical severity): impact 10.0, 3 simulations, send_certificate (Never Called, critical severity): impact 10.0, 2 simulations, update_reservation_flights (Never Called, critical severity): impact 10.0, 2 simulations
- **Critical: Tools Never Executed:** 6 tools with 'never_called' failures (critical severity): get_reservation_details, send_certificate, get_user_details, update_reservation_flights, cancel_reservation
- **High Failure Rate:** Tools with >50% failure rate: cancel_reservation, send_certificate, update_reservation_flights

---

## 🎯 Detailed Failure Analysis

### 📊 Failure Statistics

- **Total failures:** 23
- **Overall error rate:** 10.8%
- **Affected tools:** 7
- **Error categories:** 1

### 🚨 Root Cause Analysis

#### Action Check Failures

**7 tools** failed action validation checks:

- **get_reservation_details**: 11 failures (42.3% failure rate)
  - Affected 5 simulation(s)
  - Example args: `{'reservation_id': 'SDZQKO'}`
- **cancel_reservation**: 4 failures (66.7% failure rate)
  - Affected 3 simulation(s)
  - Example args: `{'reservation_id': 'NQNU5R'}`
- **get_user_details**: 2 failures (16.7% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'mei_brown_7075'}`
- **send_certificate**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'user_id': 'noah_muller_9847', 'amount': 50}`
- **update_reservation_flights**: 2 failures (100.0% failure rate)
  - Affected 2 simulation(s)
  - Example args: `{'reservation_id': 'XEHM4B', 'cabin': 'economy', 'flights': [{'flight_number': 'HAT005', 'date': '20...`
- **book_reservation**: 1 failures (50.0% failure rate)
  - Affected 1 simulation(s)
  - Example args: `{'user_id': 'sophia_silva_7557', 'origin': 'ORD', 'destination': 'PHL', 'flight_type': 'one_way', 'c...`
- **search_direct_flight**: 1 failures (25.0% failure rate)
  - Affected 1 simulation(s)
  - Example args: `{'origin': 'JFK', 'destination': 'MCO', 'date': '2024-05-22'}`

### ⚡ Performance Impact

**High-usage tools with poor performance:**

- **get_reservation_details**: 104 calls, 14.4% success rate
- **get_user_details**: 34 calls, 29.4% success rate
- **book_reservation**: 12 calls, 8.3% success rate
- **cancel_reservation**: 10 calls, 20.0% success rate
- **search_direct_flight**: 10 calls, 30.0% success rate

**Slowest tools by execution time:**

- **transfer_to_human_agents**: 1.80ms average
- **search_direct_flight**: 0.18ms average
- **book_reservation**: 0.13ms average
- **update_reservation_flights**: 0.11ms average
- **cancel_reservation**: 0.10ms average

### 💡 Failure Insights

- **Most problematic tool:** get_reservation_details (11 failures)
- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic
- **Average tool success rate:** 40.2%

### 🔍 Failure Type Comparison

Side-by-side comparison of failure types and their characteristics:

| Failure Type | Severity | Total Failures | Affected Tools | Top Failing Tools |
|--------------|----------|----------------|----------------|-------------------|
| **Never Called** | Critical | 18 | 6 | get_reservation_details (7), cancel_reservation (4), send_certificate (2) |
| **Called But No Match** | High | 4 | 1 | get_reservation_details (4) |
| **Called With Wrong Args** | Medium | 1 | 1 | book_reservation (1) |

**Key Insights:**

- **Never Called (78.3%):** Critical severity - These tools were never executed at all, indicating the agent failed to recognize when to use them.
- **Called But No Match (17.4%):** High severity - Tools were called but didn't produce expected results, suggesting execution logic issues.
- **Called With Wrong Args (4.3%):** Medium severity - Tools were called with incorrect parameters, indicating parameter validation or reasoning issues.

---

## 🎯 Performance Issues Analysis

### Performance Metrics

- **Overall success rate: 57.4%**
- **State-changing actions: 7.1% success rate**
- **Read-only actions: 62.3% success rate**
- **55%pp performance drop when actions are required** (62.3% → 7.1% success)

### 🔍 Failure Patterns

- **11% of operations result in failures**
- **Most failed operations:**
  - get_reservation_details: 42% failure rate
  - cancel_reservation: 67% failure rate
  - get_user_details: 17% failure rate
- **Action validation failures in 7 different tools**
- **100%% of failures involve validation mismatches**

### 📊 Action Complexity Impact

- **0 state changes: 62.3% success**
- **Tools with state changes: 7.1% success**
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
- **Average calls per simulation: 10.6**
- **State-changing operations: 9.4% of all calls**

---

## 💬 Communication vs Tool Call Analysis

### Transfer to Human Analysis

- **Transfer calls: 26 (12.3% of total calls)**
- **Transfer success rate: 100.0%**

### Communication Tool Usage

- **Communication calls: 2 (0.9% of total calls)**
- **Communication success rate: 0.0%**

### 🛑 Task Termination Analysis

- **Execution efficiency: 0.0%** (time spent in actual tool execution)
- **Low efficiency suggests high wait times** or communication delays
- **7 tools used extensively** (10+ calls each)
- **Possible indication of retry patterns** or complex multi-step operations

---

## ⚡ Performance Deep Dive

### 🏆 Performance Tier Analysis

**Excellent Performance (3 tools)** - Success rate ≥95%:
- `transfer_to_human_agents`: 100.0% success, 26 calls
- `get_flight_status`: 100.0% success, 10 calls
- `calculate`: 100.0% success, 2 calls

**Poor Performance (7 tools)** - Success rate <75%:
- `get_reservation_details`: 14.4% success, 104 calls
- `get_user_details`: 29.4% success, 34 calls
- `book_reservation`: 8.3% success, 12 calls
- `cancel_reservation`: 20.0% success, 10 calls
- `search_direct_flight`: 30.0% success, 10 calls
- `send_certificate`: 0.0% success, 2 calls
- `update_reservation_flights`: 0.0% success, 2 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`** (Never Called, critical severity):
  - Success rate: 14.4%
  - Total calls: 104
  - Failed calls: 89
  - Impact score: 10.6
  - Simulations affected: 5
  - State changing: No
- **`get_user_details`** (Never Called, critical severity):
  - Success rate: 29.4%
  - Total calls: 34
  - Failed calls: 23
  - Impact score: 1.7
  - Simulations affected: 2
  - State changing: No
- **`book_reservation`** (Called With Wrong Args, medium severity):
  - Success rate: 8.3%
  - Total calls: 12
  - Failed calls: 11
  - Impact score: 2.5
  - Simulations affected: 1
  - State changing: Yes
- **`cancel_reservation`** (Never Called, critical severity):
  - Success rate: 20.0%
  - Total calls: 10
  - Failed calls: 8
  - Impact score: 10.0
  - Simulations affected: 3
  - State changing: Yes
- **`search_direct_flight`** (Never Called, critical severity):
  - Success rate: 30.0%
  - Total calls: 10
  - Failed calls: 7
  - Impact score: 1.2
  - Simulations affected: 1
  - State changing: No

### ⏱️ Execution Time Analysis

- **Average execution time across all tools:** 0.26ms
- **Median execution time:** 0.09ms
- **Slowest tool:** `transfer_to_human_agents` (1.80ms)
- **Fastest tool:** `get_reservation_details` (0.04ms)

**Performance vs Usage Correlation:**
- High-usage tools (≥10 calls) average success rate: 43.2%
- Low-usage tools (<10 calls) average success rate: 33.3%

**State-Changing vs Read-Only Performance:**
- State-changing tools: 7.1% success, 0.0001s avg time (4 tools)
- Read-only tools: 62.3% success, 0.0004s avg time (6 tools)

---

## 🔄 Execution Patterns & Workflow Analysis

### ⏰ Execution Timeline

- **Total execution timespan:** 211.8 seconds
- **Actual tool execution time:** 0.0573 seconds
- **Execution efficiency:** 0.03% (time spent in tool execution)
- **Average call rate:** 1.00 calls/second

### 🔗 Tool Usage Patterns

**Most Common Tool Transitions:**

- **`get_reservation_details` → `get_reservation_details`** (59x): Self-loops indicate repeated calls to same tool
- **`get_user_details` → `get_reservation_details`** (26x): Common workflow pattern
- **`get_reservation_details` → `transfer_to_human_agents`** (16x): Common workflow pattern
- **`transfer_to_human_agents` → `get_user_details`** (15x): Common workflow pattern
- **`transfer_to_human_agents` → `get_reservation_details`** (9x): Common workflow pattern

**Pattern Analysis:**
- **Most common transition:** 28.0% of all transitions
- **Moderately concentrated** workflow with some preferred patterns
- **Self-loop rate:** 35.5% of transitions are repeated calls to same tool
- **High self-loop rate** may indicate retry logic or iterative processing

### 🧠 Workflow Intelligence

- **Tool diversity:** 10 unique tools used
- **Average calls per tool:** 21.2
- **Usage concentration:** 49.1% of calls go to most-used tool

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
