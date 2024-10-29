import lldb
from typing import Optional, Any

def read_memory(process: lldb.SBProcess, address: int, length: int) -> Optional[bytes]:
    error = lldb.SBError()
    content: bytes = process.ReadMemory(address, length, error)
    if error.Success():
        return content
    else:
        return None

def read_8B(process: lldb.SBProcess, address: int) -> Optional[int]:
    result: Optional[bytes] = read_memory(process, address, 8)
    if result == None:
        return None
    return int.from_bytes(result, "little")

def custom_closure_summary(value: lldb.SBValue, dict: dict[str, Any]) -> str:
    frame: lldb.SBFrame = value.GetFrame()
    thread: lldb.SBThread = frame.GetThread()
    process: lldb.SBProcess = thread.GetProcess()
    if not process.IsValid():
        return "<process not valid>"

    address: int = value.GetLoadAddress()

    if value.GetByteSize() == 16 or value.GetByteSize() == 8:
        return print_as_swift_closure(process, address)
    else:
        return "<invalid size of " + str(value.GetByteSize()) + ">"

def print_as_swift_closure(process: lldb.SBProcess, address: int) -> str:
    fp: Optional[int] = read_8B(process, address)
    ctx: Optional[int] = read_8B(process, address + 8)

    return "(function pointer: {fp_str}; context: {ctx_str})".format(
        fp_str=nice_hex_format(fp),
        ctx_str=nice_hex_format(ctx)
    )

def nice_hex_format(ptr: Optional[int]) -> str:
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
