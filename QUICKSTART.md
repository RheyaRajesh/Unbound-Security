# Quick Start Guide

## 1. Setup (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "UNBOUND_API_KEY=your_key_here" > .env
echo "UNBOUND_API_BASE=https://api.unboundsecurity.com/v1" >> .env
```

## 2. Run the App

```bash
streamlit run app.py
```

## 3. Create Your First Workflow

### Example: Code Generation Workflow

**Step 1: Generate Code**
- Name: "Generate Calculator"
- Model: `gpt-3.5-turbo`
- Prompt: `Create a Python calculator class with add, subtract, multiply, and divide methods`
- Criteria: `class Calculator`
- Type: `contains`
- Context: `code_blocks`
- Retries: `3`

**Step 2: Add Tests**
- Name: "Add Unit Tests"
- Model: `gpt-3.5-turbo`
- Prompt: `Write comprehensive unit tests for this calculator class: {context will be auto-injected}`
- Criteria: `def test`
- Type: `contains`
- Context: `full`
- Retries: `3`

### Example: Data Processing Workflow

**Step 1: Extract Data**
- Name: "Extract JSON"
- Model: `gpt-3.5-turbo`
- Prompt: `Extract user information from this text: "John Doe, age 30, email: john@example.com"`
- Criteria: `{"name":`
- Type: `contains`
- Context: `full`
- Retries: `2`

**Step 2: Validate**
- Name: "Validate JSON"
- Model: `gpt-3.5-turbo`
- Prompt: `Validate this JSON and format it properly: {context}`
- Criteria: (leave empty or use `json` type)
- Type: `json`
- Context: `full`
- Retries: `2`

## 4. Tips

- **Start Simple**: Test with 2-3 steps first
- **Use Contains Criteria**: Easiest to get working quickly
- **Code Blocks Context**: Use `code_blocks` extraction when passing code between steps
- **Check Logs**: If a step fails, check the execution details to see why

## 5. Troubleshooting

**API Key Error?**
- Make sure `.env` file exists
- Or enter API key in the app when prompted

**Workflow Not Running?**
- Check that all steps have prompts
- Verify API key is valid
- Check execution logs for errors

**Criteria Not Passing?**
- Try `contains` type first (easiest)
- Make criteria string more specific
- Check the output in execution details
