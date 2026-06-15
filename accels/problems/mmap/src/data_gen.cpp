#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <string>

static void usage(const char* program) {
  std::cerr << "Usage: " << program << " <output-path> <threads> <log2-n> [seed]\n";
  std::exit(2);
}

static void write_i32(std::ofstream& output, std::int32_t value) {
  output.write(reinterpret_cast<const char*>(&value), sizeof(value));
}

int main(int argc, char** argv) {
  if (argc != 4 && argc != 5) {
    usage(argv[0]);
  }

  const std::filesystem::path output_path = argv[1];
  const auto threads = static_cast<std::int32_t>(std::stol(argv[2]));
  const int log2_n = std::stoi(argv[3]);
  const unsigned seed = argc == 5 ? static_cast<unsigned>(std::stoul(argv[4])) : 0U;

  if (threads <= 0 || log2_n < 0 || log2_n > 28) {
    usage(argv[0]);
  }

  const auto n = static_cast<std::int32_t>(1U << log2_n);
  std::mt19937 rng(seed);
  std::uniform_int_distribution<std::int32_t> dist(0, 1 << 30);

  if (!output_path.parent_path().empty()) {
    std::filesystem::create_directories(output_path.parent_path());
  }
  std::ofstream output(output_path, std::ios::binary);
  write_i32(output, threads);
  write_i32(output, n);
  for (std::int32_t i = 0; i < n; ++i) {
    write_i32(output, dist(rng));
  }
}
