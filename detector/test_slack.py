from notifier import SlackNotifier

notifier = SlackNotifier()

print("Sending test alert...")
notifier.send_alert("System is online! Wandile's Anomaly Engine is officially loud and clear.")
