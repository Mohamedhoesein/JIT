#include "BaseFrontEnd.h"
#include "LLVMFrontEnd.h"

llvm::Expected<std::unique_ptr<BaseFrontEnd>> BaseFrontEnd::create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT) {
#ifdef LLVM_FRONT_END
    return LLVMFrontEnd::create(Files, std::move(JIT));
#else
    return llvm::createStringError(std::error_code(), "No front-end selected.");
#endif
}

llvm::Expected<CaptureModule> BaseFrontEnd::requestModule(llvm::StringRef Name) {
#ifdef LLVM_FRONT_END
    return LLVMFrontEnd::requestModule(Name);
#else
    return llvm::createStringError(std::error_code(), "No front-end selected.");
#endif
}