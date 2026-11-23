import sys
from pathlib import Path

# Ensure project root is in sys.path for test discovery and imports across all environments
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
