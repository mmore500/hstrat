cmake_minimum_required(VERSION 3.15...3.22)
set(CMAKE_CXX_STANDARD 20)

find_package(Python 3.7 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
# or add_subdirectory(pybind11)

# Find all .cpp files in the hstrat directory
file(GLOB_RECURSE HSTRAT_CPP_FILES ${CMAKE_SOURCE_DIR}/hstrat/*.cpp)

# Loop through each .cpp file and create a pybind11 module
foreach(CPP_FILE ${HSTRAT_CPP_FILES})
    # Extract the relative path and create a module name
    file(RELATIVE_PATH REL_PATH ${CMAKE_SOURCE_DIR}/hstrat ${CPP_FILE})

    # Replace directory separators with dots for module naming
    string(REPLACE "/" "." MODULE_NAME ${REL_PATH})
    string(REPLACE "\\" "." MODULE_NAME ${MODULE_NAME}) # For Windows paths
    string(REPLACE ".cpp" "" MODULE_NAME ${MODULE_NAME})

    # Add the module
    pybind11_add_module(${MODULE_NAME} ${CPP_FILE})

    # Optionally, set include directories for the module
    target_include_directories(${MODULE_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/hstrat)
endforeach()
