# https://github.com/apple/swift/blob/main/include/swift/Runtime/InstrumentsSupport.h

import lldb
import os
import re
from typing import Any, Optional, Union
from commons import evaluate_c_expression, dump_expr_error
from csources import cloader

multiline_litera__expr__release_code: str = """
void (*__lldbscript__original_swift_release)(void *); 

void __lldbscript__new_release(void * ptr) {
    (void)__lldbscript__print_retain_count(ptr, "will release: ", 14);
    __lldbscript__original_swift_release(ptr); 
}

"""

multiline_litera__expr__release_interpose: str = """
__lldbscript__original_swift_release = (void (*)(void *))_swift_release;
_swift_release = (void *)&__lldbscript__new_release;

"""

multiline_litera__expr__retain_code: str = """
void *(*__lldbscript__original_swift_retain)(void *); 

void *__lldbscript__new_retain(void * ptr) { 
    (void)__lldbscript__print_retain_count(ptr, "will retain: ", 13);
    return __lldbscript__original_swift_retain(ptr); 
}

"""

multiline_litera__expr__retain_interpose: str = """
__lldbscript__original_swift_retain = (void *(*)(void *))_swift_retain;
_swift_retain = (void *)&__lldbscript__new_retain;

"""

multiline_litera__expr__allocObject_code: str = """
void * (*__lldbscript__original_swift_allocObject)(void *, size_t, size_t); 

void * __lldbscript__new_swift_allocObject(void * heap_metadata, size_t size, size_t alignment) {
    void * new_alloc = __lldbscript__original_swift_allocObject(heap_metadata, size, alignment);
    (void)__lldbscript__metadata_name(heap_metadata);
    (void)__lldbscript__putstr("Did allocate ptr: ", 18);
    (void)__lldbscript__putp(new_alloc);
    (void)__lldbscript__putstr("\\n", 1);
    return new_alloc;
}

"""

multiline_litera__expr__allocObject_interpose: str = """
__lldbscript__original_swift_allocObject = (void *(*)(void *, size_t, size_t))_swift_allocObject;
_swift_allocObject = (void *)&__lldbscript__new_swift_allocObject;

"""

def make_breakpoint(frame: lldb.SBFrame, address: int):
    thread: lldb.SBThread = frame.GetThread()
    process: lldb.SBProcess = thread.GetProcess() 
    target: lldb.SBTarget = process.GetTarget()
    target.GetDebugger().HandleCommand(f"breakpoint set -a {hex(address)}")

class ArcTool:
    key: str = "ArcToolContext"

    def __init__(self):
        self.context_initialized: bool = False
    
    def lazy_initialize_context(self, frame: lldb.SBFrame):
        if self.context_initialized == True:
            return
        
        self.context_initialized = True
        self.__inject_supporting_c_routines(frame)
        self.__override_swift_retain(frame)
        self.__override_swift_release(frame)
        self.__override_swift_allocObject(frame)
    
    def __inject_supporting_c_routines(self, frame: lldb.SBFrame):
        dump_expr_error(evaluate_c_expression(frame, cloader.load_c_file(cloader.CFiles.printing), top_level=True))
        dump_expr_error(evaluate_c_expression(frame, cloader.load_c_file(cloader.CFiles.swift_printing), top_level=True))

    def __override_swift_retain(self, frame: lldb.SBFrame) -> Optional[int]:
        if dump_expr_error(evaluate_c_expression(frame, multiline_litera__expr__retain_code, top_level=True)) == None:
            return None
        result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, multiline_litera__expr__retain_interpose))
        if result == None:
            return None
        return result.GetValueAsAddress()

    def __override_swift_release(self, frame: lldb.SBFrame) -> Optional[int]:
        if dump_expr_error(evaluate_c_expression(frame, multiline_litera__expr__release_code, top_level=True)) == None:
            return None
        result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, multiline_litera__expr__release_interpose))
        if result == None:
            return None
        return result.GetValueAsAddress()
    
    def __override_swift_allocObject(self, frame: lldb.SBFrame) -> Optional[int]:
        if dump_expr_error(evaluate_c_expression(frame, multiline_litera__expr__allocObject_code, top_level=True)) == None:
            return None
        result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, multiline_litera__expr__allocObject_interpose))
        if result == None:
            return None
        return result.GetValueAsAddress()

def lazy_init(context: dict[str, Any]) -> ArcTool:
    def initializeNew() -> ArcTool:
        newInstace = ArcTool()
        context[ArcTool.key] = newInstace
        print("ARCTool initialized")
        return newInstace

    try:
        value: Any = context[ArcTool.key]
        if type(value) == ArcTool:
            return value
        else:
            return initializeNew()
    except:
        return initializeNew()

def arctool(
        debugger: lldb.SBDebugger, 
        command: str, 
        result: lldb.SBCommandReturnObject, 
        dict: dict[str, Any]
        ):
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    process: lldb.SBProcess = target.GetProcess()
    thread: lldb.SBThread = process.GetSelectedThread()
    selected_frame: lldb.SBFrame = thread.GetSelectedFrame()

    tool_instance: ArcTool = lazy_init(dict)
    tool_instance.lazy_initialize_context(selected_frame)
    return

def __lldb_init_module(
        debugger: lldb.SBDebugger, 
        internal_dict: dict[str, Any]
        ):
    # install script
    debugger.HandleCommand("command script add -f " + __name__ + ".arctool arctool")
    print("Script `arctool` is installed.")

    # create dummy breakpoint which will install arctool
    debugger.HandleCommand("breakpoint set -n main -C arctool -C c") # make onetime
