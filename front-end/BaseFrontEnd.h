#ifndef JIT_BASEFRONTEND_H
#define JIT_BASEFRONTEND_H

#include "../back-end/BaseJIT.h"

class BaseFrontEnd {
public:
    virtual ~BaseFrontEnd() = default;
    static llvm::Expected<std::unique_ptr<BaseFrontEnd>> create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT);
    static llvm::Expected<CaptureModule> requestModule(llvm::StringRef Name);
    virtual llvm::Expected<int> start(int argc, char **argv) = 0;
};

#endif //JIT_BASEFRONTEND_H