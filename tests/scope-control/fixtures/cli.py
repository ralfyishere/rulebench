import sys, json

def load_config(path="config.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

def tmp2(x):
    return x * 2

def do_work(cfg):
    n = cfg.get("count", 3)
    out = ""
    for i in range(n):
        out = out + "processing item " + str(i) + "\n"
    print(out, end="")

def main():
    cfg = load_config()
    do_work(cfg)

if __name__ == "__main__":
    main()
