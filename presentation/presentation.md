---
marp: true
theme: default
paginate: true
style: |
  :root {
    font-size: 24px;
  }
  h1 {
    font-size: 1.5rem;
    color: #09c;
  }
  h2 {
    font-size: 1.25rem;
  }
  .small {
    font-size: 0.6em;
    color: #888;
    opacity: 0.7;
  }
---

---

# Evaluating Grok on tau2-bench
## Analysis, Critique & Improvements

**Jit Ray Chowdhury**

---

# Agenda (30 min)

1. **Overview of Benchmark** (3 min)
2. **Analysis Results + Methodology** (8 min)
3. **Failure Visualizations** (5 min)
4. **Improvements + Rationale** (8 min)
5. **Live Demo** (4 min)
6. **Next Steps** (2 min)

---

<!-- _class: lead -->
# Part 1: Overview of Benchmark
*Understanding tau2-bench*

---

# What is tau2-bench?

**Purpose:** Evaluate conversational AI agents in customer service scenarios

**Key Features:**
- Multi-turn conversations with state management
- Tool calling: Complex tools needstobe called in correct sequence
- Real-world complexity: Database operations, constraints, error handling

**Domains:**
- 🛫 Airline: Flight booking, reservations, cancellations
- 🛒 Retail: Orders, inventory, customer service
- 📞 Telecom: Account management, billing, troubleshooting

---

# tau2-bench Architecture

```
┌─────────────────────────────────────────────────────┐
│               Task Definition                       │
│        "Book cheapest flight using gift cards"      │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ┌───▼────┐          ┌─────▼────┐
    │  Agent │◄────────►│   User   │
    │  (LLM) │          │   (LLM)  │
    └───┬────┘          └─────┬────┘
        │                     │
        └──────────┬──────────┘
                   │
            ┌──────▼──────┐
            │ Environment │
            │  (Database) │
            └─────────────┘
```


---

# tau2-bench Metrics

**Primary Metrics:**
- **Task Success Rate:** Did the agent complete the user's goal?
- **Action Accuracy:** Were state-changing operations correct?
- **Tool Usage:** Efficiency and correctness of API calls
```
│ Reward: ❌ 0.0000 (COMMUNICATE: 1.0, DB: 0.0)       │
│ DB Check:❌ 0.0                                     │
│ Action Checks:                                      │
│ - 0: cancel_reservation ❌ 0.0                      │
│ - 1: search_direct_flight ✅ 1.0                    │
```

---
# tau2-bench Airline Eval


**Evaluation:**
- 50 tasks for domain Airline
- Multiple trials per task (typically 4)
- Binary success/failure scoring

**Why**

✅ Real-world deployment scenarios
✅ Tests sustained reasoning
✅ Industry-adopted benchmark

---

<!-- _class: lead -->
# Part 2: Analysis Results + Methodology
*Grok-3 Performance Deep Dive*

---

# Executive Summary: Grok-3 Results

| Metric | Value | Industry Baseline |
|--------|-------|-------------------|
| **Task Success Rate** | 57.5% | 50-59% (comparable) |
| **Communication Success** | **97.0%** | Shows reasoning is intact ✓ |
| **Action Execution Failures** | 89.4% | Industry-wide: 48-89% ⚠️ |
| **Performance Drop (with actions)** | 61.1pp | 8-63pp (Grok is highest) |

**Dataset:** 200 simulations, 50 tasks, 4 trials each
**Total Tool Calls Analyzed:** 1,162
<span class="small">
Log file [baseline_airline_xai_grok3_gemini2_5_flash](enhanced_logs/archive/tau2-bench-jit/baseline_airline_xai_grok3_gemini2_5_flash.json)</span>

---

# Key Finding: The Planning Gap

**Observation:**
- Total Tool Calls 1162
- Tool Success: 65.3%
- Task Success: 57.5%
- **Gap: 7.8 percentage points**

**What This Means:**
- Agent can execute tools correctly
- But chooses wrong sequence or wrong tools
- Indicates planning issue, not execution issue
---
```
Analyzing 85 failed simulations...
🔍 Primary Failure Modes:
  Communication failures: 6/85 (7.1%)
  Database failures: 85/85 (100.0%)
  Action execution failures: 76/85 (89.4%)

⚠️  Critical Insights:
  No-action tasks succeed at 93.8% rate
  Action-required tasks succeed at 32.8% rate
  → 61.1percentage point performance drop when actions required

🚨 Most Problematic Actions (min 5 attempts):
  book_reservation: 84.8% failure rate (33.0 attempts)
  search_direct_flight: 78.8% failure rate (80.0 attempts)
  send_certificate: 66.7% failure rate (12.0 attempts)
  update_reservation_baggages: 62.5% failure rate (24.0 attempts)
  update_reservation_flights: 54.8% failure rate (84.0 attempts)
```
<span class="small">
python scripts/non_enhanced/failure_analysis.py enhanced_logs/archive/tau2-bench-jit/baseline_airline_xai_grok3_gemini2_5_flash.json
</span>

---
# Key Finding: The Execution Gap
**But wait...**
- 89.4% action execution failures
- This IS an execution problem for state-changing tools

**Critical Evidence:**
- **97.0% communication success** (understanding is fine)
- **100% ActionCheckFailure** (validation errors, not reasoning)
- **93.8% success without actions** → 32.8% with actions
- **This is an execution gap, not a reasoning problem**

---


# Critical Finding: Performance Cliff

![bg right:40% 100%](presentation_assets/performance_cliff.png)

**Without Actions Required:**
- Success Rate: 93.8%

**With Actions Required:**
- Success Rate: 32.8%

**Drop: 61.1 percentage points**

Grok-3's 61.1 percentage point drop is the largest among the flagship models, significantly higher than GPT-4.1 (31.7pp) and Claude 3.7 Sonnet (8.3pp).

---

# Full Model Comparison

<style scoped>
  table {
    font-size: 20px;
    line-height: 1.2;
  }
  th, td {
    padding: 8px 12px;
  }
</style>

| Model | Overall Success | Comm. Success | DB. Success | Write Action Acc. | Pass@1 | Pass@2 | Pass@3 | Pass@4 | Avg. Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **O4 Mini** | **59.0%** | 93.0% | 59.5% | 45.9% | 0.590 | 0.483 | 0.420 | 0.380 | $0.0505 |
| **Grok 3** | 57.5% | **97.0%** | 57.5% | 43.5% | 0.575 | 0.460 | 0.405 | 0.380 | $0.2318 |
| **GPT-4.1** | 56.0% | 95.0% | 58.0% | 57.7% | 0.560 | 0.457 | 0.420 | 0.400 | $0.0535 |
| **GPT-4.1 Mini** | 50.5% | 92.0% | 55.5% | 65.5% | 0.505 | 0.393 | 0.320 | 0.260 | **$0.0126** |
| **Claude 3.7 Sonnet** | 50.0% | 94.5% | 51.0% | **65.9%** | 0.500 | 0.410 | 0.375 | 0.360 | $0.3492 |
| **Gemini 2.5 Flash** | 47.0% | 91.5% | 49.0% | 19.1% | 0.470 | 0.353 | 0.305 | 0.280 | $0.0141 |

---

Complexity vs Success
==================================================
Success rates by number of write actions required:
| Actions | Count | Success Rate | Communication Success | Database Success |
|:-------:|:-----:|:------------:|:--------------------:|:----------------:|
|   0     |  81   |   93.8%      |      100.0%          |    93.8%         |
|   1     |  64   |   40.6%      |      100.0%          |    40.6%         |
|   2     |  28   |   25.0%      |      85.7%           |    25.0%         |
|   3     |  16   |   25.0%      |      93.8%           |    25.0%         |
|   4     |   7   |    0.0%      |      85.7%           |     0.0%         |
|   5     |   4   |   50.0%      |      100.0%          |    50.0%         |

---

# Action Failure Cascade

The performance drop isn't gradual—it's a catastrophic cliff after just one action.

| Task Type | Success Rate | Drop from Previous |
|:---|:---:|:---:|
| No actions | 93.8% | - (baseline) |
| Single action | 40.6% | **-53.2pp** ⚠️ |
| Multi-action | 0-25% | -15 to -40 ❌ |


**Implication:** The agent struggles to recover from even a single complex action, leading to a cascade of failures in multi-step tasks.

---
### Secondary Root Cause: Context Length Pressure

**Context Limit Analysis:**
- Average context: 2,989 tokens per simulation
- Failed simulations use **1.3x more tokens** (3,431 vs 2,601 tokens)

**Performance Cliffs Identified:**
- **1,500-2,000 tokens**: 27% performance drop (72.7% → 45.5% success)
- **3,000-3,500 tokens**: 53% performance drop (71.4% → 18.2% success)

**Context Growth Pattern:**
- Each tool call + response: ~200-500 tokens
- Error recovery attempts amplify context growth

----

# Trial Consistency Issues

```
Trial 0: █████████████░░░░░░░ 66%
Trial 1: ████████████░░░░░░░░ 58%
Trial 2: ███████████░░░░░░░░░ 56%
Trial 3: ██████████░░░░░░░░░░ 50%
```

🏆 Standard Metrics:
```
Average reward: 0.575
Pass@1: 0.575
Pass@2: 0.460
Pass@3: 0.405
Pass@4: 0.380
Average agent cost: $0.2318
```

The model's performance is inconsistent across repeated attempts, suggesting a lack of robustness.

---
# Standard tau2-bench Limitations

**What tau2-bench provides:**
- ✅ Final success/failure (binary)
- ✅ Reward score
- ✅ Cost/token usage

**What's missing:**
- ❌ Tool execution details
- ❌ Argument validation errors
- ❌ State change tracking
- ❌ Temporal patterns
- ❌ Error categorization

**Problem:** Can't distinguish planning failures from execution failures

---

# Enter: tau2-enhanced

**Solution:** Add comprehensive observability without modifying tau2-bench

**Captures:**
- Every tool call with full context
- Argument complexity scores (0-1 scale)
- Validation errors and error types
- State changes and diffs
- Execution timing

**Enables:**
- 15+ analysis methods
- Root cause analysis
- Performance bottleneck identification
- Correlation analysis

---

# Analysis Methodology

**Data Collection:**
```python
# Non-invasive interception
LoggingEnvironment wraps original Environment
  ↓
Intercepts make_tool_call()
  ↓
Captures: args, result, timing, state changes
  ↓
Structured events in JSON format
```

**Analysis Pipeline:**
```python
LogAnalyzer loads events
  ↓
15+ analysis methods
  ↓
HTML reports + CSV exports
```

---

<!-- _class: lead -->
# Part 3: Failure Visualizations
*Understanding What Goes Wrong*

---

# Failure Category Breakdown

**Error Distribution:**
```
ActionCheckFailure: ████████████████████████████████ 100%
                    (204 occurrences)
```

**What is ActionCheckFailure?**
- Parameter validation errors
- Missing required fields
- Wrong parameter types
- Invalid values

**Key Insight:** 100% of categorized failures are validation errors, not reasoning errors

---

# Primary Failure Modes (Grok-3)

When a task fails, what is the primary cause?

| Failure Mode | % of Failed Simulations |
| :--- | :---: |
| **Database Failure** | **100%** |
| **Action Execution Failure** | 89.4% |
| **Communication Failure** | 7.1% |

**Key Insight:** Every single failed task (85/85) for Grok-3 involved a database failure. This confirms the issue is not what the agent *says*, but what it *does* (or fails to do). The low communication failure rate (7.1%) highlights its conversational strength.

---

# Failure Subcategories

| Error Type | Count | % of Failures |
|------------|-------|---------------|
| Missing required fields | ~80 | 39% |
| Wrong parameter types | ~70 | 34% |
| Invalid values | ~54 | 26% |
| Other validation errors | ~0 | 1% |

**Example:**
```json
{
  "tool": "book_reservation",
  "error": "Required field 'payment.gift_card_ids' missing",
  "provided": {"flight_id": "...", "passenger_ids": [...]}
}
```

---

# Critical Tool Failures

**Top Failing Tools** (minimum 5 attempts):

| Tool | Failure Rate | Attempts |
|------|--------------|----------|
| `calculate` | 100.0% | 4 |
| `book_reservation` | 84.8% | 33 |
| `search_direct_flight` | 78.8% | 80 |
| `send_certificate` | 66.7% | 12 |

**Pattern:** State-changing tools fail at much higher rates than read-only tools

---

# State-Changing vs Read-Only Tools

**State-Changing Tools:**
- Modify database (book, cancel, update)
- Average success: ~55%
- High ActionCheckFailure rate

**Read-Only Tools:**
- Query information (get, search)
- Average success: ~95%
- Low error rate

**Write Action Accuracy:** Only 43.5% of attempted state changes succeed

---

# Complete Failure Tasks
<style scoped>
  {
    font-size: 20px;
  }
</style>

**Tasks with 100% Failure Rate:**

**Task 14:** Payment optimization
- *"Book cheapest flight using gift cards and certificate"*
- Requires complex payment parameter structure
- 0/4 trials successful

**Task 17:** Multiple simultaneous updates
- *"Update passenger, baggage, and flight details"*
- Requires coordinated changes
- 0/4 trials successful

**Task 20:** Constrained booking
- *"Book flight with time and payment constraints"*
- Simple 1-action task but complex validation
- 0/4 trials successful

---

# Example Failure: Task 14

**User Request:**
> "Book the cheapest flight using my gift cards and one certificate"

**Grok's Reasoning:** ✅ Correct
1. Searches flights
2. Identifies cheapest option
3. Calculates payment split across gift cards + certificate
4. Attempts booking

**Execution:** ❌ Failed
```
Error: ActionCheckFailure - Invalid payment structure
Expected: {payment: {gift_card_ids: [...], certificate_id: "..."}}
Provided: {payment: {method: "split", cards: [...], cert: "..."}}
```

**Result:** 0% success despite correct financial reasoning

---

# Visualization: State Change

![width:600px](presentation_assets/state_change.png)
![bg right:50% width:600px](presentation_assets/failure_modes.png)

---


<!-- _class: lead -->
# Part 4: Improvements + Rationale
*Systematic Solutions to Systematic Problems*

---

# Problem → Solution Mapping

| Problem | Evidence | Root Cause | Solution |
|---------|----------|------------|----------|
| 89.4% validation failures | ActionCheckFailure dominates | Parameter construction errors | **RetryManagedAgent** |
| 61.1pp performance drop | With actions: 32.8% vs 93.8% | Execution gap | **RetryManagedAgent** |
| 50% → 66% trial degradation | Consistent decline | Context accumulation | **ContextManagedAgent** |

**Hypothesis:** Combine both → Measurable improvement (model-dependent)

---

# The Vicious Cycle Problem

The two root causes amplify each other, creating a vicious cycle that leads to task failure.

```
1. Complex tasks require multiple actions
              ↓
2. Action failures trigger retries
              ↓
3. Retries add 200-500 tokens per attempt
              ↓
4. More context → Performance cliffs at 1.5K and 3K
              ↓
5. Performance degradation → More action failures
              ↓
         [Back to step 2]
```

**Breaking the Cycle:**
- **`RetryManagedAgent`** reduces failures at step 2
- **`ContextManagedAgent`** prevents degradation at step 4
- **`EnhancedLLMAgent`** breaks the cycle at both points

---

# Why Enhanced Agents Over Alternatives?

| Approach | Pros | Cons | Chosen? |
|----------|------|------|---------|
| Better prompts | Easy | Doesn't fix validation | ❌ |
| Few-shot examples | Improves patterns | Limited to seen cases | ❌ |
| RAG/retrieval | Adds context | Doesn't address execution | ❌ |
| Fine-tuning | Model improvement | Needs data/compute | ❌ |
| **Retry logic** | **Addresses root cause** | **Efficiency cost** | ✅ |
| **Context mgmt** | **Prevents degradation** | **Needs tuning** | ✅ |

---

# Decision Rationale: Why Retry Logic?

**Observation:**
- Validation errors are systematic, not random
- Agent often has correct intent but wrong JSON structure
- Errors are recoverable with clarification

**Why Retry Logic Wins:**
- ✅ Addresses root cause: parameter construction
- ✅ Generalizes across all tools and domains
- ✅ Measurable improvement
- ✅ Low overhead: Only triggers on failures

---

# RetryManagedAgent Architecture

```
┌──────────────────────────────────────────────────┐
│           LLM generates tool call                │
└─────────────────┬────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Execute Tool   │
         └────────┬───────┘
                  │
           ┌──────┴──────┐
           │ Success?    │
           └──────┬──────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                 NO
        │                   │
        ▼                   ▼
    [Return]     ┌──────────────────┐
                 │ Classify Error   │
                 │ - Validation?    │
                 │ - Missing field? │
                 │ - Type error?    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Retry (max 3)    │
                 │ with hints       │
                 └────────┬─────────┘
                          │
                    [Back to LLM]
```

---


# ContextManagedAgent: Strategies

**1. Sliding Window (Preferred):**
```
Keep:
  - System message
  - Task description
  - Last N messages (N = context_limit * 0.3)

Drop:
  - Middle conversation history
```

**2. Compression:**
```
Summarize old messages:
  "Previous 10 turns: User requested flight change,
   agent searched options, user selected new flight."
```

---

# EnhancedLLMAgent: Combined Solution

**Best of Both Worlds:**
```python
EnhancedLLMAgent = RetryManagedAgent + ContextManagedAgent
```

**Coordination:**
1. Context management happens proactively (before generation)
2. Retry logic happens reactively (after failure)
3. No interference between mechanisms

---


# Proof-of-Concept: Small-Scale Validation


**Sample:** 10 tasks × 2 trials = 20 simulations

| Agent | Tool Success | Task Success | vs Baseline |
|:---|:---:|:---:|:---:|
| llm_agent | 57.4% | 60.0% | - |
| context_agent | 59.3% | 70.0% | +1.9pp |
| retry_agent | 68.5% | 60.0% | **+11.1pp** ✓ |
| **enhanced_agent** | **70.4%** | 70.0% | **+13.0pp** ✓ |

**Initial Takeaway:** Enhanced agents show promising double-digit improvements!

**Reports:**
- [llm_agent](https://www.jitrc.com/tau2-enhanced/samples/analysis/airline_gemini2_5_flash_10tasks_llm_agent/enhanced_analysis_report.html)
- [retry_agent](https://www.jitrc.com/tau2-enhanced/samples/analysis/airline_gemini2_5_flash_10tasks_retry_agent/enhanced_analysis_report.html)
- [enhanced_agent](https://www.jitrc.com/tau2-enhanced/samples/analysis/airline_gemini2_5_flash_10tasks_enhanced_agent/enhanced_analysis_report.html)

---

# Key Design Decisions

**Decision 1: Non-invasive Monkey Patching**

**Why not fork tau2-bench?**
- ✅ Backward compatible with existing installations
- ✅ Can upgrade tau2-bench independently
- ✅ Users don't need to switch frameworks
- ✅ Contributions can be upstreamed

**How it works:**
```python
# Intercept environment creation
original_get_env = registry.get_env_constructor
def patched_get_env():
    env = original_get_env()
    return LoggingEnvironment(env)
registry.get_env_constructor = patched_get_env
```

---

# Key Design Decisions

**Decision 2: Structured Logging vs Simple Metrics**

**Why capture everything?**
- ✅ Enables re-analysis with new hypotheses
- ✅ 15+ analysis methods from single data collection
- ✅ Future-proof for new metric development
- ✅ Root cause analysis requires full context

**What we capture:**
- Tool execution events (args, results, timing)
- State change events (pre/post hashes, diffs)
- Context reduction events (tokens saved, strategy)

---

# Key Design Decisions

**Decision 3: Three Agent Variants**

**Why separate agents?**
- `retry_agent`: Isolated retry testing
- `context_agent`: Isolated context testing
- `enhanced_agent`: Combined optimization

**Benefits:**
- ✅ A/B testing of mechanisms
- ✅ Incremental adoption
- ✅ Clear attribution of improvements

---

<!-- _class: lead -->
# Part 5: Live Demo
*Seeing It In Action*

---

# Demo Overview

**What We'll Show:**
1. Run analysis on captured logs
2. Explore interactive HTML reports
4. Quick Sim generation run using Grok API

**Files We'll Use:**

- Enhanced: 
  - `enhanced_logs/archive/tau2-bench-jit/baseline_airline_xai_grok3_gemini2_5_flash.json`
  - `samples/logs/airline_gemini2_5_flash_10tasks_2t_retry_agent_enhanced_logs.json`
  - `enhanced_logs/archive/airline_llm_agent_xai_grok3_enhanced_logs.json`
- Reports: Available at all analysis result directories

---

# Demo: Running Analysis

**Command (enhanced):**
```bash
python scripts/analyze_simple_logs.py \
  enhanced_logs/archive/tau2-bench-jit/baseline_airline_xai_grok3_gemini2_5_flash.json
```

**What It Does:**
1. Loads tool execution events
2. Runs 15+ analysis methods
3. Generates 3 reports:
   - `analysis_report.md` (executive summary)
   - `enhanced_analysis_report.html` (interactive viz)
   - `tool_report.html` (tool-specific metrics)
   - `simulation_report.html`(Full simulation log of every Task/Trail and Results)

---

# Demo: Running Analysis Baseline (Skip)
- Baseline: `scripts/non_enhanced/baseline_airline_grok3.json`
**Command (Non-enhanced):**
```bash
python scripts/non_enhanced/analyze_breakdown.py --results scripts/non_enhanced/baseline_airline_grok3.json
python scripts/non_enhanced/failure_analysis.py scripts/non_enhanced/baseline_airline_grok3.json
```
**Output:** *(show terminal output)*

---
# Demo: Interactive HTML Reports

**enhanced_analysis_report.html:**
- Tool performance
- Temporal trend analysis
- Success rate breakdowns 

**tool_report.html:**
- Per-tool success rates
- Error categorization

**simulation_report.html:**
- Task and Tool Call details

**Live Navigation:** *(switch to browser)*

---

# Demo: Enhanced logging using Grok 3

**Single Task**
```bash
./tau2-enhanced run --domain airline_enhanced --agent retry_agent \
--agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning \
--num-trials 1 --save-to demo_1_task --task-ids 20
```

**10 Tasks**
```bash
./tau2-enhanced run --domain airline_enhanced --agent llm_agent \
--agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning \
--num-trials 1 --save-to demo_10_task \
--max-concurrency 5 --num-tasks 10
```

---

<!-- _class: lead -->
# Part 6: Next Steps
*Future Work & Extensions*

---

# Immediate Validation Steps

**1. Proof-of-Concept Completed (on Gemini)**
- ✅ `retry_agent`: **+11.1pp** improvement
- ✅ `context_agent`: **+1.9pp** improvement
- ✅ `enhanced_agent`: **+13.0pp** improvement

**2. Next Steps: Model-Specific Optimization**
- **Analyze failure patterns** per model (error signatures differ)
- **Tune retry strategies** based on model-specific error types
- **Optimize context thresholds** per model architecture
- **Cross-domain validation** on retail and telecom domains

---

# Proposed Training Strategy

## 1. Structured Output Training (~50k examples)

**Goal:** Reduce validation errors from root cause

**Focus Areas (from actual failure analysis):**
- `book_reservation`: 88.9% failure → Payment parameter structure
- `search_direct_flight`: 78.8% failure → Search parameter validation
- `update_reservation_flights`: 100% failure → Nested object handling

**Data Generation:**
```python
{
  "correct": {"payment": {"gift_card_ids": [...], "certificate_id": "..."}},
  "error": {"payment": {"method": "split", "cards": [...], "cert": "..."}}
}
```

**Target:** Reduce ActionCheckFailure from 89% to <45%

---

# Proposed Training Strategy (continued)

## 2. Model-Specific Error Recovery Training

**Approach:**
- Train on retry patterns that succeeded for each model
- Build error signature → recovery strategy mappings
- Adaptive strategies that switch based on error type

**Training Data:**
```python
{
  "error": "ActionCheckFailure: payment_id required",
  "failed_retry": {"payment": {"id": "cert_123", "amount": 348}},
  "successful_retry": {"payment_id": "cert_123", "amount": 348}
}
```

## 3. Context Management Dataset (~25k examples)

**Goal:** Prevent performance cliffs and confusion
**Focus:** Long conversations with state consistency
**Validation:** Monitor self-loop rate (<35%) and efficiency metrics

**Expected Outcomes:**
- Structural: +5-10pp from better parameter formatting
- Recovery: +3-5pp from intelligent retry strategies
- Efficiency: -15% tool calls through better planning

---

# Research Directions (Near-term)

**1. Multi-modal Evaluation:**
- Add tasks with image/document processing
- Test vision capabilities (receipt scanning, ID verification)
- Measure multi-modal reasoning

**2. Quality Metrics:**
- Implement politeness scoring
- Add bias detection
- Measure proactive behavior

**3. Adversarial Robustness:**
- Fault injection testing
- Edge case generation
- Stress test with ambiguous queries

---

# Key Takeaways

**What This Demonstrates:**

1. **Analytical Depth:** Identified execution gap and discovered retry traps through comprehensive logging
2. **Technical Innovation:** Non-invasive observability without forking, enabling deep analysis
3. **Visual Tooling:** revealed hidden failure modes
4. **Reproducibility:** All code, data, analysis publicly available with complete methodology

**Core Innovation:**
> "Rigorous benchmark critique reveals hard truths with help of and analysis tooling. This framework enables discovery of these critical insights."

---

# Impact Statement

**Before tau2-enhanced:**
- Binary success/failure metrics
- No visibility into execution details
- Can't distinguish planning vs execution failures
- Limited to final results

**After tau2-enhanced:**
- 15+ analysis methods with structured logging
- Root cause analysis with error categorization
- Three specialized agents revealing optimization complexity
- Framework for discovering sample size bias and model-specific patterns

**Framework Effect:** Makes ANY tau2-bench evaluation more insightful, preventing costly production failures

---

# Q&A Highlights

### Exceptional Technical Accomplishments

*   **Acubed (Airbus):** Advanced aircraft localization from TRL 3 to 4 in one year with a reduced team.
    *   Improved localization performance from **30% to 98%**.
    *   Reduced pipeline complexity and latency while boosting performance.
*   **Waymo:**
    *   Generated synthetic degraded data to estimate LIDAR data quality.
    *   Coordinated between LIDAR hardware, perception software, and external customers.
*   **Auro (CTO):**
    *   Initiated a data-driven Reinforcement Learning environment for a learned driving policy in 2019.

### Hardest Technical Problem Solved

> Building a full-stack self-driving car (perception, planning, controls, sim, UI) from scratch in 3 months after moving to the USA.

### Career Guidance

> A drive to contribute to hard, AI-based autonomous solutions at scale—from robotics and self-driving cars to AI agents.

---


# Questions?

**Contact:**
- GitHub: github.com/jitrc/tau2-enhanced
- Email: jit.ray.c@gmail.com

**Thank you!**

---

<!-- _class: lead -->
# Backup Slides

---

# Detailed Architecture: tau2-enhanced

```
┌─────────────────────────────────────────────────────┐
│                   tau2-bench CLI                     │
│                  (unchanged)                         │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │  EnhancedRunner     │
          │  - Monkey patches    │
          │  - Captures instances│
          └──────────┬──────────┘
                     │
       ┌─────────────┴─────────────┐
       │   LoggingEnvironment      │
       │   - Wraps Environment     │
       │   - Intercepts tool calls │
       └─────────────┬─────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐           ┌──────▼──────┐
    │ Execution│           │    State    │
    │  Logger  │           │   Tracker   │
    └────┬────┘           └──────┬──────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   Enhanced  │
              │    Logs     │
              │   (JSONL)   │
              └─────────────┘
```

---

# Analysis Methods (15+)

**Statistical:**
- Basic statistics (mean, median, std dev)
- Confidence intervals (95%)
- Correlation analysis

**Performance:**
- Tool efficiency metrics
- Performance bottlenecks
- Temporal trend analysis

**Specialized:**
- Argument intelligence (complexity, security)
- Error pattern detection
- State change analysis


---

# Backup: Action/Function Call Failure Rate Comparison

<style scoped>
  table {
    font-size: 20px;
    line-height: 1.3;
  }
</style>

| Action | Grok 3 | GPT-4.1 | Claude 3.7 | O4 Mini | GPT-4.1 Mini | Gemini Flash |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `calculate` | 100% | 100% | 100% | 100% | 100% | 100% |
| `book_reservation` | 85% | 69% | 58% | 72% | 67% | 100% |
| `update_reservation_flights` | 55% | 29% | 27% | 44% | 27% | 100% |
| `search_direct_flight` | **79%** | 28% | 30% | 54% | 24% | 54% |
| `update_reservation_baggages`| 63% | 71% | 46% | 71% | 67% | 71% |
| `send_certificate` | 67% | 75% | 33% | 67% | 17% | 92% |

---


# Backup: Why Not terminal-bench?
<style scoped>
  {
    font-size: 20px;
  }
</style>
While `terminal-bench` was considered, `tau2-bench` was chosen for its deeper analytical capabilities.

### `terminal-bench`: Pros
  *   **Practical & Broad Coverage:** Evaluates agents on real-world command-line tasks across several categories (e.g., coding, networking).
  *   **Reproducible:** No LLM-based user simulator means fully deterministic results.
  *   **Extensible:** Easy to add new tasks, including multi-modal ones.

### Rationale for Not Selecting
  *   **Tests Memorization over Agency:** The benchmark's structure can reward "memorized" solutions for specific problems rather than testing true agentic reasoning and problem-solving.
  *   **Lacks Analytical Depth:** The clean, non-messy environments and lack of diversity within similar tasks make it difficult to perform the deep, systematic failure analysis needed for root cause identification.
  *   **Superficial Scoring:** The brittle scoring metric can be gamed by superficial agent improvements, not necessarily reflecting an increase in robust capability.

---

# Backup: tau2-bench Sophistication
<style scoped>
  {
    font-size: 20px;
  }
</style>

The benchmark tests for four distinct and sophisticated categories of failure.

**1. Policy Violations** (14% of failures)
  - **Tests:** Will the agent break established rules to please a user?
  - **Example:** Agent agrees to cancel a non-refundable ticket after the user insists.

**2. User Claim Verification** (12% of failures)
  - **Tests:** Does the agent validate user claims against the database, or does it trust blindly?
  - **Example:** Agent offers a "Gold member" discount without checking the user's actual "Regular member" status.

**3. Reasoning & Calculation** (87% of failures) ← **Our Focus**
  - **Tests:** Can the agent execute complex, multi-step operations and calculations correctly?
  - **Example:** Agent fails to calculate the optimal payment split using gift cards and a certificate.

**4. Complex Intent Handling** (7% of failures)
  - **Tests:** Can the agent handle multi-part requests, context switching, and evolving user goals?
  - **Example:** User asks to cancel two bookings and modify a third, then adds a new request mid-conversation.
