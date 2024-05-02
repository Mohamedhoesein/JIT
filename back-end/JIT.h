#ifndef JIT_JIT_H
#define JIT_JIT_H

#include "llvm/ExecutionEngine/Orc/EPCIndirectionUtils.h"
#include "llvm/ExecutionEngine/Orc/IRCompileLayer.h"
#include "llvm/ExecutionEngine/Orc/CompileOnDemandLayer.h"
#include "llvm/ExecutionEngine/Orc/IRTransformLayer.h"
#include "llvm/ExecutionEngine/Orc/JITTargetMachineBuilder.h"
#include "llvm/ExecutionEngine/Orc/Debugging/PerfSupportPlugin.h"
#include <memory>
#include <exception>
#include <vector>

#include "BaseJIT.h"
#include "../reOptimize/ReOptimizeLayer.h"
#include "../reOptimize/JITLinkRedirectableSymbolManager.h"
#include "../util/Util.h"

namespace llvm {
    namespace orc {
        /**
         * A class to handle the the optimisations via a pass pipeline.
         */
        class OptimizationTransform {
        private:
            std::string Optimize;
            std::string Tag;
        public:
            /**
             * The constructor for the optimisations.
             * @param Optimize The pass pipeline.
             * @param Tag The tag to use when logging.
             */
            explicit OptimizationTransform(std::string Optimize, std::string Tag)
                : Optimize(std::move(Optimize)), Tag(std::move(Tag)) {}

            /**
             * The function to call when optimising.
             * @param TSM The module to optimise.
             * @param R The materialization handling.
             * @return The optimised module.
             */
            llvm::Expected<llvm::orc::ThreadSafeModule> operator()(llvm::orc::ThreadSafeModule TSM,
                                                                   const llvm::orc::MaterializationResponsibility &R);

            /**
             * The function to call when optimising.
             * @param TSM The module to optimise.
             * @return The optimised module.
             */
            llvm::Expected<llvm::orc::ThreadSafeModule&> operator()(llvm::orc::ThreadSafeModule &TSM);
        };

        /**
         * A simple JIT setup, with optimisation and a single reoptimisation step.
         */
        class JIT: public BaseJIT {
        private:
            std::unique_ptr<llvm::orc::ExecutionSession> ExecutionSession;
            std::unique_ptr<llvm::orc::EPCIndirectionUtils> EPCIU;
            std::unique_ptr<llvm::orc::ObjectLinkingLayer> ObjectLayer;
            std::unique_ptr<llvm::orc::IRCompileLayer> CompileLayer;
            // We rely on the internal state of COD layer, do the COD layer first, and then the Optimize layer,
            // they can't see if the other has created a library for some implementation, since it is not possible to
            // have two libraries with teh same name, i.e. for the same method, this can't be used. To alleviate this
            // we need to reimplement to have some shared logic between multiple instances.
            std::unique_ptr<llvm::orc::CompileOnDemandLayer> CompileOnDemandLayer;
            std::unique_ptr<llvm::orc::IRTransformLayer> OptimizeLayer;
            std::unique_ptr<llvm::orc::ReOptimizeLayer> ReOptimizeLayer;
            std::unique_ptr<llvm::orc::PerfSupportPlugin> Plugin;

            StringMap<int> Internals;
            llvm::orc::JITDylib *MainJD;
            llvm::DataLayout DataLayout;
            llvm::orc::MangleAndInterner Mangle;
            std::set<std::string> GlobalVars;
            OptimizationTransform ReOptimizationTransform;

            static void handleLazyCallThroughError();
            Error applyDataLayout(Module &Module);
        public:
            /**
             * The constructor for the JIT, please use the create method.
             * @see JIT::create(llvm::orc::RequestModuleCallback, std::vector<std::string>).
             * @param ES The execution session to use.
             * @param EPCIU The indirection utilities to used.
             * @param JTMB The target machine builder.
             * @param DL The data layout to use.
             * @param TSM The object to handle redirection for recompilation.
             * @param OL The object linking layer.
             * @param RM The callback used to request more information from the front-end.
             * @param Optimize The string to use indicate the llvm passes to use when optimizing.
             * @param ReOptimize The string to use indicate the llvm passes to use when re-optimizing.
             */
            JIT(std::unique_ptr<llvm::orc::ExecutionSession> ES,
                std::unique_ptr<llvm::orc::EPCIndirectionUtils> EPCIU,
                llvm::orc::JITTargetMachineBuilder JTMB,
                llvm::DataLayout DL,
                std::unique_ptr<llvm::orc::RedirectableSymbolManager> TSM,
                std::unique_ptr<llvm::orc::ObjectLinkingLayer> OL,
                llvm::orc::RequestModuleCallback RM,
                std::string Optimize, std::string ReOptimize);
            /**
             * The destructor to deallocate resource associated with the JIT.
             */
            ~JIT() override;
            /**
             * Create the JIT.
             * @param RequestModule The callback that is used by the back-end to request another module from the front-end.
             * @param Arguments The arguments for the back-end.
             * @return An object with either the jit or an error depending on if the lookup was successful.
             */
            static Expected<std::unique_ptr<llvm::orc::BaseJIT>> create(llvm::orc::RequestModuleCallback AddModule, std::vector<std::string> Arguments);
            /**
             * @copydoc llvm::orc::BaseJIT::addModule(llvm::orc::ThreadSafeModule)
             */
            Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) override;
            /**
             * @copydoc llvm::orc::BaseJIT::addModule(llvm::orc::ThreadSafeModule, llvm::orc::ResourceTrackerSP)
             */
            Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) override;
            /**
             * @copydoc llvm::orc::BaseJIT::lookup(llvm::StringRef)
             */
            Expected<ExecutorAddr> lookup(llvm::StringRef Name) override;
        };

    } // end namespace orc
} // end namespace llvm

#endif //JIT_JIT_H
