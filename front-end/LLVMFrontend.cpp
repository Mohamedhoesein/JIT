#include "LLVMFrontend.h"
#include "../util/Util.h"

LLVMFrontend::LLVMFrontend(std::unique_ptr<llvm::orc::BaseJIT> JIT)
    : JIT(std::move(JIT)) {}

llvm::Expected<std::unique_ptr<BaseFrontend>> LLVMFrontend::create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT) {
    for (const auto& file : Files) {
        std::unique_ptr<llvm::LLVMContext> context = std::make_unique<llvm::LLVMContext>();
        std::unique_ptr<llvm::Module> module = load_module(file, *context);
        llvm::Error addError = JIT->addModule(llvm::orc::ThreadSafeModule(
                std::move(module),
                std::move(context)
        ));
        if (addError)
            return addError;
    }
    return std::make_unique<LLVMFrontend>(std::move(JIT));
}

llvm::Expected<CaptureModule> LLVMFrontend::requestModule(llvm::StringRef Name) {
    return llvm::createStringError(std::error_code(), "Everything should be loaded.");
}

llvm::Expected<int> LLVMFrontend::start(int argc, char **argv) {
    auto mainSymbol = this->JIT->lookup("main");
    if (!mainSymbol)
        return mainSymbol.takeError();

    auto main = mainSymbol->getAddress().toPtr<int(*)(int,char**)>();
    return main(argc, argv);
}