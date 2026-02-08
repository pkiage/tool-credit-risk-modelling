"""Multi-notebook Marimo ASGI server for HF Spaces deployment."""

from pathlib import Path

import marimo
import uvicorn

# Resolve notebooks directory: works both in the monorepo (apps/marimo/server.py)
# and in the flat HF Spaces layout (server.py alongside notebooks/).
_here = Path(__file__).parent
_candidates = [_here / "notebooks", _here.parent.parent / "notebooks"]
notebooks_dir = next((d for d in _candidates if d.is_dir()), _candidates[0])

server = marimo.create_asgi_app(quiet=True, include_code=True)

# Mount landing page at root
landing_page = notebooks_dir / "00_landing.py"
if landing_page.exists():
    server = server.with_app(path="/", root=str(landing_page))

# Mount other notebooks at their respective paths
for nb in sorted(notebooks_dir.glob("*.py")):
    if nb.stem != "00_landing":  # Skip landing page (already mounted at root)
        server = server.with_app(path=f"/{nb.stem}", root=str(nb))

app = server.build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)  # nosec B104 — Docker container requires binding to all interfaces
