import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class SlackNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    def send_alert(self, message):
        """Sends a simple text alert to Slack."""
        payload = {"text": f" *Anomaly Detected*🚨\n{message}"}
        
        try:
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                print(f"Error sending to Slack: {response.status_code}")
        except Exception as e:
            print(f"Failed to connect to Slack: {e}")
