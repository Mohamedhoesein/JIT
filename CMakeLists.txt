cmake_minimum_required(VERSION 3.20)
project(jit)

# Set variables needed for compilation
set(CMAKE_DEBUG_POSTFIX d)
set(CMAKE_PREFIX_PATH "./lib/llvm")
set(NO_RTTI "-fno-rtti")
set(LLVM_ENABLE_ASSERTIONS ON)
add_compile_options(${NO_RTTI})
SET(FRONTEND "LLVM_FRONTEND")
add_compile_definitions(${FRONTEND})
set(JIT "SIMPLE_JIT_BACK_END")
add_compile_definitions(${JIT})

# Look for LLVM, and set the definitions
find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
message(STATUS "LLVM_INCLUDE_DIRS: ${LLVM_INCLUDE_DIRS}")
message(STATUS "LLVM_DEFINITIONS_LIST: ${LLVM_DEFINITIONS_LIST}")

include_directories(${LLVM_INCLUDE_DIRS})
separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})
add_compile_definitions(${LLVM_DEFINITIONS_LIST})

# Build the jit
add_executable(jit FrontEnd.cpp
        reOptimize/ReOptimizeLayer.cpp
        reOptimize/ReOptimizeLayer.h
        reOptimize/RedirectionManager.cpp
        reOptimize/RedirectionManager.h
        reOptimize/JITLinkRedirectableSymbolManager.cpp
        reOptimize/JITLinkRedirectableSymbolManager.h
        util/StringToArgv.cpp
        util/StringToArgv.h
        util/Util.cpp
        util/Util.h
        back-end/JIT.h
        back-end/JIT.cpp
        back-end/BaseJIT.h
        back-end/BaseJit.cpp
        front-end/BaseFrontend.h
        front-end/BaseFrontend.cpp
        front-end/LLVMFrontend.cpp
        front-end/LLVMFrontend.h)

# Find the libraries that correspond to the LLVM components
llvm_map_components_to_libnames(LLVM_LIBRARIES Core orcjit native Support)

# Link against LLVM libraries
target_include_directories(jit PRIVATE ${LLVM_INCLUDE_DIRS})
target_compile_definitions(jit PRIVATE ${LLVM_DEFINITIONS})
target_link_libraries(jit PRIVATE ${LLVM_LIBRARIES})