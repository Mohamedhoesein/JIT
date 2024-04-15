#ifndef JIT_UTIL_H
#define JIT_UTIL_H

#include <ctime>
#include <iostream>
#include <string>
#include <vector>
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

#define LOG_TYPES     \
X(List, "LIST")       /* If you want to list all values of a specific tag. */\
X(Average, "AVERAGE") /* If you want to take the average of all the values of the tag. */

#define X(type, name) type,
enum LogType : size_t
{
    LOG_TYPES
};
#undef X

void print_log_data(const std::string& tag, LogType type, const std::string& data);

std::vector<std::string> split(const std::string& string, char delimiter);

std::vector<std::string> split_once(const std::string& string, char delimiter);

struct Arguments getArguments(int argc, char **argv);

//https://stackoverflow.com/questions/22239801/how-to-load-llvm-bitcode-file-from-an-ifstream
std::unique_ptr<llvm::Module> load_module(llvm::StringRef file, llvm::LLVMContext &context);

//https://stackoverflow.com/questions/874134/find-out-if-string-ends-with-another-string-in-c
bool hasEnding(std::string const &fullString, std::string const &ending);

#endif //JIT_UTIL_H
