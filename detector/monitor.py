import time
import json

class LogMonitor:
    def __init__(self, log_file):
        self.log_file = log_file

    def follow(self):
        with open(self.log_file, "r") as f:
            f.seek(0, 2)  # go to end of file
            buffer = ""
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue

                buffer += line.strip()

                # Only attempt parse when we might have a complete object
                if buffer.endswith("}"):
                    try:
                        log = json.loads(buffer)
                        yield log
                        buffer = ""  # reset for next entry
                    except json.JSONDecodeError:
                        # Incomplete yet then keep accumulating
                        # But if buffer is getting huge, it's garbage then reset
                        if len(buffer) > 10_000:
                            buffer = ""
                elif buffer == "{" or buffer == "":
                    
                    pass
                else:
                    
                    pass
