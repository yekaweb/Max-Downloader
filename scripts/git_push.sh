#!/usr/bin/env bash
# Clean and safe git push script for Max-Downloader
set -e

MSG="${1:-Auto update}"
echo "📦 Adding changes to git..."
git add .

echo "📝 Committing: $MSG"
git commit -m "$MSG" || echo "No changes to commit"

echo "🚀 Pushing to origin main..."
git push origin main

echo "✅ Push complete!"
