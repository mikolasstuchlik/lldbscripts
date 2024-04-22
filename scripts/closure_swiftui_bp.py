import lldb
import os
from typing import Optional, Any

def add_closure_bp(
        debugger: lldb.SBDebugger, 
        command: str, 
        result: lldb.SBCommandReturnObject, 
        dict: dict[str, Any]
        ):
    execution_context_name: str = "closurebp_ctx"

    try:
        bp: Optional[lldb.SBBreakpoint] = dict[execution_context_name]
        if bp == None:
            print("Error")
        elif bp.IsEnabled():
            print("Disabled")
            bp.SetEnabled(False)
        else: 
            print("Enabled")
            bp.SetEnabled(True)
    except:
        target: lldb.SBTarget = debugger.GetSelectedTarget()
        executable: lldb.SBFileSpec = target.GetExecutable()
        filename: str = executable.GetFilename()
        breakpoint: lldb.SBBreakpoint = target.BreakpointCreateByRegex("closure", filename)
        breakpoint.SetScriptCallbackFunction(__name__ + ".closure_bp_callabck")
        breakpoint.SetOneShot(False)

        print("Initialized")
        dict[execution_context_name] = breakpoint
    

def closure_bp_callabck(
        frame: lldb.SBFrame, 
        bp_loc: lldb.SBBreakpointLocation, 
        dict: dict[str, Any]
        ) -> bool:
    thread: lldb.SBThread = frame.GetThread()
    if not thread.IsValid():
        return False
    
    frames: int = thread.GetNumFrames()
    for frame_index in range(frames):
        iframe: lldb.SBFrame = thread.GetFrameAtIndex(frame_index)
        func_name: Optional[str] = iframe.GetDisplayFunctionName()
        
        if func_name != None and "Gesture" in func_name:
            return True

    return False

def __lldb_init_module(
        debugger: lldb.SBDebugger, 
        dict: dict[str, Any]
        ):
    debugger.HandleCommand("command script add -f " + __name__ + ".add_closure_bp closurebp")
    print("Script `closurebp` is installed.")
