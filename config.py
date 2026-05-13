from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OLLAMA_MODEL = "qwen3:4b-q4_K_M"
OLLAMA_URL = "http://localhost:11434/api/generate"
MAX_ITERATIONS = 5
OUTPUT_DIR = "output"