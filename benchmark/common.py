"""
This module contains functions that are shared between multiple modules no matter the front-end.
"""

import os
import subprocess
import typing
import argparse

from . import default
from . import files
from . import classes


def get_repeats():
    """
    Get how many times each benchmark should be run.
    :return: How many times each benchmark should be run.
    """
    return 5


def add_quote(string: str) -> str:
    """
    Add a quote around a string if it is not present.
    :param string:
    :return: The quoted string.
    """
    if string[0] != "\"" and string[-1] != "\"":
        string = f"\"{string}\""
    return string


def get_time(err: bytes) -> float:
    """
    Get the wall clock time in milliseconds from the time command.
    :param err: The string retrieved from standard error.
    :return: The wall clock time in milliseconds from the time command.
    """
    lines = err.decode().splitlines()
    for line in lines:
        parts = line.split(" ")
        for part in parts:
            if part.startswith("real"):
                time = part.removeprefix("real")
                time = time.strip()
                first_split = time.split("m")
                minutes = float(first_split[0])
                return minutes * 60 + float(first_split[1].removesuffix("s")) * 10000


def run_command(
        name: str,
        time_data_file: str,
        command: typing.List[str],
        first: bool,
        last: bool,
        other_data_extraction: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]],
        other_data_file: str,
        extra_other: str,
        extra_base: str
) -> None:
    """
    Run a command and generate some csv files with the data. For the result of the time command will be added to a new
    line no matter what.
    :param name: A nice name for the current run, which will we placed in the first column of the row, if first is True.
    :param time_data_file: The name of the file where the result of the time command should be put.
    :param command: The command to run.
    :param first: If this is the first command to be run for the current command.
    :param last: If this is the last command to be run for the current command.
    :param other_data_extraction: A callback to extract any other information from the command.
    :param other_data_file: The name of the file where the extra data should be put.
    :param extra_other: Any extra information to place in the csv file for the other data.
    :param extra_base: Any extra information to place in the csv file for the time data.
    """
    process = subprocess.run(
        [" ".join(["time"] + command)],
        capture_output=True,
        shell=True
    )
    time = get_time(process.stderr)
    return_code = process.returncode
    line = (
        (
                f"\"{name}\"" +
                (f",{extra_base}," if extra_base != "" and extra_base is not None else ",")
        ) if first else ""
    ) + f"\"{time}\",\"{return_code}\"" + ("\n" if last else ",")
    with open(time_data_file, "a") as f:
        f.write(line)
    other_data = other_data_extraction(name, process)
    other_data = list(map(lambda x: "\"" + x + "\"", other_data))
    if first:
        other_data = ([f"\"{name}\""] +
                      ([extra_other] if extra_other != "" and extra_other is not None else []) +
                      other_data)
    other_data_row = ("," if not first and len(other_data) != 0 else "") + ",".join(other_data) + ("\n" if last else "")
    with open(other_data_file, "a") as f:
        f.write(other_data_row)


def back_end_parsing_map() -> dict:
    """
    The map between different back-ends for the JIT and a function to extract data from it.
    :return: The map itself.
    """
    mapping = {
        "recomp": default.default_back_end_data_extraction(5)
    }
    return mapping


def back_end_args_map() -> dict:
    """
    The map between different back-ends for the JIT and the different standard arguments.
    :return: The map itself.
    """
    mapping = {
        "recomp": [
            classes.Args(
                "O1-O2",
                "-opt=annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,libcalls-shrinkwrap,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,memcpyopt,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,coro-elide,adce,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O1>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify " +
                "-reopt=annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O2>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify"
            ),
            classes.Args(
                "O1-O3",
                "-opt=annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,libcalls-shrinkwrap,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,memcpyopt,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,coro-elide,adce,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O1>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify " +
                "-reopt=annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>,callsite-splitting),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,argpromotion,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,chr,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O3>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify"
            ),
            classes.Args(
                "O2-O3",
                "-opt=annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<no-nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O2>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify " +
                "-reopt=annotation2metadata,forceattrs,inferattrs,coro-early,function<eager-inv>(lower-expect,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;no-switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,sroa<modify-cfg>,early-cse<>,callsite-splitting),openmp-opt,ipsccp,called-value-propagation,globalopt,function<eager-inv>(mem2reg,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),require<globals-aa>,function(invalidate<aa>),require<profile-summary>,cgscc(devirt<4>(inline<only-mandatory>,inline,argpromotion,openmp-opt-cgscc,function<eager-inv;no-rerun>(sroa<modify-cfg>,early-cse<memssa>,speculative-execution,jump-threading,correlated-propagation,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,aggressive-instcombine,constraint-elimination,libcalls-shrinkwrap,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,reassociate,loop-mssa(loop-instsimplify,loop-simplifycfg,licm<no-allowspeculation>,loop-rotate<header-duplication;no-prepare-for-lto>,licm<allowspeculation>,simple-loop-unswitch<nontrivial;trivial>),simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>,loop(loop-idiom,indvars,loop-deletion,loop-unroll-full),sroa<modify-cfg>,vector-combine,mldst-motion<no-split-footer-bb>,gvn<>,sccp,bdce,instcombine<max-iterations=1000;no-use-loop-info>,jump-threading,correlated-propagation,adce,memcpyopt,dse,move-auto-init,loop-mssa(licm<allowspeculation>),coro-elide,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,instcombine<max-iterations=1000;no-use-loop-info>),function-attrs,function(require<should-not-run-function-passes>),coro-split)),deadargelim,coro-cleanup,globalopt,globaldce,elim-avail-extern,rpo-function-attrs,recompute-globalsaa,function<eager-inv>(float2int,lower-constant-intrinsics,chr,loop(loop-rotate<header-duplication;no-prepare-for-lto>,loop-deletion),loop-distribute,inject-tli-mappings,loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>,loop-load-elim,instcombine<max-iterations=1000;no-use-loop-info>,simplifycfg<bonus-inst-threshold=1;forward-switch-cond;switch-range-to-icmp;switch-to-lookup;no-keep-loops;hoist-common-insts;sink-common-insts;speculate-blocks;simplify-cond-branch>,slp-vectorizer,vector-combine,instcombine<max-iterations=1000;no-use-loop-info>,loop-unroll<O3>,transform-warning,sroa<preserve-cfg>,instcombine<max-iterations=1000;no-use-loop-info>,loop-mssa(licm<allowspeculation>),alignment-from-assumptions,loop-sink,instsimplify,div-rem-pairs,tailcallelim,simplifycfg<bonus-inst-threshold=1;no-forward-switch-cond;switch-range-to-icmp;no-switch-to-lookup;keep-loops;no-hoist-common-insts;no-sink-common-insts;speculate-blocks;simplify-cond-branch>),globaldce,constmerge,cg-profile,rel-lookup-table-converter,function(annotation-remarks),verify"
            )
        ]
    }
    return mapping


def back_end_parsing(back_end: str) -> typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]]:
    """
    Get the function that handles the data parsing for a back-end.
    :param back_end: The name of the back-end.
    :return: The function that handles the data parsing for a back-end
    """
    return back_end_parsing_map()[back_end]


def back_end_args(back_end: str) -> typing.List[classes.Args]:
    """
    Get the arguments for the back-end.
    :param back_end: The name of the back-end.
    :return: The arguments for the back-end.
    """
    return back_end_args_map()[back_end]


def valid_back_end(back_end: str) -> bool:
    """
    Check if the back-end is valid, which means that there is a parsing function and arguments defined for it.
    :param back_end: The back-end to check.
    :return: True if the back-end is valid.
    """
    return back_end in back_end_parsing_map()


def jit_other_data_extraction(
        front_end: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]],
        back_end: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]]
) -> typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]]:
    """
    A single wrapper function for the data extraction from the front-end and back-end. The results will be concatenated
    into a single array.
    :param front_end: The callback for the front-end.
    :param back_end: The callback for the back-end.
    :return: A callback that will call the callback for the front-end followed by the callback for the back-end.
    """
    return lambda a, b: front_end(a, b) + default.default_whole_data_extraction(a, b) + back_end(a,b)


def run(
        path: str,
        prefix: str,
        arguments: typing.Callable[[str], typing.List[str]],
        component_data: classes.ComponentData,
        extra: typing.Callable[[str, bool], str]
) -> None:
    """
    Run the benchmarks in the JIT, reference implementation, or both.
    :param path: The path to the benchmark folder.
    :param prefix: Any prefix that should be included in the name of the run in the csv file.
    :param arguments: A callback to get additional arguments for the benchmark.
    :param component_data:
    """
    benchmark_reference = files.get_time_data_reference_file(path)
    other_reference = files.get_other_data_reference_file(path)
    benchmark_jit = files.get_time_data_jit_file(path)
    other_jit = files.get_other_data_jit_file(path)
    files.remove_files([benchmark_reference, other_reference, benchmark_jit, other_jit])
    if component_data.for_reference():
        files.recreate_file([benchmark_reference, other_reference])
        reference_directories = files.get_all_directories(files.get_reference_directory(path))
        for reference_directory in sorted(reference_directories):
            print(f"started running {reference_directory}")
            full_reference_directory = os.path.join(files.get_reference_directory(path), reference_directory)
            reference = component_data.reference_command(full_reference_directory)
            reference_args = arguments(full_reference_directory)
            for i in range(get_repeats()):
                run_command(
                    (prefix if prefix.endswith("/") else prefix + "/") + reference_directory,
                    benchmark_reference,
                    reference + reference_args,
                    i == 0,
                    i == 4,
                    component_data.reference_data_extraction,
                    other_reference,
                    extra((prefix if prefix.endswith("/") else prefix + "/") + reference_directory, False),
                    ""
                )
            print(f"finished running {reference_directory}")
    if component_data.for_jit():
        files.recreate_file([benchmark_jit, other_jit])
        jit_directories = files.get_all_directories(files.get_jit_directory(path))
        for jit_directory in sorted(jit_directories):
            print(f"started running {jit_directory}")
            full_jit_directory = os.path.join(files.get_jit_directory(path), jit_directory)
            sources = component_data.jit_files(full_jit_directory)
            jit_args = list(filter(lambda arg: arg != "", [jit_directory] + arguments(full_jit_directory)))
            for f in component_data.front_end_args:
                print(f"started running front-end args {f.name}")
                for b in component_data.back_end_args:
                    print(f"started running back-end args {b.name}")
                    extra_data = extra((prefix if prefix.endswith("/") else prefix + "/") + jit_directory, True)
                    for i in range(get_repeats()):
                        run_command(
                            (prefix if prefix.endswith("/") else prefix + "/") + jit_directory + " " + b.name,
                            benchmark_jit,
                            [component_data.jit, "-i", "\"" + ",".join(sources) + "\"", "-a", "\"" + " ".join(jit_args) + "\""] +
                            (["-b", f"\"{b.args}\""] if b.args != "" else []) +
                            (["-r", f"\"{b.args}\""] if f.args != "" else []),
                            i == 0,
                            i == 4,
                            jit_other_data_extraction(component_data.front_end_extraction, component_data.back_end_extraction),
                            other_jit,
                            f"\"front-end {f.name}:{f.args}\",\"back-end {b.name}:{b.args}\"" +
                            (("," + extra_data) if extra_data != "" else ""),
                            f"\"front-end {f.name}:{f.args}\",\"back-end {b.name}:{b.args}\""
                        )
                    print(f"finished running back-end args {b.name}")
                print(f"finished running front-end args {f.name}")
            print(f"finished running {jit_directory}")


def valid_front_end(front_end: str) -> bool:
    """
    Check if the front-end is valid by checking if there is a folder present for the front-end with a run.py script.
    :param front_end: The front-end to check.
    :return: True if the front-end is valid, otherwise False.
    """
    base_directory = os.path.dirname(__file__)
    directories = files.get_all_directories(base_directory)
    return front_end in directories and os.path.isfile(os.path.join(base_directory, front_end, "run.py"))


def parse_jit_args() -> typing.Any:
    """
    Parse command line arguments for the run script of a benchmark for a specific front-end.
    :return: The objects with the properties set which are related to the set command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="benchmark",
        description="Benchmark the jit and run some reference implementation."
    )
    parser.add_argument('-j', help="The jit to use.")
    parser.add_argument('-b', nargs=1,
                        help="The back-end that is used in the jit, this determines how to parse the additional information from the jit.")
    parser.add_argument('-e', action="store_true",
                        help="If some external reference implementation will be ran for their performance.")
    args = parser.parse_args()
    if args.b is not None:
        args.b = args.b[0]
    if args.j is not None and not valid_back_end(args.b):
        print("Invalid back-end given.")
        exit(-1)
    if args.j is None and args.b is not None and args.e is not None:
        print("Ignored the -b flag.")
        args.b = None
    return args


def full_parse_jit_args() -> typing.Any:
    """
    Parse command line arguments for the top-level run script.
    :return: The objects with the properties set which are related to the set command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="benchmark",
        description="Benchmark the jit and run some reference implementation."
    )
    parser.add_argument('-j', help="The jit to use.")
    parser.add_argument('-f', required=True,
                        help="The frontend that is used in the jit, this determines which folder is taken.")
    parser.add_argument('-b', nargs=1,
                        help="The back-end that is used in the jit, this determines how to parse the additional information from the jit.")
    parser.add_argument('-e', action="store_true",
                        help="If some external reference implementation will be ran for their performance.")
    args = parser.parse_args()
    if args.b is not None:
        args.b = args.b[0]
    if not valid_front_end(args.f):
        print("Invalid frontend given.")
        exit(-1)
    elif args.j is not None and not valid_back_end(args.b):
        print("Invalid back-end given.")
        exit(-1)
    if args.j is None and args.b is not None and args.e is not None:
        print("Ignored the -b flag.")
        args.b = None
    return args


def args_to_run_array(args: typing.Any) -> typing.List[str]:
    """
    Convert the arguments object for parse_jit_args() to an array of strings to pass to the run command.
    :param args: The argument to convert.
    :return: An array of strings to pass to the run command
    """
    return ((["-j", args.j] if args.j is not None else []) +
            (["-b", args.b] if args.b != "" and args.b is not None else []) +
            (["-e"] if args.e else []))


def args_to_component(args: typing.Any) -> classes.Component:
    """
    Convert the run arguments to a classes.Component.
    :param args: The arguments to convert.
    :return: The classes.Component that is associated with the arguments.
    """
    if args.b != "" and args.b is not None and args.e:
        return classes.Component.BOTH
    elif args.e:
        return classes.Component.REFERENCE
    else:
        return classes.Component.JIT
