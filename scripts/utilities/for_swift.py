from typing import Optional
import lldb
from utilities.for_lldb import dump_expr_error, read_null_terminated_string, pointer_is_in_readwrite_memory
from utilities.for_c import evaluate_c_expression
from utilities.constants import null_constant

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

def get_opaque_summary(target: lldb.SBTarget, frame: lldb.SBFrame, heap_object: int) -> Optional[str]:
    expression: str = '(char *)swift_OpaqueSummary(*(void **){heapobject})'.format(
        heapobject=hex(heap_object)
    )
    summary_result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, expression))
    if summary_result != None and summary_result.GetValueAsAddress() != null_constant:
        return read_null_terminated_string(target, summary_result.GetValueAsAddress())

def get_type_name(target: lldb.SBTarget, frame: lldb.SBFrame, heap_object: int) -> Optional[str]:
    expression: str = '(char *)swift_getTypeName(*(void **){heapobject}, 1)'.format(
        heapobject=hex(heap_object)
    )
    summary_result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, expression))
    if summary_result != None and summary_result.GetValueAsAddress() != null_constant:
        return read_null_terminated_string(target, summary_result.GetValueAsAddress())

def get_opaque_summary_suspected_heap_object(target: lldb.SBTarget, frame: lldb.SBFrame, heap_object: int) -> Optional[str]:
    process: lldb.SBProcess = target.GetProcess()
    if not pointer_is_in_readwrite_memory(process, heap_object):
        return None

    opaque_summary: Optional[str] = get_opaque_summary(target, frame, heap_object)
    if opaque_summary != None:
        return opaque_summary
    
    type_name: Optional[str] = get_type_name(target, frame, heap_object)
    if type_name != None:
        return type_name

    return None
