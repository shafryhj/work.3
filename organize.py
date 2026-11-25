import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
TARGET_DIR = (BASE_DIR / "practice_downloads").resolve()
LOG_FILE = BASE_DIR / "log.txt"

EXTENSION_MAP = {
    "문서": {".pdf", ".xlsx", ".xls", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".csv", ".hwp"},
    "이미지": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp"},
    "압축": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "미디어": {".mp3", ".mp4", ".wav", ".mov", ".avi", ".mkv"},
}


def get_category(extension: str) -> str:
    ext = extension.lower()
    for category, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            return category
    return "기타"


def resolve_destination(dest_dir: Path, filename: str) -> Path:
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize_downloads(dry_run: bool = False) -> None:
    if not TARGET_DIR.exists() or not TARGET_DIR.is_dir():
        print(f"오류: 대상 폴더가 존재하지 않습니다: {TARGET_DIR}")
        sys.exit(1)

    files = sorted(p for p in TARGET_DIR.iterdir() if p.is_file())
    if not files:
        print("정리할 파일이 없습니다.")
        return

    mode_label = "[DRY-RUN] " if dry_run else ""
    print(f"{mode_label}대상 폴더: {TARGET_DIR}")
    print(f"{mode_label}총 {len(files)}개 파일 처리 예정\n")

    log_lines = []
    for file_path in files:
        # Safety check: never touch anything outside practice_downloads
        if file_path.resolve().parent != TARGET_DIR:
            continue

        category = get_category(file_path.suffix)
        dest_dir = TARGET_DIR / category
        dest_path = resolve_destination(dest_dir, file_path.name)
        rel_dest = f"{category}/{dest_path.name}"

        if dry_run:
            print(f"[DRY-RUN] {file_path.name} -> {rel_dest}")
        else:
            dest_dir.mkdir(exist_ok=True)
            shutil.move(str(file_path), str(dest_path))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {file_path.name} -> {rel_dest}"
            log_lines.append(log_entry)
            print(f"[MOVED] {file_path.name} -> {rel_dest}")

    if not dry_run and log_lines:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            for line in log_lines:
                f.write(line + "\n")
        print(f"\n총 {len(log_lines)}건 이동 완료. 로그가 {LOG_FILE.name}에 기록되었습니다.")
    elif dry_run:
        print(f"\n[DRY-RUN] 실제 파일 이동 및 로그 기록 없이 {len(files)}건의 계획을 출력했습니다.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="practice_downloads 폴더의 파일을 확장자별 하위 폴더로 정리합니다."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제로 파일을 옮기지 않고 정리 계획만 출력합니다.",
    )
    args = parser.parse_args()
    organize_downloads(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
