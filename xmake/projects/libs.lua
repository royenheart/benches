local function project_path(filepath)
    return "$(projectdir)/" .. filepath
end

target("bench_core")
    set_kind("headeronly")
    add_includedirs(project_path("libs/bench_core/include"), {public = true})

target("bench_data")
    set_kind("static")
    add_files(project_path("libs/bench_data/src/*.cpp"))
    add_includedirs(project_path("libs/bench_data/include"), {public = true})
    add_deps("bench_core", "bench_linalg")

target("bench_linalg")
    set_kind("headeronly")
    add_includedirs(project_path("libs/bench_linalg/include"), {public = true})

target("bench_timing")
    set_kind("headeronly")
    add_includedirs(project_path("libs/bench_timing/include"), {public = true})

target("bench_accel_runtime")
    set_kind("static")
    add_files(project_path("libs/bench_accel_runtime/src/*.cpp"))
    add_includedirs(project_path("libs/bench_accel_runtime/include"), {public = true})

target("bench_core_test")
    set_kind("binary")
    add_files(project_path("libs/bench_core/tests/*.cpp"))
    add_deps("bench_core")
    add_packages("gtest")
    add_links("gtest_main")
    add_tests("bench_core")

target("bench_data_test")
    set_kind("binary")
    add_files(project_path("libs/bench_data/tests/*.cpp"))
    add_deps("bench_data", "bench_linalg")
    add_packages("gtest")
    add_links("gtest_main")
    add_tests("bench_data")

target("bench_linalg_test")
    set_kind("binary")
    add_files(project_path("libs/bench_linalg/tests/*.cpp"))
    add_deps("bench_linalg")
    add_packages("gtest")
    add_links("gtest_main")
    add_tests("bench_linalg")
