import shutil
from pathlib import Path
from datetime import datetime


VALID_EXTENSIONS = {".csv", ".json"}
MAX_BACKUPS      = 5
LOG_FILE         = "backup_log.txt"


def log(message: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    entry     = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())


def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_file(source_file: Path, backup_dir: Path) -> None:
    stem      = source_file.stem
    suffix    = source_file.suffix
    timestamp = get_timestamp()
    dest_name = f"{stem}_{timestamp}{suffix}"
    dest_path = backup_dir / dest_name

    shutil.copy2(source_file, dest_path)
    log(f"Backed up '{source_file.name}' -> '{dest_name}'")

    existing_backups = sorted(
        backup_dir.glob(f"{stem}_*{suffix}"),
        key=lambda f: f.stat().st_mtime
    )

    if len(existing_backups) > MAX_BACKUPS:
        to_delete = existing_backups[:len(existing_backups) - MAX_BACKUPS]
        for old_file in to_delete:
            old_file.unlink()
            log(f"Deleted old backup '{old_file.name}'")


def run_backup(source_dir: str, backup_dir: str) -> None:
    source = Path(source_dir)
    backup = Path(backup_dir)

    if not source.exists():
        log(f"ERROR: Source directory '{source_dir}' does not exist.")
        return

    backup.mkdir(parents=True, exist_ok=True)
    log(f"Starting backup: '{source}' -> '{backup}'")

    files = [
        f for f in source.iterdir()
        if f.is_file() and f.suffix in VALID_EXTENSIONS
    ]

    if not files:
        log("No .csv or .json files found to back up.")
        return

    for file in files:
        backup_file(file, backup)

    log(f"Backup complete. {len(files)} file(s) processed.")


if __name__ == "__main__":
    run_backup("data", "backups")
