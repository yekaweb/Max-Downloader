#!/usr/bin/env python3
"""main_test.py

Debug harness for Max-Downloader.
This script performs:
- environment logging
- static analysis for missing Dict imports
- module import diagnostics
- simple initialization tests for the bot and phases manager
- writes all logs to terminal and bug_logs/main_test_<timestamp>.log
"""

import argparse
import asyncio
import importlib
import logging
import logging.handlers
import os
import platform
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BUG_LOG_DIR = REPO_ROOT / "bug_logs"
UPLOAD_BUG_DIR = REPO_ROOT / "upload_bug_log"
BUG_LOG_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_BUG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(log_name: str, log_file: Path) -> logging.Logger:
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=8 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug("Logger initialized")
    logger.propagate = False

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    return logger


def log_environment(logger: logging.Logger) -> None:
    logger.info("=== Environment Summary ===")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Script path: {Path(__file__).resolve()}")
    logger.info(f"Repository root: {REPO_ROOT}")
    logger.info(f"sys.path length: {len(sys.path)}")
    for idx, p in enumerate(sys.path[:10], 1):
        logger.debug(f"sys.path[{idx - 1}]: {p}")

    env_vars = {
        "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
        "PYROGRAM_APP_ID": bool(os.getenv("PYROGRAM_APP_ID")),
        "PYROGRAM_APP_HASH": bool(os.getenv("PYROGRAM_APP_HASH")),
        "TEMP_DOWNLOAD_DIR": os.getenv("TEMP_DOWNLOAD_DIR"),
        "CACHE_FILE_DIR": os.getenv("CACHE_FILE_DIR"),
    }
    logger.info("Environment variables summary:")
    for key, val in env_vars.items():
        logger.info(f"  {key}: {val}")


def scan_missing_dict_imports(logger: logging.Logger) -> None:
    logger.info("=== Static scan for Dict import issues ===")
    pattern_dict = re.compile(r"\bDict\b")
    pattern_import = re.compile(r"^\s*(from\s+typing\s+import\s+.*\bDict\b|import\s+typing)\b", re.MULTILINE)
    warned = 0

    for path in sorted(REPO_ROOT.rglob("*.py")):
        if ".git" in path.parts or "__pycache__" in path.parts or path.match("bug_logs/*") or path.match("upload_bug_log/*"):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        if not pattern_dict.search(text):
            continue

        if pattern_import.search(text):
            logger.debug(f"OK import found in {path}")
            continue

        # If file contains `Dict` and no import of Dict or typing
        lines = []
        for number, line in enumerate(text.splitlines(), 1):
            if pattern_dict.search(line) and not line.strip().startswith("#"):
                lines.append((number, line.strip()))
        if lines:
            warned += 1
            logger.warning("Potential missing typing import in %s", path)
            for line_no, src in lines[:10]:
                logger.warning("  %4d: %s", line_no, src)

    if warned == 0:
        logger.info("No obvious missing `Dict` imports found in repository scan.")
    else:
        logger.info(f"Found {warned} file(s) with possible missing `Dict` imports.")


def run_upload_diagnostics(logger: logging.Logger, file_path: Path) -> None:
    logger.info("=== Upload diagnostics ===")
    logger.info("Upload file path: %s", file_path)

    if not file_path.exists():
        logger.error("Upload file does not exist: %s", file_path)
        return

    if not file_path.is_file():
        logger.error("Upload path is not a file: %s", file_path)
        return

    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        logger.info("File exists. Size: %.2f MB", size_mb)
    except Exception:
        logger.error("Unable to stat upload file")
        logger.error(traceback.format_exc())
        return

    try:
        with file_path.open("rb") as f:
            head = f.read(64)
        logger.debug("File header bytes: %s", head.hex()[:256])
    except Exception:
        logger.error("Unable to read upload file")
        logger.error(traceback.format_exc())

    logger.info("Checking whether ffmpeg is available for decode probe...")
    try:
        import subprocess
        probe = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(file_path), "-f", "null", "-"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        logger.info("ffmpeg exit code: %s", probe.returncode)
        if probe.stdout:
            logger.info("ffmpeg stdout:\n%s", probe.stdout)
        if probe.stderr:
            logger.info("ffmpeg stderr:\n%s", probe.stderr)
        if probe.returncode != 0:
            logger.warning("ffmpeg reported decode issues for the upload file.")
        else:
            logger.info("ffmpeg probe completed successfully.")
    except FileNotFoundError:
        logger.warning("ffmpeg not installed or not found in PATH. Skipping decode probe.")
    except Exception:
        logger.error("Error while running ffmpeg probe")
        logger.error(traceback.format_exc())


def attach_loguru_sink(logger: logging.Logger, log_file: Path) -> None:
    try:
        from loguru import logger as loguru_logger
        loguru_logger.add(
            str(log_file),
            level="DEBUG",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
        logger.info("Attached loguru sink to %s", log_file)
    except Exception as exc:
        logger.warning("Unable to attach loguru sink: %s", exc)


async def _run_bot_polling(logger: logging.Logger, module, log_file: Path) -> None:
    bot_obj = getattr(module, "bot", None)
    dp_obj = getattr(module, "dp", None)
    pyrogram_client = getattr(module, "pyrogram_client", None)

    if bot_obj is None or dp_obj is None:
        logger.error("Bot or Dispatcher not available from bot.loader_professional_enhanced")
        return

    logger.info("Bot object: %s", type(bot_obj).__name__)
    logger.info("Dispatcher object: %s", type(dp_obj).__name__)
    logger.info("Pyrogram available: %s", pyrogram_client is not None)

    try:
        if pyrogram_client is not None:
            logger.info("Starting pyrogram client...")
            await pyrogram_client.start()
            logger.info("Pyrogram client started")
    except Exception:
        logger.warning("Failed to start pyrogram client")
        logger.warning(traceback.format_exc())

    try:
        logger.info("=== Bot polling started ===")
        logger.info("Send a real Telegram link to the bot now.")
        await dp_obj.start_polling(bot_obj, skip_updates=True)
        logger.info("=== Bot polling stopped normally ===")
    except Exception:
        logger.critical("Bot polling stopped with exception")
        logger.critical(traceback.format_exc())
    finally:
        if pyrogram_client is not None:
            try:
                await pyrogram_client.stop()
                logger.info("Pyrogram client stopped")
            except Exception:
                logger.warning("Failed to stop pyrogram client")
                logger.warning(traceback.format_exc())

        try:
            sess = getattr(bot_obj, "session", None)
            if sess and not callable(sess):
                await sess.close()
                logger.info("Bot session closed")
        except Exception:
            logger.warning("Failed to close bot session")
            logger.warning(traceback.format_exc())


def run_bot_harness(logger: logging.Logger, log_file: Path) -> None:
    logger.info("=== Bot harness ===")
    attach_loguru_sink(logger, log_file)

    loader_module = import_module("bot.loader_professional_enhanced", logger)
    if loader_module is None:
        return

    try:
        asyncio.run(_run_bot_polling(logger, loader_module, log_file))
    except KeyboardInterrupt:
        logger.info("Bot harness interrupted by user")
    except Exception:
        logger.error("Bot harness failed")
        logger.error(traceback.format_exc())


def import_module(module_name: str, logger: logging.Logger):
    logger.info(f"Importing {module_name}...")
    try:
        module = importlib.import_module(module_name)
        logger.info(f"Imported {module_name} successfully")
        return module
    except Exception:
        logger.error(f"Failed to import {module_name}")
        logger.error(traceback.format_exc())
        return None


def run_import_diagnostics(logger: logging.Logger) -> None:
    logger.info("=== Import diagnostics ===")
    modules = [
        "config_simple",
        "bot.loader_professional_enhanced",
        "services.phases_integration",
        "services.parallel_download_service",
        "services.compression_service",
        "services.stream_upload_service",
        "services.queue_service",
        "main",
    ]

    imported = {}
    for mod_name in modules:
        imported[mod_name] = import_module(mod_name, logger)

    # Try to instantiate the phases manager if possible
    manager_module = imported.get("services.phases_integration")
    if manager_module is not None:
        logger.info("Attempting to get phases manager from services.phases_integration")
        try:
            manager = manager_module.get_phases_manager()
            logger.info("Phases manager created: %s", type(manager).__name__)
        except Exception:
            logger.error("Failed to instantiate phases manager")
            logger.error(traceback.format_exc())

    # Try to inspect loader and bot objects if present
    loader_module = imported.get("bot.loader_professional_enhanced")
    if loader_module is not None:
        logger.info("Inspecting bot loader module")
        try:
            bot_obj = getattr(loader_module, "bot", None)
            dp_obj = getattr(loader_module, "dp", None)
            logger.info("bot: %s", type(bot_obj).__name__ if bot_obj is not None else "None")
            logger.info("dp: %s", type(dp_obj).__name__ if dp_obj is not None else "None")
        except Exception:
            logger.error("Failed to inspect bot loader module")
            logger.error(traceback.format_exc())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Debug Max-Downloader bot errors and find missing Dict imports."
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Run only the static Dict import scan and exit.",
    )
    parser.add_argument(
        "--imports-only",
        action="store_true",
        help="Run only module import diagnostics and exit.",
    )
    parser.add_argument(
        "--upload-debug",
        metavar="FILE",
        help="Run upload diagnostics for the given compressed file path.",
    )
    parser.add_argument(
        "--run-bot",
        action="store_true",
        help="Start the Telegram bot and keep polling. Send a real link to the bot in Telegram.",
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = BUG_LOG_DIR / f"main_test_{timestamp}.log"
    if args.upload_debug:
        log_file = UPLOAD_BUG_DIR / f"upload_debug_{timestamp}.log"
    logger = setup_logger("main_test", log_file)

    logger.info("=== Starting main_test.py ===")
    logger.info("Log file: %s", log_file)

    log_environment(logger)

    if args.imports_only:
        run_import_diagnostics(logger)
        logger.info("=== main_test.py complete (imports-only) ===")
        return

    if args.scan_only:
        scan_missing_dict_imports(logger)
        logger.info("=== main_test.py complete (scan-only) ===")
        return

    if args.upload_debug:
        scan_missing_dict_imports(logger)
        run_upload_diagnostics(logger, Path(args.upload_debug))
        logger.info("=== main_test.py complete (upload-debug) ===")
        logger.info("Review logs in %s", log_file)
        return

    if args.run_bot:
        scan_missing_dict_imports(logger)
        run_import_diagnostics(logger)
        run_bot_harness(logger, log_file)
        logger.info("=== main_test.py complete (run-bot) ===")
        logger.info("Review logs in %s", log_file)
        return

    scan_missing_dict_imports(logger)
    run_import_diagnostics(logger)

    logger.info("=== main_test.py complete ===")
    logger.info("Review logs in %s", log_file)


if __name__ == "__main__":
    main()
