#include "BaseFrontend.h"
#include "LLVMFrontend.h"

llvm::Expected<std::unique_ptr<BaseFrontend>> BaseFrontend::create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT) {
#ifdef LLVM_FRONTEND
    return LLVMFrontend::create(Files, std::move(JIT));
#else
    return llvm::createStringError(std::error_code(), "No front-end selected.");
#endif
}

llvm::Expected<CaptureModule> BaseFrontend::requestModule(llvm::StringRef Name) {
#ifdef LLVM_FRONTEND
    return LLVMFrontend::requestModule(Name);
#else
    return llvm::createStringError(std::error_code(), "No front-end selected.");
#endif
}