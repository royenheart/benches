-- Benches quick reference
--
-- Set proxy:
--   BENCHES_PROXY=http://127.0.0.1:7890
--
-- Base build/test:
--   xmake f -c -m debug       # configure a clean debug build
--   xmake                     # build all default targets
--   xmake test -v             # run registered tests verbosely
--   xmake show -l targets     # list available targets
--   xmake run <target>        # run one executable target
--   xmake project -k compile_commands --lsp=clangd . # generate clangd database
--
-- Formatting/linting:
--   uv run --extra dev black tools
--   uv run --extra dev flake8 tools
--   clang-format -i <file.cpp>
--
-- Optional target groups:
--   xmake f -c -m debug --enable_mpi=true
--   xmake f -c -m debug --enable_compute_graphics=true
--   xmake f -c -m debug --enable_gpgpu_accels=true
--
-- GPGPU accelerator environment:
--   xmake check_gpgpu_accels  # check CUDA/Nsight/PyTorch/TileLang tools
--   xmake configure_gpgpu_accels # configure NVIDIA repos and local SDK modulefiles
--   xmake list_gpgpu_accels   # list installable versions and local SDK URLs
--   xmake install_gpgpu_accels # install CUDA/Nsight system deps and Python deps
--   xmake update_gpgpu_accels # update CUDA/Nsight system deps and Python deps
--   xmake install_gpgpu_sdks # install latest local CUTLASS/cuDNN/TensorRT SDKs
--   xmake update_gpgpu_sdks # update latest local CUTLASS/cuDNN/TensorRT SDKs
--
--   After installing local SDKs, load them in the shell before building/running targets:
--      module use ~/envs && module load cuda/latest
--
-- Advanced dependency control:
--   python3 tools/env/gpgpu_accels_env.py configure
--   python3 tools/env/gpgpu_accels_env.py install --system --proxy http://127.0.0.1:7890
--   python3 tools/env/gpgpu_accels_env.py configure-repos
--   python3 tools/env/gpgpu_accels_env.py configure-cuda
--   python3 tools/env/gpgpu_accels_env.py install --system --cutlass --bootstrap-uv
--   python3 tools/env/gpgpu_accels_env.py install --system-spec nsight-compute=<version>
--   python3 tools/env/gpgpu_accels_env.py list --sdk
--   python3 tools/env/gpgpu_accels_env.py list --sdk --cuda-series 12
--   python3 tools/env/gpgpu_accels_env.py install-local-sdks --latest
--   python3 tools/env/gpgpu_accels_env.py update-local-sdks
--   python3 tools/env/gpgpu_accels_env.py install-local-sdks --latest --cuda-series 13
--   python3 tools/env/gpgpu_accels_env.py install-local-sdks --cudnn-archive <tar.xz> --cudnn-version <version>
--   python3 tools/env/gpgpu_accels_env.py install-local-sdks --tensorrt-archive <tar.zst|tar.gz> --tensorrt-version <version>

set_project("benches")
set_version("0.1.0")

add_rules("mode.debug", "mode.release")
set_languages("c17", "c++17")
set_warnings("all")

option("enable_mpi")
    set_default(false)
    set_showmenu(true)
    set_description("Enable MPI/OpenBLAS targets")
option_end()

option("enable_compute_graphics")
    set_default(false)
    set_showmenu(true)
    set_description("Enable compute/graphics targets, currently CUDA/OpenCV and later OpenGL/Vulkan")
option_end()

option("enable_gpgpu_accels")
    set_default(false)
    set_showmenu(true)
    set_description("Enable GPGPU accelerator development checks and optional include/library paths")
option_end()

option("cutlass_dir")
    set_default("")
    set_showmenu(true)
    set_description("CUTLASS/CuTe root directory for GPGPU accelerator targets")
option_end()

option("cudnn_dir")
    set_default("")
    set_showmenu(true)
    set_description("cuDNN root directory for GPGPU accelerator targets")
option_end()

option("tensorrt_dir")
    set_default("")
    set_showmenu(true)
    set_description("TensorRT root directory for GPGPU accelerator targets")
option_end()

add_requires("gtest", {optional = true})
add_requires("benchmark", {optional = true})
add_requires("openmp", {optional = true})

if has_config("enable_mpi") then
    add_requires("cmake::MPI", {alias = "mpi", system = true})
    add_requires("openblas", {system = true, optional = true})
end

if has_config("enable_compute_graphics") then
    add_requires("cuda")
    add_requires("cmake::OpenCV", {
        alias = "opencv",
        system = true,
        optional = true,
        configs = {components = {"core", "imgproc", "highgui"}}
    })
end

if has_config("enable_gpgpu_accels") then
    add_requires("cuda")
end

local function project_script(script)
    return path.join(os.projectdir(), script)
end

local function python_command()
    return os.getenv("PYTHON") or "python3"
end

task("check_gpgpu_accels")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "check"})
    end)
    set_menu {
        usage = "xmake check_gpgpu_accels",
        description = "Check CUDA Toolkit, Nsight tools, PyTorch, TileLang, cuDNN, TensorRT guidance.",
    }

task("configure_gpgpu_accels")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "configure"})
    end)
    set_menu {
        usage = "xmake configure_gpgpu_accels",
        description = "Configure NVIDIA repositories and local CUTLASS/cuDNN/TensorRT SDK modulefiles.",
    }

task("list_gpgpu_accels")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "list"})
    end)
    set_menu {
        usage = "xmake list_gpgpu_accels",
        description = "List available GPGPU accelerator dependency versions.",
    }

task("install_gpgpu_accels")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "install", "--system", "--bootstrap-uv", "--check"})
    end)
    set_menu {
        usage = "xmake install_gpgpu_accels",
        description = "Install CUDA/Nsight system packages and Python GPGPU accelerator dependencies, then run checks.",
    }

task("update_gpgpu_accels")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "update", "--system", "--bootstrap-uv", "--check"})
    end)
    set_menu {
        usage = "xmake update_gpgpu_accels",
        description = "Update CUDA/Nsight system packages and Python GPGPU accelerator dependencies, then run checks.",
    }

task("install_gpgpu_sdks")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "update-local-sdks"})
    end)
    set_menu {
        usage = "xmake install_gpgpu_sdks",
        description = "Install latest local CUTLASS/cuDNN/TensorRT SDKs and write modulefiles.",
    }

task("update_gpgpu_sdks")
    set_category("plugin")
    on_run(function ()
        os.execv(python_command(), {project_script("tools/env/gpgpu_accels_env.py"), "update-local-sdks"})
    end)
    set_menu {
        usage = "xmake update_gpgpu_sdks",
        description = "Update local CUTLASS/cuDNN/TensorRT SDKs and rewrite modulefiles.",
    }

includes("xmake/projects/libs.lua")
includes("xmake/projects/algorithms.lua")
includes("xmake/projects/numerics.lua")
includes("xmake/projects/accels.lua")
includes("xmake/projects/gpgpu_accels.lua")
