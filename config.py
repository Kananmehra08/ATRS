"""Central configuration settings for the ATRS requirements study.

All pipeline scripts import settings from this module.
API credentials and environment variables are loaded automatically from .env.
Ensure all path configurations use os.path for cross-platform compatibility (Windows, macOS, Linux).
"""
import os
import sys

# ------------------------------------------------------------
# Automatic .env File Loader (Zero external dependencies)
# ------------------------------------------------------------
def _load_env_file(env_path: str = None) -> None:
    """Load key-value pairs from .env into os.environ if not already present."""
    if env_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, ".env")
    
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("\"'").strip()
                        # Do not overwrite existing environment variables set by host
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

# Base paths
DATA_DIR = os.getenv("ATRS_DATA_DIR", "data")
OUT_DIR = os.getenv("ATRS_OUT_DIR", "outputs")
TEXTS_DIR = os.path.join(DATA_DIR, "texts")
USAGE_LOG_PATH = os.path.join(DATA_DIR, "usage_log.csv")

# Reproducibility seed
SEED = 42

# Sampling and dataset parameters
N_CANDIDATES = 70             # Records sampled from the ATRS metadata index
N_FINAL = 40                  # Final sample size evenly spaced across completeness (proposal target: 30-50)
MIN_WORDS = 300               # Drop records with fewer words than this threshold

# LLM API Keys & Provider Settings (Loaded strictly from .env or system environment)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Active provider: 'gemini' (preferred when Gemini key is present) or 'anthropic'
if GEMINI_API_KEY:
    PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    MODEL = os.getenv("LLM_MODEL", "gemini-3.6-flash")
else:
    PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
    MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")

TEMPERATURE = 0.0             # Deterministic generation
MAX_TOKENS = 4000
MAX_SOURCE_CHARS = 60000      # Truncation cap for very long source texts to prevent context overflow

# Evaluation and annotation settings
DOUBLE_ANNOTATE_FRACTION = 0.20  # 20% subset scored by Rater B for inter-rater agreement (Cohen's kappa)
