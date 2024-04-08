#include "BaseJIT.h"
#include "JIT.h"

llvm::orc::BaseJIT::BaseJIT(AddModuleCallback AM)
    : AddModule(std::move(AM)) {}

llvm::Error llvm::orc::BaseJIT::requestModule(StringRef Name) {
    auto module = this->AddModule(Name);
    if (!module)
        return module.takeError();
    return this->addModule(std::move(module->threadSafeModule), module->resourceTracker);
}

llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> llvm::orc::BaseJIT::create(llvm::orc::AddModuleCallback AddModule) {
#ifdef SIMPLE_JIT
    return JIT::create(std::move(AddModule));
#else
    return createStringError(std::error_code(), "No JIT selected.");
#endif
}

llvm::orc::BaseJIT::~BaseJIT() {
}
