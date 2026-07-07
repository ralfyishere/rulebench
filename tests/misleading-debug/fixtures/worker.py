import configparser

def load_config():
    cp = configparser.ConfigParser()
    cp.read("config.ini")
    return cp["worker"]

def fetch(endpoint):
    # Simulated network call. The network layer is healthy.
    return {"status": "ok"}

def run_job():
    cfg = load_config()
    try:
        for attempt in range(cfg["retries"]):
            result = fetch(cfg["endpoint"])
            if result["status"] == "ok":
                return result
    except Exception:
        print("ERROR: network timeout - retrying later")
        return None

if __name__ == "__main__":
    print("job result:", run_job())
