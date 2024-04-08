import lldb
import os
from typing import List, Dict, Any

def add_touches_began_breakpoint(debugger: lldb.SBDebugger, command: str, result: lldb.SBCommandReturnObject, dict: Dict[str, Any]):
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    breakpoint: lldb.SBBreakpoint = target.BreakpointCreateByName("-[UIResponder touchesBegan:withEvent:]")
    breakpoint.SetScriptCallbackFunction(__name__ + ".touches_began_callback")
    breakpoint.SetOneShot(False)

def touches_began_callback(frame: lldb.SBFrame, bp_loc: lldb.SBBreakpointLocation, dict: Dict[str, Any]) -> bool:
    value: lldb.SBValue = frame.EvaluateExpression("(id)$arg1")
    print(value.GetValue(), value.GetObjectDescription())
    return False

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f " + __name__ + ".add_touches_began_breakpoint touch")
    print("Script `touch` is installed.")
