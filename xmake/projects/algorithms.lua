local function project_path(filepath)
    return "$(projectdir)/" .. filepath
end

local function competitive_problem_name(sourcefile)
    local normalized = sourcefile:gsub("\\", "/")
    local basename = normalized:match("([^/]+)%.cpp$")
    return (basename:gsub("[^%w_]", "_"))
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

local competitive_sources =
    os.files(path.join(os.projectdir(), "algorithms", "competitive", "*.cpp"))
table.sort(competitive_sources)

local competitive_tests_disabled = {
    luogu_p1216 = true,
}

for _, sourcefile in ipairs(competitive_sources) do
    local problem_name = competitive_problem_name(sourcefile)
    local target_name = "algo_" .. problem_name

    target(target_name)
        set_kind("binary")
        add_files(sourcefile)
        add_deps("bench_competitive")
        add_defines("BENCH_COMPETITIVE_BUILD_MAIN")

    target(target_name .. "_test")
        set_kind("binary")
        add_files(sourcefile)
        add_deps("bench_competitive")
        add_defines("BENCH_COMPETITIVE_BUILD_TEST")
        add_packages("gtest")
        add_links("gtest_main")
        gtest_console_entry()
        if not competitive_tests_disabled[problem_name] then
            add_tests(target_name)
        end

    target(target_name .. "_bench")
        set_kind("binary")
        add_files(sourcefile)
        add_deps("bench_competitive")
        add_defines("BENCH_COMPETITIVE_BUILD_BENCH")
end

local algorithm_samples = {
    {name = "openmp_hello", dir = "algorithms/parallel/openmp/hello", openmp = true},
    {name = "openmp_merge_sort", dir = "algorithms/parallel/openmp/merge-sort", openmp = true},
    {name = "openmp_odd_even_sort", dir = "algorithms/parallel/openmp/odd-even-sort", openmp = true},
    {name = "cpp_char", dir = "algorithms/misc/cpp-char", openmp = false},
}

for _, sample in ipairs(algorithm_samples) do
    if (not sample.openmp) or has_config("enable_openmp") then
        target("algo_" .. sample.name)
            set_kind("binary")
            add_files(project_path(sample.dir .. "/src/*.cpp"))
            if sample.openmp then
                add_packages("openmp")
            end
    end
end
