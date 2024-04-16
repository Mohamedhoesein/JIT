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

/**
 * A struct wrapping the arguments to the application.
 */
struct Arguments {
    /**
     * The files to load.
     */
    std::vector<std::string> Files;
    /**
     * The arguments for the front-end.
     */
    std::string FrontEndArguments;
    /**
     * The arguments for the back-end.
     */
    std::string BackEndArguments;
    /**
     * The arguments for the application.
     */
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

/**
 * Print data to the console.
 * @param tag A tag for the data to group the data by.
 * @param type The type of the data.
 * @param data The data to print.
 */
void print_log_data(const std::string& tag, LogType type, const std::string& data);

/**
 * Split the string based on a delimiter.
 * @param string The string to split.
 * @param delimiter The delimiter to split by.
 * @return The components of the original string.
 */
std::vector<std::string> split(const std::string& string, char delimiter);

/**
 * Split the string based on a delimiter only once.
 * @param string The string to split.
 * @param delimiter The delimiter to split by.
 * @return The components of the original string.
 */
std::vector<std::string> split_once(const std::string& string, char delimiter);

/**
 * Read the arguments from argv.
 * @param argc The number of arguments.
 * @param argv The original arguments.
 * @return The parsed arguments.
 */
struct Arguments getArguments(int argc, char **argv);

/**
 * Load an llvm module from a file, from [here](https://stackoverflow.com/questions/22239801/how-to-load-llvm-bitcode-file-from-an-ifstream).
 * @param file The file from which to load the llvm module.
 * @param context The context for the module.
 * @return The llvm module for the file.
 */
std::unique_ptr<llvm::Module> load_module(llvm::StringRef file, llvm::LLVMContext &context);

/**
 * If a string ends in some substring, from [here](https://stackoverflow.com/questions/874134/find-out-if-string-ends-with-another-string-in-c).
 * @param fullString The string to check.
 * @param ending The substring.
 * @return If the string ends in some substring.
 */
bool hasEnding(std::string const &fullString, std::string const &ending);

#endif //JIT_UTIL_H
