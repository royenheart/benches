local function project_path(filepath)
    return "$(projectdir)/" .. filepath
end

target("numerics_lu_crout")
    set_kind("static")
    add_files(project_path("numerics/linear-algebra/lu-crout/src/*.c"))
    add_includedirs(project_path("numerics/linear-algebra/lu-crout/include"), {public = true})

target("numerics_lu_crout_example")
    set_kind("binary")
    add_files(project_path("numerics/linear-algebra/lu-crout/examples/lu.c"))
    add_deps("numerics_lu_crout")
    add_includedirs(project_path("numerics/linear-algebra/lu-crout/include"))
