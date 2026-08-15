#!/usr/bin/env bash
# Render Build Script
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Build React frontend
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete — backend deps installed + frontend built"
