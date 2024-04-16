#include <utility>

#include "BaseJIT.h"
#include "JIT.h"

llvm::orc::BaseJIT::BaseJIT(RequestModuleCallback AM)
    : RequestModule(std::move(AM)) {}

llvm::Error llvm::orc::BaseJIT::requestModule(StringRef Name) {
    auto module = this->RequestModule(Name);
    if (!module)
        return module.takeError();
    return this->addModule(std::move(module->threadSafeModule), module->resourceTracker);
}

llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> llvm::orc::BaseJIT::create(llvm::orc::RequestModuleCallback AddModule, std::vector<std::string> Arguments) {
#ifdef SIMPLE_JIT_BACK_END
    return llvm::orc::JIT::create(std::move(AddModule), std::move(Arguments));
#else
    return createStringError(std::error_code(), "No JIT selected.");
#endif
}