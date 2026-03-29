#!/usr/bin/env python3
"""
sync-files.py

Due to various technical limitations, some files need to be kept identical in the repository.
This script can:
1. Check whether these files are still identical.
2. Overwrite the target files with a master copy if needed.

Usage:
    # Check files only
    python .github/workflow_scripts/sync-files.py --check

    # Force sync files to master copy
    python .github/workflow_scripts/sync-files.py --sync
"""

import argparse
import filecmp
import shutil
from pathlib import Path
import sys

# Define the master files and their targets
# Key: master file, Value: list of files to keep identical
IDENTICAL_FILES_MAP = {
    "master_files/common_config.yaml": [
        "services/service_a/config.yaml",
        "services/service_b/config.yaml",
    ],
    "master_files/global_settings.json": [
        "apps/app_a/settings.json",
        "apps/app_b/settings.json",
    ],
}


def check_files():
    """Check that all files match the master copy."""
    all_ok = True
    for master, targets in IDENTICAL_FILES_MAP.items():
        master_path = Path(master)
        if not master_path.exists():
            print(f"[ERROR] Master file does not exist: {master_path}")
            all_ok = False
            continue

        for target in targets:
            target_path = Path(target)
            if not target_path.exists():
                print(f"[WARNING] Target file missing: {target_path}")
                all_ok = False
                continue

            if not filecmp.cmp(master_path, target_path, shallow=False):
                print(f"[MISMATCH] {target_path} differs from {master_path}")
                all_ok = False
    return all_ok


def sync_files():
    """Overwrite target files with master copy."""
    for master, targets in IDENTICAL_FILES_MAP.items():
        master_path = Path(master)
        if not master_path.exists():
            print(f"[ERROR] Master file does not exist: {master_path}")
            continue

        for target in targets:
            target_path = Path(target)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(master_path, target_path)
            print(f"[SYNCED] {target_path} -> updated from {master_path}")


def main():
    parser = argparse.ArgumentParser(description="Check or sync identical files.")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Overwrite target files with master copy",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check files only (default if neither option provided)",
    )
    args = parser.parse_args()

    # Default behavior: check if no flags provided
    if not (args.check or args.sync):
        args.check = True

    if args.check:
        print("Checking files for consistency...")
        success = check_files()
        if not success:
            print("\n[FAIL] Some files are not consistent with master copies.")
            sys.exit(1)
        print("\n[SUCCESS] All files are consistent.")

    if args.sync:
        print("Syncing files to match master copies...")
        sync_files()
        print("\n[SUCCESS] Files synced successfully.")


if __name__ == "__main__":
    main()
