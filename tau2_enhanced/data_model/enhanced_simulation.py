"""Enhanced simulation data models that extend tau2-bench with logging capabilities."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from tau2.data_model.simulation import Results, SimulationRun
from pydantic import BaseModel, Field


class EnhancedSimulationRun(SimulationRun):
    """Extended SimulationRun with enhanced logging capabilities."""

    execution_logs: Optional[list[dict[str, Any]]] = Field(
        description="Detailed execution logs from LoggingEnvironment",
        default=None
    )
    state_snapshots: Optional[list[dict[str, Any]]] = Field(
        description="State change snapshots from LoggingEnvironment",
        default=None
    )
    context_usage_snapshots: Optional[list[dict[str, Any]]] = Field(
        description="Context usage tracking snapshots",
        default=None
    )
    execution_metrics: Optional[dict[str, Any]] = Field(
        description="Enhanced execution metrics and statistics",
        default=None
    )
    enhanced_logging_enabled: bool = Field(
        description="Whether enhanced logging was enabled for this run",
        default=False
    )


class EnhancedResults(Results):
    """Extended Results with enhanced logging capabilities."""

    simulations: list[EnhancedSimulationRun] = Field(
        description="The list of enhanced simulations."
    )
    enhanced_logs_summary: Optional[dict[str, Any]] = Field(
        description="Summary of enhanced logging across all simulations",
        default=None
    )

    def save_enhanced(self, base_path: Path, include_logs: bool = True) -> tuple[Path, Optional[Path]]:
        """
        Save enhanced results with optional separate logs file.

        Args:
            base_path: Base path for saving files
            include_logs: Whether to save detailed logs in separate file

        Returns:
            Tuple of (main results path, logs path if saved)
        """
        # Save main results
        main_path = base_path.with_suffix('.json')
        self.save(main_path)

        logs_path = None
        if include_logs:
            # Extract and save detailed logs separately
            enhanced_data = self._extract_enhanced_data()
            if enhanced_data:
                logs_path = Path(str(base_path) + '_enhanced_logs.json')
                with open(logs_path, 'w') as f:
                    json.dump(enhanced_data, f, indent=2)

        return main_path, logs_path

    def _extract_enhanced_data(self) -> dict[str, Any]:
        """Extract enhanced logging data from all simulations."""
        enhanced_data = {
            'timestamp': datetime.now().isoformat(),
            'total_simulations': len(self.simulations),
            'enhanced_simulations': 0,
            'summary': {
                'total_execution_logs': 0,
                'total_state_snapshots': 0,
                'simulations_with_logs': 0
            },
            'simulations': {}
        }

        for sim in self.simulations:
            if hasattr(sim, 'enhanced_logging_enabled') and sim.enhanced_logging_enabled:
                enhanced_data['enhanced_simulations'] += 1

                sim_data = {}
                if sim.execution_logs:
                    sim_data['execution_logs'] = sim.execution_logs
                    enhanced_data['summary']['total_execution_logs'] += len(sim.execution_logs)

                if sim.state_snapshots:
                    sim_data['state_snapshots'] = sim.state_snapshots
                    enhanced_data['summary']['total_state_snapshots'] += len(sim.state_snapshots)

                if sim.execution_metrics:
                    sim_data['execution_metrics'] = sim.execution_metrics

                if sim.context_usage_snapshots:
                    sim_data['context_usage_snapshots'] = sim.context_usage_snapshots

                if sim_data:
                    enhanced_data['simulations'][sim.id] = sim_data
                    enhanced_data['summary']['simulations_with_logs'] += 1

        return enhanced_data if enhanced_data['enhanced_simulations'] > 0 else {}


def convert_to_enhanced_results(results: Results) -> EnhancedResults:
    """Convert regular Results to EnhancedResults."""
    # Convert SimulationRuns to EnhancedSimulationRuns
    enhanced_sims = []
    for sim in results.simulations:
        enhanced_sim = EnhancedSimulationRun(**sim.model_dump())
        enhanced_sims.append(enhanced_sim)

    # Create EnhancedResults
    enhanced_results = EnhancedResults(
        timestamp=results.timestamp,
        info=results.info,
        tasks=results.tasks,
        simulations=enhanced_sims
    )

    return enhanced_results