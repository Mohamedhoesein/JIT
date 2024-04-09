#include "llvm/ADT/StringRef.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Support/Error.h"
#include <iostream>
#include <filesystem>

#include "JIT/BaseJIT.h"
#include "util/StringToArgv.h"
#include "util/Util.h"

llvm::Expected<llvm::orc::CaptureModule> AddModule(llvm::StringRef Name) {
    return llvm::createStringError(std::error_code(), "No JIT selected.");
}

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
                "An invalid file was given: \"" << file << "\""
        )
        PRINT_ERROR(
                !std::filesystem::exists(file),
                "The given file does not exist: \"" << file << "\""
        )
    }

    int applicationArgc;
    char **applicationArgv;
    int r = string_to_argv(arguments.ApplicationArguments.c_str(), &applicationArgc, &applicationArgv);
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
    llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> jit = llvm::orc::BaseJIT::create(AddModule, backEndArguments);

    PRINT_ERROR(
            !jit,
            "An error occurred when creating the jit." << std::endl << toString(jit.takeError())
    )

    std::unique_ptr<llvm::orc::BaseJIT> true_jit = std::move(*jit);
    for (const auto& file : arguments.Files) {
        std::unique_ptr<llvm::LLVMContext> context = std::make_unique<llvm::LLVMContext>();
        std::unique_ptr<llvm::Module> module = load_module(file, *context);
        LLVMErrorRef addError = wrap(true_jit->addModule(llvm::orc::ThreadSafeModule(
                std::move(module),
                std::move(context)
        )));
        PRINT_ERROR(
                addError,
                "An error occurred when adding the module." << std::endl
                << LLVMGetErrorMessage(addError) << std::endl
        )
    }

    auto mainSymbol = true_jit->lookup("main");
    PRINT_ERROR(
            !mainSymbol,
            "An error occurred when doing a lookup for main."
    )
    auto main = mainSymbol->getAddress().toPtr<int(*)(int,char**)>();
    return main(applicationArgc, applicationArgv);
}