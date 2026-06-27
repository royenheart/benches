#!/usr/bin/env python3
"""Check, list, install, and update GPGPU accelerator dependencies.

The script intentionally separates Python dependencies from system-level
NVIDIA tooling. Python dependencies are installed with uv. CUDA, Nsight,
TensorRT, and cuDNN are checked locally and reported with OS-specific
installation guidance because they depend on drivers, package repositories,
and host policy.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
PYPROJECT_EXTRA = "gpgpu-accels"
DEFAULT_SOFTWARE_ROOT = Path.home() / "softwares"
DEFAULT_MODULE_ROOT = Path.home() / "envs"
DOWNLOAD_CACHE = Path.home() / ".cache" / "benches" / "gpgpu_accels"
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
DOWNLOAD_PROGRESS_INTERVAL = 1.0
SYSTEM_CUDA_PARENT = Path("/usr/local")
CUDNN_REDIST_INDEX_URL = (
    "https://developer.download.nvidia.com/compute/cudnn/redist/cudnn/linux-x86_64/"
)
TENSORRT_README_URL = "https://raw.githubusercontent.com/NVIDIA/TensorRT/main/README.md"
DEFAULT_CUTLASS_REF = "main"

COMMANDS = {
    "cuda compiler": "nvcc",
    "Nsight Compute": "ncu",
    "Nsight Systems": "nsys",
    "CUDA object dump": "cuobjdump",
    "CUDA disassembler": "nvdisasm",
}

PYTHON_MODULES = {
    "numpy": "numpy",
    "pytest": "pytest",
    "PyTorch": "torch",
    "TileLang": "tilelang",
}

HEADER_CHECKS = {
    "CUTLASS": {
        "env": "CUTLASS_DIR",
        "headers": ("cutlass/cutlass.h", "cute/tensor.hpp"),
    },
    "cuDNN Frontend": {
        "env": "CUDNN_DIR",
        "headers": ("cudnn.h", "cudnn_frontend.h", "cudnn_frontend/cudnn_frontend.h"),
        "any": True,
    },
    "TensorRT Plugin API": {
        "env": "TENSORRT_DIR",
        "headers": ("NvInfer.h", "NvInferPlugin.h"),
    },
}

SYSTEM_DEPENDENCIES = ("cuda-toolkit", "nsight-compute", "nsight-systems")
SYSTEM_PACKAGE_NAMES = {
    "apt": {
        "cuda-toolkit": "cuda-toolkit-{series}",
        "nsight-compute": "cuda-nsight-compute-{series}",
        "nsight-systems": "cuda-nsight-systems-{series}",
        "cudnn": "cudnn9-cuda-12-9",
        "tensorrt": "libnvinfer-dev",
    },
    "dnf": {
        "cuda-toolkit": "cuda-toolkit-{series}",
        "nsight-compute": "cuda-nsight-compute-{series}",
        "nsight-systems": "cuda-nsight-systems-{series}",
        "cudnn": "cudnn",
        "tensorrt": "libnvinfer-dev",
    },
}
SYSTEM_PACKAGE_PATTERNS = {
    "cuda-toolkit": ("cuda-toolkit-13-3", "cuda-toolkit-13", "cuda-toolkit"),
    "nsight-compute": ("cuda-nsight-compute-13-3", "cuda-nsight-compute-13", "nsight-compute"),
    "nsight-systems": ("cuda-nsight-systems-13-3", "cuda-nsight-systems-13", "nsight-systems"),
    "cudnn": ("cudnn9-cuda-12-9", "cudnn9", "cudnn"),
    "tensorrt": ("libnvinfer-dev", "libnvinfer-plugin-dev", "tensorrt"),
}
DEFAULT_PYTHON_PACKAGES = ("numpy", "pytest", "torch", "tilelang")
NVIDIA_REPO_URLS = {
    "fedora": "https://developer.download.nvidia.com/compute/cuda/repos/fedora43/x86_64/cuda-fedora43.repo",
    "rhel": "https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo",
    "ubuntu": "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb",
    "debian": "https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb",
}
PROXY_ENV_KEYS = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "all_proxy",
    "ALL_PROXY",
)
NO_PROXY_ENV_KEYS = ("no_proxy", "NO_PROXY")


def run(argv: list[str], *, check: bool = True, env: dict[str, str] | None = None) -> int:
    argv = command_with_proxy(argv)
    print("+ " + " ".join(argv), flush=True)
    completed = subprocess.run(argv, cwd=REPO_ROOT, env=env, check=False)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def command_with_proxy(argv: list[str]) -> list[str]:
    proxy_items = current_proxy_items()
    if not proxy_items or not argv or argv[0] != "sudo" or (len(argv) > 1 and argv[1] == "env"):
        return argv
    return [argv[0], "env"] + [f"{key}={value}" for key, value in proxy_items] + argv[1:]


def current_proxy_items() -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for key in PROXY_ENV_KEYS + NO_PROXY_ENV_KEYS:
        value = os.environ.get(key)
        if value:
            items.append((key, value))
    return items


def apply_proxy_environment(args: argparse.Namespace) -> None:
    proxy = getattr(args, "proxy", None) or os.environ.get("BENCHES_PROXY")
    no_proxy = getattr(args, "no_proxy", None) or os.environ.get("BENCHES_NO_PROXY")
    if proxy:
        for key in PROXY_ENV_KEYS:
            os.environ[key] = proxy
    if no_proxy:
        for key in NO_PROXY_ENV_KEYS:
            os.environ[key] = no_proxy


def find_python() -> str:
    configured = os.environ.get("PYTHON")
    if configured:
        return configured
    for candidate in ("python3", "python"):
        path = shutil.which(candidate)
        if path:
            return path
    raise SystemExit("python3/python was not found in PATH")


def ensure_uv(bootstrap: bool) -> str | None:
    uv = shutil.which("uv")
    if uv:
        return uv
    if not bootstrap:
        return None
    python = find_python()
    run([python, "-m", "pip", "install", "--user", "uv"])
    return shutil.which("uv")


def command_version(command: str) -> str:
    command_name = Path(command).name
    probes = {
        "nvcc": [command, "--version"],
        "ncu": [command, "--version"],
        "nsys": [command, "--version"],
        "cuobjdump": [command, "--version"],
        "nvdisasm": [command, "--version"],
    }
    argv = probes.get(command_name, [command, "--version"])
    try:
        completed = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except OSError:
        return ""
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return lines[0] if lines else ""


def find_tool(command: str) -> Path | None:
    path = shutil.which(command)
    if path:
        return Path(path)
    for root in cuda_toolkit_roots(include_latest=True):
        candidate = root / "bin" / command
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def module_available(module: str, use_uv: bool) -> bool:
    venv_python = virtualenv_python()
    if use_uv and venv_python:
        code = f"import {module}"
        return (
            subprocess.run(
                [str(venv_python), "-c", code],
                cwd=REPO_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    return importlib.util.find_spec(module) is not None


def virtualenv_python() -> Path | None:
    if platform.system().lower() == "windows":
        candidate = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = REPO_ROOT / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else None


def candidate_roots(env_name: str) -> list[Path]:
    roots: list[Path] = []
    env_value = os.environ.get(env_name)
    if env_value:
        roots.append(Path(env_value))
    if env_name == "CUTLASS_DIR":
        roots.extend(local_sdk_roots("cutlass"))
    if env_name == "CUDNN_DIR":
        roots.extend(local_sdk_roots("cudnn"))
    if env_name == "TENSORRT_DIR":
        roots.extend(local_sdk_roots("tensorrt"))
    roots.extend(
        [
            Path("/usr"),
            Path("/usr/local"),
            Path("/usr/local/cuda"),
            Path("/opt/nvidia"),
        ]
    )
    return roots


def local_sdk_roots(name: str) -> list[Path]:
    root = DEFAULT_SOFTWARE_ROOT / name
    if not root.exists():
        return []
    return sorted((path for path in root.iterdir() if path.is_dir()), reverse=True)


def cuda_toolkit_roots(*, include_latest: bool) -> list[Path]:
    roots: list[Path] = []
    latest = SYSTEM_CUDA_PARENT / "cuda"
    if include_latest and latest.exists():
        roots.append(latest)
    if SYSTEM_CUDA_PARENT.exists():
        roots.extend(
            sorted(
                (
                    path
                    for path in SYSTEM_CUDA_PARENT.glob("cuda-*")
                    if path.exists() and path.is_dir()
                ),
                key=lambda path: version_tuple(cuda_version_from_path(path)),
                reverse=True,
            )
        )
    return unique_paths(roots)


def unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


def cuda_version_from_path(path: Path) -> str:
    if path.name == "cuda":
        return "latest"
    match = re.match(r"cuda-(.+)$", path.name)
    return match.group(1) if match else path.name


def find_header(env_name: str, header: str) -> Path | None:
    for root in candidate_roots(env_name):
        for include_dir in (root / "include", root):
            candidate = include_dir / header
            if candidate.exists():
                return candidate
    return None


def check_headers(config: dict[str, object]) -> tuple[bool, str]:
    env_name = str(config["env"])
    headers = tuple(str(header) for header in config["headers"])
    found = [(header, find_header(env_name, header)) for header in headers]
    if config.get("any"):
        present = [(header, path) for header, path in found if path]
        if present:
            header, path = present[0]
            return True, f"{header}: {path}"
        return False, f"set {env_name} or install one of: {', '.join(headers)}"
    missing = [header for header, path in found if path is None]
    if missing:
        return False, f"set {env_name} or install missing: {', '.join(missing)}"
    first = found[0][1]
    return True, str(first)


def print_status(name: str, ok: bool, detail: str = "") -> None:
    marker = "OK" if ok else "MISSING"
    suffix = f" - {detail}" if detail else ""
    print(f"{marker:7} {name}{suffix}")


def check_environment(use_uv: bool) -> int:
    failures = 0
    print("System tools")
    for name, command in COMMANDS.items():
        path = find_tool(command)
        if path:
            print_status(name, True, f"{path}; {command_version(str(path))}")
        else:
            print_status(name, False, command)
            failures += 1

    print("\nPython modules")
    for name, module in PYTHON_MODULES.items():
        ok = module_available(module, use_uv)
        print_status(name, ok)
        if not ok:
            failures += 1

    print("\nC++/CUDA headers")
    for name, config in HEADER_CHECKS.items():
        ok, detail = check_headers(config)
        print_status(name, ok, detail)
        if not ok:
            failures += 1

    print("\nPackage managers")
    print_status("uv", shutil.which("uv") is not None, shutil.which("uv") or "install uv first")

    print("\nGuidance")
    print(system_guidance())
    return 0 if failures == 0 else 1


def install_python_dependencies(args: argparse.Namespace, *, upgrade: bool) -> None:
    uv = shutil.which("uv") if args.dry_run else ensure_uv(args.bootstrap_uv)
    if not uv and args.dry_run:
        uv = "uv"
    if not uv:
        raise SystemExit("uv was not found. Install uv first or rerun with --bootstrap-uv.")
    if not PYPROJECT.exists():
        raise SystemExit(f"{PYPROJECT} does not exist")

    for spec in args.python_spec:
        command = [uv, "add", "--optional", PYPROJECT_EXTRA, spec]
        if args.dry_run:
            print("+ " + " ".join(command), flush=True)
        else:
            run(command)

    command = [uv, "sync", "--extra", PYPROJECT_EXTRA]
    if args.python:
        command.extend(["--python", args.python])
    if upgrade:
        command.append("--upgrade")
    if args.dry_run:
        print("+ " + " ".join(command), flush=True)
        return
    run(command)


def install_cutlass(args: argparse.Namespace, *, upgrade: bool) -> None:
    git = shutil.which("git")
    if not git:
        raise SystemExit("git was not found in PATH")
    ref = args.cutlass_ref or DEFAULT_CUTLASS_REF
    version = sdk_version_from_ref(ref)
    software_root = Path(args.software_root).expanduser()
    module_root = Path(args.module_root).expanduser()
    install_root = software_root / "cutlass" / version
    modulefile = module_root / "cutlass" / version

    if install_root.exists():
        command = (
            [git, "-C", str(install_root), "pull", "--ff-only"]
            if upgrade
            else [git, "-C", str(install_root), "status", "--short"]
        )
        if args.dry_run:
            print("+ " + " ".join(command), flush=True)
        else:
            run(command)
        if not args.dry_run:
            write_modulefile("cutlass", version, install_root, modulefile, "CUTLASS_DIR")
            print(f"Configured cutlass {version}: {install_root}")
            print(f"Modulefile: {modulefile}")
        return

    command = [
        git,
        "clone",
        "--depth",
        "1",
        "--branch",
        ref,
        "https://github.com/NVIDIA/cutlass.git",
        str(install_root),
    ]
    if args.dry_run:
        print("+ " + " ".join(command), flush=True)
        print(f"+ write modulefile {modulefile}", flush=True)
        return
    install_root.parent.mkdir(parents=True, exist_ok=True)
    run(command)
    write_modulefile("cutlass", version, install_root, modulefile, "CUTLASS_DIR")
    print(f"Installed cutlass {version}: {install_root}")
    print(f"Modulefile: {modulefile}")


def sdk_version_from_ref(ref: str) -> str:
    value = ref.strip().strip("/")
    if not value:
        return DEFAULT_CUTLASS_REF
    return re.sub(r"[^A-Za-z0-9._+-]+", "_", value)


def install_local_sdks(args: argparse.Namespace) -> None:
    specs = [
        {
            "name": "cudnn",
            "url": args.cudnn_url,
            "archive": args.cudnn_archive,
            "version": args.cudnn_version,
            "latest": args.latest or args.cudnn_latest,
            "env_var": "CUDNN_DIR",
        },
        {
            "name": "tensorrt",
            "url": args.tensorrt_url,
            "archive": args.tensorrt_archive,
            "version": args.tensorrt_version,
            "latest": args.latest or args.tensorrt_latest,
            "env_var": "TENSORRT_DIR",
        },
    ]
    selected = [spec for spec in specs if spec["url"] or spec["archive"] or spec["latest"]]
    if not selected:
        raise SystemExit(
            "Provide --latest, --cudnn-latest, --tensorrt-latest, "
            "--cudnn-url/--cudnn-archive, or --tensorrt-url/--tensorrt-archive."
        )
    software_root = Path(args.software_root).expanduser()
    module_root = Path(args.module_root).expanduser()
    for spec in selected:
        if spec["latest"] and not spec["url"] and not spec["archive"]:
            spec["url"] = default_sdk_url(spec["name"], args.cuda_series)
        archive = resolve_archive(spec["name"], spec["url"], spec["archive"], args.dry_run)
        version = str(spec["version"] or infer_sdk_version(spec["name"], archive.name))
        if not version:
            raise SystemExit(
                f"Could not infer {spec['name']} version from {archive.name}; pass --{spec['name']}-version."
            )
        install_root = software_root / spec["name"] / version
        modulefile = module_root / spec["name"] / version
        if args.dry_run:
            print(f"+ extract {archive} -> {install_root}", flush=True)
            print(f"+ write modulefile {modulefile}", flush=True)
            continue
        extract_archive_flat(archive, install_root)
        write_modulefile(spec["name"], version, install_root, modulefile, str(spec["env_var"]))
        print(f"Installed {spec['name']} {version}: {install_root}")
        print(f"Modulefile: {modulefile}")


def resolve_archive(name: str, url: str | None, archive: str | None, dry_run: bool) -> Path:
    if archive:
        path = Path(archive).expanduser()
        if not path.exists() and not dry_run:
            raise SystemExit(f"{name} archive does not exist: {path}")
        return path
    if not url:
        raise SystemExit(f"No archive or URL provided for {name}")
    filename = Path(urllib.parse.urlparse(url).path).name
    if not filename:
        raise SystemExit(f"Could not infer filename from URL: {url}")
    path = DOWNLOAD_CACHE / filename
    if dry_run:
        print(f"+ download {url} -> {path}", flush=True)
        return path
    DOWNLOAD_CACHE.mkdir(parents=True, exist_ok=True)
    print(f"+ download {url} -> {path}", flush=True)
    download_with_progress(url, path)
    return path


def download_with_progress(
    url: str,
    path: Path,
    *,
    chunk_size: int = DOWNLOAD_CHUNK_SIZE,
    progress_interval: float = DOWNLOAD_PROGRESS_INTERVAL,
    progress_stream: TextIO = sys.stderr,
) -> Path:
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    part_path = partial_download_path(path)
    remote_size = remote_content_length(url)

    if path.exists():
        local_size = path.stat().st_size
        if remote_size is None or local_size == remote_size:
            print(f"+ cached {path} ({format_bytes(local_size)})", flush=True)
            return path
        if local_size < remote_size:
            if part_path.exists() and part_path.stat().st_size >= local_size:
                path.unlink()
            else:
                path.replace(part_path)
        else:
            path.unlink()

    if part_path.exists() and remote_size is not None and part_path.stat().st_size == remote_size:
        part_path.replace(path)
        print(f"+ cached {path} ({format_bytes(remote_size)})", flush=True)
        return path

    resume_from = part_path.stat().st_size if part_path.exists() else 0
    headers = {"Range": f"bytes={resume_from}-"} if resume_from else {}
    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.getcode()
            if resume_from and status != 206:
                print(
                    f"+ resume not supported for {path.name}; restarting download",
                    file=progress_stream,
                    flush=True,
                )
                resume_from = 0
                part_path.unlink(missing_ok=True)

            mode = "ab" if resume_from and status == 206 else "wb"
            total_size = response_total_size(response, resume_from)
            write_response_to_file(
                response,
                part_path,
                mode,
                path.name,
                resume_from,
                total_size,
                chunk_size,
                progress_interval,
                progress_stream,
            )
    except urllib.error.HTTPError as exc:
        if exc.code == 416 and resume_from:
            total_size = parse_content_range_total(exc.headers.get("Content-Range", ""))
            if total_size is not None and resume_from == total_size:
                part_path.replace(path)
                print(f"+ cached {path} ({format_bytes(total_size)})", flush=True)
                return path
        raise SystemExit(f"Could not download {url}: HTTP {exc.code}") from exc
    except (OSError, urllib.error.URLError) as exc:
        raise SystemExit(f"Could not download {url}: {exc}") from exc

    part_path.replace(path)
    return path


def write_response_to_file(
    response: object,
    part_path: Path,
    mode: str,
    filename: str,
    resume_from: int,
    total_size: int | None,
    chunk_size: int,
    progress_interval: float,
    progress_stream: TextIO,
) -> None:
    downloaded = resume_from
    started_at = time.monotonic()
    last_progress_at = 0.0
    with part_path.open(mode) as output:
        while True:
            chunk = response.read(chunk_size)  # type: ignore[attr-defined]
            if not chunk:
                break
            output.write(chunk)
            downloaded += len(chunk)
            now = time.monotonic()
            if progress_interval <= 0 or now - last_progress_at >= progress_interval:
                print_download_progress(
                    filename,
                    downloaded,
                    total_size,
                    started_at,
                    resume_from,
                    progress_stream,
                    final=False,
                )
                last_progress_at = now
    print_download_progress(
        filename,
        downloaded,
        total_size,
        started_at,
        resume_from,
        progress_stream,
        final=True,
    )


def partial_download_path(path: Path) -> Path:
    return Path(str(path) + ".part")


def remote_content_length(url: str) -> int | None:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return parse_int_header(response.headers.get("Content-Length"))
    except (OSError, urllib.error.URLError, ValueError):
        return None


def response_total_size(response: object, resume_from: int) -> int | None:
    headers = response.headers  # type: ignore[attr-defined]
    content_range_total = parse_content_range_total(headers.get("Content-Range", ""))
    if content_range_total is not None:
        return content_range_total
    content_length = parse_int_header(headers.get("Content-Length"))
    if content_length is None:
        return None
    return resume_from + content_length


def parse_content_range_total(value: str) -> int | None:
    match = re.search(r"/(\d+)$", value)
    return int(match.group(1)) if match else None


def parse_int_header(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def print_download_progress(
    filename: str,
    downloaded: int,
    total_size: int | None,
    started_at: float,
    started_downloaded: int,
    stream: TextIO,
    *,
    final: bool,
) -> None:
    elapsed = max(time.monotonic() - started_at, 0.001)
    transferred = max(downloaded - started_downloaded, 0)
    speed = transferred / elapsed
    if total_size:
        percent = min(downloaded / total_size * 100, 100.0)
        total_text = f" / {format_bytes(total_size)} ({percent:.1f}%)"
    else:
        total_text = " / unknown"
    end = "\n" if final else "\r"
    print(
        f"  progress {filename}: {format_bytes(downloaded)}{total_text}, "
        f"{format_bytes(speed)}/s",
        end=end,
        file=stream,
        flush=True,
    )


def format_bytes(value: float) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    for unit in units:
        if abs(size) < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    raise AssertionError("unreachable")


def default_sdk_url(name: str, cuda_series: str | None) -> str:
    if name == "cudnn":
        return latest_cudnn_url(cuda_series)
    if name == "tensorrt":
        return latest_tensorrt_url(cuda_series)
    raise SystemExit(f"No default URL resolver is defined for {name}")


def latest_cudnn_url(cuda_series: str | None) -> str:
    html = fetch_text(CUDNN_REDIST_INDEX_URL)
    candidates: list[tuple[tuple[int, ...], tuple[int, ...], str]] = []
    for href in re.findall(r"href=['\"]([^'\"]+)['\"]", html):
        filename = Path(href).name
        match = re.match(
            r"cudnn-linux-x86_64-([0-9]+(?:\.[0-9]+){1,3})_cuda([0-9]+)-archive\.tar\.(?:xz|zst|gz)$",
            filename,
        )
        if not match:
            continue
        version, cuda = match.groups()
        if cuda_series and not cuda_series_matches(cuda, cuda_series):
            continue
        candidates.append(
            (
                version_tuple(version),
                version_tuple(cuda),
                urllib.parse.urljoin(CUDNN_REDIST_INDEX_URL, href),
            )
        )
    if not candidates:
        requested = f" for CUDA {cuda_series}" if cuda_series else ""
        raise SystemExit(
            f"No cuDNN Linux x86_64 archive URL found{requested} at {CUDNN_REDIST_INDEX_URL}"
        )
    return sorted(candidates)[-1][2]


def latest_tensorrt_url(cuda_series: str | None) -> str:
    readme = fetch_text(TENSORRT_README_URL)
    candidates: list[tuple[tuple[int, ...], tuple[int, ...], str]] = []
    pattern = r"https://developer\.nvidia\.com/downloads/compute/machine-learning/tensorrt/[^\s)]+Linux-x86_64[^\s)]+\.(?:tar\.zst|tar\.gz|tgz)"
    for url in re.findall(pattern, readme):
        filename = Path(urllib.parse.urlparse(url).path).name
        version = infer_sdk_version("tensorrt", filename)
        cuda = infer_tensorrt_cuda_version(filename)
        if not version or not cuda:
            continue
        if cuda_series and not cuda_series_matches(cuda, cuda_series):
            continue
        candidates.append((version_tuple(version), version_tuple(cuda), url))
    if not candidates:
        requested = f" for CUDA {cuda_series}" if cuda_series else ""
        raise SystemExit(
            f"No TensorRT Linux x86_64 archive URL found{requested} in {TENSORRT_README_URL}"
        )
    return sorted(candidates)[-1][2]


def fetch_text(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except (OSError, urllib.error.URLError) as exc:
        raise SystemExit(f"Could not fetch {url}: {exc}") from exc


def infer_tensorrt_cuda_version(filename: str) -> str:
    match = re.search(r"cuda[-_]?([0-9]+(?:\.[0-9]+)?)", filename, re.IGNORECASE)
    return match.group(1) if match else ""


def cuda_series_matches(available: str, requested: str) -> bool:
    available_norm = normalize_cuda_series(available)
    requested_norm = normalize_cuda_series(requested)
    return (
        available_norm == requested_norm
        or available_norm.startswith(requested_norm + ".")
        or requested_norm.startswith(available_norm + ".")
    )


def normalize_cuda_series(value: str) -> str:
    value = value.strip().lower()
    value = value.removeprefix("cuda")
    value = value.strip("-_ .")
    return value.replace("-", ".").replace("_", ".")


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", value))


def infer_sdk_version(name: str, filename: str) -> str:
    if name == "cudnn":
        patterns = [
            r"cudnn.*?([0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?)",
        ]
    elif name == "tensorrt":
        patterns = [
            r"TensorRT-Enterprise-([0-9]+(?:\.[0-9]+){1,3})",
            r"TensorRT-([0-9]+(?:\.[0-9]+){1,3})",
            r"tensorrt[^0-9]*([0-9]+(?:\.[0-9]+){1,3})",
        ]
    else:
        patterns = []
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def extract_archive_flat(archive: Path, install_root: Path) -> None:
    if install_root.exists():
        shutil.rmtree(install_root)
    with tempfile.TemporaryDirectory(prefix="benches-sdk-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        if is_tar_zst(archive):
            extract_tar_zst(archive, tmpdir_path)
        elif tarfile.is_tarfile(archive):
            with tarfile.open(archive) as tar:
                try:
                    tar.extractall(tmpdir_path, filter="data")
                except TypeError:
                    tar.extractall(tmpdir_path)
        elif zipfile.is_zipfile(archive):
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(tmpdir_path)
        else:
            raise SystemExit(f"Unsupported archive format: {archive}")
        source_root = single_child_dir(tmpdir_path) or tmpdir_path
        install_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_root, install_root)


def is_tar_zst(archive: Path) -> bool:
    return archive.name.endswith(".tar.zst")


def extract_tar_zst(archive: Path, destination: Path) -> None:
    tar = shutil.which("tar")
    if not tar:
        raise SystemExit("tar was not found in PATH; it is required to extract .tar.zst archives.")
    command = [tar, "--zstd", "-xf", str(archive), "-C", str(destination)]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        output = completed.stdout.strip()
        detail = f"\n{output}" if output else ""
        raise SystemExit(f"Failed to extract .tar.zst archive with tar --zstd: {archive}{detail}")


def single_child_dir(path: Path) -> Path | None:
    children = [child for child in path.iterdir()]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return None


def write_modulefile(
    name: str, version: str, install_root: Path, modulefile: Path, env_var: str
) -> None:
    modulefile.parent.mkdir(parents=True, exist_ok=True)
    include_path = install_root / "include"
    lib_path = install_root / "lib"
    lib64_path = install_root / "lib64"
    python_path = install_root / "python"
    lines = [
        "#%Module1.0",
        f'proc ModulesHelp {{ }} {{ puts stderr "{name} {version}" }}',
        f'module-whatis "{name} {version}"',
        f'set root "{install_root}"',
        f"setenv {env_var} $root",
    ]
    if include_path.exists():
        lines.append('prepend-path CPATH "$root/include"')
    if name == "cutlass" and (install_root / "tools" / "util" / "include").exists():
        lines.append('prepend-path CPATH "$root/tools/util/include"')
    if lib_path.exists():
        lines.extend(
            [
                'prepend-path LIBRARY_PATH "$root/lib"',
                'prepend-path LD_LIBRARY_PATH "$root/lib"',
            ]
        )
    if lib64_path.exists():
        lines.extend(
            [
                'prepend-path LIBRARY_PATH "$root/lib64"',
                'prepend-path LD_LIBRARY_PATH "$root/lib64"',
            ]
        )
    if python_path.exists():
        lines.append('prepend-path PYTHONPATH "$root/python"')
    if name == "tensorrt":
        lines.append('prepend-path PATH "$root/bin"')
    modulefile.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_cuda_modulefile(version: str, install_root: Path, modulefile: Path) -> None:
    modulefile.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "#%Module1.0",
        f'proc ModulesHelp {{ }} {{ puts stderr "cuda {version}" }}',
        f'module-whatis "cuda {version}"',
        f'set root "{install_root}"',
        "setenv CUDA_HOME $root",
        "setenv CUDA_PATH $root",
        'prepend-path PATH "$root/bin"',
    ]
    if (install_root / "include").exists():
        lines.append('prepend-path CPATH "$root/include"')
    for lib_dir in ("lib64", "lib"):
        if (install_root / lib_dir).exists():
            lines.extend(
                [
                    f'prepend-path LIBRARY_PATH "$root/{lib_dir}"',
                    f'prepend-path LD_LIBRARY_PATH "$root/{lib_dir}"',
                ]
            )
    if (install_root / "lib64" / "pkgconfig").exists():
        lines.append('prepend-path PKG_CONFIG_PATH "$root/lib64/pkgconfig"')
    if (install_root / "share" / "man").exists():
        lines.append('prepend-path MANPATH "$root/share/man"')
    modulefile.write_text("\n".join(lines) + "\n", encoding="utf-8")


def configure_cuda_modulefiles(module_root: Path, dry_run: bool) -> None:
    entries: list[tuple[str, Path]] = []
    latest = SYSTEM_CUDA_PARENT / "cuda"
    if latest.exists():
        entries.append(("latest", latest))
    for root in cuda_toolkit_roots(include_latest=False):
        version = cuda_version_from_path(root)
        if version and version != "latest":
            entries.append((version, root))

    if not entries:
        print("No CUDA Toolkit roots found under /usr/local/cuda or /usr/local/cuda-*")
        return

    for version, root in entries:
        modulefile = module_root / "cuda" / version
        if dry_run:
            print(f"+ write modulefile {modulefile} -> {root}", flush=True)
            continue
        write_cuda_modulefile(version, root, modulefile)
        print(f"Modulefile: {modulefile} -> {root}")


def install_system_dependencies(args: argparse.Namespace, *, upgrade: bool) -> None:
    commands = system_install_commands(args, upgrade=upgrade)
    if not commands:
        print(system_guidance())
        raise SystemExit("No automated system install command is defined for this OS.")
    for command in commands:
        command = command_with_proxy(command)
        if args.dry_run:
            print("+ " + " ".join(command), flush=True)
        else:
            run(command)
    configure_cuda_modulefiles(Path(args.module_root).expanduser(), args.dry_run)


def configure_system_repositories(args: argparse.Namespace) -> None:
    commands = system_repo_commands()
    if not commands:
        print(system_guidance())
        raise SystemExit("No automated NVIDIA repository setup is defined for this OS.")
    for command in commands:
        command = command_with_proxy(command)
        if args.dry_run:
            print("+ " + " ".join(command), flush=True)
        else:
            run(command)


def configure_environment(args: argparse.Namespace, *, upgrade: bool) -> None:
    configure_system_repositories(args)
    configure_cuda_modulefiles(Path(args.module_root).expanduser(), args.dry_run)
    install_cutlass(args, upgrade=upgrade)
    local_args = argparse.Namespace(
        latest=True,
        cudnn_latest=False,
        cudnn_url=args.cudnn_url,
        cudnn_archive=args.cudnn_archive,
        cudnn_version=args.cudnn_version,
        tensorrt_latest=False,
        tensorrt_url=args.tensorrt_url,
        tensorrt_archive=args.tensorrt_archive,
        tensorrt_version=args.tensorrt_version,
        cuda_series=args.cuda_series,
        software_root=args.software_root,
        module_root=args.module_root,
        dry_run=args.dry_run,
    )
    install_local_sdks(local_args)


def system_repo_commands() -> list[list[str]]:
    system = platform.system().lower()
    if system != "linux":
        return []
    os_release = read_os_release()
    distro = os_release.get("ID", "linux")
    version_id = os_release.get("VERSION_ID", "")
    sudo = sudo_prefix()

    if distro in {"ubuntu", "debian"}:
        url = nvidia_repo_url(distro, version_id)
        package_path = f"/tmp/{Path(url).name}"
        return [
            ["curl", "-fsSL", "-o", package_path, url],
            sudo + ["dpkg", "-i", package_path],
            sudo + ["apt-get", "update"],
        ]

    if distro == "fedora":
        url = nvidia_repo_url(distro, version_id)
        return [sudo + ["dnf", "config-manager", "addrepo", "--from-repofile=" + url]]

    if distro in {"rhel", "centos", "rocky", "almalinux"}:
        url = nvidia_repo_url("rhel", version_id)
        executable = "dnf" if shutil.which("dnf") else "yum"
        if executable == "dnf":
            return [sudo + ["dnf", "config-manager", "addrepo", "--from-repofile=" + url]]
        return [sudo + ["yum-config-manager", "--add-repo", url]]

    return []


def nvidia_repo_url(distro: str, version_id: str) -> str:
    if distro == "fedora":
        major = digits_prefix(version_id) or "43"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/fedora{major}/x86_64/cuda-fedora{major}.repo"
    if distro == "rhel":
        major = digits_prefix(version_id) or "9"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/rhel{major}/x86_64/cuda-rhel{major}.repo"
    if distro == "ubuntu":
        key = "ubuntu" + (version_id.replace(".", "") or "2404")
        if key not in {"ubuntu2204", "ubuntu2404"}:
            key = "ubuntu2404"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/{key}/x86_64/cuda-keyring_1.1-1_all.deb"
    if distro == "debian":
        major = digits_prefix(version_id) or "12"
        key = "debian" + major
        return f"https://developer.download.nvidia.com/compute/cuda/repos/{key}/x86_64/cuda-keyring_1.1-1_all.deb"
    return NVIDIA_REPO_URLS[distro]


def digits_prefix(value: str) -> str:
    chars = []
    for char in value:
        if char.isdigit():
            chars.append(char)
        else:
            break
    return "".join(chars)


def package_manager() -> str | None:
    system = platform.system().lower()
    if system != "linux":
        return None
    distro = read_os_release().get("ID", "linux")
    if distro in {"ubuntu", "debian"}:
        return "apt"
    if distro in {"fedora", "rhel", "centos", "rocky", "almalinux"}:
        return "dnf"
    return None


def sudo_prefix() -> list[str]:
    if platform.system().lower() == "linux" and os.geteuid() != 0:
        return ["sudo"]
    return []


def parse_specs(values: list[str]) -> dict[str, str]:
    specs: dict[str, str] = {}
    for value in values:
        name, separator, version = value.partition("=")
        if not name or not separator or not version:
            raise SystemExit(f"Expected NAME=VERSION, got: {value}")
        specs[name] = version
    return specs


def selected_system_packages(args: argparse.Namespace, manager: str) -> list[str]:
    package_map = SYSTEM_PACKAGE_NAMES[manager]
    specs = parse_specs(args.system_spec)
    selected = args.system_package or list(SYSTEM_DEPENDENCIES)
    packages: list[str] = []
    for logical_name in selected:
        package_name = package_map.get(logical_name, logical_name).format(
            series=default_cuda_series()
        )
        version = specs.get(logical_name) or specs.get(package_name)
        if version and manager == "apt":
            packages.append(f"{package_name}={version}")
        elif version and manager == "dnf":
            packages.append(f"{package_name}-{version}")
        else:
            packages.append(package_name)
    return packages


def default_cuda_series() -> str:
    if platform.system().lower() != "linux":
        return "13-3"
    distro = read_os_release().get("ID", "linux")
    if distro == "fedora":
        return "13-2"
    return "13-3"


def system_install_commands(args: argparse.Namespace, *, upgrade: bool) -> list[list[str]]:
    manager = package_manager()
    if manager is None:
        return []
    packages = selected_system_packages(args, manager)
    sudo = sudo_prefix()
    if manager == "apt":
        action = "install"
        command = sudo + ["apt-get", action, "-y"]
        if upgrade:
            command.append("--only-upgrade")
        return [sudo + ["apt-get", "update"], command + packages]
    if manager == "dnf":
        executable = "dnf" if shutil.which("dnf") else "yum"
        action = "upgrade" if upgrade else "install"
        return [sudo + [executable, action, "-y"] + packages]
    return []


def list_system_versions(args: argparse.Namespace) -> None:
    repo_url = nvidia_repo_index_url()
    if repo_url is None:
        print(system_guidance())
        return
    filenames = remote_repo_filenames(repo_url)
    if not filenames:
        print(f"No package index entries found at {repo_url}")
        return
    selected = args.system_package or list(SYSTEM_DEPENDENCIES)
    for logical_name in selected:
        package_names = SYSTEM_PACKAGE_PATTERNS.get(logical_name, (logical_name,))
        print(f"\n[{logical_name}]")
        matches = matching_repo_packages(filenames, package_names)
        if matches:
            for filename in matches[-40:]:
                print(filename)
        else:
            print(f"No matches in {repo_url} for: {', '.join(package_names)}")


def list_local_sdk_urls(args: argparse.Namespace) -> None:
    series_values = [args.cuda_series] if args.cuda_series else ["13", "12"]
    print("\n[local-sdk source cutlass]")
    print(f"cutlass: {DEFAULT_CUTLASS_REF}")
    print("  https://github.com/NVIDIA/cutlass.git")
    for cuda_series in series_values:
        suffix = f" CUDA {cuda_series}" if cuda_series else ""
        print(f"\n[local-sdk URLs{suffix}]")
        for name, resolver in (("cudnn", latest_cudnn_url), ("tensorrt", latest_tensorrt_url)):
            try:
                url = resolver(cuda_series)
            except SystemExit as exc:
                print(f"{name}: {exc}")
                continue
            filename = Path(urllib.parse.urlparse(url).path).name
            version = infer_sdk_version(name, filename) or "unknown"
            print(f"{name}: {version}")
            print(f"  {url}")


def nvidia_repo_index_url() -> str | None:
    system = platform.system().lower()
    if system != "linux":
        return None
    os_release = read_os_release()
    distro = os_release.get("ID", "linux")
    version_id = os_release.get("VERSION_ID", "")
    if distro == "fedora":
        major = digits_prefix(version_id) or "43"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/fedora{major}/x86_64/"
    if distro in {"rhel", "centos", "rocky", "almalinux"}:
        major = digits_prefix(version_id) or "9"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/rhel{major}/x86_64/"
    if distro == "ubuntu":
        key = "ubuntu" + (version_id.replace(".", "") or "2404")
        if key not in {"ubuntu2204", "ubuntu2404"}:
            key = "ubuntu2404"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/{key}/x86_64/"
    if distro == "debian":
        major = digits_prefix(version_id) or "12"
        return f"https://developer.download.nvidia.com/compute/cuda/repos/debian{major}/x86_64/"
    return None


def remote_repo_filenames(repo_url: str) -> list[str]:
    try:
        with urllib.request.urlopen(repo_url, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")
    except (OSError, urllib.error.URLError) as exc:
        print(f"Could not fetch NVIDIA repo index {repo_url}: {exc}")
        return []
    return sorted(set(re.findall(r"href='([^']+)'", html)))


def matching_repo_packages(filenames: list[str], package_names: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for filename in filenames:
        for package_name in package_names:
            if (
                filename.startswith(package_name + "-")
                or filename.startswith(package_name + "_")
                or filename == package_name
            ):
                matches.append(filename)
                break
    return sorted(set(matches))


def list_python_versions(args: argparse.Namespace) -> None:
    packages = args.python_package or list(DEFAULT_PYTHON_PACKAGES)
    for package in packages:
        print(f"\n[{package}] PyPI")
        url = f"https://pypi.org/pypi/{package}/json"
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            print(f"Could not fetch PyPI metadata: {exc}")
            continue
        versions = list(data.get("releases", {}).keys())
        if not versions:
            print("No versions found")
            continue
        for version in versions[-30:]:
            print(version)


def list_versions(args: argparse.Namespace) -> int:
    explicit_category = args.system or args.python or args.sdk
    list_system = args.system or not explicit_category
    list_python = args.python or not explicit_category
    list_sdk = args.sdk or not explicit_category
    if list_system:
        list_system_versions(args)
    if list_sdk:
        list_local_sdk_urls(args)
    if list_python:
        list_python_versions(args)
    return 0


def system_guidance() -> str:
    system = platform.system().lower()
    if system == "linux":
        distro = read_os_release().get("ID", "linux")
        if distro in {"ubuntu", "debian"}:
            return "\n".join(
                [
                    "Ubuntu/Debian system dependencies are normally installed from NVIDIA repositories.",
                    "Install or verify the NVIDIA driver first, then install CUDA Toolkit and Nsight tools.",
                    "CUDA/Nsight package names are versioned, e.g. cuda-toolkit-13-2 or cuda-toolkit-13-3 depending on distribution.",
                    "cuDNN and TensorRT package names vary by CUDA version and distribution; list them before installing.",
                    "Use NVIDIA's current repository instructions for your distribution and CUDA version.",
                ]
            )
        if distro in {"fedora", "rhel", "centos", "rocky", "almalinux"}:
            return "\n".join(
                [
                    "RHEL/Fedora-family systems should use NVIDIA's rpm repositories.",
                    "Install or verify the NVIDIA driver first, then CUDA Toolkit and Nsight tools.",
                    "cuDNN and TensorRT availability depends on the selected NVIDIA repository and distribution; list them before installing.",
                ]
            )
        return "Use NVIDIA's Linux repository or container images for CUDA Toolkit, Nsight, cuDNN, and TensorRT."
    if system == "darwin":
        return "\n".join(
            [
                "macOS cannot run modern local NVIDIA CUDA workloads.",
                "Use a Linux NVIDIA GPU host, WSL2 with NVIDIA GPU support, or an NVIDIA CUDA container on a Linux host.",
                "You can still use uv to prepare Python metadata locally.",
            ]
        )
    if system == "windows":
        return "\n".join(
            [
                "Windows options: install NVIDIA CUDA Toolkit and Nsight tools natively, or use WSL2 with NVIDIA GPU support.",
                "For GPGPU accelerator development, WSL2/Linux is usually closer to deployment environments.",
                "Install Python dependencies with: uv sync --extra gpgpu-accels",
            ]
        )
    return (
        "Unsupported OS for automated guidance. Prefer a Linux NVIDIA GPU host or CUDA container."
    )


def read_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def add_proxy_args(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument(
        "--proxy",
        help="temporary proxy URL for downloads/package managers, e.g. http://127.0.0.1:7890",
    )
    command_parser.add_argument(
        "--no-proxy",
        help="comma-separated hosts that bypass the temporary proxy",
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="check system tools and Python modules")
    add_proxy_args(check_parser)
    check_parser.add_argument(
        "--no-uv-run",
        action="store_true",
        help="check Python modules in the current interpreter instead of uv run",
    )

    list_parser = subparsers.add_parser(
        "list", help="list available system and Python dependency versions"
    )
    add_proxy_args(list_parser)
    list_parser.add_argument(
        "--system", action="store_true", help="list system package versions only"
    )
    list_parser.add_argument(
        "--python", action="store_true", help="list Python package versions only"
    )
    list_parser.add_argument(
        "--sdk", action="store_true", help="list latest local cuDNN/TensorRT SDK archive URLs only"
    )
    list_parser.add_argument(
        "--cuda-series",
        help="prefer a CUDA series for SDK archive URLs, e.g. 13, 13.2, 12, or 12.9",
    )
    list_parser.add_argument(
        "--system-package",
        action="append",
        default=[],
        help="logical or native system package name to list; may be repeated",
    )
    list_parser.add_argument(
        "--python-package",
        action="append",
        default=[],
        help="Python package name to list from PyPI; may be repeated",
    )

    def add_install_args(command_parser: argparse.ArgumentParser) -> None:
        add_proxy_args(command_parser)
        command_parser.add_argument("--python", help="Python interpreter/version passed to uv sync")
        command_parser.add_argument(
            "--python-spec",
            action="append",
            default=[],
            help="Python requirement to add before sync, e.g. torch==2.5.1; may be repeated",
        )
        command_parser.add_argument(
            "--bootstrap-uv",
            action="store_true",
            help="install uv with python -m pip install --user uv if uv is missing",
        )
        command_parser.add_argument(
            "--check",
            action="store_true",
            help="run dependency checks after installing dependencies",
        )
        command_parser.add_argument(
            "--system",
            action="store_true",
            help="install Linux system packages through apt/dnf when NVIDIA repositories are configured",
        )
        command_parser.add_argument(
            "--system-package",
            action="append",
            default=[],
            help="logical or native system package to install/update; default is all system dependencies",
        )
        command_parser.add_argument(
            "--system-spec",
            action="append",
            default=[],
            help="pin a system package version, e.g. nsight-compute=2026.3.1; may be repeated",
        )
        command_parser.add_argument(
            "--cutlass",
            action="store_true",
            help="clone or update CUTLASS/CuTe into ~/softwares/cutlass/<ref>",
        )
        command_parser.add_argument(
            "--cutlass-ref",
            default=DEFAULT_CUTLASS_REF,
            help="CUTLASS git branch/tag to install, default: main",
        )
        command_parser.add_argument(
            "--software-root",
            default=str(DEFAULT_SOFTWARE_ROOT),
            help="root for local SDKs, default: ~/softwares",
        )
        command_parser.add_argument(
            "--module-root",
            default=str(DEFAULT_MODULE_ROOT),
            help="root for environment modulefiles, default: ~/envs",
        )
        command_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="print install/update commands without running them",
        )

    def add_local_sdk_args(command_parser: argparse.ArgumentParser) -> None:
        add_proxy_args(command_parser)
        command_parser.add_argument(
            "--latest",
            action="store_true",
            help="use latest default Linux x86_64 cuDNN and TensorRT URLs",
        )
        command_parser.add_argument(
            "--cudnn-latest",
            action="store_true",
            help="use latest default Linux x86_64 cuDNN URL",
        )
        command_parser.add_argument("--cudnn-url", help="cuDNN tar/zip URL")
        command_parser.add_argument("--cudnn-archive", help="local cuDNN tar/zip archive")
        command_parser.add_argument("--cudnn-version", help="cuDNN version directory/module name")
        command_parser.add_argument(
            "--tensorrt-latest",
            action="store_true",
            help="use latest default Linux x86_64 TensorRT URL",
        )
        command_parser.add_argument("--tensorrt-url", help="TensorRT tar/zip URL")
        command_parser.add_argument("--tensorrt-archive", help="local TensorRT tar/zip archive")
        command_parser.add_argument(
            "--tensorrt-version", help="TensorRT version directory/module name"
        )
        command_parser.add_argument(
            "--cuda-series",
            help="prefer a CUDA series for default URLs, e.g. 13, 13.2, 12, or 12.9",
        )
        command_parser.add_argument(
            "--software-root",
            default=str(DEFAULT_SOFTWARE_ROOT),
            help="root for extracted SDKs, default: ~/softwares",
        )
        command_parser.add_argument(
            "--module-root",
            default=str(DEFAULT_MODULE_ROOT),
            help="root for environment modulefiles, default: ~/envs",
        )
        command_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="print download/extract/modulefile actions without running them",
        )

    install_parser = subparsers.add_parser("install", help="install latest dependencies by default")
    add_install_args(install_parser)

    update_parser = subparsers.add_parser(
        "update", help="update installed dependencies to newer available versions"
    )
    add_install_args(update_parser)

    configure_all_parser = subparsers.add_parser(
        "configure",
        help="configure NVIDIA repositories and local CUTLASS/cuDNN/TensorRT SDKs",
    )
    configure_all_parser.add_argument(
        "--cutlass-ref",
        default=DEFAULT_CUTLASS_REF,
        help="CUTLASS git branch/tag to install, default: main",
    )
    add_local_sdk_args(configure_all_parser)

    configure_parser = subparsers.add_parser(
        "configure-repos", help="configure NVIDIA CUDA package repositories"
    )
    add_proxy_args(configure_parser)
    configure_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print repository setup commands without running them",
    )

    cuda_parser = subparsers.add_parser(
        "configure-cuda",
        help="write CUDA Toolkit modulefiles from /usr/local/cuda and /usr/local/cuda-*",
    )
    cuda_parser.add_argument(
        "--module-root",
        default=str(DEFAULT_MODULE_ROOT),
        help="root for environment modulefiles, default: ~/envs",
    )
    cuda_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print modulefile actions without writing them",
    )

    local_sdk_parser = subparsers.add_parser(
        "install-local-sdks",
        help="download/extract local cuDNN and TensorRT SDK archives and write environment modulefiles",
    )
    add_local_sdk_args(local_sdk_parser)

    update_sdk_parser = subparsers.add_parser(
        "update-local-sdks",
        help="update local CUTLASS and latest cuDNN/TensorRT SDK archives and modulefiles",
    )
    update_sdk_parser.add_argument(
        "--cutlass-ref",
        default=DEFAULT_CUTLASS_REF,
        help="CUTLASS git branch/tag to update, default: main",
    )
    add_local_sdk_args(update_sdk_parser)

    subparsers.add_parser("guidance", help="print OS-specific system dependency guidance")

    args = parser.parse_args(argv)
    apply_proxy_environment(args)
    if args.command == "check":
        return check_environment(use_uv=not args.no_uv_run)
    if args.command == "configure":
        configure_environment(args, upgrade=False)
        return 0
    if args.command == "configure-repos":
        configure_system_repositories(args)
        return 0
    if args.command == "configure-cuda":
        configure_cuda_modulefiles(Path(args.module_root).expanduser(), args.dry_run)
        return 0
    if args.command == "install-local-sdks":
        install_local_sdks(args)
        return 0
    if args.command == "update-local-sdks":
        args.latest = True
        install_cutlass(args, upgrade=True)
        install_local_sdks(args)
        return 0
    if args.command == "list":
        return list_versions(args)
    if args.command == "install":
        if args.system:
            install_system_dependencies(args, upgrade=False)
        if args.cutlass:
            install_cutlass(args, upgrade=False)
        install_python_dependencies(args, upgrade=False)
        if args.check:
            return check_environment(use_uv=True)
        return 0
    if args.command == "update":
        if args.system:
            install_system_dependencies(args, upgrade=True)
        if args.cutlass:
            install_cutlass(args, upgrade=True)
        install_python_dependencies(args, upgrade=True)
        if args.check:
            return check_environment(use_uv=True)
        return 0
    if args.command == "guidance":
        print(system_guidance())
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
