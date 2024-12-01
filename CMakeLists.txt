cmake_minimum_required(VERSION 3.15...3.27)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX)

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
# https://github.com/scikit-build/scikit-build/issues/506#issuecomment-706791791
if(SKBUILD)
  set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
  set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
  set(Python_LIBRARY "${PYTHON_LIBRARY}")
endif()
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 20)
if (MSVC)
    # Windows (MSVC-specific flags)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /arch:SSE4.2 /W4 /permissive-")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Zi /Od /MDd")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /DNDEBUG /MD")
else()
    # Non-Windows (GCC/Clang-specific flags)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -msse4.2 -Wall -Wextra")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")
endif()

find_package(pybind11 CONFIG REQUIRED)
# or add_subdirectory(pybind11)

# Find all .cpp files in the hstrat directory
file(GLOB_RECURSE HSTRAT_CPP_FILES ${CMAKE_SOURCE_DIR}/hstrat/*.cpp)
list(FILTER HSTRAT_CPP_FILES EXCLUDE REGEX "\\.rendered.*\\.cpp")

# Loop through each .cpp file and create a pybind11 module
foreach(CPP_FILE ${HSTRAT_CPP_FILES})
    # Extract the relative path and create a module name
    file(RELATIVE_PATH REL_PATH ${CMAKE_SOURCE_DIR}/hstrat ${CPP_FILE})

    # Replace directory separators with dots for module naming
    get_filename_component(MODULE_NAME ${CPP_FILE} NAME_WE)
    message(STATUS "MODULE_NAME: ${MODULE_NAME}")

    # Get the directory component of the relative path
    get_filename_component(REL_DIR ${REL_PATH} DIRECTORY)

    # Add the module
    # RE https://github.com/pybind/scikit_build_example/blob/550c09c1906c92f2709769cd8b859c941c575537/CMakeLists.txt
    pybind11_add_module(${MODULE_NAME} ${CPP_FILE} WITH_SOABI)
    target_link_libraries(${MODULE_NAME} PRIVATE pybind11::headers)
    target_include_directories(${MODULE_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/hstrat)

    # Install the module into the corresponding directory in the wheel
    install(TARGETS ${MODULE_NAME} LIBRARY DESTINATION hstrat/${REL_DIR})
endforeach()
