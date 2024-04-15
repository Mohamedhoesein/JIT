#ifndef JIT_BASEFRONTEND_H
#define JIT_BASEFRONTEND_H

#include "../back-end/BaseJIT.h"

class BaseFrontend {
public:
    virtual ~BaseFrontend() = default;
    static llvm::Expected<std::unique_ptr<BaseFrontend>> create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT);
    static llvm::Expected<CaptureModule> requestModule(llvm::StringRef Name);
    virtual llvm::Expected<int> start(int argc, char **argv) = 0;
};

#endif //JIT_BASEFRONTEND_H