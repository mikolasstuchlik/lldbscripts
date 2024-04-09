from typing import Optional
import lldb

def make_breakpoint(frame: lldb.SBFrame, address: int):
    thread: lldb.SBThread = frame.GetThread()
    process: lldb.SBProcess = thread.GetProcess() 
    target: lldb.SBTarget = process.GetTarget()
    target.GetDebugger().HandleCommand(f"breakpoint set -a {hex(address)}")

def read_qword(process: lldb.SBProcess, address: int) -> Optional[int]:
    result: Optional[bytes] = read_memory(process, address, 8)
    if result == None:
        return None
    
    # ARM64 is big endian, but bytes are returned in little endian order
    return int.from_bytes(result, "little")

def read_memory(process: lldb.SBProcess, address: int, length: int) -> Optional[bytes]:
    error = lldb.SBError()
    content: bytes = process.ReadMemory(address, length, error)
    if error.Success():
        return content
    else:
        return None

def pointer_is_in_readwrite_memory(process: lldb.SBProcess, address: int) -> bool:
    info = lldb.SBMemoryRegionInfo()
    result: lldb.SBError = process.GetMemoryRegionInfo(address, info)

    if result.Success() and info.IsReadable() and info.IsWritable():
        return True
    else:
        return False
    
def read_null_terminated_string(target: lldb.SBTarget, base: int) -> Optional[str]:
    process = target.GetProcess()

    error = lldb.SBError()
    address = base

    accumulator = ""

    while True:
        byte_data = read_memory(process, address, 1)
        
        if error.Fail() or byte_data == b'\0' or byte_data == None:
            break

        accumulator += byte_data.decode('utf-8')
        address += 1

    if error.Success():
        return accumulator
    else:
        return None

def address_is_in_executable_memory(process: lldb.SBProcess, address: int) -> bool:
    info = lldb.SBMemoryRegionInfo()
    result: lldb.SBError = process.GetMemoryRegionInfo(address, info)

    if result.Success() and info.IsExecutable():
        return True
    else:
        return False

def dump_expr_error(result: tuple[bool, lldb.SBValue]) -> Optional[lldb.SBValue]:
    if result[0] == False:
        print(result[1].GetError().GetCString())
        return None

    return result[1]
