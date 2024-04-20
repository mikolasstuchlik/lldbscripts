import lldb
from typing import Any, Optional
from utilities.for_lldb import read_qword, address_is_in_executable_memory

def custom_closure_summary(value: lldb.SBValue, dict: dict[str, Any]) -> str:
    frame: lldb.SBFrame = value.GetFrame()
    if not frame.IsValid():
        return "<frame not valid>"

    thread: lldb.SBThread = frame.GetThread()
    if not thread.IsValid():
        return "<thread not valid>"

    process: lldb.SBProcess = thread.GetProcess()
    if not process.IsValid():
        return "<process not valid>"

    address: int = value.GetLoadAddress()

    if value.GetByteSize() == 16:
        return print_as_swift_closure(process, address)
    elif value.GetByteSize() == 8:
        return print_assuming_preceeds_closure_ctx(process, address)
    else:
        return "<invalid size of " + str(value.GetByteSize()) + ">"

def print_as_swift_closure(process: lldb.SBProcess, address: int) -> str:
    fp: Optional[int] = read_qword(process, address)
    ctx: Optional[int] = read_qword(process, address + 8)

    return "(function pointer: {fp}; context: {ctx})".format(
        fp=pointer_to_str(fp),
        ctx=pointer_to_str(ctx)
    )

def print_assuming_preceeds_closure_ctx(process: lldb.SBProcess, address: int) -> str:
    fp: Optional[int] = read_qword(process, address)
    if fp != None and ( fp == 0 or address_is_in_executable_memory(process, fp)):
        return print_as_swift_closure(process, address)
    else:
        return "<invalid>"

def pointer_to_str(ptr: Optional[int]) -> str:
    if ptr == None:
        return "<invalid>"
    elif ptr == 0:
        return "NULL"
    else:
        return hex(ptr)

def __lldb_init_module(debugger: lldb.SBDebugger, dict: dict[str, Any]):
    debugger.HandleCommand(
        "type summary add --python-function " + __name__ + ".custom_closure_summary -x '{regex}'".format(
            regex="^\\([a-zA-Z\\.\\,\\_ ]*\\) \\-\\> \\([a-zA-Z\\.\\,\\_ ]*\\)$"
        )
    )
    print("Script `closure formatter` is installed.")
