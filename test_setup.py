"""Simple test script to verify setup"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import streamlit: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import requests: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False
    
    return True

def test_local_imports():
    """Test that local modules can be imported"""
    try:
        from config import UNBOUND_API_KEY, UNBOUND_API_BASE
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from storage import Storage
        storage = Storage()
        print("✅ Storage module imported and initialized successfully")
    except Exception as e:
        print(f"❌ Failed to import/initialize storage: {e}")
        return False
    
    try:
        from unbound_client import UnboundClient
        client = UnboundClient()
        print("✅ UnboundClient imported successfully")
    except Exception as e:
        print(f"❌ Failed to import UnboundClient: {e}")
        return False
    
    try:
        from workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        print("✅ WorkflowEngine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import WorkflowEngine: {e}")
        return False
    
    return True

def test_directories():
    """Test that storage directories can be created"""
    try:
        from storage import Storage
        storage = Storage()
        if storage.workflows_dir.exists():
            print("✅ Workflows directory exists")
        else:
            print("⚠️  Workflows directory will be created on first use")
        
        if storage.executions_dir.exists():
            print("✅ Executions directory exists")
        else:
            print("⚠️  Executions directory will be created on first use")
        
        return True
    except Exception as e:
        print(f"❌ Error checking directories: {e}")
        return False

def main():
    print("Running setup tests...\n")
    
    all_passed = True
    
    print("1. Testing external imports...")
    if not test_imports():
        all_passed = False
    print()
    
    print("2. Testing local imports...")
    if not test_local_imports():
        all_passed = False
    print()
    
    print("3. Testing directory structure...")
    if not test_directories():
        all_passed = False
    print()
    
    if all_passed:
        print("✅ All tests passed! Setup looks good.")
        print("\nNext steps:")
        print("1. Set UNBOUND_API_KEY in .env file")
        print("2. Run: streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
