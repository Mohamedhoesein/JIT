#include "BaseFrontEnd.h"
#include "LLVMFrontEnd.h"
#include <iostream>

llvm::Expected<std::unique_ptr<BaseFrontEnd>> BaseFrontEnd::create(std::vector<std::string> Arguments, std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT) {
#ifdef LLVM_FRONT_END
    return LLVMFrontEnd::create(Arguments, Files, std::move(JIT));
#else
    return llvm::createStringError(std::error_code(), "No front-end selected.");
#endif
}

llvm::Expected<struct llvm::orc::CaptureModule> BaseFrontEnd::requestModule(llvm::StringRef Name) {
#ifdef LLVM_FRONT_END
    return LLVMFrontEnd::requestModule(Name);
#else
    return llvm::createStringError(std::error_code(), "No front-end selected.");
#endif
}