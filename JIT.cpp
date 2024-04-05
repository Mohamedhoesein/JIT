#include <utility>

#include "JIT.h"

using namespace llvm;
using namespace orc;

void JIT::handleLazyCallThroughError() {
    errs() << "LazyCallThrough error: Could not find function body";
    exit(1);
}

Expected<ThreadSafeModule> JIT::optimizeModule(ThreadSafeModule TSM, const MaterializationResponsibility &R) {
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

JIT::JIT(std::unique_ptr<ExecutionSession> ES, std::unique_ptr<EPCIndirectionUtils> EPCIU,
         JITTargetMachineBuilder JTMB, DataLayout DL, std::unique_ptr<RedirectableSymbolManager> JLRSM,
         std::unique_ptr<ObjectLinkingLayer> OL)
        : ES(std::move(ES)), EPCIU(std::move(EPCIU)),
          DL(std::move(DL)), Mangle(*this->ES, this->DL),
          MainJD(this->ES->getJITDylibByName("main")),
          //ObjectLayer(std::move(std::make_unique<RTDyldObjectLinkingLayer>(*this->ES, []() { return std::make_unique<SectionMemoryManager>(); }))),
          ObjectLayer(std::move(OL)),
          CompileLayer(
                  std::move(std::make_unique<IRCompileLayer>(
                          *this->ES, *this->ObjectLayer,
                          std::make_unique<ConcurrentIRCompiler>(std::move(JTMB))
                  ))
          ),
          CODLayer(
                  std::move(std::make_unique<CompileOnDemandLayer>(
                          *this->ES, *this->CompileLayer,
                          this->EPCIU->getLazyCallThroughManager(),
                          [this] { return this->EPCIU->createIndirectStubsManager(); }
                  ))
          ),
          OptimizeLayer(
                  std::move(std::make_unique<IRTransformLayer>(
                          *this->ES, *this->CODLayer, optimizeModule
                  ))
          ),
          ReOpLayer(
                  std::move(std::make_unique<ReOptimizeLayer>(
                          *this->ES, *this->OptimizeLayer, std::move(JLRSM)
                  ))
          ) {
    this->MainJD->addGenerator(
            cantFail(
                    DynamicLibrarySearchGenerator::GetForCurrentProcess(DL.getGlobalPrefix())
            )
    );
    auto &currentEPC = this->ES->getExecutorProcessControl();
    cantFail(getMainJITDylib()->define(absoluteSymbols(
            {
                    {this->ES->intern("__orc_rt_jit_dispatch"),
                            {currentEPC.getJITDispatchInfo().JITDispatchFunction,
                                    JITSymbolFlags::Exported}},
                    {this->ES->intern("__orc_rt_jit_dispatch_ctx"),
                            {currentEPC.getJITDispatchInfo().JITDispatchContext,
                                    JITSymbolFlags::Exported}},
                    {this->ES->intern("__orc_rt_reoptimize_tag"),
                            {ExecutorAddr(), JITSymbolFlags::Exported}}
            }
    )));
    cantFail(this->ReOpLayer->reigsterRuntimeFunctions(*getMainJITDylib()));
    this->ReOpLayer->setReoptimizeFunc(
            [&](ReOptimizeLayer &Parent, ReOptMaterializationUnitID MUID,
                unsigned CurVersion, ResourceTrackerSP OldRT, ThreadSafeModule &TSM) {
                    return Error::success();
                });
}

JIT::~JIT() {
    if (auto Err = this->ES->endSession())
        this->ES->reportError(std::move(Err));
    if (auto Err = this->EPCIU->cleanup())
        this->ES->reportError(std::move(Err));
}


Expected<std::unique_ptr<JIT>> JIT::Create() {
    auto EPC = SelfExecutorProcessControl::Create();
    if (!EPC)
        return EPC.takeError();

    auto ES = std::make_unique<ExecutionSession>(std::move(*EPC));

    auto EPCIU = EPCIndirectionUtils::Create(*ES);
    if (!EPCIU)
        return EPCIU.takeError();

    (*EPCIU)->createLazyCallThroughManager(
            *ES, ExecutorAddr::fromPtr(&JIT::handleLazyCallThroughError));

    if (auto Err = setUpInProcessLCTMReentryViaEPCIU(**EPCIU))
        return std::move(Err);

    JITTargetMachineBuilder JTMB(
            ES->getExecutorProcessControl().getTargetTriple());

    auto DL = JTMB.getDefaultDataLayoutForTarget();
    if (!DL)
        return DL.takeError();


    auto OL = std::make_unique<ObjectLinkingLayer>(
            *ES, std::make_unique<jitlink::InProcessMemoryManager>(4096));

    auto JLRSM = JITLinkRedirectableSymbolManager::Create(*ES, *OL, ES->createBareJITDylib("main"));

    if (!JLRSM)
        return JLRSM.takeError();

    return std::make_unique<JIT>(std::move(ES), std::move(*EPCIU),
                                 std::move(JTMB), std::move(*DL), std::move(*JLRSM),
                                 std::move(OL));
}

Error JIT::applyDataLayout(Module &M) {
    M.setDataLayout(this->getDataLayout());

    if (M.getDataLayout() != this->getDataLayout())
        return make_error<StringError>(
                "Added modules have incompatible data layouts: " +
                M.getDataLayout().getStringRepresentation() + " (module) vs " +
                this->DL.getStringRepresentation() + " (jit)",
                inconvertibleErrorCode());

    return Error::success();
}

Error JIT::addModule(ThreadSafeModule TSM, ResourceTrackerSP RT) {
    if (!RT)
        RT = this->MainJD->getDefaultResourceTracker();
    std::vector<GlobalVariable *> varsToRemove;
    if (auto Err =
            TSM.withModuleDo([&](Module &M) {
                // Functions need to be externally linked so that it shows up in the symbol table and reoptimize can make use of it.
                // We rename the function to avoid conflicts with other internal functions that could have the same name.
                for (auto &F : M)
                    if (!F.isDeclaration() && F.hasInternalLinkage()) {
                        int index = 0;
                        if (internals.contains(F.getName()))
                        {
                            index = internals.at(F.getName()) + 1;
                            internals.insert_or_assign(F.getName(), index);
                        }
                        else {
                            internals.insert(std::pair(F.getName(), index));
                        }
                        F.setName(F.getName() + Twine(index));
                        F.setLinkage(GlobalValue::ExternalLinkage);
                    }
                return applyDataLayout(M);
            }))
        return Err;

    return this->OptimizeLayer->add(RT, std::move(TSM));
}

Expected<ExecutorSymbolDef> JIT::lookup(StringRef Name) {
    return this->ES->lookup({this->MainJD}, this->Mangle(Name.str()));
}