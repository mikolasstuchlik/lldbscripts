import lldb
import os
import re
from typing import Any, Optional, Union
from commons import evaluate_c_expression

class ArcTool:
    key: str = "ArcToolContext"

    def __init__(self):
        self.context_initialized: bool = False
    
    def lazy_initialize_context(self, frame: lldb.SBFrame):
        if self.context_initialized == True:
            return
        
        self.context_initialized = True
        #self.__override_swift_release(frame)
        print(self.__override_swift_allocObject(frame))
    
    def __override_swift_release(self, frame: lldb.SBFrame) -> int:
        expression: str = """
void (*__lldbscript__original_swift_release)(void *); 

void * last_destroyed;

void __lldbscript__new_release(void * ptr) { 
    if (ptr != 0) { 
        char * res = (char *)swift_getTypeName(*(void **)ptr, true); 
        if (res != 0) {
            (int)printf("%s\n", res);
        }
    }
    (int)printf("%p %p\\n", ptr, last_destroyed);
    last_destroyed = ptr;
    __lldbscript__original_swift_release(ptr); 
}

"""
        evaluate_c_expression(frame, expression, top_level=True)

        expression: str = """
__lldbscript__original_swift_release = (void (*)(void *))_swift_release;
_swift_release = (void *)&__lldbscript__new_release;

"""
        return evaluate_c_expression(frame, expression).GetValueAsAddress()
    


    def __override_swift_allocObject(self, frame: lldb.SBFrame) -> int:
        expression: str = """
void * (*__lldbscript__original_swift_allocObject)(void *, size_t, size_t); 

void * __lldbscript__new_swift_allocObject(void * heap_metadata, size_t size, size_t alignment) {
    if (heap_metadata != 0) { 
        char * res = (char *)swift_getTypeName(heap_metadata, true); 
        if (res != 0) {
            (int)printf("%s\\n", res);
        }
        res = (char *)swift_OpaqueSummary(heap_metadata); 
        if (res != 0) {
            (int)printf("%s\\n", res);
        }
    }
    return __lldbscript__original_swift_allocObject(heap_metadata, size, alignment); 
}

"""
        print(evaluate_c_expression(frame, expression, top_level=True))

        expression: str = """
__lldbscript__original_swift_allocObject = (void *(*)(void *, size_t, size_t))_swift_allocObject;
_swift_allocObject = (void *)&__lldbscript__new_swift_allocObject;

"""
        return evaluate_c_expression(frame, expression).GetValueAsAddress()

#  (int)printf("%s\n", (char *)swift_getTypeName(heap_metadata, true));
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
    debugger.HandleCommand("command script add -f " + __name__ + ".arctool arctool")
    print("Retain script loaded")
