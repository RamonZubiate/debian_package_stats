## Overview

A Debian package is a standard format for distributing software on Debian-based Linux systems, such as Ubuntu, Debian, and Raspbian. These packages are stored as .deb files and contain compiled binaries, metadata, and dependency information.

This repository contains a CLI tool that:
1. Takes a Debian mirror URL
2. Downloads the Contents file for a specific architecture
3. Parses the file 
4. Provides package statistics

## Approach

I brainstormed multiple ways to approach this problem, many of which involved multiprocessing, caching, batching, and optimizing the parsing algorithm to handle large files efficiently. I decided to implement a single-threaded download, parsing, and caching system to promote simplicity and maintainability. I also prioritized my time spent on this project, as I knew that I had a limit of time to complete this project in order to continue with the interview process. 

However, I recognize the tradeoffs of not incorporating parallelism or asynchronous processing:

- Multiprocessing could speed up file parsing by utilizing multiple CPU cores, especially for very large Contents-<arch>.gz files.
- Asynchronous downloading could allow multiple architecture files to be fetched simultaneously, reducing network latency bottlenecks.
- Batch processing could improve memory efficiency by reading large files in chunks instead of loading everything into memory at once.

Ultimately, I prioritized code readability, ease of debugging, and reliability over aggressive optimizations. Future iterations of this project could explore concurrent processing for further performance gains while maintaining the same core functionality very feasibly. I am certain these processing methods will not be difficult for me to implement.

## Running the CLI tool

This was written in Python3, and you can install the required packages by running:
```
pip install -r requirements.txt
```

In order to run the tool, a user must:

```
cd src
```

For Windows:
```
python package_statistics.py <architecture>
```

For Linux:
```
./package_statistics.py <architecture>
```

The Contents file will be downloaded into `/downloads`, and the output of the package statistics will be in `/output`. Any appropriate Linux architecture will be downloaded.

If an invalid architecture is input, the CLI tool will exit.

## Example Output

Here is the expected output of using the CLI tool, downloading and parsing a AMD64 architecture:

```
Top 10 packages for amd64 by file count:

1.	devel/piglit                	53007 files
2.	science/esys-particle       	18408 files
3.	math/acl2-books             	16907 files
4.	libdevel/libboost1.81-dev   	15456 files
5.	libdevel/libboost1.74-dev   	14333 files
6.	lisp/racket                 	9599 files
7.	net/zoneminder              	8161 files
8.	electronics/horizon-eda     	8130 files
9.	libdevel/libtorch-dev       	8089 files
10.	libdevel/liboce-modeling-dev	7458 files
```

## Test Cases

The CLI tool has test cases written to ensure unit testing compliance. In order to test the application, a user must:
```
cd tests
pytest run_tests.py
```

This will execute the testing suite which will validate the integrity and validity of each individual component of this package. The testing suite will also pass in testing arguments, which will be processed and output into the outputs folder.

## Logging

This CLI tool includes logging to provide real-time feedback and assist with debugging. Logging helps track progress, identify issues, and ensure smooth execution. Logs are printed to the terminal in real-time.

- INFO – General runtime messages (e.g., file downloads, parsing progress).
- ERROR – Critical failures (e.g., download errors, invalid architectures).

## Caching

Downloading and redownloading files may prove to be inefficient. This tool implements caching to avoid redundant downloads and improve performance.

When the script runs, it checks the `src/downloads/` directory for a previously downloaded Contents-arch.gz file.
- If a cached file exists, it is used instead of downloading a new one.
- If --force-download flag is used, the cache is bypassed, and a fresh download is performed.

To bypass the cache and fetch a new Contents file (if you want an updated file):

For Windows:
```
python package_statistics.py <architecture> --force-download
```

For Linux:
```
./package_statistics.py <architecture> --force-download
```

## Substituting a Mirror

If you have a mirror that you would rather use than the mirror provided by default:

For Windows:
```
python package_statistics.py <architecture> --mirror-url <mirror_url>
```

For Linux:
```
./package_statistics.py <architecture> --mirror-url <mirror_url>
```

The default mirror being used is: http://ftp.uk.debian.org/debian/dists/stable/main/