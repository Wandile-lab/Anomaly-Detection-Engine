import subprocess
import logging

class FirewallBlocker:
    def __init__(self, whitelist):
        self.whitelist = whitelist

    def block_ip(self, ip):
        if ip in self.whitelist:
            print(f" WHITELIST: Refusing to block admin IP {ip}")
            return False

        try:
            # Check if already blocked (Return 0 means it exists)
            check = subprocess.run(["sudo", "iptables", "-C", "DOCKER-USER", "-s", ip, "-j", "DROP"], capture_output=True)
            if check.returncode == 0:
                return False 

            # Insert at the top (-I) of the DOCKER-USER chain
            subprocess.run(["sudo", "iptables", "-I", "DOCKER-USER", "-s", ip, "-j", "DROP"], check=True)
            print(f" BANNED in DOCKER-USER: {ip}")
            return True
        except Exception as e:
            print(f"Error blocking {ip}: {e}")
            return False

    def unblock_ip(self, ip):
        try:
            # Remove from DOCKER-USER
            subprocess.run(["sudo", "iptables", "-D", "DOCKER-USER", "-s", ip, "-j", "DROP"], check=True)
            print(f" UNBANNED from DOCKER-USER: {ip}")
            return True
        except Exception as e:
            print(f"Error unblocking {ip}: {e}")
            return False
