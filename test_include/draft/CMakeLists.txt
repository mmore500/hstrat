cmake_minimum_required(VERSION 3.4)
project(include)

execute_process(COMMAND git rev-parse --show-cdup OUTPUT_VARIABLE TO_ROOT)

find_package(pybind11 REQUIRED)  # or `add_subdirectory(pybind11)`

# specify the C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# RE: -fvisibility
# see https://pybind11.readthedocs.io/en/stable/faq.html#someclass-declared-with-greater-visibility-than-the-type-of-its-field-someclass-member-wattributes
SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -fcoroutines -fvisibility=hidden")

add_executable(include include.cpp)
target_include_directories(include PRIVATE "../../include/")
#target_include_directories(include PRIVATE "../../third-party/")
target_link_libraries(include PRIVATE pybind11::embed)
