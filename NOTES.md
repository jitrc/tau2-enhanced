# Tau2 info

**Eval**:
    *   `ActionEvaluator`: Evaluates whether the agent performed the required actions.
    *   `CommunicateEvaluator`: Evaluates whether the agent communicated the required information to the user.
    *   `EnvironmentEvaluator`: Evaluates the end state of the simulation environment.
    *   `NLAssertionsEvaluator`: Uses a large language model to evaluate whether the conversation adheres to a set of natural language assertions.
**Metrics:**
    * Binary
    * Pass@k scores, and average agent cost
    * Component breakdown: communication, environment, database, and write actions
        * result_reward_analysis
        * result_reward_actions_analysis
  ┌───┬─────────┬───────────────┬─────────────┬──────────┬──────────────────────────┬──────────────────┬─────────┬───────┐
  │   │ success │ communication │ environment │ database │ num_correct_write_action │ num_write_action │ task_id │ trial │
  ├───┼─────────┼───────────────┼─────────────┼──────────┼──────────────────────────┼──────────────────┼─────────┼───────┤
  │ 0 │ True    │ 1.0           │ 1.0         │ 1.0      │ 2                        │ 2                │ task-01 │ 0     │
  │ 1 │ False   │ 1.0           │ 0.0         │ 1.0      │ 1                        │ 2                │ task-02 │ 0     │
  │ 2 │ False   │ 0.0           │ 1.0         │ 1.0      │ 2                        │ 2                │ task-03 │ 0     │
  └───┴─────────┴───────────────┴─────────────┴──────────┴──────────────────────────┴──────────────────┴─────────┴───────┘

  ┌───┬───────────┬─────────────────────┬───────────────────────────────────────────┬──────────────┬─────────┬───────┐
  │   │ requestor │ action_name         │ action                                    │ action_match │ task_id │ trial │
  ├───┼───────────┼─────────────────────┼───────────────────────────────────────────┼──────────────┼─────────┼───────┤
  │ 0 │ assistant │ get_booking_details │ get_booking_details(booking_ref='XYZ123') │ True         │ task-01 │ 0     │
  │ 1 │ assistant │ cancel_booking      │ cancel_booking(booking_ref='XYZ123')      │ True         │ task-01 │ 0     │
  │ 2 │ assistant │ get_booking_details │ get_booking_details(booking_ref='ABC456') │ True         │ task-02 │ 0     │
  │ 3 │ assistant │ cancel_booking      │ cancel_booking(booking_ref='ABC456')      │ False        │ task-02 │ 0     │
  └───┴───────────┴─────────────────────┴───────────────────────────────────────────┴──────────────┴─────────┴───────┘

## View
tau2 view --file data/simulations/baseline_airline_grok3.json
tau2 view --file data/tau2/results/final/claude-3-7-sonnet-20250219_airline_default_gpt-4.1-2025-04-14_4trials.json

Simulation ID: 5c13cd06-b180-42ed-9247-d274b25fa657   │
│ Task ID: 9                                          │
│ Trial: 2                                            │
│ Start Time: 2025-09-27T14:37:09.629475              │
│ End Time: 2025-09-27T14:38:05.115934                │
│ Duration: 55.49s                                    │
│ Termination Reason: TerminationReason.USER_STOP     │
│ Agent Cost: $0.1593                                 │
│ User Cost: $0.0098                                  │
│ Reward: ❌ 0.0000 (COMMUNICATE: 1.0, DB: 0.0)       │
│                                                     │
│ DB Check:❌ 0.0                                     │
│                                                     │
│ Action Checks:                                      │
│ - 0: cancel_reservation ❌ 0.0                      │
│ - 1: search_direct_flight ✅ 1.0                    │

## Re-evaluate
tau2 evaluate-trajs data/simulations/baseline_airline_grok3.json

│ 🏆 Average Reward: 0.5333                      │
│                                                │
│ 📈 Pass^k Metrics:                             │
│ k=1: 0.533                                     │
│ k=2: 0.400                                     │
│ k=3: 0.340                                     │
│                                                │
│ 💰 Average Cost per Conversation: $0.2256      |

## Metrics Breakdown
python analyze_results.py --file scripts/non_enhanced/baseline_airline_grok3.json

# Tau2-Enhanced

## Metrics Breakdown
python scripts/non_enhanced/analyze_breakdown.py --results baseline_airline_grok3.json
python scripts/non_enhanced/failure_analysis.py baseline_airline_grok3.json
python ../tau2-bench/analyze_results.py --file scripts/non_enhanced/baseline_airline_grok3.json

### tau2-bench-jit
bash tau2-bench-jit/scripts/run_analysis.sh basic tau2-bench-jit/data/simulations/baseline_airline_xai_grok3_gemini2_5_flash.json


## Sim Run

### xai/grok-3 

### Single Task
./tau2-enhanced run --domain airline_enhanced --agent retry_agent --agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning --num-trials 1 --save-to airline_llm_agent_xai_grok3_1task_1tr --task-ids 20

#### 10 task
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning --num-trials 1 --save-to airline_llm_agent_xai_grok3_10tasks_1tr --max-concurrency 1 --num-tasks 10

#### 1 Trail
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning --num-trials 1 --save-to airline_llm_agent_xai_grok3_1tr --max-concurrency 5
./tau2-enhanced run --domain airline_enhanced --agent retry_agent --agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning --num-trials 1 --save-to airline_retry_agent_xai_grok3_1tr --max-concurrency 5
./tau2-enhanced run --domain airline_enhanced --agent context_agent --agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning --num-trials 1 --save-to airline_context_agent_xai_grok3_1tr --max-concurrency 5
./tau2-enhanced run --domain airline_enhanced --agent enhanced_agent --agent-llm xai/grok-3 --user-llm xai/grok-4-fast-reasoning --num-trials 1 --save-to airline_enhanced_agent_xai_grok3_1tr --max-concurrency 5

### Generate Reports
python scripts/analyze_simple_logs.py /home/jit/code/tau2/tau2-enhanced/enhanced_logs/airline_llm_agent_xai_grok3_1tr_enhanced_logs.json
python scripts/analyze_simple_logs.py /home/jit/code/tau2/tau2-enhanced/enhanced_logs/airline_retry_agent_xai_grok3_1tr_enhanced_logs.json
python scripts/analyze_simple_logs.py /home/jit/code/tau2/tau2-enhanced/enhanced_logs/airline_context_agent_xai_grok3_1tr_enhanced_logs.json

### gemini/gemini-2.5-flash 

#### 10 task
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-trials 1 --save-to airline_gemini2_5_flash_llm_agent_10tasks_1tr --max-concurrency 1 --num-tasks 10

#### 1 Trail
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-trials 1 --save-to airline_gemini2_5_flash_llm_agent_full_1tr --max-concurrency 5
./tau2-enhanced run --domain airline_enhanced --agent retry_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-trials 1 --save-to airline_gemini2_5_flash_retry_agent_full_1tr --max-concurrency 5
./tau2-enhanced run --domain airline_enhanced --agent context_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-trials 1 --save-to airline_gemini2_5_flash_context_agent_full_1tr --max-concurrency 5
./tau2-enhanced run --domain airline_enhanced --agent enhanced_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-trials 1 --save-to airline_gemini2_5_flash_enhanced_agent_full_1tr --max-concurrency 5

### Single Task
./tau2-enhanced run --domain airline_enhanced --agent retry_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-trials 1 --save-to temp_retry --task-ids 20


# Regenerate analysis for the 'samples' directory
python3 scripts/analyze_simple_logs.py samples/logs/airline_gemini2_5_flash_10tasks_2t_context_agent_enhanced_logs.json -o samples/analysis
python3 scripts/analyze_simple_logs.py samples/logs/airline_gemini2_5_flash_10tasks_2t_enhanced_agent_enhanced_logs.json -o samples/analysis
python3 scripts/analyze_simple_logs.py samples/logs/airline_gemini2_5_flash_10tasks_2t_retry_agent_enhanced_logs.json -o samples/analysis
python3 scripts/analyze_simple_logs.py samples/logs/airline_gemini2_5_flash_10tasks_2t_enhanced_logs.json -o samples/analysis
python3 scripts/analyze_simple_logs.py enhanced_logs/archive/tau2-bench-jit/baseline_airline_xai_grok3_gemini2_5_flash.json -o samples/analysis
python3 scripts/analyze_simple_logs.py enhanced_logs/archive/tau2-bench-jit/baseline_airline_gemini2_5_flash.json -o samples/analysis

