#ifndef JIT_LLVMFRONTEND_H
#define JIT_LLVMFRONTEND_H

#include "BaseFrontEnd.h"

class LLVMFrontEnd: public BaseFrontEnd {
protected:
    std::unique_ptr<llvm::orc::BaseJIT> JIT;
public:
    LLVMFrontEnd(std::unique_ptr<llvm::orc::BaseJIT> JIT);
    ~LLVMFrontEnd() override = default;
    static llvm::Expected<std::unique_ptr<BaseFrontEnd>> create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT);
    static llvm::Expected<CaptureModule> requestModule(llvm::StringRef Name);
    llvm::Expected<int> start(int argc, char **argv) override;
};

#endif //JIT_LLVMFRONTEND_H