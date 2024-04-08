#include "llvm/ADT/StringRef.h"
#include "llvm/IR/Module.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/Error.h"
#include <iostream>
#include <filesystem>

#include "JIT/BaseJIT.h"

//https://stackoverflow.com/questions/22239801/how-to-load-llvm-bitcode-file-from-an-ifstream
std::unique_ptr<llvm::Module> load_module(llvm::StringRef file, llvm::LLVMContext &context)
{
    llvm::SMDiagnostic error;
    std::unique_ptr<llvm::Module> module = parseIRFile(file, error, context);

    if(!module)
    {
        std::string what;
        llvm::raw_string_ostream os(what);
        error.print("error after ParseIR()", os);
        std::cerr << what;
        exit(-1);
    }

    return module;
}

//https://stackoverflow.com/questions/874134/find-out-if-string-ends-with-another-string-in-c
bool hasEnding(std::string const &fullString, std::string const &ending) {
    if (fullString.length() >= ending.length()) {
        return (0 == fullString.compare (fullString.length() - ending.length(), ending.length(), ending));
    } else {
        return false;
    }
}

llvm::Expected<llvm::orc::CaptureModule> AddModule(llvm::StringRef Name) {
    return llvm::createStringError(std::error_code(), "No JIT selected.");
}

int main(int argc, char **argv) {
    llvm::InitializeNativeTarget();
    llvm::InitializeNativeTargetAsmPrinter();
    if (argc == 1) {
        std::cout << "A filename is required." << std::endl;
        exit(-1);
    }

    int base = 1;
    for (; base < argc; base++) {
        if (!hasEnding(argv[base], ".ll") || !std::filesystem::exists(argv[base])) {
            base--;
            break;
        }
    }
    if (base == argc)
        base--;

    if (base == 0) {
        std::cout << "The given file does not exist." << std::endl;
        exit(-1);
    }

    llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> jit = llvm::orc::BaseJIT::create(AddModule);

    if (!jit) {
        std::cout << "An error occurred when creating the jit." << std::endl << toString(jit.takeError()) << std::endl;
        exit(-1);
    }

    std::unique_ptr<llvm::orc::BaseJIT> true_jit = std::move(*jit);
    for (int i = 1; i <= base; i++) {
        std::unique_ptr<llvm::LLVMContext> context = std::make_unique<llvm::LLVMContext>();
        std::unique_ptr<llvm::Module> module = load_module(argv[i], *context);
        LLVMErrorRef addError = wrap(true_jit->addModule(llvm::orc::ThreadSafeModule(
                std::move(module),
                std::move(context)
        )));
        if (addError) {
            std::cout << "An error occurred when adding the module." << std::endl
                      << LLVMGetErrorMessage(addError) << std::endl;
            exit(-1);
        }
    }

    auto mainSymbol = true_jit->lookup("main");
    if (!mainSymbol) {
        std::cout << "An error occurred when doing a lookup for main." << std::endl;
        exit(-1);
    }
    auto main = mainSymbol->getAddress().toPtr<int(*)(int,char**)>();
    return main(argc - base - 1, argv + base + 1);
}