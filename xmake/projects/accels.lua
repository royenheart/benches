local function project_path(filepath)
    return "$(projectdir)/" .. filepath
end

target("parallel_tests_datagen")
    set_kind("binary")
    add_files(project_path("accels/experiments/parallel-tests/matrix-multiply/src/datagen.cpp"))

target("parallel_tests_matrix_openmp")
    set_kind("binary")
    add_files(project_path("accels/experiments/parallel-tests/matrix-multiply/src/matrix_cal_openmp.cpp"))
    add_includedirs(project_path("accels/experiments/parallel-tests/matrix-multiply/include"))
    add_packages("openmp")

if has_config("enable_mpi") then
    target("parallel_tests_matrix_mpi_openmp")
        set_kind("binary")
        add_files(project_path("accels/experiments/parallel-tests/matrix-multiply/src/matrix_cal_mpi_openmp.cpp"))
        add_includedirs(project_path("accels/experiments/parallel-tests/matrix-multiply/include"))
        add_packages("mpi", "openmp")
end

local openmp_labs = {
    "hello_world",
    "loop_test",
    "macro_openmp",
    "master-worker",
    "omp_funcs",
    "optimize_strength_reduction",
    "pi_calculate",
    "section_test",
    "simple_array_cal",
    "single_test",
    "sort_test",
    "synchronization_test",
    "task_test",
    "var_parallel",
    "worksharing_constructs",
}

for _, name in ipairs(openmp_labs) do
    target("accels_openmp_" .. name:gsub("-", "_"))
        set_kind("binary")
        add_files(project_path("accels/openmp/labs/" .. name .. "/src/main.cpp"))
        add_packages("openmp")
end

if has_config("enable_mpi") then
    local mpi_labs = {
        {name = "hello_world", dir = "hello-world"},
        {name = "learn_hello", dir = "learn-hello", common = true},
        {name = "scatter", dir = "scatter"},
        {name = "gather", dir = "gather", common = true},
        {name = "jacobi", dir = "jacobi", common = true},
    }

    for _, lab in ipairs(mpi_labs) do
        target("accels_mpi_" .. lab.name)
            set_kind("binary")
            add_files(project_path("accels/mpi/labs/" .. lab.dir .. "/src/main.cpp"))
            add_packages("mpi")
            if lab.common then
                add_includedirs(project_path("accels/mpi/common/include"))
                add_packages("openblas")
            end
    end
end

if has_config("enable_cuda") then
    local cuda_targets = {
        {name = "atom_opt_cpu", file = "accels/cuda/labs/atomics/src/atomOptCPU.cu", common = {"data"}},
        {name = "atom_opt_gpu", file = "accels/cuda/labs/atomics/src/atomOptGPU.cu", common = {"data"}},
        {name = "dot_mul_atom_lock", file = "accels/cuda/labs/atomics/src/dotMulAtomLock.cu"},
        {name = "cuda_stream", file = "accels/cuda/labs/streams/src/cudaStream.cu"},
        {name = "cuda_multi_stream", file = "accels/cuda/labs/streams/src/cudaMultiStream.cu"},
        {name = "cuda_multi_stream_overlap", file = "accels/cuda/labs/streams/src/cudaMultiStreamOverlap.cu"},
        {name = "io_no_pagelock_mem", file = "accels/cuda/labs/memory/src/ioNoPagelockMem.cu"},
        {name = "io_pagelock_mem", file = "accels/cuda/labs/memory/src/ioPagelockMem.cu"},
        {name = "zero_copy_mem", file = "accels/cuda/labs/memory/src/zeroCopyMem.cu"},
        {name = "get_cuda_dev_prop", file = "accels/cuda/labs/device/src/getCudaDevProp.cu"},
        {name = "dot_mul", file = "accels/cuda/labs/vector/src/dotMul.cu"},
        {name = "bitmap_shared_mem", file = "accels/cuda/labs/image/src/bitmap_sharedMem.cu", image = true},
        {name = "julia", file = "accels/cuda/labs/image/src/juila.cu", image = true},
        {name = "game_life", file = "accels/cuda/simulations/game-life/src/GameLife.cu", image = true},
        {name = "heat_conduction_no_texture", file = "accels/cuda/simulations/heat-conduction/src/heatConductionNoTexture.cu", image = true},
        {name = "heat_conduction_texture", file = "accels/cuda/simulations/heat-conduction/src/heatConductionTexture.cu", image = true},
        {name = "caustics", file = "accels/cuda/simulations/caustics/src/caustics.cu"},
        {name = "ray_tracing", file = "accels/cuda/simulations/ray-tracing/src/rayTracing.cu", image = true},
    }

    target("accels_cuda_data")
        set_kind("static")
        add_files(project_path("accels/cuda/common/src/data.cu"))
        add_includedirs(project_path("accels/cuda/common/include"), {public = true})
        add_packages("cuda")

    target("accels_cuda_image")
        set_kind("static")
        add_files(project_path("accels/cuda/common/src/image.cu"))
        add_includedirs(project_path("accels/cuda/common/include"), {public = true})
        add_packages("cuda", "opencv")

    for _, item in ipairs(cuda_targets) do
        target("accels_cuda_" .. item.name)
            set_kind("binary")
            add_files(project_path(item.file))
            add_includedirs(project_path("accels/cuda/common/include"))
            add_packages("cuda")
            if item.common then
                add_deps("accels_cuda_data")
            end
            if item.image then
                add_deps("accels_cuda_image")
                add_packages("opencv")
            end
            add_cugencodes("native")
    end
end

target("accels_simd_vec_test")
    set_kind("binary")
    add_files(project_path("accels/simd/labs/vec-test/src/main.cpp"))
    add_cxxflags("-mavx", {force = true})
