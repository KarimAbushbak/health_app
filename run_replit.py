"""Start Streamlit for Replit (Run button and Deployments)."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    port = os.environ.get("PORT", "8080")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        port,
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false",
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
