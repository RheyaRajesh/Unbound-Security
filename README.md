# Agentic Workflow Builder

A system for creating and executing multi-step AI workflows that chain LLM calls together. Each step can use different models, prompts, and completion criteria, with automatic context passing between steps.

## Features

- **Multi-step Workflows**: Create workflows with multiple sequential steps
- **Flexible Completion Criteria**: Support for string matching, regex, JSON validation, and LLM-based evaluation
- **Context Passing**: Automatically pass output from one step to the next (full output, code blocks, or summary)
- **Retry Logic**: Configurable retry attempts per step with automatic retry on failure
- **Real-time Progress**: Watch workflow execution in real-time
- **Execution History**: View past executions with detailed logs
- **Model Selection**: Choose from multiple LLM models per step

## Setup

### Prerequisites

- Python 3.8+
- Unbound API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Unbound Security"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root (optional - API key is already configured):
```env
UNBOUND_API_KEY=c87829d8a0dd941e60fa2a2e265728f039534d4061b36f6a572159678eab3bca8829550ada87bc4f496d150dc4d0420a
UNBOUND_API_BASE=https://api.getunbound.ai/v1
```

**Note:** The API key is already configured in `config.py`, so you can run the app immediately without setting up `.env`.

## Usage

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Creating a Workflow

1. Click "➕ Create New Workflow"
2. Enter a workflow name
3. Click "➕ Add Step" to add steps
4. For each step, configure:
   - **Step Name**: Descriptive name for the step
   - **Model**: LLM model to use (e.g., gpt-3.5-turbo, gpt-4)
   - **Prompt**: The prompt for this step
   - **Completion Criteria**: What indicates the step is complete
   - **Criteria Type**: How to check the criteria (contains, regex, json, llm)
   - **Context Extraction**: How to extract context for the next step
   - **Max Retries**: Number of retry attempts if criteria fails
5. Click "💾 Save Workflow" to save
6. Click "▶️ Run Workflow" to execute

### Example Workflow

**Step 1: Generate Code**
- Model: kimi-k2-instruct-0905
- Prompt: "Write a Python function to calculate factorial"
- Criteria: "def factorial"
- Type: contains
- Context: code_blocks

**Step 2: Add Tests**
- Model: kimi-k2-instruct-0905
- Prompt: "Write unit tests for this function: {context from step 1}"
- Criteria: "def test"
- Type: contains
- Context: full

### Completion Criteria Types

- **contains**: Output must contain the specified string
- **regex**: Output must match the regex pattern
- **string**: Output must exactly match the criteria
- **json**: Output must be valid JSON
- **llm**: Use another LLM call to evaluate if criteria are met

### Context Extraction

- **full**: Pass the entire output to the next step
- **code_blocks**: Extract only code blocks (between ```)
- **summary**: Pass first 500 characters

## Project Structure

```
.
├── app.py                 # Streamlit frontend
├── workflow_engine.py     # Workflow execution engine
├── unbound_client.py      # Unbound API client
├── storage.py             # Workflow and execution storage
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── workflows/            # Saved workflows (auto-created)
└── executions/           # Execution history (auto-created)
```

## API Integration

The application uses the Unbound API for all LLM calls. The API client expects:

- Endpoint: `{UNBOUND_API_BASE}/chat/completions`
- Method: POST
- Headers: `Authorization: Bearer {UNBOUND_API_KEY}`
- Body: Standard OpenAI-compatible chat completion format

**Note:** If the Unbound API uses a different endpoint structure, update `unbound_client.py` accordingly. The current implementation assumes OpenAI-compatible format, which is common for many LLM APIs.

## Workflow Storage

Workflows are stored as JSON files in the `workflows/` directory. Each workflow file contains:
- Workflow metadata (name, ID, timestamps)
- Step definitions (model, prompt, criteria, etc.)

Execution history is stored in the `executions/` directory with:
- Execution metadata
- Step-by-step results
- Token usage
- Error logs

## Example Workflow

An example workflow is included in `example_workflow.json`. You can import it using the "Import Workflow" feature in the app.

The example demonstrates a 3-step workflow:
1. Generate a Python calculator class
2. Add unit tests for the calculator
3. Create a requirements.txt file

## Deployment (Streamlit Cloud)

The app is ready for deployment on Streamlit Cloud:

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository
5. Set the main file path to `streamlit_app.py`
6. Add secrets in Streamlit Cloud dashboard:
   - `UNBOUND_API_KEY`: Your Unbound API key (optional if already in config.py)
7. Deploy!

The app will be accessible at `https://your-app-name.streamlit.app`

## Demo Video

[Link to demo video will be added here]

## Bonus Features Implemented

- ✅ **Hosting**: Ready for Streamlit Cloud deployment
- ✅ **Retry Budget**: Configurable retry limit per step with graceful failure handling
- ✅ **Cost Tracking**: Token usage and cost tracking per step and workflow with budget caps
- ✅ **Budget Caps**: Set budget limits per step and per workflow
- ✅ **Workflow Export/Import**: Workflows stored as JSON files can be easily shared
- ⏳ **Auto Model Selection**: (Future enhancement)
- ⏳ **Alert on Completion**: (Future enhancement)
- ⏳ **Parallel Steps**: (Future enhancement)
- ⏳ **Branching Workflows**: (Future enhancement)

## Troubleshooting

### API Key Issues
If you see "UNBOUND_API_KEY not set", make sure:
1. Your `.env` file exists and contains `UNBOUND_API_KEY=your_key`
2. Or enter the API key in the app when prompted

### Workflow Execution Fails
- Check that your API key is valid
- Verify the Unbound API endpoint is accessible
- Review the execution logs in the app for detailed error messages

## License

This project was created for a hackathon challenge.
