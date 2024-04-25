#include "llvm/ADT/StringRef.h"
#include "llvm/ExecutionEngine/Orc/CompileUtils.h"
#include "llvm/ExecutionEngine/Orc/Core.h"
#include "llvm/ExecutionEngine/Orc/ExecutionUtils.h"
#include "llvm/ExecutionEngine/Orc/ExecutorProcessControl.h"
#include "llvm/ExecutionEngine/Orc/LLJIT.h"
#include "llvm/ExecutionEngine/Orc/Mangling.h"
#include "llvm/ExecutionEngine/Orc/Shared/ExecutorSymbolDef.h"
#include "llvm/IR/DataLayout.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Transforms/Scalar.h"
#include <utility>

#include "JIT.h"
#include "../util/Util.h"

void llvm::orc::JIT::handleLazyCallThroughError() {
    errs() << "LazyCallThrough error: Could not find function body";
    exit(1);
}

llvm::orc::JIT::JIT(std::unique_ptr<llvm::orc::ExecutionSession> ES,
         std::unique_ptr<llvm::orc::EPCIndirectionUtils> EPCIU,
         llvm::orc::JITTargetMachineBuilder JTMB,
         llvm::DataLayout DL,
         std::unique_ptr<llvm::orc::RedirectableSymbolManager> RSM,
         std::unique_ptr<llvm::orc::ObjectLinkingLayer> OL,
         llvm::orc::RequestModuleCallback RM,
         std::string Optimize, std::string ReOptimize)
        : BaseJIT(std::move(RM)), ExecutionSession(std::move(ES)),
          EPCIU(std::move(EPCIU)), DataLayout(DL),
          Mangle(*this->ExecutionSession, this->DataLayout),
          MainJD(this->ExecutionSession->getJITDylibByName("main")),
          ObjectLayer(std::move(OL)),
          CompileLayer(
                  std::move(std::make_unique<llvm::orc::IRCompileLayer>(
                          *this->ExecutionSession, *this->ObjectLayer,
                          cantFail(createCompiler(std::move(JTMB)))
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
                          *this->ExecutionSession, *this->CompileOnDemandLayer, OptimizationTransform(std::move(Optimize))
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
                unsigned CurrentVersion, llvm::orc::ResourceTrackerSP OldResourceTracker,
                llvm::orc::ThreadSafeModule &TSM) {
                    TSM.withModuleDo([&ReOptimize](Module &M) {
                        print_log_data("Recompiled", LogType::List, LogPart::BackEnd, "recompiled module " + std::string(M.getName()));
                        llvm::LoopAnalysisManager lam;
                        llvm::FunctionAnalysisManager fam;
                        llvm::CGSCCAnalysisManager cgam;
                        llvm::ModuleAnalysisManager mam;

                        llvm::PassBuilder pb;
                        pb.registerModuleAnalyses(mam);
                        pb.registerCGSCCAnalyses(cgam);
                        pb.registerFunctionAnalyses(fam);
                        pb.registerLoopAnalyses(lam);
                        pb.crossRegisterProxies(lam, fam, cgam, mam);

                        llvm::ModulePassManager mpm;
                        if (auto Err = pb.parsePassPipeline(mpm, llvm::StringRef(ReOptimize)))
                            return;
                        mpm.run(M, mam);
                    });
                    return Error::success();
                });
}

llvm::orc::JIT::~JIT() {
    if (auto Err = this->ExecutionSession->endSession())
        this->ExecutionSession->reportError(std::move(Err));
    if (auto Err = this->EPCIU->cleanup())
        this->ExecutionSession->reportError(std::move(Err));
}

llvm::Expected<std::unique_ptr<llvm::orc::BaseJIT>> llvm::orc::JIT::create(llvm::orc::RequestModuleCallback AddModule, std::vector<std::string> Arguments) {
    std::string optimize = O1;
    std::string reOptimize = O2;
    for (const auto& argument : Arguments) {
        auto splitArgument = split_once(argument, '=');
        if (splitArgument[0] == "-opt") {
            optimize = splitArgument[1];
        }
        else if (splitArgument[0] == "-reopt") {
            reOptimize = splitArgument[1];
        }
    }
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

    auto dl = jtmb.getDefaultDataLayoutForTarget();
    if (!dl)
        return dl.takeError();

    auto ol = std::make_unique<ObjectLinkingLayer>(
            *es, std::make_unique<jitlink::InProcessMemoryManager>(4096));

    auto jlrsm = JITLinkRedirectableSymbolManager::Create(*es, *ol, es->createBareJITDylib("main"));

    if (!jlrsm)
        return jlrsm.takeError();

    return std::make_unique<JIT>(std::move(es), std::move(*epciu),
                                 std::move(jtmb), std::move(*dl), std::move(*jlrsm),
                                 std::move(ol), std::move(AddModule),
                                 optimize, reOptimize);
}

llvm::Error llvm::orc::JIT::addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) {
    return this->addModule(std::move(ThreadSafeModule), this->MainJD->getDefaultResourceTracker());
}

llvm::Error llvm::orc::JIT::addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) {
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

    return this->ReOptimizeLayer->add(std::move(ResourceTracker), std::move(ThreadSafeModule));
}

llvm::Expected<llvm::orc::ExecutorAddr> llvm::orc::JIT::lookup(llvm::StringRef Name) {
    auto result = this->ExecutionSession->lookup({this->MainJD}, this->Mangle(Name.str()));
    if (!result)
        return result.takeError();
    return result->getAddress();
}

llvm::Error llvm::orc::JIT::applyDataLayout(llvm::Module &Module) {
    Module.setDataLayout(this->DataLayout);

    if (Module.getDataLayout() != this->DataLayout)
        return make_error<llvm::StringError>(
                "Added modules have incompatible data layouts: " +
                Module.getDataLayout().getStringRepresentation() + " (module) vs " +
                this->DataLayout.getStringRepresentation() + " (jit)",
                inconvertibleErrorCode());

    return Error::success();
}