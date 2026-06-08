---
name: benches-development
description: Use when modifying this benches repository, adding experiments, tests, benchmarks, tooling, or dependency scripts.
---

# Benches Development Rules

## Repository Boundaries

- `backups/` is source material only. Do not modify, delete, reformat, or migrate from it unless the user explicitly asks.
- `libs/` contains reusable project-owned helper libraries. Put shared test, benchmark, data, timing, and accelerator helpers here.
- `tests/inputs/` contains correctness-test input files. `tests/expected/` contains expected output files.
- `benchmarks/suites/` contains performance benchmark programs. `benchmarks/data/` contains benchmark inputs. `benchmarks/results/` contains generated benchmark output and is ignored.
- `accels/` is for accelerator, parallel, SIMD, CUDA, MPI, OpenMP, and related experiments.
- `algorithms/` is for algorithm and competitive-programming style code.
- `numerics/` is for numerical methods experiments.
- `tools/` is for repository automation scripts. Keep migration logs out of version control.

## Build And Test

- Use xmake as the build entry point.
- Configure a clean debug build with `xmake f -c -m debug`.
- Build with `xmake` or `xmake build <target>`.
- Run correctness tests with `xmake test -v`.
- Generate compile commands for clangd/static analysis with:
  `xmake project -k compile_commands --lsp=clangd .`

## Formatting And Linting

- C, C++, CUDA, and headers use `.clang-format`.
- Python uses Black for formatting and flake8 for linting.
- Format Python with `uv run --extra dev black tools`.
- Lint Python with `uv run --extra dev flake8 tools`.
- Do not reformat `backups/`, generated files, build outputs, or downloaded SDKs.

## GPGPU Environment

- Use `xmake install_gpgpu_accels` for CUDA Toolkit, Nsight tools, and Python dependencies.
- Use `xmake install_gpgpu_sdks` or `xmake update_gpgpu_sdks` for CUTLASS, cuDNN, and TensorRT under `~/softwares/<name>/<version>` with modulefiles under `~/envs/<name>/<version>`.
- Use `BENCHES_PROXY` and `BENCHES_NO_PROXY` for temporary project-wide proxy settings.
- Do not place external SDK sources in `libs/`; use `~/softwares` or package managers.

## VSCode

- Keep `.vscode/settings.json`, `tasks.json`, `launch.json`, and `extensions.json` versioned.
- Debug targets through the configured xmake tasks.
- Use Nsight Systems, Nsight Compute, and Linux perf through VSCode tasks when profiling.

## Change Discipline

- Keep edits scoped to the requested area.
- Preserve existing code, tests, and experiment explanations.
- Add tests or focused verification when changing shared library behavior or build/tooling contracts.
- Before claiming completion, run the relevant verification command and report what passed or failed.
