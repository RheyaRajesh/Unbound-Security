🚀 Agentic Workflow Builder

✨ Design, chain, and automate multi-step AI workflows with ease

A lightweight system to build sequential LLM pipelines where each step can use different models, prompts, completion rules, and automatically pass context to the next step.

🧠 Perfect For

Prompt engineering

Iterative AI tasks

Code generation & testing

Evaluation pipelines

Agent-style workflows

🌟 Features

✅ Multi-step sequential workflows

✅ Flexible completion checks (String, Regex, JSON, LLM)

✅ Automatic context passing between steps

✅ Retry logic with configurable attempts

✅ Real-time execution tracking

✅ Execution history with logs

✅ Per-step model selection

✅ Token usage & cost tracking

✅ Workflow import/export (JSON sharing)

🛠️ Setup
📋 Prerequisites

Python 3.8+

Unbound API key

📦 Installation
git clone <repository-url>
cd "Unbound Security"
pip install -r requirements.txt

🔐 Environment Setup (Optional)

Create a .env file:

UNBOUND_API_KEY=your_key_here
UNBOUND_API_BASE=https://api.getunbound.ai/v1


💡 The API key is already configured in config.py, so this step is optional.

▶️ Run the App
streamlit run app.py


Open in browser:

http://localhost:8501

🧩 Creating a Workflow

➕ Create new workflow

Add steps

Configure each step:

Model

Prompt

Completion criteria

Criteria type

Context extraction

Retry count

Save

▶️ Run

💡 Example Workflow
Step 1 — Generate Code

Model: kimi-k2-instruct-0905

Prompt: Write a Python factorial function

Criteria: contains "def factorial"

Context: code_blocks

Step 2 — Add Tests

Prompt uses previous step output

Criteria: contains "def test"

Context: full

🚀 Agentic Workflow Builder

✨ Design, chain, and automate multi-step AI workflows with ease

A lightweight system to build sequential LLM pipelines where each step can use different models, prompts, completion rules, and automatically pass context to the next step.

🧠 Perfect For

Prompt engineering

Iterative AI tasks

Code generation & testing

Evaluation pipelines

Agent-style workflows

🌟 Features

✅ Multi-step sequential workflows

✅ Flexible completion checks (String, Regex, JSON, LLM)

✅ Automatic context passing between steps

✅ Retry logic with configurable attempts

✅ Real-time execution tracking

✅ Execution history with logs

✅ Per-step model selection

✅ Token usage & cost tracking

✅ Workflow import/export (JSON sharing)

🛠️ Setup
📋 Prerequisites

Python 3.8+

Unbound API key

📦 Installation
git clone <repository-url>
cd "Unbound Security"
pip install -r requirements.txt

🔐 Environment Setup (Optional)

Create a .env file:

UNBOUND_API_KEY=your_key_here
UNBOUND_API_BASE=https://api.getunbound.ai/v1


💡 The API key is already configured in config.py, so this step is optional.

▶️ Run the App
streamlit run app.py


Open in browser:

http://localhost:8501

🧩 Creating a Workflow

➕ Create new workflow

Add steps

Configure each step:

Model

Prompt

Completion criteria

Criteria type

Context extraction

Retry count

Save

▶️ Run

💡 Example Workflow
Step 1 — Generate Code

Model: kimi-k2-instruct-0905

Prompt: Write a Python factorial function

Criteria: contains "def factorial"

Context: code_blocks

Step 2 — Add Tests

Prompt uses previous step output

Criteria: contains "def test"

Context: full

💾 Storage
Workflows

workflows/ → workflow definitions (JSON)

Executions

executions/ → logs, outputs, tokens, errors

🏆 Bonus Features

✅ Hosting ready (Streamlit Cloud)

✅ Retry budgets

✅ Cost tracking

✅ Budget caps

✅ Workflow import/export

⏳ Parallel steps (planned)

⏳ Branching workflows (planned)

⏳ Auto model selection (planned)

🚀 Deployment (Streamlit Cloud)

Push project to GitHub

Visit https://share.streamlit.io

Select repository

Set main file → streamlit_app.py

Add API key in Secrets

Deploy

🐛 Troubleshooting
API Issues

Check API key

Verify endpoint

Confirm network access

Workflow Failures

Review execution logs

Validate completion criteria

Check prompt formatting

📜 License

Built for a Hackathon 🚀
