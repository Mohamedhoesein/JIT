#ifndef JIT_BASEJIT_H
#define JIT_BASEJIT_H

#include "llvm/Support/Error.h"
#include "llvm/ExecutionEngine/Orc/ThreadSafeModule.h"
#include "llvm/ExecutionEngine/Orc/Core.h"
#include <memory>

namespace llvm {
    namespace orc {
        typedef struct {
            ThreadSafeModule threadSafeModule;
            ResourceTrackerSP resourceTracker;
        } CaptureModule;
        using AddModuleCallback = unique_function<Expected<CaptureModule>(StringRef)>;

        class BaseJIT {
        protected:
            AddModuleCallback AddModule;
            explicit BaseJIT(AddModuleCallback AM);
            Error requestModule(StringRef Name);
        public:
            virtual ~BaseJIT();
            static Expected<std::unique_ptr<BaseJIT>> create(AddModuleCallback AddModule);
            virtual Error addModule(ThreadSafeModule ThreadSafeModule) = 0;
            virtual Error addModule(ThreadSafeModule ThreadSafeModule, ResourceTrackerSP ResourceTracker) = 0;
            virtual Expected<ExecutorSymbolDef> lookup(StringRef Name) = 0;
        };
    }
}

#endif //JIT_BASEJIT_H
