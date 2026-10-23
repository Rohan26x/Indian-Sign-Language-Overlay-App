#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==============================================================="
echo "  Real-Time Audio to ISL 3D Avatar Overlay Application"
echo "==============================================================="

echo "[1/3] Checking Database..."
if [ ! -f "backend/sign_lexicon.db" ]; then
    echo "Seeding ISL dictionary and fingerspelling database..."
    python3 backend/seed_db.py
fi

echo "[2/3] Launching Python Async WebSocket Pipeline Server..."
python3 backend/main.py &
BACKEND_PID=$!

sleep 2

echo "[3/3] Launching Electron Transparent Overlay Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npx electron .

kill $BACKEND_PID 2>/dev/null || true
echo "Application session ended."
