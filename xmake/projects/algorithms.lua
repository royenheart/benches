local algorithm_problems = {
    {name = "luogu_p1003", dir = "algorithms/competitive/luogu/p1003", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "luogu_p1067", dir = "algorithms/competitive/luogu/p1067", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "luogu_p1216", dir = "algorithms/competitive/luogu/p1216", headerdir = "algorithms/competitive/test-support/include", test = false},
    {name = "luogu_p1540", dir = "algorithms/competitive/luogu/p1540", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "codeforces_div3_977a", dir = "algorithms/competitive/codeforces/div3-977a", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "codeforces_div3_977b", dir = "algorithms/competitive/codeforces/div3-977b", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "codeforces_div3_977c", dir = "algorithms/competitive/codeforces/div3-977c", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "codeforces_div3_977d", dir = "algorithms/competitive/codeforces/div3-977d", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "pat_a1", dir = "algorithms/competitive/pat/pat-a1", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "pat_a2", dir = "algorithms/competitive/pat/pat-a2", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "pat_a3", dir = "algorithms/competitive/pat/pat-a3", headerdir = "algorithms/competitive/test-support/include", test = true},
    {name = "pat_a4", dir = "algorithms/competitive/pat/pat-a4", headerdir = "algorithms/competitive/test-support/include", test = true},
}

for _, problem in ipairs(algorithm_problems) do
    target("algo_" .. problem.name)
        set_kind("binary")
        add_files(problem.dir .. "/src/*.cpp")
        add_includedirs(problem.dir .. "/include")

    target("algo_" .. problem.name .. "_test")
        set_kind("binary")
        add_files(problem.dir .. "/tests/*.cpp")
        add_includedirs(problem.dir .. "/include")
        add_includedirs(problem.headerdir)
        add_packages("gtest")
        if problem.test then
            add_tests("algo_" .. problem.name)
        end
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
        add_files(sample.dir .. "/src/*.cpp")
        if sample.openmp then
            add_packages("openmp")
        end
end
