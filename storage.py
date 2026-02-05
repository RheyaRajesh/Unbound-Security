"""Storage layer for workflows and executions"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from config import WORKFLOWS_DIR, EXECUTIONS_DIR


class Storage:
    """Handles persistence of workflows and execution history"""
    
    def __init__(self):
        self.workflows_dir = Path(WORKFLOWS_DIR)
        self.executions_dir = Path(EXECUTIONS_DIR)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create storage directories if they don't exist"""
        self.workflows_dir.mkdir(exist_ok=True)
        self.executions_dir.mkdir(exist_ok=True)
    
    def save_workflow(self, workflow: Dict[str, Any]) -> str:
        """Save a workflow and return its ID"""
        workflow_id = workflow.get("id") or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        workflow["id"] = workflow_id
        workflow["updated_at"] = datetime.now().isoformat()
        
        file_path = self.workflows_dir / f"{workflow_id}.json"
        with open(file_path, "w") as f:
            json.dump(workflow, f, indent=2)
        
        return workflow_id
    
    def load_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load a workflow by ID"""
        file_path = self.workflows_dir / f"{workflow_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all saved workflows"""
        workflows = []
        for file_path in self.workflows_dir.glob("*.json"):
            with open(file_path, "r") as f:
                workflow = json.load(f)
                workflows.append({
                    "id": workflow.get("id", file_path.stem),
                    "name": workflow.get("name", "Unnamed Workflow"),
                    "updated_at": workflow.get("updated_at", ""),
                    "steps_count": len(workflow.get("steps", []))
                })
        
        # Sort by updated_at descending
        workflows.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return workflows
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        file_path = self.workflows_dir / f"{workflow_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def save_execution(self, execution: Dict[str, Any]) -> str:
        """Save an execution record"""
        execution_id = execution.get("id") or f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        execution["id"] = execution_id
        execution["created_at"] = datetime.now().isoformat()
        
        file_path = self.executions_dir / f"{execution_id}.json"
        with open(file_path, "w") as f:
            json.dump(execution, f, indent=2)
        
        return execution_id
    
    def load_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Load an execution by ID"""
        file_path = self.executions_dir / f"{execution_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def list_executions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all executions, optionally filtered by workflow_id"""
        executions = []
        for file_path in self.executions_dir.glob("*.json"):
            with open(file_path, "r") as f:
                execution = json.load(f)
                if workflow_id is None or execution.get("workflow_id") == workflow_id:
                    executions.append({
                        "id": execution.get("id", file_path.stem),
                        "workflow_id": execution.get("workflow_id", ""),
                        "status": execution.get("status", "unknown"),
                        "created_at": execution.get("created_at", ""),
                        "steps_completed": sum(1 for s in execution.get("step_results", []) if s.get("status") == "completed")
                    })
        
        executions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return executions
