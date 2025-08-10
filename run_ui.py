#!/usr/bin/env python3
"""
Launcher script for NYC Services GPT MVP UI

This script ensures proper Python path handling and launches the Streamlit interface.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit UI with proper configuration"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # Add src to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("📝 Please copy env.example to .env and configure your API keys")
        print("🔑 Required: OPENAI_API_KEY")
        print()
    
    # Check if vector store exists
    vector_db_path = project_root / "data" / "vector_db"
    if not vector_db_path.exists():
        print("⚠️  Vector database not found!")
        print("📚 Please run document processing first to create the vector store")
        print("💡 Try: python process_pdfs_targeted.py")
        print()
    
    # Launch Streamlit
    ui_path = src_path / "api" / "ui_streamlit.py"
    
    if not ui_path.exists():
        print(f"❌ UI file not found: {ui_path}")
        return 1
    
    print("🚀 Launching NYC Services GPT MVP UI...")
    print(f"📁 Project root: {project_root}")
    print(f"🔧 UI file: {ui_path}")
    print()
    print("💡 Tips:")
    print("   - Use the sidebar to configure feature flags")
    print("   - Try example questions to test the system")
    print("   - Monitor debug info for performance metrics")
    print()
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(ui_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\n👋 UI stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch UI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
