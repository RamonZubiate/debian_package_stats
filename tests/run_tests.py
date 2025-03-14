import sys
import pathlib
import gzip
import filecmp

sys.path.append("../")

from src.package_statistics import (
    get_contents_file,
    download_contents_file,
    parse_contents,
    save_results
)

TEST_ARCH = "arm64" # Example architecture
TEST_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"
INVALID_MIRROR = "http://invalid-url.debian.org/debian/dists/stable/main/"
SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()

# test directories
DOWNLOADS_DIR = SCRIPT_DIR.parent / "src" / "downloads"
OUTPUT_DIR = SCRIPT_DIR.parent / "src" / "output"
TEST_DIR = SCRIPT_DIR / "test_files"  # Mock test files

# Define expected output file paths
EXPECTED_OUTPUT_FILE = TEST_DIR / "expected_output.txt"
MOCK_CONTENTS_FILE = TEST_DIR / "Contents-test.gz"

### Test fetching a valid contents file
def test_get_contents_file():
    gz_path = get_contents_file(TEST_ARCH, TEST_MIRROR, force_download=False)

    assert gz_path.exists(), f"Contents file {gz_path} should exist after fetching."
    assert gz_path.suffix == ".gz", "Fetched file should be a .gz file."


### Test handling invalid download URL
def test_download_invalid_mirror():
    gz_path = DOWNLOADS_DIR / f"Contents-{TEST_ARCH}.gz"
    result_path = download_contents_file(TEST_ARCH, INVALID_MIRROR, gz_path)

    assert result_path is None, "Download should return None for an invalid URL."


### Test parsing a valid contents file
def test_parse_contents():
    gz_path = get_contents_file(TEST_ARCH, TEST_MIRROR, force_download=False)
    package_counts = parse_contents(gz_path)

    assert isinstance(package_counts, dict), "Parsed result should be a dictionary."
    assert len(package_counts) > 0, "Parsed dictionary should not be empty."


### Test parsing an empty `.gz` file
def test_parse_empty_contents():
    empty_gz = DOWNLOADS_DIR / "Contents-empty.gz"

    # Create an empty gzip file
    with gzip.open(empty_gz, "wt", encoding="utf-8") as f:
        f.write("")

    package_counts = parse_contents(empty_gz)

    assert isinstance(package_counts, dict), "Parsed result should be a dictionary."
    assert len(package_counts) == 0, "Parsed dictionary should be empty for an empty file."

    # Cleanup after test
    empty_gz.unlink(missing_ok=True)


### Test handling of malformed `.gz` file
def test_parse_malformed_contents():
    malformed_gz = DOWNLOADS_DIR / "Contents-malformed.gz"

    malformed_data = """\
/usr/bin/gcc    devel/gcc-11
/usr/bin/python3
/usr/bin/rsync   net/rsync,net
/usr/bin/
"""

    # Create malformed gzip file
    with gzip.open(malformed_gz, "wt", encoding="utf-8") as f:
        f.write(malformed_data)

    try:
        package_counts = parse_contents(malformed_gz)
        assert isinstance(package_counts, dict), "Parsed result should be a dictionary."
        assert "devel/gcc-11" in package_counts, "Expected 'devel/gcc-11' to be parsed."
        assert len(package_counts) > 0, "Some valid data should be extracted."
    finally:
        # Cleanup test file
        malformed_gz.unlink(missing_ok=True)


### Test that save_results limits output to 10 packages
def test_save_results_max_10():
    package_counts = {f"package_{i}": i for i in range(15)}  # 15 fake packages

    save_results(package_counts, TEST_ARCH)
    output_file = OUTPUT_DIR / f"output_{TEST_ARCH}.txt"

    assert output_file.exists(), "Output file should be created in src/output/"

    with open(output_file, "r") as f:
        contents = f.readlines()

    num_package_lines = sum(1 for line in contents if line.strip() and line[0].isdigit())
    assert num_package_lines == 10, "Output should contain exactly 10 package entries."


### Test comparing mock output with expected output
def test_check_mock_output():

    assert MOCK_CONTENTS_FILE.exists(), "Mock contents file should exist before testing."

    test_output = parse_contents(MOCK_CONTENTS_FILE)
    assert test_output, "Parsed output should not be empty."

    save_results(test_output, "test")

    generated_output_file = OUTPUT_DIR / "output_test.txt"
    assert generated_output_file.exists(), "Generated output file should exist."

    assert EXPECTED_OUTPUT_FILE.exists(), "Expected output file should exist for comparison."

    # Compare the generated output with the expected output
    assert filecmp.cmp(generated_output_file, EXPECTED_OUTPUT_FILE, shallow=False), \
        "Generated output file does not match expected output."
