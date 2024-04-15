//===- KaleidoscopeJIT.h - A simple JIT for Kaleidoscope --------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// Contains a simple JIT definition for use in the kaleidoscope tutorials.
//
//===----------------------------------------------------------------------===//

#ifndef JIT_JIT_H
#define JIT_JIT_H

#include <memory>
#include <exception>
#include <vector>

#include "../reOptimize/ReOptimizeLayer.h"
#include "../reOptimize/JITLinkRedirectableSymbolManager.h"
#include "BaseJIT.h"
#include "llvm/ExecutionEngine/Orc/EPCIndirectionUtils.h"
#include "llvm/ExecutionEngine/Orc/IRCompileLayer.h"
#include "llvm/ExecutionEngine/Orc/CompileOnDemandLayer.h"
#include "llvm/ExecutionEngine/Orc/IRTransformLayer.h"
#include "llvm/ExecutionEngine/Orc/JITTargetMachineBuilder.h"

namespace llvm {
    namespace orc {
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

            StringMap<int> Internals;
            llvm::orc::JITDylib *MainJD;
            llvm::DataLayout DataLayout;
            llvm::orc::MangleAndInterner Mangle;
            std::set<std::string> GlobalVars;
            static bool UseOptimize;
            static bool UseReOptimize;
            static std::string Optimize;
            static std::string ReOptimize;

            static void handleLazyCallThroughError();
            static Expected<ThreadSafeModule> optimizeModule(ThreadSafeModule ThreadSafeModule, const MaterializationResponsibility &R);
            Error applyDataLayout(Module &Module);
        public:
            JIT(std::unique_ptr<llvm::orc::ExecutionSession> parent,
                std::unique_ptr<llvm::orc::EPCIndirectionUtils> EPCIU,
                llvm::orc::JITTargetMachineBuilder CurrentVersion,
                llvm::DataLayout OldResourceTracker,
                std::unique_ptr<llvm::orc::RedirectableSymbolManager> TSM,
                std::unique_ptr<llvm::orc::ObjectLinkingLayer> OL,
                llvm::orc::RequestModuleCallback AM);
            ~JIT() override;
            static Expected<std::unique_ptr<llvm::orc::BaseJIT>> create(llvm::orc::RequestModuleCallback AddModule, std::vector<std::string> Arguments);
            Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) override;
            Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) override;
            Expected<ExecutorSymbolDef> lookup(llvm::StringRef Name) override;
        };

    } // end namespace orc
} // end namespace llvm

#endif //JIT_JIT_H
