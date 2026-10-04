import sys
import os

def check_env():
    print("Checking environment variables...")
    required = ["TRONGRID_API_KEY"]
    for req in required:
        if not os.environ.get(req):
            print(f"WARNING: {req} is not set. Some features may be rate limited.")
        else:
            print(f"OK: {req} is set.")

def check_db():
    print("Checking database connection...")
    print("OK: Database connection successful (simulated).")

def main():
    print("=== ChainNetra Preflight Check ===")
    check_env()
    check_db()
    print("Preflight complete. Ready for demo.")
    sys.exit(0)

if __name__ == "__main__":
    main()
