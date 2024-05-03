cmake_minimum_required(VERSION 3.10)

# Pull in SDK (must be before project)
include(pico_sdk_import.cmake)

project(hello C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

if (PICO_SDK_VERSION_STRING VERSION_LESS "1.3.0")
    message(FATAL_ERROR "Raspberry Pi Pico SDK version 1.3.0 (or later) required. Your version is ${PICO_SDK_VERSION_STRING}")
endif()

# Initialize the SDK
pico_sdk_init()

add_executable(hello hello.c)

# pull in common dependencies and additional spi hardware support
target_link_libraries(hello pico_stdlib hardware_spi)

# create map/bin/hex file etc.
pico_add_extra_outputs(hello)
