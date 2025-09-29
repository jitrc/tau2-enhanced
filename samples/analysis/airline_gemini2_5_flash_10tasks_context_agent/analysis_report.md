# Enhanced Tau2 Execution Analysis Report

**Source File:** `airline_gemini2_5_flash_10tasks_2t_context_agent_enhanced_logs.json`
**Generated:** 2025-09-29 02:47:33
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

| Tool Name | Error Type | Count | Failure Rate |
|-----------|------------|-------|-------------|
| get_reservation_details | ActionCheckFailure | 8 | 30.8% |
| cancel_reservation | ActionCheckFailure | 3 | 50.0% |
| get_user_details | ActionCheckFailure | 3 | 25.0% |
| book_reservation | ActionCheckFailure | 2 | 100.0% |
| search_direct_flight | ActionCheckFailure | 2 | 50.0% |
| send_certificate | ActionCheckFailure | 2 | 100.0% |
| update_reservation_flights | ActionCheckFailure | 2 | 100.0% |

**Key Failure Metrics:**
- Total failures: **22**
- Affected tools: **7**
- Error categories: **1**

**Most Common Error Types:**
- ActionCheckFailure: 22 occurrences

---

## 🔄 State Change Analysis

### State-Changing Tools (4 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| cancel_reservation | 12 | 100.0% | 0.10 |
| book_reservation | 4 | 100.0% | 0.16 |
| send_certificate | 2 | 100.0% | 0.06 |
| update_reservation_flights | 2 | 100.0% | 0.11 |

### Read-Only Tools (6 tools)

| Tool Name | Calls | Success Rate | Avg Time (ms) |
|-----------|-------|--------------|---------------|
| get_reservation_details | 120 | 95.0% | 0.04 |
| get_user_details | 36 | 100.0% | 0.12 |
| transfer_to_human_agents | 20 | 100.0% | 0.03 |
| book_reservation | 8 | 0.0% | 0.08 |
| get_flight_status | 8 | 100.0% | 0.04 |
| search_direct_flight | 8 | 100.0% | 0.20 |

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
| search_direct_flight | book_reservation | 6 |
| get_reservation_details | search_direct_flight | 6 |
| book_reservation | book_reservation | 6 |
| cancel_reservation | cancel_reservation | 5 |

---

## 🔍 Key Insights

- **2** out of 9 tools have excellent performance (≥95% success rate)
- **get_reservation_details** is the most frequently used tool with 120 calls
- Overall system reliability: **59.3%**
- **7** tools showing poor performance require attention
- **10.0%** error rate across all tool executions
- **get_reservation_details** has the highest failure count with 8 failures
- **22** failures are due to action validation issues
- Tool distribution: **4** state-changing, **6** read-only
- High self-loop rate (42.9%) indicates potential retry patterns
- Most common pattern: **get_reservation_details** → **get_reservation_details** (76 times)

---

## 💡 Recommendations

- **Priority**: Investigate high-usage poor performers: get_reservation_details, get_user_details, book_reservation, cancel_reservation
- **Optimize** 7 tools with poor performance categories
- **Action Validation**: Review argument validation logic for action check failures
- **Database Consistency**: Ensure action execution aligns with database state expectations
- **Critical Fix**: Address tools with >50% failure rate: book_reservation, send_certificate, update_reservation_flights
- **System Reliability**: Overall tool success rate below 80% requires immediate attention
- **Task Success**: Low task completion rate suggests fundamental workflow issues

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
- **⚠️ Low overall success rate** suggests systemic issues requiring investigation

---

## 🎯 Performance Issues Analysis

### Overall Performance Assessment

- **Overall success: 59.3% (concerning)**
- **State-changing actions accuracy: 6.2%**
- **Read-only actions accuracy: 53.0%**
- **Critical**: State-changing actions show severe accuracy issues
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

**Excellent Performance (2 tools)** - High success rate (≥95%) and fast execution (≤1s):
- `transfer_to_human_agents`: 100.0% success, 0.03ms avg time, 20 calls
- `get_flight_status`: 100.0% success, 0.04ms avg time, 8 calls

**Poor Performance (7 tools)** - Low success rate (<75%):
- `get_reservation_details`: 15.0% success, 0.04ms avg time, 120 calls
- `get_user_details`: 25.0% success, 0.12ms avg time, 36 calls
- `book_reservation`: 0.0% success, 0.10ms avg time, 12 calls
- `cancel_reservation`: 25.0% success, 0.10ms avg time, 12 calls
- `search_direct_flight`: 25.0% success, 0.20ms avg time, 8 calls
- `send_certificate`: 0.0% success, 0.06ms avg time, 2 calls
- `update_reservation_flights`: 0.0% success, 0.11ms avg time, 2 calls

### 🚨 Critical Performance Issues

**High-Usage Poor Performers** (≥5 calls with poor performance):

- **`get_reservation_details`**:
  - Success rate: 15.0%
  - Total calls: 120
  - Failed calls: 102
  - Impact score: 102.0 (calls × failure rate)
  - State changing: No
- **`get_user_details`**:
  - Success rate: 25.0%
  - Total calls: 36
  - Failed calls: 27
  - Impact score: 27.0 (calls × failure rate)
  - State changing: No
- **`book_reservation`**:
  - Success rate: 0.0%
  - Total calls: 12
  - Failed calls: 12
  - Impact score: 12.0 (calls × failure rate)
  - State changing: Yes
- **`cancel_reservation`**:
  - Success rate: 25.0%
  - Total calls: 12
  - Failed calls: 9
  - Impact score: 9.0 (calls × failure rate)
  - State changing: Yes
- **`search_direct_flight`**:
  - Success rate: 25.0%
  - Total calls: 8
  - Failed calls: 6
  - Impact score: 6.0 (calls × failure rate)
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
- State-changing tools: 6.2% success, 0.0001s avg time
- Read-only tools: 53.0% success, 0.0001s avg time
- ⚠️ State-changing tools show 46.8% lower success rate

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

The following interactive visualizations have been generated:

- `summary_dashboard.html` - Executive dashboard with key metrics
- `failure_analysis.html` - Detailed failure analysis charts
- `state_change_analysis.html` - State change patterns and performance
- `tool_flow_sankey.html` - Tool usage flow diagram
- `performance_bottlenecks.html` - Performance analysis scatter plot
- `tool_report.html` - Comprehensive HTML tool analysis report
- `report.html` - Comprehensive HTML simulation report

---

*Report generated by Enhanced Tau2 Analytics Framework*
