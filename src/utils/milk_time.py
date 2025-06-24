from datetime import datetime

MILK_TIME_PATH = '/tmp/milk_time.txt'

class MilkTimeManager:
    def get_milk_time(self):
        try:
            with open(MILK_TIME_PATH, 'r') as f:
                milk_time_str = f.read().strip()
                return datetime.strptime(milk_time_str, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return None

    def format_time_ago(self, milk_time):
        if milk_time is None:
            return "No milk time data"
        
        now = datetime.now()
        diff = now - milk_time
        
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        
        return f"MILK: {hours:02d}h{minutes:02d}m{seconds:02d}s" 