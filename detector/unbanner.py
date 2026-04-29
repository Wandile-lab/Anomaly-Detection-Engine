import time

class UnbanManager:
    def __init__(self, blocker, schedule):
        self.blocker = blocker
        self.schedule = schedule # [600, 1800, 7200]
        self.banned_ips = {} 

    def add_ban(self, ip):
        # Determine how many times they've been banned before
        count = self.banned_ips.get(ip, {}).get("ban_count", 0)
        
        # Get duration from schedule (if they keep attacking, it gets longer)
        index = min(count, len(self.schedule) - 1)
        duration = self.schedule[index]
        
        unban_at = time.time() + duration
        self.banned_ips[ip] = {
            "unban_at": unban_at,
            "ban_count": count + 1,
            "duration": duration
        }
        return duration

    def check_unbans(self):
        now = time.time()
        to_unban = []

        for ip, data in self.banned_ips.items():
            if now >= data["unban_at"]:
                to_unban.append(ip)

        for ip in to_unban:
            self.blocker.unblock_ip(ip)
            # Keep the ban_count so if they attack again, the next ban is longer
            self.banned_ips[ip]["unban_at"] = float('inf') 
            print(f" UNBANNED: {ip} has served their time.")
            
        return to_unban
