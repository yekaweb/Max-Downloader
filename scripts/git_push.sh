#!/usr/bin/env bash
# Clean and safe git push script for Max-Downloader
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

MSG="${1:-Auto update}"
echo "📦 Adding changes to git in $REPO_DIR..."
git add .

echo "📝 Committing: $MSG"
git commit -m "$MSG" || echo "No changes to commit"

echo "🚀 Pushing to origin main..."
git push origin main

echo "✅ Push complete!"
