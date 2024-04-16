#ifndef JIT_BASEJIT_H
#define JIT_BASEJIT_H

#include "llvm/Support/Error.h"
#include "llvm/ExecutionEngine/Orc/ThreadSafeModule.h"
#include "llvm/ExecutionEngine/Orc/Core.h"
#include <memory>

namespace llvm {
    namespace orc {
        /**
         * The data for a requested module.
         */
        struct CaptureModule {
            llvm::orc::ThreadSafeModule threadSafeModule;
            llvm::orc::ResourceTrackerSP resourceTracker;
        };
        /**
         * The type for the callback to retrieve another module.
         */
        using RequestModuleCallback = unique_function<struct llvm::Expected<CaptureModule>(llvm::StringRef)>;

        /**
         * The base class for the JIT.
         */
        class BaseJIT {
        protected:
            /**
             * The callback used to request more information from the front-end.
             */
            RequestModuleCallback RequestModule;
            /**
             * The base constructor for a JIT.
             * @param RM The callback used to request more information from the front-end.
             */
            explicit BaseJIT(RequestModuleCallback RM);
            /**
             * A wrapper function to request another module from the front-end.
             * @param Name The fully qualified name of the class or function that the back-end wants to load.
             * @return An llvm error object representing if the request was successful.
             */
            llvm::Error requestModule(llvm::StringRef Name);
        public:
            /**
             * The destructor for the JIT to free the needed resources.
             */
            virtual ~BaseJIT() = default;
            /**
             * Create a JIT based on the compiler flag that is set. When creating a new JIT add it in a elifdef directive
             * with a unique macro is required, also add logic to handle the additional information for the benchmark by
             * adding it to the appropriate functions in benchmark/common.py.
             * @param RequestModule The callback that is used by the back-end to request another module from the front-end.
             * @param Arguments The arguments for the back-end.
             * @return An object with either the jit or an error depending on if the lookup was successful.
             */
            static llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> create(RequestModuleCallback RequestModule, std::vector<std::string> Arguments);
            /**
             * Add a module to the JIT. The other addModule is called with the resource tracker of the module.
             * @see llvm::orc::BaseJIT::addModule(llvm::orc::ThreadSafeModule)
             * @param ThreadSafeModule The module to add to the jit.
             * @return An llvm error object representing if the request was successful.
             */
            virtual llvm::Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) = 0;
            /**
             * Add a module with the given resource tracker to the JIT.
             * @param ThreadSafeModule The module to add to the jit.
             * @param ResourceTracker The resource tracker for the module.
             * @return An llvm error object representing if the request was successful.
             */
            virtual llvm::Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) = 0;
            /**
             * Lookup a symbol by its name.
             * @param Name The name of the symbol to lookup.
             * @return An object with either the symbol or an error depending on if the lookup was successful.
             */
            virtual llvm::Expected<llvm::orc::ExecutorSymbolDef> lookup(llvm::StringRef Name) = 0;
        };
    }
}

#endif //JIT_BASEJIT_H