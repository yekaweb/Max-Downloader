#!/usr/bin/env python3
"""Quick fix deployment for Windows"""

import subprocess
import sys

print("=" * 60)
print("🚀 DLBot Download Flow Fix - Auto Deploy")
print("=" * 60)
print()

# Step 1: Show changes
print("📋 Files changed:")
result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
print(result.stdout)

print()
result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
print(result.stdout)

# Step 2: Stage
print("\n📦 Staging changes...")
subprocess.run(["git", "add", "."])

# Step 3: Show staged
result = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True)
print(result.stdout)

# Step 4: Ask for commit
print("\n📝 Creating commit...")
commit_msg = """fix: download flow hanging on media extraction, string formatting

- Added 30-second timeout to yt_dlp.extract_info()
- Fixed ValueError: Cannot specify ',' with 's' on line 665
- Improved error logging with detailed messages
- Better FSM state management with try-catch
- Clear error messages when extraction fails
- Added test_ytdlp.py for debugging

Fixes: 
  - Bot hanging indefinitely during media info fetch
  - String formatting error in media info display
  - FSM state stuck on error

Improves:
  - Error messages clarity
  - Debugging experience
  - User experience during download flow"""

result = subprocess.run([
    "git", "commit", "-m", commit_msg,
    "-m", "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Commit created")
else:
    print(f"❌ Commit failed: {result.stderr}")
    sys.exit(1)

# Step 5: Show commit
print("\n📊 Commit info:")
result = subprocess.run(["git", "log", "-1", "--oneline"], capture_output=True, text=True)
print(result.stdout)

# Step 6: Push
print("\n🚀 Pushing to GitHub...")
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Push successful!")
    print("\n🔗 View on GitHub:")
    print("   https://github.com/yekaweb/dlbot-telegram/commits/main")
else:
    print(f"⚠️ Push warning: {result.stdout}{result.stderr}")

print("\n" + "=" * 60)
print("✨ Deploy complete!")
print("=" * 60)
