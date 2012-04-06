cmake_minimum_required(VERSION 2.6)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_library(dcpu-emu SHARED
    emu/emu.c
)

add_executable(dcpu
    dcpu.c
)

target_link_libraries(dcpu
    dcpu-emu
)
