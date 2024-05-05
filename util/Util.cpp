#include "llvm/Support/SourceMgr.h"
#include "llvm/IRReader/IRReader.h"
#include <iostream>
#include <filesystem>
#include <getopt.h>

#include "Util.h"

std::string O1 = "annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,libcalls-shrinkwrap,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,memcpyopt,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,coro-elide,adce,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O1>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify";
std::string O2 = "annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O2>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify";

#define X(type, name) name,
char const *log_type_name[] =
        {
                LOG_TYPES
        };
#undef X

#define X(type, name) name,
char const *log_part_name[] =
        {
                LOG_PART
        };
#undef X

void print_main_entry_time() {
    std::chrono::time_point<std::chrono::system_clock> now = std::chrono::system_clock::now();
    auto duration = now.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
    print_log_data("Start", LogType::List, LogPart::Whole, std::to_string(millis));
    print_log_data("Main_Entry", LogType::List, LogPart::Whole, std::to_string(millis));
}

bool is_number(const std::string& s)
{
    return !s.empty() && std::find_if(s.begin(),
                                      s.end(), [](unsigned char c) { return !std::isdigit(c); }) == s.end();
}

void print_log_data(const std::string& tag, LogType type, LogPart part, const std::string& data) {
    std::chrono::time_point<std::chrono::system_clock> now = std::chrono::system_clock::now();
    auto duration = now.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
    std::cout << "[DATA," << millis << "," << log_type_name[type] << "," << log_part_name[part] << "," << tag << "] " << " "
              << data << std::endl;
}

std::vector<std::string> split(const std::string& string, const char delimiter) {
    std::stringstream stream(string);
    std::string segment;
    std::vector<std::string> parts;
    while (std::getline(stream, segment, delimiter))
        parts.push_back(segment);
    return parts;
}

std::vector<std::string> split_once(const std::string& string, const char delimiter) {
    std::vector<std::string> parts;
    parts.emplace_back(string.substr(0, string.find(delimiter)));
    parts.emplace_back(string.substr(string.find(delimiter) + 1));
    return parts;
}

struct Arguments getArguments(int argc, char **argv) {
    struct Arguments arguments = (struct Arguments){
            .Files = {},
            .FrontEndArguments = "",
            .BackEndArguments = "",
            .ApplicationArguments = ""
    };
    int character;
    while (true) {
        character = getopt(argc, argv, "i:r:b:a:");
        if (character == -1)
            break;

        switch (character) {
            case 'i':
                arguments.Files = split(optarg, ',');
                break;
            case 'r':
                arguments.FrontEndArguments = optarg;
                break;
            case 'b':
                arguments.BackEndArguments = optarg;
                break;
            case 'a':
                arguments.ApplicationArguments = optarg;
                break;
            default:
                std::cerr << "Invalid argument given." << std::endl;
                exit(-1);
        }
    }
    return arguments;
}

std::unique_ptr<llvm::Module> load_module(llvm::StringRef file, llvm::LLVMContext &context)
{
    llvm::SMDiagnostic error;
    std::unique_ptr<llvm::Module> module = parseIRFile(file, error, context);

    PRINT_ERROR_FULL(
            !module,
            std::string what;llvm::raw_string_ostream os(what);error.print("error after ParseIR()", os);,
            what
    )

    return module;
}

bool hasEnding(std::string const &fullString, std::string const &ending) {
    if (fullString.length() >= ending.length()) {
        return (0 == fullString.compare(fullString.length() - ending.length(), ending.length(), ending));
    } else {
        return false;
    }
}

llvm::Expected<std::unique_ptr<llvm::orc::IRCompileLayer::IRCompiler>> createCompiler(llvm::orc::JITTargetMachineBuilder JTMB, llvm::ObjectCache *ObjCache) {
#ifdef LOG
    return std::make_unique<LogCompiler>(std::move(JTMB), ObjCache);
#else
    return std::make_unique<llvm::orc::ConcurrentIRCompiler>(std::move(JTMB), ObjCache);
#endif
}