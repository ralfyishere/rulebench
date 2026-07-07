import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import old_fetch

def main():
    assert old_fetch("/ping")["via"] == "old"
    print("client test passed")

if __name__ == "__main__":
    main()
