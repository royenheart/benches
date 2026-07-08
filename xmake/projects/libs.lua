local function project_path(filepath)
    return "$(projectdir)/" .. filepath
end

-- gtest_main provides main() through a static library. MSVC infers the entry
-- point/subsystem only from object files on the link line, not from libraries,
-- so a test target whose objects contain no main() fails with LNK1561. Forcing
-- the console subsystem makes the linker use its default entry (mainCRTStartup),
-- which then resolves main() from gtest_main.lib. No-op on non-MSVC platforms.
local function gtest_console_entry()
    if is_plat("windows") then
        add_ldflags("/subsystem:console", {force = true})
    end
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

target("bench_competitive")
    set_kind("headeronly")
    add_includedirs(project_path("libs/bench_competitive/include"), {public = true})
    add_packages("fmt", {public = true})
    add_deps("bench_core", "bench_timing", {public = true})

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
    gtest_console_entry()

target("bench_data_test")
    set_kind("binary")
    add_files(project_path("libs/bench_data/tests/*.cpp"))
    add_deps("bench_data", "bench_linalg")
    add_packages("gtest")
    add_links("gtest_main")
    add_tests("bench_data")
    gtest_console_entry()

target("bench_linalg_test")
    set_kind("binary")
    add_files(project_path("libs/bench_linalg/tests/*.cpp"))
    add_deps("bench_linalg")
    add_packages("gtest")
    add_links("gtest_main")
    add_tests("bench_linalg")
    gtest_console_entry()

target("bench_competitive_test")
    set_kind("binary")
    add_files(project_path("libs/bench_competitive/tests/*.cpp"))
    add_deps("bench_competitive")
    add_packages("gtest")
    add_links("gtest_main")
    add_tests("bench_competitive")
    gtest_console_entry()
