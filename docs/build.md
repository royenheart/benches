# Build Notes

The repository is organized around xmake. Install xmake before running project targets.

Common commands:

```bash
xmake f -m debug
xmake
xmake test
```

Environment-sensitive groups such as CUDA, MPI, OpenCV, OpenBLAS, MKL, and KML are kept in separate xmake fragments so ordinary algorithm tests can run without accelerator or cluster dependencies.

CUDA and MPI targets are disabled by default because they require local SDKs/toolchains:

```bash
xmake f --enable_cuda=true
xmake f --enable_mpi=true
```
