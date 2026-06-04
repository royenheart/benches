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

option("enable_cuda")
    set_default(false)
    set_showmenu(true)
    set_description("Enable CUDA/OpenCV targets")
option_end()

add_requires("gtest", {optional = true})
add_requires("benchmark", {optional = true})
add_requires("openmp", {optional = true})

if has_config("enable_mpi") then
    add_requires("cmake::MPI", {alias = "mpi", system = true})
    add_requires("openblas", {system = true, optional = true})
end

if has_config("enable_cuda") then
    add_requires("cuda")
    add_requires("cmake::OpenCV", {
        alias = "opencv",
        system = true,
        optional = true,
        configs = {components = {"core", "imgproc", "highgui"}}
    })
end

includes("xmake/projects/libs.lua")
includes("xmake/projects/algorithms.lua")
includes("xmake/projects/numerics.lua")
includes("xmake/projects/accels.lua")
