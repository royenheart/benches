#include <bench/accel_runtime/environment.hpp>

#include <cstdlib>

namespace bench::accel_runtime {

std::map<std::string, std::string> capture_environment(const std::vector<std::string>& names) {
    std::map<std::string, std::string> values;
    for (const auto& name : names) {
        if (const char* value = std::getenv(name.c_str())) {
            values[name] = value;
        }
    }
    return values;
}

} // namespace bench::accel_runtime
