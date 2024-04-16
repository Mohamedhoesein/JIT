#ifndef JIT_BASEFRONTEND_H
#define JIT_BASEFRONTEND_H

#include "../back-end/BaseJIT.h"

/**
 * The base class for the front-end.
 */
class BaseFrontEnd {
public:
    /**
     * The destructor for the front-end to free the needed resources.
     */
    virtual ~BaseFrontEnd() = default;
    /**
     * Create a front-end based on a compiler flag. When creating a new front-ned add it in an elifdef directive with a
     * unique macro is required, also add the callback to request a module to the requestModule function. Add benchmarks
     * to the benchmark folder, it should be a top-level folder with a run.py script.
     * @param Files The files the front-end should load.
     * @param JIT The back-end that will execute the code.
     * @return An object with either the front-end or an error depending on if the creation was successful.
     */
    static llvm::Expected<std::unique_ptr<BaseFrontEnd>> create(std::vector<std::string> Files, std::unique_ptr<llvm::orc::BaseJIT> JIT);
    /**
     * Load the module based on the name.
     * @param Name The fully qualified name of the class or function that should be loaded.
     * @return An object with either the module or an error depending on if the request was successful.
     */
    static llvm::Expected<struct llvm::orc::CaptureModule> requestModule(llvm::StringRef Name);
    /**
     * Start the JIT with the given arguments.
     * @param argc The number of arguments.
     * @param argv The arguments.
     * @return An object with either the exit code of the application or an error depending on if the lookup was successful.
     */
    virtual llvm::Expected<int> start(int argc, char **argv) = 0;
};

#endif //JIT_BASEFRONTEND_H