# BAT Archive

This folder contains archived copies of the repository's Windows batch scripts (`*.bat`).

## What was done
- Created `bat_archive/` in the project root.
- Copied all root `.bat` files into `bat_archive/`.

## Notes
- Most of these files are Windows-only deployment / git wrapper scripts.
- They are not required for a Linux-based project workflow.
- The following files are the most generally useful Windows helpers and can be kept if you want to preserve Windows support:
  - `create_structure.bat`
  - `deploy.bat`
  - `START_BOT.bat`
  - `RUN_BOT.bat`

## Recommended cleanup
The following `.bat` scripts are largely redundant or specific to old git/deploy workflows and can be removed if you want to minimize clutter:
  - `COMMIT_AND_PUSH.bat`
  - `DEPLOY_FSM_NOW.bat`
  - `DEPLOY_NOW.bat`
  - `FINAL_DEPLOYMENT.bat`
  - `FINAL_PUSH.bat`
  - `FIX_AND_PUSH.bat`
  - `FIX_AND_RUN.bat`
  - `GIT_PUSH_NOW.bat`
  - `MASTER_PUSH.bat`
  - `PUSH_BUG_FIX.bat`
  - `PUSH_CACHE_NOW.bat`
  - `PUSH_FIX_NOW.bat`
  - `PUSH_URL_FIX.bat`
  - `PUSH_YTDLP.bat`
  - `go.bat`

## Important
- The root `.bat` files were not deleted in this environment because direct file removal operations were not available.
- The archive folder now contains safe copies for review and restoration.
