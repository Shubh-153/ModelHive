import asyncio
import os

def load_env_manual():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    # Strip potential quotes
                    if (value.startswith("\"") and value.endswith("\"")) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ[key] = value

load_env_manual()  # Load environment variables from .env manually BEFORE other imports

from orchestrator import run
from cleanup import cleanup

if __name__ == "__main__":
    cleanup()  # clean previous output first
    user_prompt = input("What web app do you want to build? ")
    asyncio.run(run(user_prompt))
