from typing import Optional, Any
from utilities.for_lldb import read_qword, address_is_in_executable_memory
from utilities.for_swift import get_opaque_summary_suspected_heap_object
import lldb
import argparse
import shlex

def describe_closure_cmd(
        debugger: lldb.SBDebugger, 
        command: str, 
        result: lldb.SBCommandReturnObject, 
        dict: dict[str, Any]):
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    process: lldb.SBProcess = target.GetProcess()
    thread: lldb.SBThread = process.GetSelectedThread()
    selected_frame: lldb.SBFrame = thread.GetSelectedFrame()

    parser: argparse.ArgumentParser = generateOptionParser()
    args = parser.parse_args(shlex.split(command))
    
    name: str = args.var_name
    describe: bool = args.runtime_describe == True

    value: lldb.SBValue
    if not (value := selected_frame.FindVariable(name)).IsValid():
        if not (value := target.FindFirstGlobalVariable(name)).IsValid():
            print("No valid variable for name '" + name + "'")
            return

    address: int = value.GetLoadAddress()

    if value.GetByteSize() != 16:
        print("Variable has invalid size of " + str(value.GetByteSize()))
        return
    
    fp: Optional[int] = read_qword(process, address)
    ctx: Optional[int] = read_qword(process, address + 8)

    if fp == None or ctx == None:
        print("Failed to access remote memory")
        return
    
    # I assume that Optional<(Function)>.none is always 0
    if fp == 0 and ctx == 0:
        print_result("NULL", "NULL")
        return

    if not address_is_in_executable_memory(process, fp):
        print("Assumed function ptr does not point to executable memory")
        return

    if not describe:
        print_result(hex(fp), hex(ctx))
        return
    
    describe_result(target, selected_frame, fp, ctx)

def describe_result(target: lldb.SBTarget, frame: lldb.SBFrame, fp: int, ctx: int):
    fp_desc: str = "<error>"
    sym_addr: lldb.SBAddress = target.ResolveLoadAddress(fp)
    symbol: lldb.SBSymbol
    if sym_addr.IsValid() and (symbol := sym_addr.GetSymbol()).IsValid():
        fp_desc = hex(ctx) + " " + symbol.GetName()
    else:
        fp_desc = hex(ctx)

    ctx_desc: str = "<error>"
    if ctx == 0:
        ctx_desc = "NULL"
    elif (ctx_summary := get_opaque_summary_suspected_heap_object(target, frame, ctx)) is not None:
        ctx_desc = hex(ctx) + " " + ctx_summary
    else:
        ctx_desc = hex(ctx) + " <unknown>"

def print_result(fp: str, ctx: str):
    print("Function ptr: " + fp)
    print("Context: " + ctx)

def generateOptionParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(usage='closuredesc')

    parser.add_argument(
        "-n", "--name", 
        type=str, 
        action="store", 
        dest="var_name", 
        required=True,
        help="Name of a closure variable in current frame or global scope"
        )

    parser.add_argument(
        '-d', 
        '--describe', 
        action='store_true',
        dest="runtime_describe",
        help="Will try to add description closure and context"
        )
    return parser

def __lldb_init_module(debugger, internal_dict):
    helpText: str = generateOptionParser().format_help()
    debugger.HandleCommand(
        'command script add --help "{help}" --function {function} {name}'.format(
            # escape quotes
            # I don't know why, but my spaces are getting trimmed.
            help=helpText.replace(" ", "\xa0").replace('"', '\\"'), 
            function=__name__ + ".describe_closure_cmd",
            name="closuredesc"
        )
    )
    print("Script `closuredesc` is installed.")

