#include "llvm/Support/TargetSelect.h"
#include <filesystem>

#include "front-end/BaseFrontEnd.h"
#include "back-end/BaseJIT.h"
#include "util/StringToArgv.h"
#include "util/Util.h"

int main(int argc, char **argv) {
#ifdef LOG
    std::chrono::time_point<std::chrono::system_clock> now = std::chrono::system_clock::now();
    auto duration = now.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
    print_log_data("Start", LogType::List, LogPart::Whole, std::to_string(millis));
#endif
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

    std::vector<std::string> backEndArguments;
    r = string_to_argv_vector(arguments.BackEndArguments.c_str(), &backEndArguments);
    PRINT_ERROR(
            r != 0,
            "Invalid arguments for the back-end."
    )

    auto jit = llvm::orc::BaseJIT::create(BaseFrontEnd::requestModule, backEndArguments);
    PRINT_ERROR(
            !jit,
            "An error occurred when creating the jit."
    )

    std::vector<std::string> frontEndArguments;
    r = string_to_argv_vector(arguments.FrontEndArguments.c_str(), &frontEndArguments);
    PRINT_ERROR(
            r != 0,
            "Invalid arguments for the front-end."
    )

    std::unique_ptr<llvm::orc::BaseJIT> true_jit = std::move(*jit);
    auto frontend = BaseFrontEnd::create(frontEndArguments, arguments.Files, std::move(true_jit));

    PRINT_ERROR(
            !frontend,
            "An error occurred when creating the front-end."
    )

    auto true_frontend = std::move(*frontend);
    auto result = true_frontend->start(applicationArgc, applicationArgv);

    PRINT_ERROR(
            !result,
            "An error occurred when doing a lookup for main."
    )

    return *result;
}