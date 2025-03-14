#!/usr/bin/env python3
import argparse
import requests
import gzip
import collections
import pathlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to console (stdout)
    ]
)

# Logger instance
logger = logging.getLogger(__name__)

DEFAULT_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"

# Get the directory where the script is located (src directory)
SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()

def main():
    # Parse Command-Line Arguments
    args = parse_arguments()
    
    # Download or Use Cached File
    gz_file = get_contents_file(args.architecture, args.mirror_url, args.force_download)
    if not gz_file:
        logger.error("Download failed or file not found.")
        return

    # Parse the .gz file and build a package/file count
    package_counts = parse_contents(gz_file)
    
    # Save the results to output/output.txt
    save_results(package_counts, args.architecture)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch and analyze Debian package statistics (top 10 by file count)."
    )
    parser.add_argument(
        "architecture",
        help="Architecture to analyze, e.g. amd64, arm64, mips"
    )
    parser.add_argument(
        "--mirror-url",
        default=DEFAULT_MIRROR,
        help=f"Debian mirror URL (default: {DEFAULT_MIRROR})"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force re-download of Contents file even if it exists."
    )

    return parser.parse_args()

def get_contents_file(architecture: str, mirror_url: str, force_download: bool) -> pathlib.Path:
    """
    Determines which Contents-<architecture>.gz file to use.
    - Uses cached file if available.
    - Downloads the file otherwise.
    """
    
    download_dir = SCRIPT_DIR / "downloads"
    download_dir.mkdir(exist_ok=True, parents=True)

    gz_path = download_dir / f"Contents-{architecture}.gz"

    # Check if file already exists
    if gz_path.exists() and not force_download:
        logger.info(f"Using cached file: {gz_path}")
        return gz_path

    # Otherwise, download it
    return download_contents_file(architecture, mirror_url, gz_path)

def download_contents_file(architecture: str, mirror_url: str, gz_path: pathlib.Path) -> pathlib.Path:
    """
    Downloads 'Contents-<architecture>.gz' and saves it in 'downloads/'.
    Returns the path to the downloaded file.
    """
    url = f"{mirror_url}Contents-{architecture}.gz"
    logger.info(f"Downloading: {url}")

    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        return None

    # Save the downloaded file
    with open(gz_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    logger.info(f"Saved to: {gz_path}")
    return gz_path

def parse_contents(gz_path: pathlib.Path) -> collections.Counter:
    """
    Reads the .gz file line by line, counts how many times each package appears.
    Returns a Counter object mapping {package_name: file_count}.
    """
    package_counts = collections.Counter() 

    logger.info(f"Parsing file: {gz_path}")

    with gzip.open(gz_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.rsplit(" ", 1)
            if len(parts) < 2:
                continue
            file_path, packages_str = parts
            packages = packages_str.split(",")
            for package in packages:
                package_counts[package] += 1

    logger.info(f"Parsed {len(package_counts)} unique packages.")
    return package_counts

def save_results(package_counts, architecture: str):
    """
    Saves the top 10 packages by file count into 'output/output_arch.txt'
    """
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True, parents=True)

    output_file = output_dir / f"output_{architecture}.txt"

    if not isinstance(package_counts, collections.Counter):
        package_counts = collections.Counter(package_counts)

    top_10 = package_counts.most_common(10)

    # Determine max length for alignment
    max_pkg_length = max(len(pkg) for pkg, _ in top_10) if top_10 else 30

    with open(output_file, "w") as f:
        f.write(f"Top 10 packages for {architecture} by file count:\n\n")
        for i, (pkg, count) in enumerate(top_10, start=1):
            f.write(f"{i}.\t{pkg.ljust(max_pkg_length)}\t{count} files\n")


    logger.info(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()