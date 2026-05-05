import time
import os
import requests

# --- CONFIGURATION ---
# Target IP of the Raspberry Pi receiver
PI_IP = "192.168.137.16" 
URL = f"http://{PI_IP}:5000/log"

# Path to World of Warcraft logs
LOG_PATH = r"E:\World of Warcraft\_anniversary_\Logs"

def get_latest_log():
    """Returns the most recently modified log file in the directory."""
    try:
        files = [os.path.join(LOG_PATH, f) for f in os.listdir(LOG_PATH) if f.endswith(".txt")]
        return max(files, key=os.path.getmtime) if files else None
    except Exception as e:
        print(f"Error accessing directory: {e}")
        return None

def follow_log():
    """Tails the log file and streams new entries to the Pi via HTTP POST."""
    log_file = get_latest_log()
    
    if not log_file:
        print("Log source not found. Ensure /combatlog is enabled in-game.")
        return

    print(f"Tracking file: {log_file}")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        # Move pointer to the end of the file (tailing mode)
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1) # Idle CPU throttling
                continue
            
            # Monitoring output for local debugging
            print(f"Streaming: {line[:50].strip()}...") 
            
            try:
                # Synchronous POST request with 5s timeout for network stability
                requests.post(URL, data=line.encode('utf-8'), timeout=5.0)
            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}")

if __name__ == "__main__":
    print("Initializing WoW Log Streamer...")
    follow_log()