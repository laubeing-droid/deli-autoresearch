"""P3 Research automation -- priority-ordered research task queue.

Provides ResearchTaskQueue: a heapq-backed priority queue that respects
dependency constraints and per-task max_concurrent limits when dequeuing.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchTask:
    """A research task with priority, dependency, and concurrency constraints.

    Fields:
        task_id: Unique identifier for this task.
        priority_score: Numeric priority (higher = more important).
        dependencies: List of task_ids that must be completed before this task can run.
        max_concurrent: Maximum number of concurrently running tasks allowed when
            this task is being considered for dequeue.
        metadata: Optional additional data attached to the task.
    """

    task_id: str
    priority_score: float
    dependencies: list[str] = field(default_factory=list)
    max_concurrent: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


class ResearchTaskQueue:
    """Priority queue for research tasks with dependency and concurrency awareness.

    Tasks are ordered by priority_score (descending). On dequeue, only tasks
    whose dependencies are all completed and whose max_concurrent limit is not
    yet reached are eligible. If the highest-priority eligible task cannot
    dequeue due to constraints, the algorithm scans down the priority order
    until it finds one that can -- this prevents head-of-line blocking.
    """

    def __init__(self) -> None:
        # Min-heap of (negated_priority, insertion_seq, ResearchTask).
        # Negating priority makes highest score come out first.
        self._heap: list[tuple[float, int, ResearchTask]] = []
        self._seq: int = 0
        self._task_map: dict[str, ResearchTask] = {}
        self._completed: set[str] = set()
        self._running: set[str] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enqueue(self, task: ResearchTask) -> None:
        """Add a task to the queue. Raises ValueError if task_id already exists."""
        if task.task_id in self._task_map:
            raise ValueError(f"Task '{task.task_id}' already enqueued")
        self._task_map[task.task_id] = task
        heapq.heappush(self._heap, (-task.priority_score, self._seq, task))
        self._seq += 1

    def dequeue(self) -> ResearchTask | None:
        """Remove and return the highest-priority eligible task.

        A task is eligible when:
          - All its dependency task_ids are in the completed set.
          - The number of currently running tasks is less than its max_concurrent.

        Returns None if no eligible task is found.
        """
        temp: list[tuple[float, int, ResearchTask]] = []
        result: ResearchTask | None = None

        while self._heap:
            _neg_pri, _seq, task = heapq.heappop(self._heap)

            # Skip tasks that have already been completed or are already running.
            if task.task_id in self._completed or task.task_id in self._running:
                continue

            if self._all_deps_met(task) and len(self._running) < task.max_concurrent:
                self._running.add(task.task_id)
                result = task
                break

            temp.append((-task.priority_score, _seq, task))

        # Restore tasks that were skipped back to the heap.
        for item in temp:
            heapq.heappush(self._heap, item)

        return result

    def peek(self) -> ResearchTask | None:
        """Return the highest-priority task without removing it.

        Does NOT apply dependency or concurrency filters -- this is the raw
        top of the priority heap.
        """
        if not self._heap:
            return None
        return self._heap[0][2]

    def status(self, task_id: str) -> str:
        """Return the current status of a task.

        Possible return values:
            'completed' -- task was marked completed.
            'running'   -- task was dequeued but not yet marked completed.
            'pending'   -- task is enqueued and not yet running/completed.
            'unknown'   -- task_id was never enqueued.
        """
        if task_id in self._completed:
            return "completed"
        if task_id in self._running:
            return "running"
        if task_id in self._task_map:
            return "pending"
        return "unknown"

    def mark_completed(self, task_id: str) -> None:
        """Move a task from running to completed, unlocking its dependents.

        Raises ValueError if task_id is not currently running.
        """
        if task_id not in self._running:
            raise ValueError(
                f"Task '{task_id}' is not running (status: {self.status(task_id)})"
            )
        self._running.discard(task_id)
        self._completed.add(task_id)

    def __len__(self) -> int:
        """Return the number of pending tasks currently in the heap."""
        return len(self._heap)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _all_deps_met(self, task: ResearchTask) -> bool:
        """Check whether every dependency of *task* has been completed."""
        return all(dep in self._completed for dep in task.dependencies)
