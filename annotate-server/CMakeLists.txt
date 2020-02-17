cmake_minimum_required(VERSION 3.16)

project(annotate-server)

add_subdirectory(mongoose-cpp)

add_executable(annotate-server src/main.cpp)

target_include_directories(annotate-server PUBLIC mongoose-cpp)

target_link_libraries(annotate-server mongoose)