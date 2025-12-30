#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
echo "➡️ Installing Playwright Chromium..."
playwright install chromium --with-deps
echo "✅ Playwright Installation Complete."
