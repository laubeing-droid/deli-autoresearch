"""Tests for deli_autoresearch.priority_queue -- ResearchTaskQueue."""

from __future__ import annotations

import pytest

from deli_autoresearch.priority_queue import ResearchTask, ResearchTaskQueue


class TestResearchTaskQueue:
    """10 tests covering basic operations, priority ordering, empty queue,
    dependency constraints, and concurrency limits."""

    # ------------------------------------------------------------------
    # 1. Basic enqueue + length
    # ------------------------------------------------------------------

    def test_enqueue_increases_length(self) -> None:
        """Enqueuing tasks increases the heap size."""
        q = ResearchTaskQueue()
        assert len(q) == 0
        q.enqueue(ResearchTask(task_id="a", priority_score=1.0))
        assert len(q) == 1
        q.enqueue(ResearchTask(task_id="b", priority_score=2.0))
        assert len(q) == 2

    # ------------------------------------------------------------------
    # 2. Priority ordering on dequeue
    # ------------------------------------------------------------------

    def test_dequeue_returns_highest_priority_first(self) -> None:
        """Tasks with higher priority_score are dequeued before lower ones."""
        q = ResearchTaskQueue()
        q.enqueue(ResearchTask(task_id="low", priority_score=0.1, max_concurrent=10))
        q.enqueue(ResearchTask(task_id="high", priority_score=10.0, max_concurrent=10))
        q.enqueue(ResearchTask(task_id="mid", priority_score=5.0, max_concurrent=10))

        first = q.dequeue()
        second = q.dequeue()
        third = q.dequeue()

        assert first is not None and first.task_id == "high"
        assert second is not None and second.task_id == "mid"
        assert third is not None and third.task_id == "low"

    # ------------------------------------------------------------------
    # 3. Empty queue returns None
    # ------------------------------------------------------------------

    def test_dequeue_empty_returns_none(self) -> None:
        """Dequeuing from an empty queue returns None."""
        q = ResearchTaskQueue()
        assert q.dequeue() is None

    def test_peek_empty_returns_none(self) -> None:
        """Peeking an empty queue returns None."""
        q = ResearchTaskQueue()
        assert q.peek() is None

    # ------------------------------------------------------------------
    # 4. Peek returns top without removing
    # ------------------------------------------------------------------

    def test_peek_returns_top_without_removing(self) -> None:
        """Peek returns the highest-priority task but does not dequeue it."""
        q = ResearchTaskQueue()
        q.enqueue(ResearchTask(task_id="first", priority_score=3.0))
        q.enqueue(ResearchTask(task_id="second", priority_score=7.0))

        top = q.peek()
        assert top is not None and top.task_id == "second"
        assert len(q) == 2  # both still present

    # ------------------------------------------------------------------
    # 5. Dependency constraint -- unmet deps block dequeue
    # ------------------------------------------------------------------

    def test_dependency_blocks_dequeue(self) -> None:
        """A task whose dependencies are not completed cannot be dequeued."""
        q = ResearchTaskQueue()
        q.enqueue(ResearchTask(
            task_id="child", priority_score=100.0,
            dependencies=["parent"],
        ))
        # Even though priority is max, dequeue returns None because parent
        # hasn't been completed.
        assert q.dequeue() is None

    def test_dependency_resolved_allows_dequeue(self) -> None:
        """Once a dependency is completed, the dependent task can dequeue."""
        q = ResearchTaskQueue()
        parent = ResearchTask(task_id="parent", priority_score=1.0)
        child = ResearchTask(
            task_id="child", priority_score=10.0,
            dependencies=["parent"],
        )
        q.enqueue(parent)
        q.enqueue(child)

        # Parent dequeues first (no deps).
        p = q.dequeue()
        assert p is not None and p.task_id == "parent"
        # Mark parent completed.
        q.mark_completed("parent")
        # Now child should be eligible.
        c = q.dequeue()
        assert c is not None and c.task_id == "child"

    # ------------------------------------------------------------------
    # 6. Concurrency limit blocks when running count >= max_concurrent
    # ------------------------------------------------------------------

    def test_concurrency_limit_blocks_dequeue(self) -> None:
        """When max_concurrent is reached, no more tasks can dequeue."""
        q = ResearchTaskQueue()
        # All tasks have max_concurrent=1, so only one can run at a time.
        q.enqueue(ResearchTask(
            task_id="a", priority_score=10.0, max_concurrent=1,
        ))
        q.enqueue(ResearchTask(
            task_id="b", priority_score=9.0, max_concurrent=1,
        ))

        first = q.dequeue()
        assert first is not None and first.task_id == "a"
        # a is now running; max_concurrent=1 blocks b.
        assert q.dequeue() is None

        # Complete a, then b should become eligible.
        q.mark_completed("a")
        second = q.dequeue()
        assert second is not None and second.task_id == "b"

    # ------------------------------------------------------------------
    # 7. Status tracking
    # ------------------------------------------------------------------

    def test_status_reflects_current_state(self) -> None:
        """status() returns correct state for each lifecycle phase."""
        q = ResearchTaskQueue()
        assert q.status("nonexistent") == "unknown"

        q.enqueue(ResearchTask(task_id="t1", priority_score=5.0))
        assert q.status("t1") == "pending"

        dequeued = q.dequeue()
        assert dequeued is not None
        assert q.status("t1") == "running"

        q.mark_completed("t1")
        assert q.status("t1") == "completed"

    # ------------------------------------------------------------------
    # 8. Duplicate enqueue raises
    # ------------------------------------------------------------------

    def test_duplicate_enqueue_raises_valueerror(self) -> None:
        """Enqueuing the same task_id twice raises ValueError."""
        q = ResearchTaskQueue()
        q.enqueue(ResearchTask(task_id="dup", priority_score=1.0))
        with pytest.raises(ValueError, match="already enqueued"):
            q.enqueue(ResearchTask(task_id="dup", priority_score=2.0))

    # ------------------------------------------------------------------
    # 9. Mark completed on non-running raises
    # ------------------------------------------------------------------

    def test_mark_completed_on_non_running_raises(self) -> None:
        """Calling mark_completed on a non-running task raises ValueError."""
        q = ResearchTaskQueue()
        q.enqueue(ResearchTask(task_id="t", priority_score=1.0))
        with pytest.raises(ValueError, match="not running"):
            q.mark_completed("t")  # still pending, not running

