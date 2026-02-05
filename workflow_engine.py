"""Workflow execution engine"""
import re
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from unbound_client import UnboundClient
from config import DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY


class CompletionChecker:
    """Handles completion criteria checking"""
    
    def __init__(self, unbound_client: UnboundClient):
        self.client = unbound_client
    
    def check(
        self,
        output: str,
        criteria: str,
        criteria_type: str = "string"
    ) -> Dict[str, Any]:
        """
        Check if output meets completion criteria
        
        Args:
            output: The LLM output to check
            criteria: The completion criteria
            criteria_type: One of "string", "regex", "llm", "json", "contains"
        
        Returns:
            Dict with 'passed' (bool) and 'reason' (str)
        """
        if criteria_type == "string":
            return self._check_string(output, criteria)
        elif criteria_type == "regex":
            return self._check_regex(output, criteria)
        elif criteria_type == "llm":
            return self.client.check_completion_with_llm(output, criteria)
        elif criteria_type == "json":
            return self._check_json(output)
        elif criteria_type == "contains":
            return self._check_contains(output, criteria)
        else:
            return {"passed": False, "reason": f"Unknown criteria type: {criteria_type}"}
    
    def _check_string(self, output: str, criteria: str) -> Dict[str, Any]:
        """Exact string match"""
        passed = output.strip() == criteria.strip()
        return {
            "passed": passed,
            "reason": "Exact match" if passed else "Strings do not match"
        }
    
    def _check_regex(self, output: str, pattern: str) -> Dict[str, Any]:
        """Regex pattern match"""
        try:
            passed = bool(re.search(pattern, output, re.MULTILINE | re.DOTALL))
            return {
                "passed": passed,
                "reason": f"Pattern {'matched' if passed else 'not found'}"
            }
        except re.error as e:
            return {"passed": False, "reason": f"Invalid regex: {str(e)}"}
    
    def _check_json(self, output: str) -> Dict[str, Any]:
        """Check if output is valid JSON"""
        try:
            json.loads(output)
            return {"passed": True, "reason": "Valid JSON"}
        except json.JSONDecodeError as e:
            return {"passed": False, "reason": f"Invalid JSON: {str(e)}"}
    
    def _check_contains(self, output: str, criteria: str) -> Dict[str, Any]:
        """Check if output contains the criteria string"""
        passed = criteria.lower() in output.lower()
        return {
            "passed": passed,
            "reason": f"'{criteria}' {'found' if passed else 'not found'} in output"
        }


class WorkflowEngine:
    """Executes workflows step by step"""
    
    def __init__(self, unbound_client: Optional[UnboundClient] = None):
        self.client = unbound_client or UnboundClient()
        self.checker = CompletionChecker(self.client)
    
    def execute_step(
        self,
        step: Dict[str, Any],
        context: str = "",
        step_index: int = 0,
        budget_cap: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Returns:
            Dict with 'status', 'output', 'tokens_used', 'attempts', etc.
        """
        # Build prompt with context
        prompt = step.get("prompt", "")
        if context and step_index > 0:
            # Check if prompt has placeholder, otherwise prepend context
            if "{context" in prompt.lower() or "{previous" in prompt.lower():
                # Replace common placeholder patterns
                prompt = prompt.replace("{context from previous step}", context)
                prompt = prompt.replace("{context}", context)
                prompt = prompt.replace("{previous step output}", context)
                prompt = prompt.replace("{previous_output}", context)
            else:
                # Prepend context if no placeholder found
                context_prompt = f"""Context from previous step:
{context}

"""
                prompt = context_prompt + prompt
        
        model = step.get("model", "gpt-3.5-turbo")
        max_retries = step.get("max_retries", DEFAULT_MAX_RETRIES)
        criteria = step.get("completion_criteria", "")
        criteria_type = step.get("criteria_type", "contains")
        context_extraction = step.get("context_extraction", "full")  # full, code_blocks, summary
        
        attempts = []
        last_output = ""
        step_cost = 0.0
        step_budget_cap = step.get("budget_cap") or budget_cap
        
        for attempt in range(max_retries + 1):
            # Check budget before attempting
            if step_budget_cap and step_cost >= step_budget_cap:
                return {
                    "status": "failed",
                    "output": last_output,
                    "attempts": attempts,
                    "tokens_used": sum(a.get("tokens_used", 0) for a in attempts),
                    "cost": step_cost,
                    "error": f"Budget cap of ${step_budget_cap:.4f} exceeded. Current cost: ${step_cost:.4f}"
                }
            
            # Call LLM
            result = self.client.call_llm(
                model=model,
                prompt=prompt,
                temperature=step.get("temperature", 0.7),
                max_tokens=step.get("max_tokens", 2000)
            )
            
            if "error" in result:
                attempts.append({
                    "attempt": attempt + 1,
                    "status": "error",
                    "output": "",
                    "error": result["error"],
                    "tokens_used": 0,
                    "cost": 0.0
                })
                if attempt == max_retries:
                    return {
                        "status": "failed",
                        "output": "",
                        "error": result["error"],
                        "attempts": attempts,
                        "tokens_used": 0,
                        "cost": step_cost
                    }
                time.sleep(DEFAULT_RETRY_DELAY)
                continue
            
            output = result["response"]
            last_output = output
            tokens_used = result.get("tokens_used", 0)
            attempt_cost = result.get("cost", 0.0)
            step_cost += attempt_cost
            
            # Check completion criteria
            if criteria:
                check_result = self.checker.check(output, criteria, criteria_type)
                passed = check_result["passed"]
            else:
                # No criteria = always pass
                passed = True
                check_result = {"passed": True, "reason": "No criteria specified"}
            
            attempts.append({
                "attempt": attempt + 1,
                "status": "passed" if passed else "failed",
                "output": output,
                "tokens_used": tokens_used,
                "cost": attempt_cost,
                "check_result": check_result
            })
            
            if passed:
                # Extract context for next step
                extracted_context = self._extract_context(output, context_extraction)
                
                return {
                    "status": "completed",
                    "output": output,
                    "extracted_context": extracted_context,
                    "attempts": attempts,
                    "tokens_used": tokens_used,
                    "cost": step_cost,
                    "check_result": check_result
                }
            
            # Failed, retry if attempts remaining
            if attempt < max_retries:
                time.sleep(DEFAULT_RETRY_DELAY)
        
        # All retries exhausted
        return {
            "status": "failed",
            "output": last_output,
            "attempts": attempts,
            "tokens_used": sum(a.get("tokens_used", 0) for a in attempts),
            "cost": step_cost,
            "error": f"Failed to meet completion criteria after {max_retries + 1} attempts"
        }
    
    def _extract_context(self, output: str, extraction_type: str) -> str:
        """Extract relevant context from output for next step"""
        if extraction_type == "full":
            return output
        elif extraction_type == "code_blocks":
            # Extract code blocks
            code_blocks = re.findall(r'```[\w]*\n(.*?)```', output, re.DOTALL)
            return "\n\n".join(code_blocks) if code_blocks else output
        elif extraction_type == "summary":
            # Use LLM to summarize (simplified - just return first 500 chars)
            return output[:500] + "..." if len(output) > 500 else output
        else:
            return output
    
    def execute_workflow(
        self,
        workflow: Dict[str, Any],
        progress_callback: Optional[callable] = None,
        workflow_budget_cap: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow
        
        Args:
            workflow: Workflow definition with steps
            progress_callback: Optional function to call with progress updates
        
        Returns:
            Dict with execution results
        """
        workflow_id = workflow.get("id", "unknown")
        steps = workflow.get("steps", [])
        
        execution = {
            "workflow_id": workflow_id,
            "workflow_name": workflow.get("name", "Unnamed"),
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "step_results": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "workflow_budget_cap": workflow_budget_cap
        }
        
        context = ""
        workflow_budget = workflow.get("budget_cap") or workflow_budget_cap
        
        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i+1}")
            
            # Check workflow budget before step
            if workflow_budget and execution["total_cost"] >= workflow_budget:
                execution["status"] = "failed"
                execution["failed_at_step"] = i + 1
                execution["completed_at"] = datetime.now().isoformat()
                execution["error"] = f"Workflow budget cap of ${workflow_budget:.4f} exceeded. Current cost: ${execution['total_cost']:.4f}"
                break
            
            if progress_callback:
                progress_callback({
                    "current_step": i + 1,
                    "total_steps": len(steps),
                    "step_name": step_name,
                    "status": "running"
                })
            
            step_result = self.execute_step(step, context, i, workflow_budget)
            step_result["step_index"] = i
            step_result["step_name"] = step_name
            execution["step_results"].append(step_result)
            execution["total_tokens"] += step_result.get("tokens_used", 0)
            execution["total_cost"] += step_result.get("cost", 0.0)
            
            if step_result["status"] == "failed":
                execution["status"] = "failed"
                execution["failed_at_step"] = i + 1
                execution["completed_at"] = datetime.now().isoformat()
                if progress_callback:
                    progress_callback({
                        "current_step": i + 1,
                        "total_steps": len(steps),
                        "step_name": step_name,
                        "status": "failed"
                    })
                break
            
            # Update context for next step
            context = step_result.get("extracted_context", step_result.get("output", ""))
        
        if execution["status"] == "running":
            execution["status"] = "completed"
            execution["completed_at"] = datetime.now().isoformat()
            if progress_callback:
                progress_callback({
                    "current_step": len(steps),
                    "total_steps": len(steps),
                    "status": "completed"
                })
        
        return execution
