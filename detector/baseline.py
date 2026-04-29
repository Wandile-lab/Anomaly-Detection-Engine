import datetime
import numpy as np
from collections import deque

class BaselineManager:
    def __init__(self):
        # 24 slots (0-23), each holding a history of traffic counts
        # Maxlen=1800 means we keep the last 30 minutes of data (1800 seconds)
        self.hourly_slots = {i: deque(maxlen=1800) for i in range(24)}
        
        # Floor values to prevent math errors (Mean cannot be 0)
        self.effective_mean = 1.0
        self.effective_stddev = 0.5

    def update(self, count):
        """Adds the current traffic count to the correct hourly slot."""
        current_hour = datetime.datetime.now().hour
        self.hourly_slots[current_hour].append(count)

    def recalculate(self):
        """
        Compute mean and stddev from the current hour's rolling 30-minute window.
        Requirement: Recalculated every 60 seconds.
        """
        current_hour = datetime.datetime.now().hour
        data = list(self.hourly_slots[current_hour])
        
        # At least 30 seconds of data to form a 'baseline'
        if len(data) > 30:
            self.effective_mean = max(float(np.mean(data)), 1.0)
            self.effective_stddev = max(float(np.std(data)), 0.5)
        
        return self.effective_mean, self.effective_stddev

    def get_stats(self):
        """Returns the current 'learned' values for the current hour."""
        return self.effective_mean, self.effective_stddev
