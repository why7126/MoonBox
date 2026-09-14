"""Import the backend-shipped stdlib-only lifecycle contract for CLI usage."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src/backend"))
from app.governance.lifecycle import change_state, execution_metadata
