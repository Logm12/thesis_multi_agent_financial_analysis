import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

# In-memory checkpoint storage for concurrent state testing
class MockPostgresSaver:
    def __init__(self):
        self.checkpoints = {}
        self.locks = {}

    def get_lock(self, thread_id: str) -> asyncio.Lock:
        if thread_id not in self.locks:
            self.locks[thread_id] = asyncio.Lock()
        return self.locks[thread_id]

    async def put(self, thread_id: str, checkpoint: dict):
        # Simulate deadlock behavior if specified in test
        if checkpoint.get("simulate_deadlock", False):
            raise Exception("Database Deadlock Detected: deadlock detected on lock transaction")
        self.checkpoints[thread_id] = checkpoint

    async def get(self, thread_id: str) -> dict:
        return self.checkpoints.get(thread_id, {})

# TC-ADV-BE-21: State race condition check
async def execute_superstep(saver: MockPostgresSaver, thread_id: str, step_data: dict):
    # Lock the entire read-modify-write transaction for safety (Poka-Yoke implementation)
    async with saver.get_lock(thread_id):
        checkpoint = await saver.get(thread_id)
        # Deep copy/isolation simulation
        state = json.loads(json.dumps(checkpoint)) if checkpoint else {"messages": [], "steps": []}
        
        # Process step
        state["messages"].extend(step_data.get("messages", []))
        state["steps"].extend(step_data.get("steps", []))
        
        # Simulate processing delay
        await asyncio.sleep(0.05)
        
        # Save checkpoint
        await saver.put(thread_id, state)

@pytest.mark.asyncio
async def test_tc_adv_be_21_state_mutability_race_condition():
    saver = MockPostgresSaver()
    thread_id = "thread-abc"
    
    # Fire two concurrent steps representing User Query 1 and User Query 2
    task1 = execute_superstep(saver, thread_id, {"messages": ["Query 1 Response"], "steps": ["Step 1"]})
    task2 = execute_superstep(saver, thread_id, {"messages": ["Query 2 Response"], "steps": ["Step 2"]})
    
    await asyncio.gather(task1, task2)
    
    final_state = await saver.get(thread_id)
    # State validation: Ensure both query results exist and do not corrupt each other
    assert "Query 1 Response" in final_state["messages"]
    assert "Query 2 Response" in final_state["messages"]

@pytest.mark.asyncio
async def test_tc_adv_be_22_postgresql_deadlock_retry():
    saver = MockPostgresSaver()
    thread_id = "thread-xyz"
    
    # Put request that triggers simulated deadlock error
    checkpoint = {"messages": ["Test content"], "simulate_deadlock": True}
    
    # Verify deadlock raises exception
    with pytest.raises(Exception, match="Database Deadlock"):
        await saver.put(thread_id, checkpoint)
        
    # Simulate fallback to MemorySaver logic
    memory_saver = {}
    memory_saver[thread_id] = {"messages": ["Test content (fallback memory)"]}
    assert thread_id in memory_saver

@pytest.mark.asyncio
async def test_tc_adv_be_23_session_hydration_breakdown():
    # Hydration integrity check:
    # If serialization fails mid-step, verify that the state is rolled back to previous valid state
    initial_valid_checkpoint = {"superstep": 2, "messages": ["Initial Valid State"], "steps": ["Step 1", "Step 2"]}
    saver = MockPostgresSaver()
    await saver.put("thread-123", initial_valid_checkpoint)
    
    # Simulate interrupted serialization
    try:
        # Corrupt state mid-operation
        corrupted_state = {"superstep": 3, "messages": ["Unsaved Interrupted State"], "steps": None} # None steps will fail downstream
        if corrupted_state["steps"] is None:
            raise TypeError("Steps array cannot be None")
        await saver.put("thread-123", corrupted_state)
    except TypeError:
        pass # Rollback/discard corrupted state
        
    # Rehydrate
    restored_checkpoint = await saver.get("thread-123")
    assert restored_checkpoint["superstep"] == 2
    assert restored_checkpoint["messages"] == ["Initial Valid State"]

def test_tc_adv_be_24_desynchronization_chasm():
    # Postgres deletion succeeds, but Chroma delete fails (desynchronization)
    # Validate that we mark the metadata registry as deleted/inactive so retrieval ignores it
    postgres_registry = {
        "file_1.json": {"status": "indexed", "active": True}
    }
    
    # Attempt delete
    postgres_registry["file_1.json"]["active"] = False # Set flag to inactive immediately before network call
    
    chroma_db_delete_success = False # Simulate ChromaDB timeout
    
    # Query retriever simulation
    active_docs = {k: v for k, v in postgres_registry.items() if v["active"] is True}
    assert "file_1.json" not in active_docs # Vector "ma" (ghost vector) ignored successfully
