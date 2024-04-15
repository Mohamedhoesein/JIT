import os
import subprocess
import shutil
import typing
import time
import argparse
from enum import Enum
from datetime import datetime


class Component(Enum):
    BOTH = 1
    JIT = 2
    REFERENCE = 3


class BackEndArgs:
    def __init__(self, name: str, args: [str]):
        self.name = name
        self.args = args


class ComponentData:
    def __init__(
            self,
            component: Component,
            backend: typing.List[BackEndArgs],
            jit_data_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]],
            reference_data_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]]
    ):
        self.component = component
        self.backend = backend
        self.jit_data_extraction = jit_data_extraction
        self.reference_data_extraction = reference_data_extraction

    def for_reference(self):
        return self.component == Component.REFERENCE or self.component == Component.BOTH


    def for_jit(self):
        return self.component == Component.JIT or self.component == Component.BOTH


def get_repeats():
    return 5


def add_compile_file(path: str) -> str:
    return os.path.join(path, "compile.py")


def add_run_file(path: str) -> str:
    return os.path.join(path, "run.py")


def get_time_data_reference_file(path: str) -> str:
    return os.path.join(path, "time_data_reference.csv")


def get_time_data_jit_file(path: str) -> str:
    return os.path.join(path, "time_data_jit.csv")


def get_other_data_reference_file(path: str) -> str:
    return os.path.join(path, "other_data_reference.csv")


def get_other_data_jit_file(path: str) -> str:
    return os.path.join(path, "other_data_jit.csv")


def get_source_directory(path: str) -> str:
    return os.path.join(path, "source")


def get_reference_directory(path: str) -> str:
    return os.path.join(path, "reference")


def get_jit_directory(path: str) -> str:
    return os.path.join(path, "jit")


def get_data_directory(path: str) -> str:
    return os.path.join(path, "data")


def recreate_file(paths: [str]) -> None:
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w+")
        f.close()


def get_source_files(path: str, filter: typing.Callable[[str], bool]) -> [str]:
    if path == "":
        return []
    sources = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if (name.endswith(".c") or name.endswith(".h")) and filter(name):
                sources.append(os.path.join(path, name))
    return sources


def get_recursive_source_files(paths: [str], filter: typing.Callable[[str], bool]) -> [str]:
    sources = []
    for path in paths:
        sources += get_source_files(path, filter)
    return sources


def get_all_directories(path: str) -> [str]:
    return [
        f
        for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f)) and f != "__pycache__"
    ]


def get_all_concat_directories(path: str) -> [str]:
    return list(map(lambda f: os.path.join(path, f), get_all_directories(path)))


def remove_if_exists(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def remove_files(paths: [str]) -> None:
    for path in paths:
        remove_if_exists(path)


def remove_data_files(directory: str) -> None:
    remove_files([
        get_time_data_reference_file(directory),
        get_time_data_jit_file(directory),
        get_other_data_reference_file(directory),
        get_other_data_jit_file(directory)
    ])


def append_file(source: str, target: str) -> None:
    while not os.path.exists(source):
        time.sleep(1)
    subprocess.run(["cat " + source + " >> " + target], shell=True, check=True)


def add_new_line(file: str) -> None:
    with open(file, "a") as f:
        f.write("\n")


def persist_data_files(path: str, frontend: str, backend: str) -> None:
    data_directory = get_data_directory(os.path.dirname(__file__))
    if not os.path.isdir(data_directory):
        os.makedirs(data_directory)
    basename = os.path.basename(path)
    basename = datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + "." + frontend + ("." + backend if backend is not None else "") + "_" + basename
    target = os.path.join(data_directory, basename)

    subprocess.run(["cat " + path + " >> " + target], shell=True, check=True)
    remove_if_exists(path)


def copy_data(source: str, target: str, frontend: str, backend: str, persist: bool) -> None:
    append_file(source, target)
    add_new_line(target)
    if persist:
        persist_data_files(target, frontend, backend)


def simple_copy_data_files(subdirectory: str, base_directory: str, component: Component) -> None:
    copy_data_files(subdirectory, base_directory, component, "", "", False)


def copy_data_files(
        subdirectory: str,
        base_directory: str,
        component: Component,
        frontend: str,
        backend: str,
        persist: bool = True
) -> None:
    if component == Component.REFERENCE or component == Component.BOTH:
        benchmark_reference = get_time_data_reference_file(subdirectory)
        base_benchmark_reference = get_time_data_reference_file(base_directory)
        copy_data(benchmark_reference, base_benchmark_reference, frontend, backend, persist)

        other_reference = get_other_data_reference_file(subdirectory)
        base_other_reference = get_other_data_reference_file(base_directory)
        copy_data(other_reference, base_other_reference, frontend, backend, persist)

    if component == Component.JIT or component == Component.BOTH:
        benchmark_jit = get_time_data_jit_file(subdirectory)
        base_benchmark_jit = get_time_data_jit_file(base_directory)
        copy_data(benchmark_jit, base_benchmark_jit, frontend, backend, persist)

        other_jit = get_other_data_jit_file(subdirectory)
        base_other_jit = get_other_data_jit_file(base_directory)
        copy_data(other_jit, base_other_jit, frontend, backend, persist)


def copy_file(full_source: str, directory: str, file: str) -> None:
    source_input = os.path.join(full_source, file)
    target_input = os.path.join(directory, file)
    shutil.copyfile(source_input, target_input)


def add_quote(string: str) -> str:
    if string[0] != "\"":
        string = "\"" + string
    if string[-1] != "\"":
        string = string + "\""
    return string


def run_command(
        name: str,
        time_data_file: str,
        command: [str],
        first: bool,
        last: bool,
        other_data_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]],
        other_data_file: str,
        args: str
) -> None:
    name = add_quote(name)
    args = add_quote(args)
    process = subprocess.run(
        [
            "/usr/bin/time",
            "-q", "-a", "-o" + time_data_file,
                        "-f" + ((name + ","  + args + ",") if first else "")
                        + "\"%e\",\"%x\"" + ("\n" if last else ",")
        ] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    other_data = other_data_extraction(process)
    other_data = list(map(lambda x: "\"" + x + "\"", other_data))
    if first:
        other_data = [name + "," + args] + other_data
    other_data_row = str("," if not first and len(other_data) != 0 else "") + str(",".join(other_data)) + str(
        "\n" if last else "")
    with open(other_data_file, "a") as f:
        f.write(other_data_row)


# https://stackoverflow.com/questions/1877999/delete-final-line-in-file-with-python
def clean_other_csv(file: str) -> None:
    with open(file, "r+", encoding="utf-8") as file:
        file.seek(0, os.SEEK_END)

        pos = file.tell() - 1

        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()


def clean_benchmark_csv(file: str) -> None:
    search_and_replace(file, "\n\"", "\"")
    search_and_replace(file, "\n\n", "")


# https://www.tutorialspoint.com/How-to-search-and-replace-text-in-a-file-using-Python
def search_and_replace(file_path: str, search_word: str, replace_word: str) -> None:
    with open(file_path, 'r') as file:
        file_contents = file.read()
        updated_contents = file_contents.replace(search_word, replace_word)
    with open(file_path, 'w') as file:
        file.write(updated_contents)


def default_filter(name: str) -> bool:
    return True


def default_additional_steps(full_source: str, full_reference_target: str, full_jit_target: str,
                             component: Component) -> None:
    pass


def default_arguments(directory: str) -> [str]:
    return []


def default_data_extraction(result: subprocess.CompletedProcess[bytes]) -> [str]:
    return []


def to_arg(flag: str, args: [str]):
    return "-" + flag + "\"" + ",".join(args) + "\""


def run(
        path: str,
        jit: str,
        prefix: str,
        arguments: typing.Callable[[str], typing.List[str]],
        reference_command: typing.Callable[[str], str],
        jit_files: typing.Callable[[str], str],
        component_data: ComponentData
) -> None:
    jit_directories = get_all_directories(get_jit_directory(path))
    benchmark_reference = get_time_data_reference_file(path)
    other_reference = get_other_data_reference_file(path)
    benchmark_jit = get_time_data_jit_file(path)
    other_jit = get_other_data_jit_file(path)
    remove_files([benchmark_reference, other_reference, benchmark_jit, other_jit])
    if component_data.for_reference():
        recreate_file([benchmark_reference, other_reference])
    if component_data.for_jit():
        recreate_file([benchmark_jit, other_jit])
    for jit_directory in jit_directories:
        print("started running " + jit_directory)
        full_reference_directory = os.path.join(get_reference_directory(path), jit_directory)
        full_jit_directory = os.path.join(get_jit_directory(path), jit_directory)
        sources = jit_files(full_jit_directory)
        reference_args = arguments(jit_directory)
        jit_args = [jit_directory] + reference_args
        reference = reference_command(full_reference_directory)
        if component_data.for_reference():
            for i in range(get_repeats()):
                run_command(
                    (prefix if prefix.endswith("/") else prefix + "/") + jit_directory,
                    benchmark_reference,
                    [reference] + reference_args,
                    i == 0,
                    i == 4,
                    component_data.reference_data_extraction,
                    other_reference,
                    ""
                )
        if component_data.for_jit():
            for b in component_data.backend:
                print("started running args: " + b.name)
                for i in range(get_repeats()):
                    run_command(
                        (prefix if prefix.endswith("/") else prefix + "/") + jit_directory + " " + b.name,
                        benchmark_jit,
                        [jit, "-f" + ",".join(sources), "-a" + ",".join(jit_args), "-b" + b.args + ""],
                        i == 0,
                        i == 4,
                        component_data.jit_data_extraction,
                        other_jit,
                        b.args
                    )
                print("finished running args: " + b.name)
        print("finished running " + jit_directory)

    if component_data.for_reference():
        clean_benchmark_csv(benchmark_reference)
        clean_other_csv(other_reference)
    if component_data.for_jit():
        clean_benchmark_csv(benchmark_jit)
        clean_other_csv(other_jit)


def valid_frontend(frontend: str) -> bool:
    base_directory = os.path.dirname(__file__)
    directories = get_all_directories(base_directory)
    return frontend in directories


def backend_args_map() -> dict:
    mapping = {
        "simple": [
            BackEndArgs(
                "O1-O2",
                "\"-opt annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function-attrs<skip-non-recursive>,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,libcalls-shrinkwrap,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,memcpyopt,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,coro-elide,adce,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O1>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify" +
                "-reopt annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function-attrs<skip-non-recursive>,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O2>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify\""
            ),
            BackEndArgs(
                "O1-O3",
                "\"-opt annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function-attrs<skip-non-recursive>,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,libcalls-shrinkwrap,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,memcpyopt,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,coro-elide,adce,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O1>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify" +
                "-reopt annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>,callsite-splitting),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function-attrs<skip-non-recursive>,argpromotion,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,chr,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O3>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify\""
            ),
            BackEndArgs(
                "O2-O3",
                "\"-opt annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function-attrs<skip-non-recursive>,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O2>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify" +
                "-reopt annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>,callsite-splitting),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function-attrs<skip-non-recursive>,argpromotion,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,chr,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O3>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify\""
            )
        ]
    }
    return mapping


def backend_args(backend: str) -> [BackEndArgs]:
    if not valid_backend(backend):
        return BackEndArgs("None", "")
    return backend_args_map()[backend]


def backend_parsing_map() -> dict:
    mapping = {"simple": default_data_extraction}
    return mapping


def backend_parsing(backend: str) -> typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]]:
    if not valid_backend(backend):
        return default_data_extraction
    return backend_parsing_map()[backend]


def valid_backend(backend: str) -> bool:
    return backend in backend_parsing_map()


def parse_jit_args() -> typing.Any:
    parser = argparse.ArgumentParser(
        prog="benchmark",
        description="Benchmark the jit and run some reference implementation."
    )
    parser.add_argument('-j', help="The jit to use.")
    parser.add_argument('-b', nargs=1,
                        help="The backend that is used in the jit, this determines how to parse the additional information from the jit.")
    parser.add_argument('-e', action="store_true",
                        help="If some external reference implementation will be ran for their performance.")
    args = parser.parse_args()
    args.b = args.b[0]
    if args.j is not None and not valid_backend(args.b):
        print("Invalid backend given.")
        exit(-1)
    if args.j is None and args.b is not None and args.e is not None:
        print("Ignored the -b flag.")
        args.b = None
    return args


def full_parse_jit_args() -> typing.Any:
    parser = argparse.ArgumentParser(
        prog="benchmark",
        description="Benchmark the jit and run some reference implementation."
    )
    parser.add_argument('-j', help="The jit to use.")
    parser.add_argument('-f', required=True,
                        help="The frontend that is used in the jit, this determines which folder is taken.")
    parser.add_argument('-b', nargs=1,
                        help="The backend that is used in the jit, this determines how to parse the additional information from the jit.")
    parser.add_argument('-e', action="store_true",
                        help="If some external reference implementation will be ran for their performance.")
    args = parser.parse_args()
    args.b = args.b[0]
    if not valid_frontend(args.f):
        print("Invalid frontend given.")
        exit(-1)
    elif args.j is not None and not valid_backend(args.b):
        print("Invalid backend given.")
        exit(-1)
    if args.j is None and args.b is not None and args.e is not None:
        print("Ignored the -b flag.")
        args.b = None
    return args


def args_to_run_array(args: typing.Any) -> [str]:
    return ["-j", args.j] + (["-b", args.b] if args.b != "" and args.b is not None else []) + (["-e"] if args.e else [])


def compile_args_to_component(args: typing.Any) -> Component:
    if args.b and args.e:
        return Component.BOTH
    elif args.e:
        return Component.REFERENCE
    else:
        return Component.JIT

def args_to_component(args: typing.Any) -> Component:
    if args.b != "" and args.e:
        return Component.BOTH
    elif args.e:
        return Component.REFERENCE
    else:
        return Component.JIT