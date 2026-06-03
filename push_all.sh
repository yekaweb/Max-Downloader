#!/usr/bin/env bash
set -euo pipefail

################################################################################
# push_all.sh
#
# Interactive helper to safely commit and push repository changes to GitHub.
# Features:
# - Explains how to make the script executable and run it.
# - Detects whether git push will authenticate; if not, prompts user for
#   credentials (PAT) or suggests using `gh auth login` / SSH setup.
# - Scans for likely sensitive files (envs, keys, files containing SECRET/TOKEN)
#   and creates `.example` copies with redacted values, adds the examples and
#   makes sure the originals are not pushed.
# - Stages, commits (with provided or default message) and pushes to the
#   current branch on the chosen remote.
#
# Usage:
# 1) Make executable: chmod +x push_all.sh
# 2) Run: ./push_all.sh [remote] ["Commit message"]
#    - Default remote is `origin`.
#    - If no commit message is provided a timestamped auto-message is used.

cd "$(dirname "$0")"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: this directory is not a git repository." >&2
  exit 1
fi

REMOTE=${1:-origin}
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ $# -ge 2 ]; then
  # allow: ./push_all.sh origin "message with spaces"
  shift
  MSG="$*"
else
  MSG="Auto commit: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
echo "Repository: $REPO_ROOT"
echo "Branch: $BRANCH"
echo "Remote: $REMOTE"

################################################################################
# Helpers
################################################################################

prompt_confirm() {
  # prompt_confirm "Question?"
  local prompt
  prompt="$1 [y/N]: "
  read -r -p "$prompt" ans || return 1
  case "$ans" in
    [Yy]|[Yy][Ee][Ss]) return 0 ;;
    *) return 1 ;;
  esac
}

test_push_auth() {
  # Try a safe dry-run push to detect whether push will require auth.
  # Use credential helper store to avoid VSCode socket helpers in the terminal.
  if git -c credential.helper=store push --dry-run "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

configure_https_pat() {
  echo
  echo "Configure GitHub HTTPS credentials using a Personal Access Token (PAT)."
  echo "A PAT with 'repo' scope is usually enough for repo push access."
  read -r -p "GitHub username: " gh_user
  echo -n "GitHub Personal Access Token (input hidden): "
  read -r -s gh_pat
  echo

  # Ensure remote uses https; if it's ssh, offer to switch to https temporarily
  remote_url=$(git remote get-url "$REMOTE")
  if printf "%s" "$remote_url" | grep -q "^git@"; then
    echo "Remote currently uses SSH: $remote_url"
    if prompt_confirm "Switch remote to HTTPS (https://github.com/OWNER/REPO.git) to use PAT now?"; then
      # build https url from ssh form git@github.com:owner/repo.git
      https_url=$(printf "%s" "$remote_url" | sed -E 's#git@([^:]+):#https://\1/#')
      git remote set-url "$REMOTE" "$https_url"
      echo "Remote set to $https_url"
    else
      echo "Keep SSH remote. Please set up SSH keys or use 'gh auth login' separately." >&2
      return 1
    fi
  fi

  # Configure credential helper to store (so push won't prompt again)
  git config --global credential.helper store || true

  # Approve credential (stores in credential store)
  printf "protocol=https\nhost=github.com\nusername=%s\npassword=%s\n" "$gh_user" "$gh_pat" | git -c credential.helper=store credential approve || true

  echo "Saved credentials to git credential store. Retrying push test..."
}

ensure_auth_or_prompt() {
  if test_push_auth; then
    echo "Authenticated: push dry-run successful."
    return 0
  fi

  echo "Push dry-run failed; it looks like this environment is not authenticated for pushing to $REMOTE."
  echo "Options:"
  echo "  1) Use GitHub CLI (gh) interactive login (recommended)"
  echo "  2) Provide GitHub username + Personal Access Token (PAT) to store in git credential store"
  echo "  3) Use SSH key (if remote is SSH) — follow the printed steps"

  if command -v gh >/dev/null 2>&1; then
    if prompt_confirm "Run 'gh auth login' now (interactive) to authenticate?"; then
      gh auth login
      if test_push_auth; then
        echo "Authenticated via gh."; return 0
      fi
    fi
  fi

  # If remote is SSH, guide user
  remote_url=$(git remote get-url "$REMOTE") || remote_url=""
  if printf "%s" "$remote_url" | grep -q "^git@"; then
    echo "Remote uses SSH: $remote_url"
    echo "To authenticate via SSH, ensure you have an SSH key added to your GitHub account." 
    if prompt_confirm "Do you want this script to show your SSH public key (to paste into GitHub) now?"; then
      ssh_key_file=~/.ssh/id_rsa.pub
      if [ ! -f "$ssh_key_file" ]; then
        echo "No SSH key found at $ssh_key_file. Creating one (no passphrase)."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
      fi
      echo "--- Begin public key ---"
      cat ~/.ssh/id_rsa.pub
      echo "--- End public key ---"
      echo "Add the above key in https://github.com/settings/ssh/new then re-run this script."
      return 1
    fi
  fi

  if prompt_confirm "Provide username+PAT now to configure git credential store?"; then
    if configure_https_pat; then
      if test_push_auth; then
        echo "Authentication OK after PAT setup."; return 0
      else
        echo "Authentication still failing after PAT setup." >&2
        return 1
      fi
    else
      echo "PAT setup skipped/failed." >&2
      return 1
    fi
  fi

  echo "Authentication not set. Aborting push." >&2
  return 1
}

################################################################################
# Sensitive file handling
################################################################################

redact_to_example() {
  local src="$1"
  local dst
  local base
  base=$(basename -- "$src")
  # Create example name: .env -> .env.example, config.py -> config.py.example
  dst="$REPO_ROOT/${base}.example"

  echo "Creating example for $src -> $dst"

  # Generic redaction: for .env style KEY=VALUE -> KEY=REDACTED
  # For python/json/yaml very basic redaction for common patterns.
  # Use a heredoc for the awk program to avoid shell quoting issues
  awk -f - "$src" > "$dst" <<'AWKSCRIPT' || cp "$src" "$dst"
BEGIN{IGNORECASE=1}
# dotenv key=value
/^[A-Za-z0-9_]+=[^=].*/ { split($0,a,"="); printf "%s=REDACTED\n", a[1]; next }
# python assignment SECRET = "..."
/^[ \t]*[A-Za-z0-9_]+[ \t]*=[ \t]*".*"/ { sub(/".*"/, "\"REDACTED\""); print; next }
/^[ \t]*[A-Za-z0-9_]+[ \t]*=[ \t]*'.*'/ { sub(/'.*'/, "'REDACTED'"); print; next }
# json "key": "value"
/^[ \t]*"[A-Za-z0-9_]+"[ \t]*:[ \t]*".*"/ { sub(/:[[:space:]]*".*"/, ": \"REDACTED\""); print; next }
# fallback: redact lines containing common keywords
/SECRET|TOKEN|API[_-]?KEY|PASSWORD|PASS|PRIVATE[_-]?KEY/ { print "REDACTED"; next }
{ print }
AWKSCRIPT

  git add -- "$dst"
  # prevent original from being pushed: if tracked, remove from index
  if git ls-files --error-unmatch -- "$src" >/dev/null 2>&1; then
    git rm --cached --ignore-unmatch -- "$src" || true
  else
    # if untracked, ensure we don't add it by mistake later
    :
  fi
}

find_sensitive_files() {
  # Search tracked files and top-level files for known sensitive names or content.
  # Avoid broad matching of arbitrary paths like bot/loader.py.
  local files
  files=$(git ls-files)
  while IFS= read -r f; do files="$files\n$f"; done < <(find "$REPO_ROOT" -maxdepth 1 -type f -printf "%P\n")
  echo "$files" | sort -u | while IFS= read -r f; do
    # skip example and markdown files
    case "$f" in
      *.example|*.md) continue;;
    esac
    # name-based heuristics for likely secret/config files.
    if printf "%s" "$f" | grep -Ei '(^|[_.\-/])(\.env|env|secret|secrets|credential|credentials|passwd|password|token|id_rsa|\.key|\.pem|\.crt|\.p12)([_.\-/]|$)' >/dev/null 2>&1; then
      printf "%s\n" "$REPO_ROOT/$f"
      continue
    fi
    # content-based heuristics: search only small text files for common secrets.
    if printf "%s" "$f" | grep -Ei '\.(env|conf|cfg|ini|json|yaml|yml|py|sh)$' >/dev/null 2>&1 && \
       grep -I -E 'SECRET|TOKEN|API[_-]?KEY|PASSWORD|PASS|PRIVATE[_-]?KEY' "$REPO_ROOT/$f" >/dev/null 2>&1; then
      printf "%s\n" "$REPO_ROOT/$f"
    fi
  done
}

################################################################################
# Main flow
################################################################################

echo "Scanning for sensitive files..."
sensitive_files=$(find_sensitive_files || true)

default_for_example=0

if [ -n "$sensitive_files" ]; then
  echo "Sensitive candidate files found:";
  echo "$sensitive_files"
  if prompt_confirm "Create .example redacted copies and avoid pushing originals?"; then
    # iterate and create examples
    while IFS= read -r sf; do
      [ -z "$sf" ] && continue
      if [ -f "$sf" ]; then
        redact_to_example "$sf"
      fi
    done <<< "$sensitive_files"
  else
    echo "Skipping creation of example files. Be careful not to push secrets." >&2
  fi
else
  echo "No obvious sensitive files detected."
fi

################################################################################
# Stage and commit
################################################################################

echo "Staging remaining changes..."
# Stage everything except ensure originals of sensitive files are not staged
git add -A

# After staging, ensure sensitive originals are not in the index
if [ -n "$sensitive_files" ]; then
  while IFS= read -r sf; do
    [ -z "$sf" ] && continue
    git rm --cached --ignore-unmatch -- "$sf" >/dev/null 2>&1 || true
  done <<< "$sensitive_files"
fi

if git diff --cached --quiet; then
  echo "No changes to commit. Skipping commit." 
else
  echo "Committing: $MSG"
  git commit -m "$MSG"
fi

################################################################################
# Ensure authentication then push
################################################################################

if test_push_auth; then
  echo "Authenticated: performing push..."
else
  if ! ensure_auth_or_prompt; then
    echo "Authentication required but not configured. Aborting." >&2
    exit 3
  fi
fi

echo "Pushing to ${REMOTE}/${BRANCH}..."
if git -c credential.helper=store push "$REMOTE" "$BRANCH"; then
  echo "Push successful.";
  exit 0
else
  echo "Push failed. If you see authentication errors, please run 'gh auth login' or provide a PAT and re-run this script." >&2
  exit 2
fi
