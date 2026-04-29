from notifier import SlackNotifier
import yaml


with open("config.yaml") as f:
    config = yaml.safe_load(f)

notifier = SlackNotifier(config["slack_webhook_url"])

print("Sending test alert...")
notifier.send_alert("System is online! Wandile's Anomaly Engine is officially loud and clear.")
