set_project("benches")
set_version("0.1.0")

add_rules("mode.debug", "mode.release")
set_languages("c17", "c++17")
set_warnings("all")

add_requires("gtest", {optional = true})
add_requires("benchmark", {optional = true})
add_requires("openmp", {optional = true})
add_requires("cmake::MPI", {alias = "mpi", system = true, optional = true})
add_requires("cuda", {optional = true})
add_requires("cmake::OpenCV", {
    alias = "opencv",
    system = true,
    optional = true,
    configs = {components = {"core", "imgproc", "highgui"}}
})
add_requires("openblas", {system = true, optional = true})

includes("xmake/projects/libs.lua")
includes("xmake/projects/algorithms.lua")
includes("xmake/projects/numerics.lua")
includes("xmake/projects/accels.lua")
