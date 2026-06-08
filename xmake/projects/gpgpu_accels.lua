if has_config("enable_gpgpu_accels") then
    local function local_sdk_dir(name, version)
        local home = os.getenv("HOME")
        if home then
            local candidate = path.join(home, "softwares", name, version)
            if os.isdir(candidate) then
                return candidate
            end
        end
        return nil
    end

    target("gpgpu_accels_vendor")
        set_kind("headeronly")
        add_packages("cuda", {public = true})

        local cutlass_dir = get_config("cutlass_dir")
        if not cutlass_dir or cutlass_dir == "" then
            cutlass_dir = os.getenv("CUTLASS_DIR") or local_sdk_dir("cutlass", "main")
        end
        if cutlass_dir and cutlass_dir ~= "" then
            add_includedirs(path.join(cutlass_dir, "include"), {public = true})
            add_includedirs(path.join(cutlass_dir, "tools", "util", "include"), {public = true})
        end

        local cudnn_dir = get_config("cudnn_dir")
        if not cudnn_dir or cudnn_dir == "" then
            cudnn_dir = os.getenv("CUDNN_DIR")
        end
        if cudnn_dir and cudnn_dir ~= "" then
            add_includedirs(path.join(cudnn_dir, "include"), {public = true})
            add_linkdirs(path.join(cudnn_dir, "lib"), {public = true})
            add_linkdirs(path.join(cudnn_dir, "lib64"), {public = true})
            add_links("cudnn", {public = true})
        end

        local tensorrt_dir = get_config("tensorrt_dir")
        if not tensorrt_dir or tensorrt_dir == "" then
            tensorrt_dir = os.getenv("TENSORRT_DIR")
        end
        if tensorrt_dir and tensorrt_dir ~= "" then
            add_includedirs(path.join(tensorrt_dir, "include"), {public = true})
            add_linkdirs(path.join(tensorrt_dir, "lib"), {public = true})
            add_linkdirs(path.join(tensorrt_dir, "lib64"), {public = true})
            add_links("nvinfer", "nvinfer_plugin", "nvonnxparser", {public = true})
        end
end
