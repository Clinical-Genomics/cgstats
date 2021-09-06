from pathlib import Path


def check_for_rapid_support(unaligned_dir_path: Path) -> bool:
    """Check if a support.txt file exists, implying on a rapid 2500 flowcell"""
    rapid_support_file = "support.txt"
    return unaligned_dir_path.joinpath(rapid_support_file).exists()
