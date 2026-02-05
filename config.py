"""Configuration settings for the Agentic Workflow Builder"""
import os
from dotenv import load_dotenv

load_dotenv()

# Unbound API Configuration
UNBOUND_API_KEY = os.getenv("UNBOUND_API_KEY", "c87829d8a0dd941e60fa2a2e265728f039534d4061b36f6a572159678eab3bca8829550ada87bc4f496d150dc4d0420a")
UNBOUND_API_BASE = os.getenv("UNBOUND_API_BASE", "https://api.getunbound.ai/v1")

# Storage
WORKFLOWS_DIR = "workflows"
EXECUTIONS_DIR = "executions"

# Default settings
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2  # seconds

# Model pricing (cost per 1K tokens) - approximate pricing for kimi models
MODEL_PRICING = {
    "kimi-k2p5": {
        "input": 0.001,  # $0.001 per 1K input tokens
        "output": 0.002  # $0.002 per 1K output tokens
    },
    "kimi-k2-instruct-0905": {
        "input": 0.0005,  # $0.0005 per 1K input tokens
        "output": 0.001   # $0.001 per 1K output tokens
    }
}

# Default model (cheaper option)
DEFAULT_MODEL = "kimi-k2-instruct-0905"
