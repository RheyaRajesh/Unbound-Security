"""Streamlit frontend for Agentic Workflow Builder"""
import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from workflow_engine import WorkflowEngine
from storage import Storage
from unbound_client import UnboundClient
from config import UNBOUND_API_KEY

# Page config
st.set_page_config(
    page_title="Agentic Workflow Builder",
    page_icon="🤖",
    layout="wide"
)

# Session state will be initialized in main() function
# Available models (Unbound API)
AVAILABLE_MODELS = [
    "kimi-k2p5",
    "kimi-k2-instruct-0905"
]

CRITERIA_TYPES = [
    "contains",  # Output contains a string
    "regex",     # Output matches regex pattern
    "string",    # Exact string match
    "json",      # Valid JSON
    "llm"        # LLM evaluates criteria
]

CONTEXT_EXTRACTION_TYPES = [
    "full",        # Pass full output
    "code_blocks", # Extract only code blocks
    "summary"      # First 500 chars
]


def render_step_editor(step: Dict[str, Any], step_index: int) -> Dict[str, Any]:
    """Render UI for editing a single step"""
    with st.expander(f"Step {step_index + 1}: {step.get('name', 'Unnamed Step')}", expanded=True):
        name = st.text_input("Step Name", value=step.get("name", f"Step {step_index + 1}"), key=f"step_name_{step_index}")
        
        col1, col2 = st.columns(2)
        with col1:
            default_model = step.get("model", "kimi-k2-instruct-0905")
            model_index = AVAILABLE_MODELS.index(default_model) if default_model in AVAILABLE_MODELS else 0
            model = st.selectbox("Model", AVAILABLE_MODELS, 
                               index=model_index,
                               key=f"step_model_{step_index}")
        with col2:
            temperature = st.slider("Temperature", 0.0, 2.0, value=float(step.get("temperature", 0.7)), 
                                  key=f"step_temp_{step_index}", step=0.1)
        
        prompt = st.text_area("Prompt", value=step.get("prompt", ""), 
                            height=150, key=f"step_prompt_{step_index}",
                            placeholder="Enter the prompt for this step...")
        
        st.markdown("**Completion Criteria**")
        col1, col2 = st.columns([2, 1])
        with col1:
            criteria = st.text_input("Criteria", value=step.get("completion_criteria", ""),
                                    key=f"step_criteria_{step_index}",
                                    placeholder="e.g., 'SUCCESS' or regex pattern")
        with col2:
            criteria_type = st.selectbox("Type", CRITERIA_TYPES,
                                       index=CRITERIA_TYPES.index(step.get("criteria_type", "contains")) if step.get("criteria_type") in CRITERIA_TYPES else 0,
                                       key=f"step_criteria_type_{step_index}")
        
        col1, col2 = st.columns(2)
        with col1:
            context_extraction = st.selectbox("Context Extraction", CONTEXT_EXTRACTION_TYPES,
                                             index=CONTEXT_EXTRACTION_TYPES.index(step.get("context_extraction", "full")) if step.get("context_extraction") in CONTEXT_EXTRACTION_TYPES else 0,
                                             key=f"step_context_{step_index}",
                                             help="How to extract context for next step")
        with col2:
            max_retries = st.number_input("Max Retries", min_value=0, max_value=10,
                                         value=step.get("max_retries", 3),
                                         key=f"step_retries_{step_index}")
        
        # Handle None budget_cap values properly
        step_budget = step.get("budget_cap")
        if step_budget is None or step_budget == 0:
            step_budget = 0.0
        else:
            try:
                step_budget = float(step_budget)
            except (TypeError, ValueError):
                step_budget = 0.0
        
        budget_cap = st.number_input("Budget Cap ($)", min_value=0.0, max_value=1000.0,
                                    value=step_budget,
                                    step=0.01,
                                    key=f"step_budget_{step_index}",
                                    help="Maximum cost for this step (0 = no limit)")
        
        return {
            "name": name,
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "completion_criteria": criteria,
            "criteria_type": criteria_type,
            "context_extraction": context_extraction,
            "max_retries": max_retries,
            "max_tokens": step.get("max_tokens", 2000),
            "budget_cap": budget_cap if budget_cap > 0 else None
        }


def create_workflow_page():
    """Page for creating/editing workflows"""
    # Ensure session state is initialized
    if "storage" not in st.session_state:
        st.session_state.storage = Storage()
    if "engine" not in st.session_state:
        st.session_state.engine = WorkflowEngine()
    
    st.title("🤖 Agentic Workflow Builder")
    st.markdown("Create multi-step AI workflows that chain LLM calls together")
    
    # Check API key
    if not UNBOUND_API_KEY:
        st.warning("⚠️ UNBOUND_API_KEY not set. Please set it in your .env file or environment variables.")
        api_key = st.text_input("Enter Unbound API Key", type="password")
        if api_key:
            st.session_state.engine.client.api_key = api_key
    
    # Load or create workflow
    workflow_id = None
    try:
        workflow_id = st.query_params.get("workflow_id")
    except AttributeError:
        # Fallback for older Streamlit versions
        if "workflow_id" in st.session_state:
            workflow_id = st.session_state.workflow_id
    workflow = None
    
    if workflow_id:
        workflow = st.session_state.storage.load_workflow(workflow_id)
        if workflow:
            st.subheader(f"Editing: {workflow.get('name', 'Unnamed Workflow')}")
        else:
            st.error(f"Workflow {workflow_id} not found")
            workflow = None
    
    # Store workflow in session state to persist between reruns
    workflow_key = f"editing_workflow_{workflow_id or 'new'}"
    
    if workflow_id and workflow:
        # Editing existing workflow - load it
        if workflow_key not in st.session_state:
            st.session_state[workflow_key] = workflow.copy()
        workflow = st.session_state[workflow_key]
    else:
        # Creating new workflow
        if workflow_key not in st.session_state:
            st.session_state[workflow_key] = {
                "name": "My Workflow",
                "steps": [],
                "budget_cap": 0.0
            }
        workflow = st.session_state[workflow_key]
    
    # Update workflow name from input
    workflow_name = st.text_input("Workflow Name", value=workflow.get("name", "My Workflow"))
    workflow["name"] = workflow_name
    
    # Workflow-level budget cap - handle None values properly
    budget_cap_value = workflow.get("budget_cap")
    # If budget_cap is None or 0, use 0.0 for the input
    if budget_cap_value is None or budget_cap_value == 0:
        budget_cap_value = 0.0
    else:
        try:
            budget_cap_value = float(budget_cap_value)
        except (TypeError, ValueError):
            budget_cap_value = 0.0
    
    workflow_budget = st.number_input("Workflow Budget Cap ($)", min_value=0.0, max_value=10000.0,
                                     value=budget_cap_value,
                                     step=0.1,
                                     help="Maximum total cost for entire workflow (0 = no limit)")
    # Store as None only if explicitly 0, otherwise store the value
    workflow["budget_cap"] = None if workflow_budget == 0.0 else workflow_budget
    
    # Steps editor
    st.markdown("### Steps")
    
    if "steps" not in workflow:
        workflow["steps"] = []
    
    # Add step button
    if st.button("➕ Add Step"):
        workflow["steps"].append({
            "name": f"Step {len(workflow['steps']) + 1}",
            "model": "kimi-k2-instruct-0905",
            "prompt": "",
            "temperature": 0.7,
            "completion_criteria": "",
            "criteria_type": "contains",
            "context_extraction": "full",
            "max_retries": 3,
            "max_tokens": 2000,
            "budget_cap": None
        })
        st.rerun()
    
    # Render steps
    edited_steps = []
    for i, step in enumerate(workflow["steps"]):
        edited_step = render_step_editor(step, i)
        edited_steps.append(edited_step)
        
        # Delete step button
        if st.button("🗑️ Delete Step", key=f"delete_{i}"):
            workflow["steps"].pop(i)
            st.rerun()
    
    workflow["steps"] = edited_steps
    # Update session state with edited steps
    st.session_state[workflow_key] = workflow
    
    # Save workflow
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Workflow", type="primary", use_container_width=True):
            workflow["id"] = workflow_id or None
            saved_id = st.session_state.storage.save_workflow(workflow)
            st.success(f"Workflow saved! ID: {saved_id}")
            # Clear editing workflow from session state after saving
            if workflow_key in st.session_state:
                del st.session_state[workflow_key]
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("▶️ Run Workflow", use_container_width=True):
            if not workflow["steps"]:
                st.error("Add at least one step to run the workflow")
            else:
                # Make a copy for running
                workflow_copy = workflow.copy()
                workflow_copy["steps"] = [s.copy() for s in workflow["steps"]]
                st.session_state.run_workflow = workflow_copy
                st.rerun()


def run_workflow_page(workflow: Dict[str, Any]):
    """Page for running a workflow with real-time progress"""
    # Ensure session state is initialized
    if "storage" not in st.session_state:
        st.session_state.storage = Storage()
    if "engine" not in st.session_state:
        st.session_state.engine = WorkflowEngine()
    
    st.title("▶️ Running Workflow")
    st.markdown(f"**{workflow.get('name', 'Unnamed Workflow')}**")
    
    # Progress tracking
    progress_placeholder = st.empty()
    logs_placeholder = st.empty()
    
    # Execution state
    execution_state = {
        "current_step": 0,
        "total_steps": len(workflow["steps"]),
        "status": "running"
    }
    
    def progress_callback(progress: Dict[str, Any]):
        """Update progress in real-time"""
        execution_state.update(progress)
        st.session_state.execution_progress = progress
    
    # Run workflow
    workflow_budget = workflow.get("budget_cap")
    with st.spinner("Executing workflow..."):
        execution = st.session_state.engine.execute_workflow(workflow, progress_callback, workflow_budget)
    
    # Save execution
    execution_id = st.session_state.storage.save_execution(execution)
    execution["id"] = execution_id
    st.session_state.current_execution = execution
    
    # Display results
    st.markdown("### Execution Results")
    
    status_color = {
        "completed": "🟢",
        "failed": "🔴",
        "running": "🟡"
    }
    
    status_emoji = status_color.get(execution["status"], "⚪")
    st.markdown(f"**Status:** {status_emoji} {execution['status'].upper()}")
    
    if execution.get("failed_at_step"):
        st.error(f"Workflow failed at step {execution['failed_at_step']}")
    
    # Step results
    for i, step_result in enumerate(execution["step_results"]):
        step_name = step_result.get("step_name", f"Step {i+1}")
        status = step_result.get("status", "unknown")
        
        with st.expander(f"{step_name} - {status.upper()}", expanded=status == "failed"):
            # Attempts
            attempts = step_result.get("attempts", [])
            st.markdown(f"**Attempts:** {len(attempts)}")
            
            for attempt in attempts:
                attempt_status = attempt.get("status", "unknown")
                check_result = attempt.get("check_result", {})
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Attempt {attempt['attempt']}:** {attempt_status}")
                with col2:
                    st.markdown(f"Tokens: {attempt.get('tokens_used', 0)}")
                with col3:
                    cost = attempt.get('cost', 0.0)
                    st.markdown(f"Cost: ${cost:.4f}")
                
                if check_result:
                    passed = check_result.get("passed", False)
                    reason = check_result.get("reason", "")
                    st.markdown(f"Criteria: {'✅ Passed' if passed else '❌ Failed'} - {reason}")
                
                # Show output
                output = attempt.get("output", "")
                if output:
                    with st.expander(f"View Output (Attempt {attempt['attempt']})"):
                        st.code(output, language="text")
            
            # Final output
            if step_result.get("output"):
                st.markdown("**Final Output:**")
                st.code(step_result.get("output", ""), language="text")
            
            # Error if failed
            if step_result.get("error"):
                st.error(f"Error: {step_result.get('error')}")
    
    # Summary
    st.markdown("### Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Steps", len(execution["step_results"]))
    with col2:
        st.metric("Tokens Used", execution.get("total_tokens", 0))
    with col3:
        total_cost = execution.get("total_cost", 0.0)
        st.metric("Total Cost", f"${total_cost:.4f}")
    with col4:
        completed = sum(1 for s in execution["step_results"] if s.get("status") == "completed")
        st.metric("Steps Completed", f"{completed}/{len(execution['step_results'])}")
    
    # Budget info
    if execution.get("workflow_budget_cap"):
        budget_remaining = execution.get("workflow_budget_cap", 0) - total_cost
        if budget_remaining < 0:
            st.warning(f"⚠️ Budget exceeded! Cap: ${execution['workflow_budget_cap']:.4f}, Used: ${total_cost:.4f}")
        else:
            st.info(f"💰 Budget remaining: ${budget_remaining:.4f} out of ${execution['workflow_budget_cap']:.4f}")
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Workflows", use_container_width=True):
            if "run_workflow" in st.session_state:
                del st.session_state.run_workflow
            st.rerun()
    with col2:
        if st.button("📊 View Execution History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()


def workflows_list_page():
    """Page showing list of saved workflows"""
    # Ensure session state is initialized (defensive check for Streamlit Cloud)
    try:
        _ = st.session_state.storage
    except (AttributeError, KeyError):
        st.session_state.storage = Storage()
    
    try:
        _ = st.session_state.engine
    except (AttributeError, KeyError):
        st.session_state.engine = WorkflowEngine()
    
    st.title("📋 Saved Workflows")
    
    # Import/Export section
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📥 Import Workflow")
        uploaded_file = st.file_uploader("Upload workflow JSON", type=["json"], key="import_workflow")
        if uploaded_file:
            try:
                workflow_data = json.load(uploaded_file)
                workflow_id = st.session_state.storage.save_workflow(workflow_data)
                st.success(f"Workflow imported successfully! ID: {workflow_id}")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error importing workflow: {str(e)}")
    
    with col2:
        st.markdown("### 📤 Export All Workflows")
        if st.button("Download All Workflows as JSON"):
            workflows = st.session_state.storage.list_workflows()
            all_workflows = []
            for wf in workflows:
                full_wf = st.session_state.storage.load_workflow(wf["id"])
                if full_wf:
                    all_workflows.append(full_wf)
            
            json_str = json.dumps(all_workflows, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"workflows_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.divider()
    
    workflows = st.session_state.storage.list_workflows()
    
    if not workflows:
        st.info("No workflows saved yet. Create a new workflow to get started!")
        if st.button("➕ Create New Workflow"):
            st.session_state.page = "create"
            st.rerun()
        return
    
    # Create new workflow button and navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Create New Workflow", use_container_width=True):
            st.session_state.page = "create"
            st.rerun()
    with col2:
        if st.button("📊 View Execution History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
    
    # Display workflows
    for workflow_meta in workflows:

        # 🔥 LOAD FULL WORKFLOW TO GET NAME
        workflow = st.session_state.storage.load_workflow(workflow_meta["id"])
        if not workflow:
            continue

        name = workflow.get("name", "Unnamed Workflow")

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

            with col1:
                st.markdown(f"### {name}")
                st.caption(f"ID: {workflow_meta['id']} | Updated: {workflow_meta.get('updated_at', '')[:19]}")

            with col2:
                st.metric("Steps", len(workflow.get("steps", [])))

            with col3:
                if st.button("✏️ Edit", key=f"edit_{workflow_meta['id']}"):
                    try:
                        st.query_params["workflow_id"] = workflow_meta["id"]
                    except:
                        st.session_state.workflow_id = workflow_meta["id"]
                    st.session_state.page = "create"
                    st.rerun()

            with col4:
                col_run, col_export, col_del = st.columns(3)

                with col_run:
                    if st.button("▶️ Run", key=f"run_{workflow_meta['id']}"):
                        st.session_state.run_workflow = workflow
                        st.rerun()

                with col_export:
                    json_str = json.dumps(workflow, indent=2)
                    st.download_button(
                        label="📥",
                        data=json_str,
                        file_name=f"{name}_{workflow_meta['id']}.json",
                        mime="application/json",
                        key=f"export_{workflow_meta['id']}"
                    )

                with col_del:
                    if st.button("🗑️", key=f"del_{workflow_meta['id']}"):
                        st.session_state.storage.delete_workflow(workflow_meta["id"])
                        st.rerun()

        st.divider()


def execution_history_page():
    """Page showing execution history"""
    # Ensure session state is initialized
    if "storage" not in st.session_state:
        st.session_state.storage = Storage()
    if "engine" not in st.session_state:
        st.session_state.engine = WorkflowEngine()
    
    st.title("📊 Execution History")
    
    if st.button("← Back"):
        st.session_state.page = "workflows"
        st.rerun()
    
    workflow_id = None
    try:
        workflow_id = st.query_params.get("workflow_id")
    except AttributeError:
        if "workflow_id" in st.session_state:
            workflow_id = st.session_state.workflow_id
    executions = st.session_state.storage.list_executions(workflow_id)
    
    if not executions:
        st.info("No executions yet. Run a workflow to see execution history.")
        return
    
    for exec_info in executions:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                status_emoji = "🟢" if exec_info["status"] == "completed" else "🔴" if exec_info["status"] == "failed" else "🟡"
                st.markdown(f"### {status_emoji} Execution {exec_info['id'][:8]}")
                st.caption(f"Workflow: {exec_info.get('workflow_id', 'unknown')} | {exec_info.get('created_at', '')[:19]}")
            with col2:
                st.metric("Status", exec_info["status"].upper())
            with col3:
                st.metric("Steps", f"{exec_info.get('steps_completed', 0)}")
            with col4:
                if st.button("View Details", key=f"view_{exec_info['id']}"):
                    execution = st.session_state.storage.load_execution(exec_info["id"])
                    st.session_state.view_execution = execution
                    st.rerun()
            
            st.divider()


def main():
    """Main app router"""
    # Sidebar navigation
    with st.sidebar:
        st.title("🤖 Workflow Builder")
        st.markdown("---")
        
        page_options = {
            "📋 Workflows": "workflows",
            "➕ Create Workflow": "create",
            "📊 Execution History": "history"
        }
        
        selected = st.radio("Navigation", list(page_options.keys()))
        st.session_state.page = page_options[selected]
        
        st.markdown("---")
        st.markdown("### Quick Links")
        if st.button("📖 View README"):
            st.info("Check README.md for full documentation")
        if st.button("🚀 Quick Start"):
            st.info("Check QUICKSTART.md for examples")
        
        st.markdown("---")
        st.caption("Agentic Workflow Builder v1.0")
    
    # Check if we should run a workflow
    if "run_workflow" in st.session_state:
        run_workflow_page(st.session_state.run_workflow)
        return
    
    # Check if we should view an execution
    if "view_execution" in st.session_state:
        execution = st.session_state.view_execution
        st.title("📊 Execution Details")
        
        if st.button("← Back to History"):
            del st.session_state.view_execution
            st.session_state.page = "history"
            st.rerun()
        
        # Display execution details similar to run_workflow_page
        status_color = {
            "completed": "🟢",
            "failed": "🔴",
            "running": "🟡"
        }
        
        status_emoji = status_color.get(execution.get("status", "unknown"), "⚪")
        st.markdown(f"**Status:** {status_emoji} {execution.get('status', 'unknown').upper()}")
        st.markdown(f"**Workflow:** {execution.get('workflow_name', 'Unknown')}")
        st.markdown(f"**Started:** {execution.get('started_at', '')[:19]}")
        if execution.get("completed_at"):
            st.markdown(f"**Completed:** {execution.get('completed_at', '')[:19]}")
        
        if execution.get("failed_at_step"):
            st.error(f"Workflow failed at step {execution['failed_at_step']}")
        
        # Step results
        st.markdown("### Step Results")
        for i, step_result in enumerate(execution.get("step_results", [])):
            step_name = step_result.get("step_name", f"Step {i+1}")
            status = step_result.get("status", "unknown")
            
            with st.expander(f"{step_name} - {status.upper()}", expanded=status == "failed"):
                attempts = step_result.get("attempts", [])
                st.markdown(f"**Attempts:** {len(attempts)}")
                
                for attempt in attempts:
                    attempt_status = attempt.get("status", "unknown")
                    check_result = attempt.get("check_result", {})
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**Attempt {attempt['attempt']}:** {attempt_status}")
                    with col2:
                        st.markdown(f"Tokens: {attempt.get('tokens_used', 0)}")
                    with col3:
                        cost = attempt.get('cost', 0.0)
                        st.markdown(f"Cost: ${cost:.4f}")
                    
                    if check_result:
                        passed = check_result.get("passed", False)
                        reason = check_result.get("reason", "")
                        st.markdown(f"Criteria: {'✅ Passed' if passed else '❌ Failed'} - {reason}")
                    
                    output = attempt.get("output", "")
                    if output:
                        with st.expander(f"View Output (Attempt {attempt['attempt']})"):
                            st.code(output, language="text")
                
                # Step cost
                step_cost = step_result.get("cost", 0.0)
                if step_cost > 0:
                    st.markdown(f"**Step Cost:** ${step_cost:.4f}")
                
                if step_result.get("output"):
                    st.markdown("**Final Output:**")
                    st.code(step_result.get("output", ""), language="text")
                
                if step_result.get("error"):
                    st.error(f"Error: {step_result.get('error')}")
        
        # Summary
        st.markdown("### Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Steps", len(execution.get("step_results", [])))
        with col2:
            st.metric("Tokens Used", execution.get("total_tokens", 0))
        with col3:
            total_cost = execution.get("total_cost", 0.0)
            st.metric("Total Cost", f"${total_cost:.4f}")
        with col4:
            completed = sum(1 for s in execution.get("step_results", []) if s.get("status") == "completed")
            total = len(execution.get("step_results", []))
            st.metric("Steps Completed", f"{completed}/{total}")
        
        return
    
    # Route to appropriate page
    if st.session_state.page == "create":
        create_workflow_page()
    elif st.session_state.page == "history":
        execution_history_page()
    else:
        workflows_list_page()


if __name__ == "__main__":
    main()
