from pyngrok import ngrok
import time

# Set your ngrok auth token if you have one (optional, but recommended for more features)
# ngrok.set_auth_token("YOUR_AUTH_TOKEN")

# Start ngrok tunnel on port 5000 (default Flask port)
public_url = ngrok.connect(5000)
print(f"Public URL: {public_url}")

# Keep the tunnel open
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ngrok.disconnect(public_url)
    print("Tunnel closed")
