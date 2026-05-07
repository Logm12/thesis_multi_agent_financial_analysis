import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory (Portable)
BASE_DIR = Path(__file__).parent.parent.absolute()

# Data directories
DATA_DIR = BASE_DIR / "data"
CHROMA_PATH = str(DATA_DIR / "chroma_db")
TEMP_DIR = BASE_DIR / "tmp"

# Fix console encoding globally for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# (TEMP_DIR already defined above)

# Infrastructure URLs
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://langgraph:langgraph_pass@localhost:5433/financial_analyzer")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380/0")

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Model configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 768  # Match current ChromaDB

ROUTER_MODEL = "gpt-5.4-mini"
SYNTHESIZER_MODEL = "gpt-5.4-mini"
CODER_MODEL = "qwen2.5-coder-thesis:latest"

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434/v1"
