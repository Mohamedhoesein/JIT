#ifndef JIT_LLVMFRONTEND_H
#define JIT_LLVMFRONTEND_H

#include "BaseFrontEnd.h"

class LLVMFrontEnd: public BaseFrontEnd {
protected:
    /**
     * The JIT to execute.
     */
    std::unique_ptr<llvm::orc::BaseJIT> JIT;
public:
    /**
     * The constructor for the front-end.
     * @param JIT The JIT to execute.
     */
    LLVMFrontEnd(std::unique_ptr<llvm::orc::BaseJIT> JIT);
    /**
     * The destructor to deallocate resource associated with the front-end.
     */
    ~LLVMFrontEnd() override = default;
    /**
     * Create the front-end based on a compiler flag.
     * @param Arguments Arguments for the front-end.
     * @param Files The files the front-end should load.
     * @param JIT The back-end that will execute the code.
     * @return An object with either the front-end or an error depending on if the creation was successful.
     */
    static llvm::Expected<std::unique_ptr<BaseFrontEnd>> create(std::vector<std::string> Arguments, std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT);
    /**
     * Always create an error since everything should be loaded ahead of time.
     * @param Name The fully qualified name of the class or function that should be loaded.
     * @return An error indicating that nothing can be loaded.
     */
    static llvm::Expected<struct llvm::orc::CaptureModule> requestModule(llvm::StringRef Name);
    /**
     * @copydoc BaseFrontEnd::start(int, char**)
     */
    llvm::Expected<int> start(int argc, char **argv) override;
};

#endif //JIT_LLVMFRONTEND_H