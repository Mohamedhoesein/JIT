#ifndef JIT_BASEJIT_H
#define JIT_BASEJIT_H

#include "llvm/Support/Error.h"
#include "llvm/ExecutionEngine/Orc/ThreadSafeModule.h"
#include "llvm/ExecutionEngine/Orc/Core.h"
#include <memory>

typedef struct {
    llvm::orc::ThreadSafeModule threadSafeModule;
    llvm::orc::ResourceTrackerSP resourceTracker;
} CaptureModule;

namespace llvm {
    namespace orc {
        using RequestModuleCallback = unique_function<llvm::Expected<CaptureModule>(llvm::StringRef)>;

        class BaseJIT {
        protected:
            RequestModuleCallback AddModule;
            explicit BaseJIT(RequestModuleCallback AM);
            llvm::Error requestModule(llvm::StringRef Name);
        public:
            virtual ~BaseJIT() = default;
            static llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> create(RequestModuleCallback AddModule, std::vector<std::string> Arguments);
            virtual llvm::Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) = 0;
            virtual llvm::Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) = 0;
            virtual llvm::Expected<llvm::orc::ExecutorSymbolDef> lookup(llvm::StringRef Name) = 0;
        };
    }
}

#endif //JIT_BASEJIT_H