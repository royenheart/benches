#pragma once

#include <map>
#include <string>
#include <vector>

namespace bench::accel_runtime {

std::map<std::string, std::string> capture_environment(const std::vector<std::string>& names);

} // namespace bench::accel_runtime
