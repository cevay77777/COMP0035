"""
Check file sizes inside the COMP0035 Coursework folder.

Lists files larger than a given threshold (default: 1 MB).
"""

from pathlib import Path

ROOT = Path(".")
THRESHOLD_MB = 1.0  # change if needed


def sizeof_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def main() -> None:
    print(f"Scanning folder: {ROOT.resolve()}")
    print(f"Showing files larger than {THRESHOLD_MB:.1f} MB\n")

    large_files = []

    for path in ROOT.rglob("*"):
        if path.is_file():
            size_mb = sizeof_mb(path)
            if size_mb >= THRESHOLD_MB:
                large_files.append((size_mb, path))

    if not large_files:
        print("✅ No large files found.")
        return

    for size_mb, path in sorted(large_files, reverse=True):
        print(f"{size_mb:8.2f} MB  |  {path}")

    total = sum(size for size, _ in large_files)
    print(f"\nTotal size of listed files: {total:.2f} MB")


if __name__ == "__main__":
    main()

