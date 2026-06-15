project(answer)

find_package(CUDA REQUIRED)

file (GLOB SOURCE_FILES "*.cu" )
cuda_add_library(answer SHARED ${SOURCE_FILES})

set(LIBRARY_OUTPUT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../build")
