#ifndef JIT_UTIL_H
#define JIT_UTIL_H

#include <vector>
#include <string>
#include "llvm/IR/Module.h"


#define PRINT_ERROR(condition, message) PRINT_ERROR_FULL(condition, {}, message)

#define PRINT_ERROR_FULL(condition, message_creation, message) \
{                                                              \
    if (condition) {                                           \
        {                                                      \
            message_creation                                   \
            std::cerr << message << std::endl;                 \
        }                                                      \
        exit(-1);                                              \
    }                                                          \
}

struct Arguments {
    std::vector<std::string> Files;
    std::string BackEndArguments;
    std::string ApplicationArguments;
};

struct Arguments getArguments(int argc, char **argv);

//https://stackoverflow.com/questions/22239801/how-to-load-llvm-bitcode-file-from-an-ifstream
std::unique_ptr<llvm::Module> load_module(llvm::StringRef file, llvm::LLVMContext &context);

//https://stackoverflow.com/questions/874134/find-out-if-string-ends-with-another-string-in-c
bool hasEnding(std::string const &fullString, std::string const &ending);

#endif //JIT_UTIL_H
