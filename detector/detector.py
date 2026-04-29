from collections import deque
import time

class AnomalyDetector:
    def __init__(self, baseline_manager):
        self.baseline = baseline_manager
        self.ip_windows = {}    # {ip: deque of timestamps}
        self.global_window = deque() 
        self.ip_errors = {}     # {ip: error_count_in_last_60s}
        self.window_size = 60   # seconds

    def _clean_window(self, window, now):
        """Removes timestamps older than 60 seconds from a deque."""
        while window and now - window[0] > self.window_size:
            window.popleft()

    def process_log(self, log):
        now = time.time()
        ip = log.get('source_ip')
        status = int(log.get('status', 200))
        
        
        if ip not in self.ip_windows:
            self.ip_windows[ip] = deque()

        # Add current request to windows
        self.ip_windows[ip].append(now)
        self.global_window.append(now)

        # Clean old data (Sliding Window logic)
        self._clean_window(self.ip_windows[ip], now)
        self._clean_window(self.global_window, now)

        # Error Surge Tracking
        if status >= 400:
            self.ip_errors[ip] = self.ip_errors.get(ip, 0) + 1
        else:
            # Gradually decay error count so it doesn't stay high forever
 
            if self.ip_errors.get(ip, 0) > 0:
                self.ip_errors[ip] -= 0.1 

        
        mean, stddev = self.baseline.get_stats()
        
        # Calculate IP-specific Z-Score
        current_ip_rate = len(self.ip_windows[ip])
        z_score = (current_ip_rate - mean) / stddev if stddev > 0 else 0
        
        # Threshold Logic (Z-Score > 3.0 OR Rate > 5x Mean)
        # Tighten to 1.5 if the IP is throwing too many errors
        threshold = 3.0
        if self.ip_errors.get(ip, 0) > 5: 
            threshold = 1.5 
            
        if z_score > threshold or current_ip_rate > (mean * 5):
            
            return True, f"Z-Score {z_score:.2f} (Threshold {threshold})", current_ip_rate, mean
            
        return False, None, current_ip_rate, mean
