import gzip
import pathlib

# Define test directory and file path
test_dir = pathlib.Path("tests/mock_files")
test_dir.mkdir(parents=True, exist_ok=True)
test_gz_file = test_dir / "Contents-test.gz"

# Write mock data to the gzip file
mock_data = """\
bin/bash                                            admin/bash
bin/ls                                              utils/coreutils
bin/cp                                              utils/coreutils
bin/mv                                              utils/coreutils
bin/rm                                              utils/coreutils
bin/chmod                                           admin/coreutils
bin/chown                                           admin/coreutils
usr/bin/python3                                     python/python3
usr/bin/python3.11                                  python/python3.11
usr/bin/gcc                                         devel/gcc-11,devel/gcc-12
usr/bin/g++                                         devel/gcc-11,devel/gcc-12
usr/bin/make                                        devel/make
usr/bin/cmake                                       devel/cmake
usr/bin/git                                         vcs/git
usr/bin/ssh                                         net/openssh-client
usr/bin/scp                                         net/openssh-client
usr/bin/rsync                                       net/rsync
usr/bin/curl                                        net/curl
usr/bin/wget                                        net/wget
usr/lib/libc.so.6                                   libs/libc6
usr/lib/libm.so.6                                   libs/libm6
usr/lib/libcrypto.so.1.1                            libs/libssl
usr/lib/python3.11/site-packages/numpy/core/        science/python3-numpy
usr/lib/python3.11/site-packages/numpy/linalg.py    science/python3-numpy
usr/bin/dump2geo                                    science/esys-particle
usr/bin/dump2pov                                    science/esys-particle
usr/bin/dump2vtk                                    science/esys-particle
usr/bin/esysparticle                                science/esys-particle
usr/bin/fftw-wisdom                                 science/fftw
usr/bin/fftw-wisdom-3                               science/fftw
usr/bin/fftw-wisdom-3f                              science/fftw
usr/bin/fftw-wisdom-3l                              science/fftw
usr/bin/fftw-wisdom-3d                              science/fftw
"""
with gzip.open(test_gz_file, "wt", encoding="utf-8") as f:
    f.write(mock_data)

print(f"✅ Mock file generated: {test_gz_file}")