import lldb
import os
import re
from typing import Any, Optional, Union
from utilities.for_lldb import pointer_is_in_readwrite_memory, read_qword, read_memory, address_is_in_executable_memory
from utilities.for_swift import get_opaque_summary, get_type_name, get_opaque_summary_suspected_heap_object
from utilities.constants import arm_instruction_size_constant

def report_closure_usage(
        debugger: lldb.SBDebugger, 
        command: str, 
        result: lldb.SBCommandReturnObject, 
        dict: dict[str, Any]
        ):
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    process: lldb.SBProcess = target.GetProcess()
    thread: lldb.SBThread = process.GetSelectedThread()
    selected_frame: lldb.SBFrame = thread.GetSelectedFrame()
    
    is_in_selected_frame: bool = False
    current_closure_base_address: Optional[int] = None
    frames: int = thread.GetNumFrames()
    for frame_index in range(frames):
        frame: lldb.SBFrame = thread.GetFrameAtIndex(frame_index)
        
        if selected_frame == frame:
            is_in_selected_frame = True
        
        if not is_in_selected_frame: 
            continue
        
        if current_closure_base_address == None:
            if frame_symbol_indicates_closure(frame):
                symbol: lldb.SBSymbol = frame.GetSymbol()
                address: lldb.SBAddress = symbol.GetStartAddress()
                if address.IsValid():
                    current_closure_base_address = address.GetLoadAddress(target)
            continue

        search_hit = search_frame_for_closure(target, frame, current_closure_base_address)
        if search_hit == None:
            continue
        
        if search_hit[1] == 0:
            print("Closure: " + hex(search_hit[0]))
            print("Capture: " + "NULL")
        else:
            detail: Optional[str] = get_opaque_summary_suspected_heap_object(target, frame, search_hit[1])
            if detail == None:
                detail = "<unknown entity>"
            
            print("Closure: " + hex(search_hit[0]))
            print("Capture: " + detail + " " + hex(search_hit[1]))

        return

def search_frame_for_closure(target: lldb.SBTarget, frame: lldb.SBFrame, closure_base: int) -> Optional[tuple[int, int]]:
    pcReg: lldb.SBValue = frame.FindRegister("pc")
    pc_reg_address = pcReg.GetValueAsAddress() # invariant: we didn't start in frame 0
    
    symbol: lldb.SBSymbol = frame.GetSymbol()
    symbol_start: lldb.SBAddress = symbol.GetStartAddress()
    if not symbol_start.IsValid():
         return None
    symbol_start_address = symbol_start.GetLoadAddress(target)

    pc_reg_address -= arm_instruction_size_constant

    traced_register = address_represents_branch_reg_instruction(target, pc_reg_address)
    if traced_register == None:
        return None
    pc_reg_address -= arm_instruction_size_constant
    
    while pc_reg_address >= symbol_start_address:
        result = address_loads_to_register_with_sp_offset(target, pc_reg_address, traced_register)
        if result != None:
            return test_suspected_address_for_closure(frame, target, result)
        pc_reg_address -= arm_instruction_size_constant
    
    return None

def test_suspected_address_for_closure(
        frame: lldb.SBFrame,
        target: lldb.SBTarget,
        sp_offset: int) -> Optional[tuple[int, int]]:
    process: lldb.SBProcess = target.GetProcess()
    spReg: lldb.SBValue = frame.FindRegister("sp")
    sp_reg_address = spReg.GetValueAsAddress()

    closure_address = sp_reg_address + sp_offset
    closure_capture_address = sp_reg_address + sp_offset + 8
    
    if not pointer_is_in_readwrite_memory(process, closure_address) or not pointer_is_in_readwrite_memory(process, closure_capture_address):
        return None
    
    closure = read_qword(process, closure_address)
    if closure == None:
        return None
    
    #We can not compare pointer to a specific address, because there might be a tail call in between
    if not address_is_in_executable_memory(process, closure):
        return None
    
    capture = read_qword(process, closure_capture_address)
    if capture == None:
        return None
    
    return (closure, capture)


def address_represents_branch_reg_instruction(target: lldb.SBTarget, addr: int) -> Optional[str]:
    content = read_memory(target.GetProcess(), addr, 4)
    disassembly: lldb.SBInstructionList = target.GetInstructions(lldb.SBAddress(addr, target), content)

    instruction: lldb.SBInstruction = disassembly.GetInstructionAtIndex(0)
    if instruction.IsValid() and instruction.DoesBranch():
        operand: str = instruction.GetOperands(target)
        if re.match("^x\\d+$", operand):
            return operand
    return None

def address_loads_to_register_with_sp_offset(target: lldb.SBTarget, addr: int, reg: str) -> Optional[int]:
    content = read_memory(target.GetProcess(), addr, 4)
    disassembly: lldb.SBInstructionList = target.GetInstructions(lldb.SBAddress(addr, target), content)

    instruction: lldb.SBInstruction = disassembly.GetInstructionAtIndex(0)
    if instruction.IsValid():
        mnemonic: str = instruction.GetMnemonic(target)
        operand: str = instruction.GetOperands(target)

        if mnemonic == "ldr":
            if operand == reg + ", [sp]":
                return 0
            pattern = re.compile("^" + reg + ", \\[sp, \\#0x([0-9a-fA-F]+)\\]$")
            result = pattern.match(operand)
            if result:
                return int(result.group(1), base=16)
    return None

def is_address_entry_point_to_known_closure(target: lldb.SBTarget, address: int) -> bool:
    bound_address: lldb.SBAddress = lldb.SBAddress(address, target)
    symbol_context: lldb.SBSymbolContext = target.ResolveSymbolContextForAddress(bound_address, lldb.eSymbolContextEverything)
    if symbol_context.IsValid():
        if not symbol_name_indicates_closure(symbol_context.GetSymbol().GetName()):
            return False
        if symbol_context.GetSymbol().GetStartAddress().GetLoadAddress(target) == address:
            return True
    return False

def frame_symbol_indicates_closure(frame: lldb.SBFrame) -> bool:
    name: str = frame.GetSymbol().GetName()
    return symbol_name_indicates_closure(name)

def symbol_name_indicates_closure(name: str) -> bool:
    if re.match("^closure #\\d+ .*$", name) == None:
        return False
    else:
        return True

def __lldb_init_module(
        debugger: lldb.SBDebugger, 
        internal_dict: dict[str, Any]
        ):
    debugger.HandleCommand("command script add -f " + __name__ + ".report_closure_usage closuresearch")
    print("Script `closuresearch` is installed.")
