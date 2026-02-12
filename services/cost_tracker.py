
import os
from datetime import datetime
from threading import Lock

# GPT-4o Pricing (approx)
COST_INPUT_1M = 2.50
COST_OUTPUT_1M = 10.00

LOG_FILE = "cost_log.txt"

class CostTracker:
    _lock = Lock()
    
    @staticmethod
    def track_cost(agent_name: str, input_tokens: int, output_tokens: int):
        cost_in = (input_tokens / 1_000_000) * COST_INPUT_1M
        cost_out = (output_tokens / 1_000_000) * COST_OUTPUT_1M
        total_cost = cost_in + cost_out
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = (
            f"[{timestamp}] [{agent_name}] "
            f"In: {input_tokens} | Out: {output_tokens} | "
            f"Cost: ${total_cost:.5f}\n"
        )
        
        with CostTracker._lock:
            try:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            except Exception as e:
                print(f"Failed to log cost: {e}")
        
        return total_cost

    @staticmethod
    def get_total_cost() -> float:
        """Parse log file to calculate total session cost."""
        total = 0.0
        if not os.path.exists(LOG_FILE):
            return 0.0
            
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "Cost: $" in line:
                        part = line.split("Cost: $")[-1].strip()
                        try:
                            total += float(part)
                        except:
                            pass
        except:
            pass
        return total
