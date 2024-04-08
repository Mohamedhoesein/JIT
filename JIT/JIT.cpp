#include <utility>

#include "JIT.h"

using namespace llvm;
using namespace orc;

void llvm::orc::JIT::handleLazyCallThroughError() {
    errs() << "LazyCallThrough error: Could not find function body";
    exit(1);
}

Expected<ThreadSafeModule> llvm::orc::JIT::optimizeModule(ThreadSafeModule TSM, const MaterializationResponsibility &R) {
    TSM.withModuleDo([](Module &M) {
        // Create a function pass manager.
        auto FPM = std::make_unique<legacy::FunctionPassManager>(&M);

        // Add some optimizations.
        FPM->add(createInstructionCombiningPass());
        FPM->add(createReassociatePass());
        FPM->add(createGVNPass());
        FPM->add(createCFGSimplificationPass());
        FPM->doInitialization();

        // Run the optimizations over all functions in the module being added to
        // the JIT.
        for (auto &F: M)
            FPM->run(F);
    });

    return std::move(TSM);
}

llvm::orc::JIT::JIT(std::unique_ptr<llvm::orc::ExecutionSession> ES,
         std::unique_ptr<llvm::orc::EPCIndirectionUtils> EPCIU,
         llvm::orc::JITTargetMachineBuilder JTMB,
         llvm::DataLayout DL,
         std::unique_ptr<llvm::orc::RedirectableSymbolManager> RSM,
         std::unique_ptr<llvm::orc::ObjectLinkingLayer> OLayer,
         llvm::orc::AddModuleCallback AM)
        : BaseJIT(std::move(AM)), ExecutionSession(std::move(ES)),
          EPCIU(std::move(EPCIU)), DataLayout(std::move(DL)),
          Mangle(*this->ExecutionSession, this->DataLayout),
          MainJD(this->ExecutionSession->getJITDylibByName("main")),
          ObjectLayer(std::move(OLayer)),
          CompileLayer(
                  std::move(std::make_unique<llvm::orc::IRCompileLayer>(
                          *this->ExecutionSession, *this->ObjectLayer,
                          std::make_unique<ConcurrentIRCompiler>(std::move(JTMB))
                  ))
          ),
          CompileOnDemandLayer(
                  std::move(std::make_unique<llvm::orc::CompileOnDemandLayer>(
                          *this->ExecutionSession, *this->CompileLayer,
                          this->EPCIU->getLazyCallThroughManager(),
                          [this] { return this->EPCIU->createIndirectStubsManager(); }
                  ))
          ),
          OptimizeLayer(
                  std::move(std::make_unique<llvm::orc::IRTransformLayer>(
                          *this->ExecutionSession, *this->CompileOnDemandLayer, optimizeModule
                  ))
          ),
          ReOptimizeLayer(
                  std::move(std::make_unique<llvm::orc::ReOptimizeLayer>(
                          *this->ExecutionSession, *this->OptimizeLayer, std::move(RSM)
                  ))
          ) {
    this->MainJD->addGenerator(
            cantFail(
                    DynamicLibrarySearchGenerator::GetForCurrentProcess(DL.getGlobalPrefix())
            )
    );
    auto &currentEPC = this->ExecutionSession->getExecutorProcessControl();
    cantFail(this->MainJD->define(absoluteSymbols(
            {
                    {this->ExecutionSession->intern("__orc_rt_jit_dispatch"),
                            {currentEPC.getJITDispatchInfo().JITDispatchFunction,
                                    JITSymbolFlags::Exported}},
                    {this->ExecutionSession->intern("__orc_rt_jit_dispatch_ctx"),
                            {currentEPC.getJITDispatchInfo().JITDispatchContext,
                                    JITSymbolFlags::Exported}},
                    {this->ExecutionSession->intern("__orc_rt_reoptimize_tag"),
                            {ExecutorAddr(), JITSymbolFlags::Exported}}
            }
    )));
    cantFail(this->ReOptimizeLayer->reigsterRuntimeFunctions(*this->MainJD));
    this->ReOptimizeLayer->setReoptimizeFunc(
            [&](llvm::orc::ReOptimizeLayer &parent, llvm::orc::ReOptMaterializationUnitID MUID,
                unsigned currentVersion, llvm::orc::ResourceTrackerSP oldResourceTracker,
                llvm::orc::ThreadSafeModule &threadSafeModule) {
                    return Error::success();
                });
}

llvm::orc::JIT::~JIT() {
    if (auto Err = this->ExecutionSession->endSession())
        this->ExecutionSession->reportError(std::move(Err));
    if (auto Err = this->EPCIU->cleanup())
        this->ExecutionSession->reportError(std::move(Err));
}


Expected<std::unique_ptr<llvm::orc::BaseJIT>> llvm::orc::JIT::create(llvm::orc::AddModuleCallback AddModule) {
    auto epc = SelfExecutorProcessControl::Create();
    if (!epc)
        return epc.takeError();

    auto es = std::make_unique<llvm::orc::ExecutionSession>(std::move(*epc));

    auto epciu = EPCIndirectionUtils::Create(*es);
    if (!epciu)
        return epciu.takeError();

    (*epciu)->createLazyCallThroughManager(
            *es, ExecutorAddr::fromPtr(&llvm::orc::JIT::handleLazyCallThroughError));

    if (auto err = setUpInProcessLCTMReentryViaEPCIU(**epciu))
        return std::move(err);

    JITTargetMachineBuilder jtmb(
            es->getExecutorProcessControl().getTargetTriple());

    auto DL = jtmb.getDefaultDataLayoutForTarget();
    if (!DL)
        return DL.takeError();


    auto ol = std::make_unique<ObjectLinkingLayer>(
            *es, std::make_unique<jitlink::InProcessMemoryManager>(4096));

    auto jlrsm = JITLinkRedirectableSymbolManager::Create(*es, *ol, es->createBareJITDylib("main"));

    if (!jlrsm)
        return jlrsm.takeError();

    std::unique_ptr<BaseJIT> baseJIT = std::make_unique<JIT>(std::move(es), std::move(*epciu),
                                 std::move(jtmb), std::move(*DL), std::move(*jlrsm),
                                 std::move(ol), std::move(AddModule));
    return baseJIT;
}

Error llvm::orc::JIT::applyDataLayout(llvm::Module &Module) {
    Module.setDataLayout(this->DataLayout);

    if (Module.getDataLayout() != this->DataLayout)
        return make_error<llvm::StringError>(
                "Added modules have incompatible data layouts: " +
                Module.getDataLayout().getStringRepresentation() + " (module) vs " +
                this->DataLayout.getStringRepresentation() + " (jit)",
                inconvertibleErrorCode());

    return Error::success();
}

Error llvm::orc::JIT::addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) {
    return this->addModule(std::move(ThreadSafeModule), this->MainJD->getDefaultResourceTracker());
}

Error llvm::orc::JIT::addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) {
    if (ResourceTracker == nullptr)
        ResourceTracker = this->MainJD->getDefaultResourceTracker();
    if (auto Err =
            ThreadSafeModule.withModuleDo([&](llvm::Module &module) {
                // Functions need to be externally linked so that it shows up in the symbol table and reoptimize can make use of it.
                // We rename the function to avoid conflicts with other internal functions that could have the same name.
                for (auto &function : module)
                    if (!function.isDeclaration() && function.hasInternalLinkage()) {
                        int index = 0;
                        if (Internals.contains(function.getName()))
                        {
                            index = Internals.at(function.getName()) + 1;
                            Internals.insert_or_assign(function.getName(), index);
                        }
                        else {
                            Internals.insert(std::pair(function.getName(), index));
                        }
                        function.setName(function.getName() + Twine(index));
                        function.setLinkage(GlobalValue::ExternalLinkage);
                    }
                return applyDataLayout(module);
            }))
        return Err;

    return this->OptimizeLayer->add(std::move(ResourceTracker), std::move(ThreadSafeModule));
}

Expected<ExecutorSymbolDef> llvm::orc::JIT::lookup(llvm::StringRef Name) {
    return this->ExecutionSession->lookup({this->MainJD}, this->Mangle(Name.str()));
}