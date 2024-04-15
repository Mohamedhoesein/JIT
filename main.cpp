#include "llvm/ADT/StringRef.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Support/Error.h"
#include <filesystem>

#include "front-end/BaseFrontend.h"
#include "back-end/BaseJIT.h"
#include "util/StringToArgv.h"
#include "util/Util.h"

int main(int argc, char **argv) {
    llvm::InitializeNativeTarget();
    llvm::InitializeNativeTargetAsmPrinter();

    struct Arguments arguments = getArguments(argc, argv);

    PRINT_ERROR(
            arguments.ApplicationArguments.empty(),
            "At least one argument for the application is needed, which is the name of the application."
    )

    PRINT_ERROR(
            arguments.Files.empty(),
            "A filename is required."
    )

    for (const auto& file : arguments.Files) {
        PRINT_ERROR(
                !hasEnding(file, ".ll"),
                "An invalid file was given: " << file
        )
        PRINT_ERROR(
                !std::filesystem::exists(file),
                "The given file does not exist: " << file
        )
    }

    int applicationArgc;
    char **applicationArgv;
    auto r = string_to_argv(arguments.ApplicationArguments.c_str(), &applicationArgc, &applicationArgv);
    PRINT_ERROR(
            r != 0,
            "Invalid arguments for the application."
    )

    int backEndArgc;
    char **backEndArgv;
    r = string_to_argv(arguments.BackEndArguments.c_str(), &backEndArgc, &backEndArgv);
    PRINT_ERROR(
            r != 0,
            "Invalid arguments for the backend."
    )
    std::vector<std::string> backEndArguments;
    backEndArguments.reserve(backEndArgc);
    for (int i = 0; i < backEndArgc; i++)
        backEndArguments.emplace_back(backEndArgv[i]);
    auto jit = llvm::orc::BaseJIT::create(BaseFrontend::requestModule, backEndArguments);

    PRINT_ERROR(
            !jit,
            "An error occurred when creating the jit." << std::endl << toString(jit.takeError())
    )

    std::unique_ptr<llvm::orc::BaseJIT> true_jit = std::move(*jit);
    auto frontend = BaseFrontend::create(arguments.Files, std::move(true_jit));

    PRINT_ERROR(
            !frontend,
            "An error occurred when adding the module."
    )

    auto true_frontend = std::move(*frontend);
    auto result = true_frontend->start(applicationArgc, applicationArgv);

    PRINT_ERROR(
            !result,
            "An error occurred when doing a lookup for main."
    )

    return *result;
}