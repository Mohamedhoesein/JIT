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

#ifndef LLVM_EXECUTIONENGINE_ORC_KALEIDOSCOPEJIT_H
#define LLVM_EXECUTIONENGINE_ORC_KALEIDOSCOPEJIT_H

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

#include "reOptimize/ReOptimizeLayer.h"
#include "reOptimize/JITLinkRedirectableSymbolManager.h"

namespace llvm {
    namespace orc {

        class JIT {
        private:
            std::unique_ptr<ExecutionSession> ES;
            std::unique_ptr<EPCIndirectionUtils> EPCIU;
            std::unique_ptr<ObjectLinkingLayer> ObjectLayer;
            std::unique_ptr<IRCompileLayer> CompileLayer;
            // We rely on the internal state of COD layer, do the COD layer first, and then the Optimize layer,
            // they can't see if the other has created a library for some implementation, since it is not possible to
            // have two libraries with teh same name, i.e. for the same method, this can't be used. To alleviate this
            // we need to reimplement to have some shared logic between multiple instances.
            std::unique_ptr<CompileOnDemandLayer> CODLayer;
            std::unique_ptr<IRTransformLayer> OptimizeLayer;
            std::unique_ptr<ReOptimizeLayer> ReOpLayer;

            StringMap<int> internals;
            JITDylib *MainJD;
            DataLayout DL;
            MangleAndInterner Mangle;
            std::set<std::string> globalVars;

            static void handleLazyCallThroughError();
            static Expected<ThreadSafeModule> optimizeModule(ThreadSafeModule TSM, const MaterializationResponsibility &R);
        public:
            static Expected<std::unique_ptr<JIT>> Create();

            JIT(std::unique_ptr<ExecutionSession> ES,
                std::unique_ptr<EPCIndirectionUtils> EPCIU,
                JITTargetMachineBuilder JTMB,
                DataLayout DL,
                std::unique_ptr<RedirectableSymbolManager> JLRSM,
                std::unique_ptr<ObjectLinkingLayer> OL);
            ~JIT();
            Error applyDataLayout(Module &M);
            Error addModule(ThreadSafeModule TSM, ResourceTrackerSP RT = nullptr);
            Expected<ExecutorSymbolDef> lookup(StringRef Name);
            const DataLayout &getDataLayout() const { return DL; }
            JITDylib *getMainJITDylib() { return MainJD; }
            void dump() {this->ES->dump(dbgs());}
        };

    } // end namespace orc
} // end namespace llvm

#endif // LLVM_EXECUTIONENGINE_ORC_KALEIDOSCOPEJIT_H
