from typing import Optional
import lldb

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
    
def read_c_string(target: lldb.SBTarget, base: int) -> Optional[str]:
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

def locate_swift_API_functin_in_binary(target: lldb.SBTarget, name: str) -> Optional[int]:
    matches: lldb.SBSymbolContextList = target.FindGlobalFunctions(name, 0, lldb.eMatchTypeRegex)
    if not matches.IsValid():
        return None
    
    context: lldb.SBSymbolContext
    for context in matches:
        module: lldb.SBModule = context.GetModule()
        module_name: str = module.GetFileSpec().GetFilename()
        if module_name.endswith("libswiftCore.dylib"):
            return context.symbol.addr.GetLoadAddress(target)

    return None

def address_is_in_executable_memory(process: lldb.SBProcess, address: int) -> bool:
    info = lldb.SBMemoryRegionInfo()
    result: lldb.SBError = process.GetMemoryRegionInfo(address, info)

    if result.Success() and info.IsExecutable():
        return True
    else:
        return False

def evaluate_c_expression(frame: lldb.SBFrame, expression: str, top_level: bool = False) -> tuple[bool, lldb.SBValue]:
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeC)
    options.SetGenerateDebugInfo(True)
    if top_level == True:
        options.SetTopLevel(True)
    summary_result: lldb.SBValue = frame.EvaluateExpression(expression, options)
    success: bool = True
    error: lldb.SBError = summary_result.GetError()
    # https://discourse.llvm.org/t/lldb-expressions-unknown-error-is-returned-upon-successful-evaluation/78012
    if not error.Success() and error.GetCString() != "unknown error":
        success = False
    return (success, summary_result)

def dump_expr_error(result: tuple[bool, lldb.SBValue]) -> Optional[lldb.SBValue]:
    if result[0] == False:
        print(result[1].GetError().GetCString())
        return None

    return result[1]