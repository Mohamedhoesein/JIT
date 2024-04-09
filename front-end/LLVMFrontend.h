#ifndef JIT_LLVMFRONTEND_H
#define JIT_LLVMFRONTEND_H

#include "BaseFrontend.h"

class LLVMFrontend: public BaseFrontend {
protected:
    std::unique_ptr<llvm::orc::BaseJIT> JIT;
public:
    LLVMFrontend(std::unique_ptr<llvm::orc::BaseJIT> JIT);
    ~LLVMFrontend() override = default;
    static llvm::Expected<std::unique_ptr<BaseFrontend>> create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT);
    static llvm::Expected<CaptureModule> requestModule(llvm::StringRef Name);
    llvm::Expected<int> start(int argc, char **argv) override;
};

#endif //JIT_LLVMFRONTEND_H