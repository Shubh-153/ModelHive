from orchestrator import run
from cleanup import cleanup

if __name__ == "__main__":
    cleanup()  # clean previous output first
    user_prompt = input("What web app do you want to build? ")
    run(user_prompt)
