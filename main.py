
#!/usr/bin/env python3
"""
AgentCraft - Specialized AI Agent Architecture
Main entry point for the application
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def print_banner():
    """Print AgentCraft banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                         🛠️  AgentCraft                           ║
    ║              Specialized AI Agent Architecture                   ║
    ║          Demonstrating domain expertise advantages               ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  Starting React Frontend (Port 3000) + FastAPI Backend (8000)   ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def install_node_dependencies():
    """Install Node.js dependencies if needed"""
    if not Path("node_modules").exists():
        print("📦 Installing Node.js dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True, capture_output=True)
            print("✅ Node.js dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Node.js dependencies: {e}")
            return False
        except FileNotFoundError:
            print("❌ Node.js/npm not found. Please install Node.js first.")
            print("   On Replit, Node.js should be automatically available.")
            return False
    return True

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting FastAPI backend on port 8000...")
    try:
        # Change to backend directory and start server
        backend_dir = Path("backend")
        if not backend_dir.exists():
            backend_dir.mkdir()
        
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", 
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Give backend time to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ FastAPI backend started successfully")
            return process
        else:
            print("❌ Failed to start FastAPI backend")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start React frontend development server"""
    print("🚀 Starting React frontend on port 3000...")
    
    # Set environment variables for React
    env = os.environ.copy()
    env['REACT_APP_API_URL'] = 'http://localhost:8000'
    env['PORT'] = '3000'
    env['HOST'] = '0.0.0.0'
    env['DANGEROUSLY_DISABLE_HOST_CHECK'] = 'true'
    
    try:
        process = subprocess.Popen(
            ["npm", "start"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print("✅ React frontend starting...")
        print("🌐 Frontend will be available at: http://localhost:3000")
        print("🔧 Backend API available at: http://localhost:8000")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def monitor_processes(backend_process, frontend_process):
    """Monitor both processes and handle cleanup"""
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down AgentCraft...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            # Check if processes are still running
            backend_running = backend_process and backend_process.poll() is None
            frontend_running = frontend_process and frontend_process.poll() is None
            
            if not backend_running and not frontend_running:
                print("❌ Both processes have stopped")
                break
            elif not backend_running:
                print("❌ Backend process has stopped")
                break
            elif not frontend_running:
                print("❌ Frontend process has stopped")
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    finally:
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()

def main():
    """Main entry point"""
    print_banner()
    
    # Check if we're in development mode
    if len(sys.argv) > 1 and sys.argv[1] == "--streamlit":
        print("🔄 Starting Streamlit version instead...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/demo/streamlit_dashboard.py",
            "--server.port", "5000",
            "--server.address", "0.0.0.0"
        ])
        return
    
    print("🔧 Setting up AgentCraft React + FastAPI stack...")
    
    # Install dependencies
    if not install_node_dependencies():
        print("❌ Cannot proceed without Node.js dependencies")
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot start frontend without backend")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        if backend_process:
            backend_process.terminate()
        return
    
    print("\n" + "="*70)
    print("🎉 AgentCraft is now running!")
    print("🌐 Open your browser to: http://localhost:3000")
    print("📡 API Documentation: http://localhost:8000/docs")
    print("💬 Interactive demo ready for Salesforce presentation")
    print("="*70 + "\n")
    
    # Monitor processes
    monitor_processes(backend_process, frontend_process)

if __name__ == "__main__":
    main()
