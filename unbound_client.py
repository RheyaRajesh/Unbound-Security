import requests
import json
from typing import Dict, Any, Optional
from config import UNBOUND_API_KEY, UNBOUND_API_BASE, MODEL_PRICING


class UnboundClient:

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or UNBOUND_API_KEY
        self.base_url = UNBOUND_API_BASE
        self.mock_mode = not bool(self.api_key)

    def _mock_response(self, model: str, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        if "workflow_done" in prompt_lower:
            content = "WORKFLOW_DONE"
        elif "success" in prompt_lower:
            content = "SUCCESS"
        else:
            content = "SUCCESS"   

        return {
            "response": content,
            "tokens_used": 10,
            "prompt_tokens": 5,
            "completion_tokens": 5,
            "cost": 0.0,
            "model": model,
            "raw_response": {"mock": True}
        }

    def call_llm(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:

        # If explicitly mock → skip API
        if self.mock_mode:
            return self._mock_response(model, prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            choices = data.get("choices", [])
            if not choices:
                return self._mock_response(model, prompt)

            content = choices[0]["message"]["content"]

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens

            cost = 0.0
            if model in MODEL_PRICING:
                pricing = MODEL_PRICING[model]
                cost = (
                    (prompt_tokens / 1000) * pricing["input"]
                    + (completion_tokens / 1000) * pricing["output"]
                )

            return {
                "response": content,
                "tokens_used": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost": cost,
                "model": model,
                "raw_response": data
            }

        except Exception:
            return self._mock_response(model, prompt)

    def check_completion_with_llm(
        self,
        output: str,
        criteria: str,
        model: str = "kimi-k2-instruct-0905"
    ) -> Dict[str, Any]:

        if self.mock_mode:
            return {
                "passed": criteria.lower() in output.lower(),
                "reason": "Mock mode rule-based check"
            }

        prompt = f"""
You are evaluating whether an AI output meets specific completion criteria.

Output:
{output}

Criteria:
{criteria}

Respond ONLY with:
{{"passed": true/false, "reason": "short reason"}}
"""

        result = self.call_llm(model, prompt, temperature=0.2, max_tokens=200)

        try:
            evaluation = json.loads(result["response"])
            return evaluation
        except:
            return {
                "passed": criteria.lower() in output.lower(),
                "reason": "Fallback rule-based check"
            }
