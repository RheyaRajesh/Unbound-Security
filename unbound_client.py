"""Unbound API client for LLM calls"""
import requests
import json
from typing import Dict, Any, Optional
from config import UNBOUND_API_KEY, UNBOUND_API_BASE, MODEL_PRICING


class UnboundClient:
    """Client for interacting with Unbound API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or UNBOUND_API_KEY
        self.base_url = UNBOUND_API_BASE
        
    def call_llm(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Call the Unbound API with the specified model and prompt
        
        Returns:
            Dict with 'response', 'tokens_used', 'cost', etc.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract response text
            choices = data.get("choices", [])
            if not choices:
                return {
                    "response": "",
                    "error": "No choices in API response",
                    "tokens_used": 0,
                    "model": model
                }
            
            content = choices[0].get("message", {}).get("content", "")
            
            # Extract token usage
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            # Calculate cost
            cost = 0.0
            if model in MODEL_PRICING:
                pricing = MODEL_PRICING[model]
                input_cost = (prompt_tokens / 1000) * pricing["input"]
                output_cost = (completion_tokens / 1000) * pricing["output"]
                cost = input_cost + output_cost
            
            return {
                "response": content,
                "tokens_used": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost": cost,
                "model": model,
                "raw_response": data
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg)
                except:
                    pass
            return {
                "response": "",
                "error": error_msg,
                "tokens_used": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost": 0.0,
                "model": model
            }
    
    def check_completion_with_llm(
        self,
        output: str,
        criteria: str,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Use an LLM to check if output meets completion criteria
        
        Returns:
            Dict with 'passed' (bool) and 'reason' (str)
        """
        prompt = f"""You are evaluating whether an AI output meets specific completion criteria.

Output to evaluate:
{output}

Completion criteria:
{criteria}

Respond with a JSON object containing:
- "passed": true or false
- "reason": a brief explanation

Only respond with the JSON object, no other text."""

        result = self.call_llm(model, prompt, temperature=0.3, max_tokens=200)
        
        if "error" in result:
            return {"passed": False, "reason": f"Error checking criteria: {result['error']}"}
        
        try:
            # Try to extract JSON from response
            response_text = result["response"].strip()
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(response_text)
            return {
                "passed": evaluation.get("passed", False),
                "reason": evaluation.get("reason", "No reason provided")
            }
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: simple keyword check
            criteria_lower = criteria.lower()
            if "success" in criteria_lower and "success" in output.lower():
                return {"passed": True, "reason": "Found 'success' keyword"}
            return {"passed": False, "reason": f"Could not parse evaluation: {str(e)}"}
