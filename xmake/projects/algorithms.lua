local function project_path(filepath)
    return "$(projectdir)/" .. filepath
end

local function competitive_problem_name(sourcefile)
    local normalized = sourcefile:gsub("\\", "/")
    local basename = normalized:match("([^/]+)%.cpp$")
    return (basename:gsub("[^%w_]", "_"))
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
    target("algo_" .. sample.name)
        set_kind("binary")
        add_files(project_path(sample.dir .. "/src/*.cpp"))
        if sample.openmp then
            add_packages("openmp")
        end
end
