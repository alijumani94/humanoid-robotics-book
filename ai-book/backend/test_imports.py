"""Quick import test to verify all modules can be imported."""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")
errors = []

# Test config
try:
    from app.config import Settings
    print("[OK] app.config")
except Exception as e:
    errors.append(f"[FAIL] app.config: {e}")
    print(f"[FAIL] app.config: {e}")

# Test models
try:
    from app.models.schemas import ChatRequest, ChatResponse
    print("[OK] app.models.schemas")
except Exception as e:
    errors.append(f"[FAIL] app.models.schemas: {e}")
    print(f"[FAIL] app.models.schemas: {e}")

try:
    from app.models.database import User, ChatHistory, Chunk
    print("[OK] app.models.database")
except Exception as e:
    errors.append(f"[FAIL] app.models.database: {e}")
    print(f"[FAIL] app.models.database: {e}")

# Test utils
try:
    from app.utils.chunking import chunk_text, TextChunk
    print("[OK] app.utils.chunking")
except Exception as e:
    errors.append(f"[FAIL] app.utils.chunking: {e}")
    print(f"[FAIL] app.utils.chunking: {e}")

try:
    from app.utils.validators import sanitize_input, validate_input
    print("[OK] app.utils.validators")
except Exception as e:
    errors.append(f"[FAIL] app.utils.validators: {e}")
    print(f"[FAIL] app.utils.validators: {e}")

# Summary
print("\n" + "="*50)
if errors:
    print(f"FAILED: {len(errors)} import errors")
    for error in errors:
        print(f"  {error}")
else:
    print("SUCCESS: All imports working!")
print("="*50)
