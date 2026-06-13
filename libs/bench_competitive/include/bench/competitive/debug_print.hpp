#pragma once

#include <fmt/ranges.h>

#include <array>
#include <deque>
#include <list>
#include <map>
#include <ostream>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace bench::competitive::debug_print_detail {

template <typename T>
std::ostream& write_formatted(std::ostream& output, const T& value) {
    return output << fmt::format("{}", value);
}

} // namespace bench::competitive::debug_print_detail

template <typename T, typename Allocator>
std::ostream& operator<<(std::ostream& output,
                         const std::vector<T, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename T, typename Allocator>
std::ostream& operator<<(std::ostream& output,
                         const std::deque<T, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename T, typename Allocator>
std::ostream& operator<<(std::ostream& output,
                         const std::list<T, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename T, std::size_t Size>
std::ostream& operator<<(std::ostream& output,
                         const std::array<T, Size>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename Key, typename Compare, typename Allocator>
std::ostream& operator<<(std::ostream& output,
                         const std::set<Key, Compare, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename Key, typename Hash, typename Equal, typename Allocator>
std::ostream&
operator<<(std::ostream& output,
           const std::unordered_set<Key, Hash, Equal, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename Key, typename T, typename Compare, typename Allocator>
std::ostream& operator<<(std::ostream& output,
                         const std::map<Key, T, Compare, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}

template <typename Key, typename T, typename Hash, typename Equal,
          typename Allocator>
std::ostream&
operator<<(std::ostream& output,
           const std::unordered_map<Key, T, Hash, Equal, Allocator>& value) {
    return bench::competitive::debug_print_detail::write_formatted(output,
                                                                   value);
}
