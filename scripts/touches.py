import lldb
import os
from typing import Any

def add_touches_began_breakpoint(debugger: lldb.SBDebugger, command: str, result: lldb.SBCommandReturnObject, dict: dict[str, Any]):
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    breakpoint: lldb.SBBreakpoint = target.BreakpointCreateByName("-[UIResponder touchesBegan:withEvent:]")
    breakpoint.SetScriptCallbackFunction(__name__ + ".touches_began_callback")
    breakpoint.SetOneShot(False)

def touches_began_callback(frame: lldb.SBFrame, bp_loc: lldb.SBBreakpointLocation, dict: dict[str, Any]) -> bool:
    value: lldb.SBValue = frame.EvaluateExpression("(id)$arg1")
    print(value.GetValue(), value.GetObjectDescription())
    return False

def __lldb_init_module(debugger: lldb.SBDebugger, dict: dict[str, Any]):
    debugger.HandleCommand("command script add -f " + __name__ + ".add_touches_began_breakpoint touch")
    print("Script `touch` is installed.")
