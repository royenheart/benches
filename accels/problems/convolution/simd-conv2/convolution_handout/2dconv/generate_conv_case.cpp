#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>

namespace fs = std::filesystem;

static void usage(const char* program) {
  std::cerr << "Usage: " << program
            << " <output-dir> <input-rows> <input-cols> <kernel-rows> <kernel-cols> [seed]\n";
  std::exit(2);
}

static std::vector<float> random_matrix(std::size_t count, std::mt19937& rng) {
  std::uniform_real_distribution<float> dist(-1.0f, 1.0f);
  std::vector<float> values(count);
  for (float& value : values) {
    value = dist(rng);
  }
  return values;
}

static void write_matrix(const fs::path& path, int rows, int cols, const std::vector<float>& values) {
  std::ofstream output(path);
  output << rows << ' ' << cols << '\n';
  output << std::setprecision(9);
  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      if (c != 0) {
        output << ' ';
      }
      output << values[static_cast<std::size_t>(r) * cols + c];
    }
    output << '\n';
  }
}

int main(int argc, char** argv) {
  if (argc != 6 && argc != 7) {
    usage(argv[0]);
  }

  const fs::path output_dir = argv[1];
  const int input_rows = std::stoi(argv[2]);
  const int input_cols = std::stoi(argv[3]);
  const int kernel_rows = std::stoi(argv[4]);
  const int kernel_cols = std::stoi(argv[5]);
  const unsigned seed = argc == 7 ? static_cast<unsigned>(std::stoul(argv[6])) : 0U;

  if (input_rows <= 0 || input_cols <= 0 || kernel_rows <= 0 || kernel_cols <= 0 ||
      kernel_rows > input_rows || kernel_cols > input_cols) {
    usage(argv[0]);
  }

  std::mt19937 rng(seed);
  const auto input = random_matrix(static_cast<std::size_t>(input_rows) * input_cols, rng);
  const auto kernel = random_matrix(static_cast<std::size_t>(kernel_rows) * kernel_cols, rng);

  const int output_rows = input_rows - kernel_rows + 1;
  const int output_cols = input_cols - kernel_cols + 1;
  std::vector<float> output(static_cast<std::size_t>(output_rows) * output_cols, 0.0f);

  for (int r = 0; r < output_rows; ++r) {
    for (int c = 0; c < output_cols; ++c) {
      float sum = 0.0f;
      for (int kr = 0; kr < kernel_rows; ++kr) {
        for (int kc = 0; kc < kernel_cols; ++kc) {
          sum += input[static_cast<std::size_t>(r + kr) * input_cols + c + kc] *
                 kernel[static_cast<std::size_t>(kr) * kernel_cols + kc];
        }
      }
      output[static_cast<std::size_t>(r) * output_cols + c] = sum;
    }
  }

  fs::create_directories(output_dir);
  write_matrix(output_dir / "input.txt", input_rows, input_cols, input);
  write_matrix(output_dir / "weight.txt", kernel_rows, kernel_cols, kernel);
  write_matrix(output_dir / "output.txt", output_rows, output_cols, output);
}
