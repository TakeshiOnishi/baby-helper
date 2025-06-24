import json

CACHE_PATH = '/tmp/switchbot_cache.json'

class TemperatureManager:
    def get_temp_hum(self):
        try:
            with open(CACHE_PATH, 'r') as f:
                cache = json.load(f)
                temp = cache['data'].get('temperature', '--')
                hum = cache['data'].get('humidity', '--')
                return temp, hum
        except Exception:
            return '--', '--' 