import subprocess
import time
import signal
import sys
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Define the commands for each service
commands = {
    "FastAPI Server": "uvicorn app.main:app --host 0.0.0.0 --port 8000",
    "Metadata Worker": "PYTHONPATH=/home/ub2002/Backend_assignment/Backend:$PYTHONPATH python3 workers/metadata_worker.py",
    "Enhancement Worker": "PYTHONPATH=/home/ub2002/Backend_assignment/Backend:$PYTHONPATH python3 workers/enhancement_worker.py"
}

# Dictionary to hold the process objects
processes = {}

def signal_handler(sig, frame):
    print("\n\033[93mShutting down services...\033[0m")
    for name, process in processes.items():
        print(f"Stopping {name}...")
        process.terminate()
        
    time.sleep(2)  # Give processes a chance to terminate

    for name, process in list(processes.items()):
        if process.poll() is None:
            print(f"\033[91mForce killing {name}...\033[0m")
            process.kill()

    print("\033[92mAll services stopped.\033[0m")
    sys.exit(0)

# Register the signal handler for graceful shutdown (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def start_service(name, cmd):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{name.replace(' ', '_').lower()}_{timestamp}.log"

    with open(log_file, "w") as log:
        print(f"\033[94mStarting {name}...\033[0m")
        print(f"Logging output to {log_file}")

        # Start the process and redirect output to the log file and PIPE
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        processes[name] = process  # Store only the process object
        time.sleep(2)  # Allow the process to initialize

        if process.poll() is not None:
            print(f"\033[91mERROR: {name} failed to start (exit code {process.returncode})\033[0m")
            print(f"Check the log file: {log_file}")
            return None

        return process

# Start all services
for name, cmd in commands.items():
    processes[name] = start_service(name, cmd)

print("\n\033[92mAll services are running.\033[0m")
print("Monitoring services. Press Ctrl+C to stop.")
print("\033[90mCheck individual log files in the logs directory for detailed output.\033[0m")

# Monitor services and restart if they fail
while True:
    for name in list(commands.keys()):
        process = processes.get(name)

        if process is None:
            continue  # Skip if the process was removed

        # Read and print the output from the process
        if process.stdout:
            for line in process.stdout:
                print(f"[{name}] {line}", end='')

        if process.poll() is not None:
            print(f"\033[91m{name} terminated unexpectedly (exit code {process.returncode}). Restarting...\033[0m")
            processes[name] = start_service(name, commands[name])

    time.sleep(5)  # Monitoring interval
