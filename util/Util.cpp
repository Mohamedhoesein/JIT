#include "llvm/Support/SourceMgr.h"
#include "llvm/IRReader/IRReader.h"
#include <iostream>
#include <filesystem>
#include <getopt.h>

#include "Util.h"

std::vector<std::string> split(const std::string& string, const char delimiter) {
    std::stringstream stream(string);
    std::string segment;
    std::vector<std::string> parts;
    while (std::getline(stream, segment, delimiter))
        parts.push_back(segment);
    return parts;
}

struct Arguments getArguments(int argc, char **argv) {
    struct Arguments arguments = (struct Arguments){
            .Files = {},
            .BackEndArguments = "",
            .ApplicationArguments = ""
    };
    int character;
    while (true) {
        character = getopt(argc, argv, "f:b:a:");
        if (character == -1)
            break;

        switch (character) {
            case 'f':
                arguments.Files = split(optarg, ',');
                break;
            case 'b':
                arguments.BackEndArguments = optarg;
                break;
            case 'a':
                arguments.ApplicationArguments = optarg;
                break;
            default:
                std::cerr << "Invalid argument given." << std::endl;
                exit(-1);
        }
    }
    return arguments;
}

std::unique_ptr<llvm::Module> load_module(llvm::StringRef file, llvm::LLVMContext &context)
{
    llvm::SMDiagnostic error;
    std::unique_ptr<llvm::Module> module = parseIRFile(file, error, context);

    PRINT_ERROR_FULL(
            !module,
            std::string what;llvm::raw_string_ostream os(what);error.print("error after ParseIR()", os);,
            what
    )

    return module;
}

//https://stackoverflow.com/questions/874134/find-out-if-string-ends-with-another-string-in-c
bool hasEnding(std::string const &fullString, std::string const &ending) {
    if (fullString.length() >= ending.length()) {
        return (0 == fullString.compare(fullString.length() - ending.length(), ending.length(), ending));
    } else {
        return false;
    }
}