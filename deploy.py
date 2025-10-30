import subprocess
import time
import urllib.request
import zipfile
import os

def run_flask_app():
    # Run Flask app in the background using Popen
    print("Starting Flask app...")
    flask_process = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return flask_process

def create_localtunnel():
    try:
        # Check if npm is installed
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        print("npm is available.")

        # Install localtunnel globally if not installed
        try:
            subprocess.run(['npm', 'list', '-g', 'localtunnel'], check=True, capture_output=True)
            print("localtunnel is already installed.")
        except subprocess.CalledProcessError:
            print("Installing localtunnel...")
            subprocess.run(['npm', 'install', '-g', 'localtunnel'], check=True)

        # Start localtunnel
        print("Starting localtunnel...")
        tunnel_process = subprocess.Popen(['lt', '--port', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for tunnel to start and capture URL
        time.sleep(5)
        stdout, stderr = tunnel_process.communicate(timeout=15)
        if tunnel_process.returncode == 0:
            # Parse the tunnel URL from stdout
            lines = stdout.split('\n')
            for line in lines:
                if 'https://' in line and '.loca.lt' in line:
                    url = line.strip()
                    print(f"Tunnel URL: {url}")
                    break
        else:
            print("Error creating tunnel:", stderr)

        return tunnel_process

    except subprocess.CalledProcessError:
        print("npm not installed or localtunnel failed. Please install Node.js and npm.")
        print("Alternative: Download ngrok from https://ngrok.com/download and run 'ngrok http 5000'")
        return None
    except Exception as e:
        print("Failed to use localtunnel:", str(e))
        return None

if __name__ == "__main__":
    flask_process = run_flask_app()
    time.sleep(2)  # Wait for Flask to start
    tunnel_process = create_localtunnel()

    # Keep the script running to maintain the tunnel
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        if tunnel_process:
            tunnel_process.terminate()
        flask_process.terminate()
