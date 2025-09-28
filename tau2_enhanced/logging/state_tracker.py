"""
StateTracker for environment state snapshots and diff tracking.

This module provides the StateTracker class that handles environment state
monitoring, snapshot creation, and state change detection.
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field

from loguru import logger


@dataclass
class StateSnapshot:
    """Snapshot of environment state at a specific point in time."""

    timestamp: float = field(default_factory=time.time)
    step_number: int = 0
    agent_turn: bool = True
    state_data: Dict[str, Any] = field(default_factory=dict)
    context_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    state_hash: Optional[str] = None
    action_trigger: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'step_number': self.step_number,
            'agent_turn': self.agent_turn,
            'state_data': self.state_data,
            'context_size': self.context_size,
            'metadata': self.metadata,
            'state_hash': self.state_hash,
            'action_trigger': self.action_trigger
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        """Create snapshot from dictionary."""
        return cls(**data)


@dataclass
class StateDiff:
    """Difference between two state snapshots."""

    from_snapshot: StateSnapshot
    to_snapshot: StateSnapshot
    changes: Dict[str, Any] = field(default_factory=dict)
    additions: Set[str] = field(default_factory=set)
    deletions: Set[str] = field(default_factory=set)
    modifications: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    diff_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert diff to dictionary for serialization."""
        return {
            'from_timestamp': self.from_snapshot.timestamp,
            'to_timestamp': self.to_snapshot.timestamp,
            'from_hash': self.from_snapshot.state_hash,
            'to_hash': self.to_snapshot.state_hash,
            'changes': self.changes,
            'additions': list(self.additions),
            'deletions': list(self.deletions),
            'modifications': self.modifications,
            'diff_summary': self.diff_summary
        }


class StateTracker:
    """
    State tracking and snapshot utilities for environment monitoring.

    This class provides functionality to capture environment state snapshots,
    track changes, and analyze state transitions.
    """

    def __init__(
        self,
        max_snapshots: int = 1000,
        auto_snapshot: bool = True,
        track_state_hash: bool = True,
        snapshot_triggers: Optional[List[str]] = None
    ):
        """
        Initialize StateTracker.

        Args:
            max_snapshots: Maximum number of snapshots to keep in memory
            auto_snapshot: Whether to automatically create snapshots
            track_state_hash: Whether to compute and track state hashes
            snapshot_triggers: List of actions that trigger snapshots
        """
        self.snapshots: List[StateSnapshot] = []
        self.max_snapshots = max_snapshots
        self.auto_snapshot = auto_snapshot
        self.track_state_hash = track_state_hash
        self.snapshot_triggers = snapshot_triggers or [
            'tool_execution',
            'state_change',
            'step_start',
            'step_end'
        ]

        # State tracking
        self._current_step = 0
        self._last_hash = None
        self._state_change_count = 0

    def create_snapshot(
        self,
        state_data: Dict[str, Any],
        action_trigger: str = "",
        agent_turn: bool = True,
        context_size: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StateSnapshot:
        """
        Create a state snapshot.

        Args:
            state_data: Current state data to snapshot
            action_trigger: Action that triggered this snapshot
            agent_turn: Whether it's currently the agent's turn
            context_size: Size of current context
            metadata: Additional metadata

        Returns:
            Created StateSnapshot
        """
        # Compute state hash if enabled
        state_hash = None
        if self.track_state_hash:
            state_hash = self._compute_state_hash(state_data)

        snapshot = StateSnapshot(
            step_number=self._current_step,
            agent_turn=agent_turn,
            state_data=state_data.copy() if state_data else {},
            context_size=context_size,
            metadata=metadata.copy() if metadata else {},
            state_hash=state_hash,
            action_trigger=action_trigger
        )

        # Add to snapshots list
        self.snapshots.append(snapshot)

        # Maintain max snapshots limit
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)

        # Update tracking
        if state_hash and state_hash != self._last_hash:
            self._state_change_count += 1
            self._last_hash = state_hash

        logger.debug(f"Created state snapshot: step={self._current_step}, trigger={action_trigger}")
        return snapshot

    def snapshot_if_changed(
        self,
        state_data: Dict[str, Any],
        action_trigger: str = "",
        **kwargs
    ) -> Optional[StateSnapshot]:
        """
        Create a snapshot only if the state has changed.

        Args:
            state_data: Current state data
            action_trigger: Action that triggered this check
            **kwargs: Additional arguments for create_snapshot

        Returns:
            Created StateSnapshot if state changed, None otherwise
        """
        if not self.track_state_hash:
            # If not tracking hashes, always create snapshot
            return self.create_snapshot(state_data, action_trigger, **kwargs)

        current_hash = self._compute_state_hash(state_data)

        if current_hash != self._last_hash:
            return self.create_snapshot(state_data, action_trigger, **kwargs)

        return None

    def track_tool_execution(
        self,
        tool_name: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        **kwargs
    ) -> Optional[StateDiff]:
        """
        Track state changes during tool execution.

        Args:
            tool_name: Name of the executed tool
            pre_state: State before tool execution
            post_state: State after tool execution
            **kwargs: Additional snapshot metadata

        Returns:
            StateDiff if state changed, None otherwise
        """
        # Create pre-execution snapshot
        pre_snapshot = self.create_snapshot(
            pre_state,
            action_trigger=f"before_{tool_name}",
            **kwargs
        )

        # Create post-execution snapshot
        post_snapshot = self.create_snapshot(
            post_state,
            action_trigger=f"after_{tool_name}",
            **kwargs
        )

        # Increment step counter
        self._current_step += 1

        # Create diff if states are different
        if (self.track_state_hash and
            pre_snapshot.state_hash != post_snapshot.state_hash):
            return self.create_state_diff(pre_snapshot, post_snapshot)

        return None

    def create_state_diff(
        self,
        from_snapshot: StateSnapshot,
        to_snapshot: StateSnapshot
    ) -> StateDiff:
        """
        Create a diff between two state snapshots.

        Args:
            from_snapshot: Earlier state snapshot
            to_snapshot: Later state snapshot

        Returns:
            StateDiff object
        """
        diff = StateDiff(
            from_snapshot=from_snapshot,
            to_snapshot=to_snapshot
        )

        # Compare state data
        from_data = from_snapshot.state_data
        to_data = to_snapshot.state_data

        # Find additions, deletions, and modifications
        from_keys = set(from_data.keys())
        to_keys = set(to_data.keys())

        diff.additions = to_keys - from_keys
        diff.deletions = from_keys - to_keys
        common_keys = from_keys & to_keys

        # Check for modifications in common keys
        for key in common_keys:
            if from_data[key] != to_data[key]:
                diff.modifications[key] = {
                    'from': from_data[key],
                    'to': to_data[key]
                }

        # Create summary
        changes = []
        if diff.additions:
            changes.append(f"added {len(diff.additions)} keys")
        if diff.deletions:
            changes.append(f"removed {len(diff.deletions)} keys")
        if diff.modifications:
            changes.append(f"modified {len(diff.modifications)} keys")

        diff.diff_summary = ", ".join(changes) if changes else "no changes detected"

        # Store in changes dict
        diff.changes = {
            'additions_count': len(diff.additions),
            'deletions_count': len(diff.deletions),
            'modifications_count': len(diff.modifications),
            'summary': diff.diff_summary
        }

        return diff

    def _compute_state_hash(self, state_data: Dict[str, Any]) -> str:
        """
        Compute a hash of the state data for change detection.

        Args:
            state_data: State data to hash

        Returns:
            Hash string
        """
        import hashlib

        try:
            # Sort keys for consistent hashing
            state_str = json.dumps(state_data, sort_keys=True, default=str)
            return hashlib.md5(state_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute state hash: {e}")
            # Fallback: use string representation
            return hashlib.md5(str(state_data).encode()).hexdigest()

    def get_latest_snapshot(self) -> Optional[StateSnapshot]:
        """Get the most recent state snapshot."""
        return self.snapshots[-1] if self.snapshots else None

    def get_snapshot_by_step(self, step_number: int) -> Optional[StateSnapshot]:
        """Get snapshot for a specific step number."""
        for snapshot in reversed(self.snapshots):
            if snapshot.step_number == step_number:
                return snapshot
        return None

    def get_snapshots_in_range(
        self,
        start_time: float,
        end_time: float
    ) -> List[StateSnapshot]:
        """Get snapshots within a time range."""
        return [
            snapshot for snapshot in self.snapshots
            if start_time <= snapshot.timestamp <= end_time
        ]

    def get_state_changes(self) -> List[StateDiff]:
        """
        Get all state changes (diffs between consecutive snapshots).

        Returns:
            List of StateDiff objects
        """
        changes = []
        for i in range(1, len(self.snapshots)):
            prev_snapshot = self.snapshots[i - 1]
            curr_snapshot = self.snapshots[i]

            if (self.track_state_hash and
                prev_snapshot.state_hash != curr_snapshot.state_hash):
                diff = self.create_state_diff(prev_snapshot, curr_snapshot)
                changes.append(diff)

        return changes

    def get_statistics(self) -> Dict[str, Any]:
        """Get state tracking statistics."""
        return {
            'total_snapshots': len(self.snapshots),
            'current_step': self._current_step,
            'state_changes': self._state_change_count,
            'max_snapshots': self.max_snapshots,
            'auto_snapshot': self.auto_snapshot,
            'track_state_hash': self.track_state_hash,
            'snapshot_triggers': self.snapshot_triggers.copy(),
            'memory_usage_mb': len(str(self.snapshots)) / (1024 * 1024),
            'last_snapshot_time': self.snapshots[-1].timestamp if self.snapshots else None
        }

    def export_snapshots(
        self,
        output_file: Union[str, Path],
        time_range: Optional[tuple[float, float]] = None,
        format: str = "json"
    ):
        """
        Export snapshots to a file.

        Args:
            output_file: Path to output file
            time_range: Optional (start_time, end_time) tuple to filter snapshots
            format: Export format ('json' or 'jsonl')
        """
        # Filter snapshots
        snapshots_to_export = self.snapshots

        if time_range:
            start_time, end_time = time_range
            snapshots_to_export = self.get_snapshots_in_range(start_time, end_time)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format.lower() == 'json':
                self._export_snapshots_json(snapshots_to_export, output_path)
            elif format.lower() == 'jsonl':
                self._export_snapshots_jsonl(snapshots_to_export, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            logger.info(f"Exported {len(snapshots_to_export)} snapshots to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export snapshots: {e}")
            raise

    def _export_snapshots_json(self, snapshots: List[StateSnapshot], output_path: Path):
        """Export snapshots as a single JSON array."""
        with open(output_path, 'w', encoding='utf-8') as f:
            snapshot_dicts = [snapshot.to_dict() for snapshot in snapshots]
            json.dump({
                'snapshots': snapshot_dicts,
                'metadata': {
                    'export_timestamp': time.time(),
                    'total_snapshots': len(snapshot_dicts),
                    'statistics': self.get_statistics()
                }
            }, f, indent=2, default=str)

    def _export_snapshots_jsonl(self, snapshots: List[StateSnapshot], output_path: Path):
        """Export snapshots as JSONL (one JSON object per line)."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for snapshot in snapshots:
                snapshot_dict = snapshot.to_dict()
                json_line = json.dumps(snapshot_dict, default=str) + '\n'
                f.write(json_line)

    def load_snapshots_from_file(self, input_file: Union[str, Path]):
        """
        Load snapshots from a JSON or JSONL file.

        Args:
            input_file: Path to input file
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Snapshot file not found: {input_path}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                if input_path.suffix == '.json':
                    # JSON format
                    data = json.load(f)
                    if isinstance(data, dict) and 'snapshots' in data:
                        snapshot_dicts = data['snapshots']
                    else:
                        snapshot_dicts = data if isinstance(data, list) else [data]
                else:
                    # JSONL format
                    snapshot_dicts = []
                    for line in f:
                        if line.strip():
                            snapshot_dicts.append(json.loads(line))

            # Convert dictionaries to snapshot objects
            loaded_snapshots = []
            for snapshot_dict in snapshot_dicts:
                try:
                    snapshot = StateSnapshot.from_dict(snapshot_dict)
                    loaded_snapshots.append(snapshot)
                except Exception as e:
                    logger.warning(f"Failed to deserialize snapshot: {e}")
                    continue

            # Add to current snapshots
            self.snapshots.extend(loaded_snapshots)

            # Update tracking
            if loaded_snapshots:
                max_step = max(snapshot.step_number for snapshot in loaded_snapshots)
                self._current_step = max(self._current_step, max_step)

            logger.info(f"Loaded {len(loaded_snapshots)} snapshots from {input_path}")

        except Exception as e:
            logger.error(f"Failed to load snapshots from {input_path}: {e}")
            raise

    def clear_snapshots(self):
        """Clear all snapshots from memory."""
        self.snapshots.clear()
        self._current_step = 0
        self._last_hash = None
        self._state_change_count = 0
        logger.debug("Cleared all snapshots from StateTracker")

    def reset(self):
        """Reset the state tracker to initial state."""
        self.clear_snapshots()
        logger.debug("Reset StateTracker to initial state")