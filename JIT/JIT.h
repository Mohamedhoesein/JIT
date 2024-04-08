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

#include "llvm/ADT/StringRef.h"
#include "llvm/ExecutionEngine/Orc/CompileOnDemandLayer.h"
#include "llvm/ExecutionEngine/Orc/CompileUtils.h"
#include "llvm/ExecutionEngine/Orc/Core.h"
#include "llvm/ExecutionEngine/Orc/EPCIndirectionUtils.h"
#include "llvm/ExecutionEngine/Orc/ExecutionUtils.h"
#include "llvm/ExecutionEngine/Orc/ExecutorProcessControl.h"
#include "llvm/ExecutionEngine/Orc/IRCompileLayer.h"
#include "llvm/ExecutionEngine/Orc/IRTransformLayer.h"
#include "llvm/ExecutionEngine/Orc/JITTargetMachineBuilder.h"
#include "llvm/ExecutionEngine/Orc/RTDyldObjectLinkingLayer.h"
#include "llvm/ExecutionEngine/Orc/Shared/ExecutorSymbolDef.h"
#include "llvm/ExecutionEngine/SectionMemoryManager.h"
#include "llvm/IR/DataLayout.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/Transforms/InstCombine/InstCombine.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/Scalar/GVN.h"
#include "llvm/ExecutionEngine/Orc/LLJIT.h"
#include <memory>
#include <exception>
#include <vector>

#include "../reOptimize/ReOptimizeLayer.h"
#include "../reOptimize/JITLinkRedirectableSymbolManager.h"
#include "BaseJIT.h"

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

            static void handleLazyCallThroughError();
            static Expected<ThreadSafeModule> optimizeModule(ThreadSafeModule ThreadSafeModule, const MaterializationResponsibility &R);
            Error applyDataLayout(Module &Module);
        public:
            static Expected<std::unique_ptr<llvm::orc::BaseJIT>> create(llvm::orc::AddModuleCallback AddModule, std::vector<std::string> Arguments);

            JIT(std::unique_ptr<llvm::orc::ExecutionSession> parent,
                std::unique_ptr<llvm::orc::EPCIndirectionUtils> EPCIU,
                llvm::orc::JITTargetMachineBuilder currentVersion,
                llvm::DataLayout oldResourceTracker,
                std::unique_ptr<llvm::orc::RedirectableSymbolManager> JLRSM,
                std::unique_ptr<llvm::orc::ObjectLinkingLayer> OL,
                llvm::orc::AddModuleCallback AM);
            ~JIT();
            Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule) override;
            Error addModule(llvm::orc::ThreadSafeModule ThreadSafeModule, llvm::orc::ResourceTrackerSP ResourceTracker) override;
            Expected<ExecutorSymbolDef> lookup(llvm::StringRef Name) override;
        };

    } // end namespace orc
} // end namespace llvm

#endif //JIT_JIT_H
