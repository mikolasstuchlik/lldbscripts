from typing import Optional, Any
from utilities.for_swift import get_opaque_summary_suspected_heap_object
from utilities.commons import str_to_i
import lldb
import argparse
import shlex

def describe_heap_object(
        debugger: lldb.SBDebugger, 
        command: str, 
        result: lldb.SBCommandReturnObject, 
        dict: dict[str, Any]):
    target: lldb.SBTarget = debugger.GetSelectedTarget()
    process: lldb.SBProcess = target.GetProcess()
    thread: lldb.SBThread = process.GetSelectedThread()
    selected_frame: lldb.SBFrame = thread.GetSelectedFrame()

    args: list[str] = shlex.split(command)

    for address in args:
        try:
            int_address = str_to_i(address)
            if (summary := get_opaque_summary_suspected_heap_object(target, selected_frame, int_address)) != None:
                print(summary)
            else:
                print("<No summary>")
        except:
            print("Address " + address + " is not a valid input")

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        'command script add --help "{help}" --function {function} {name}'.format(
            # escape quotes
            # I don't know why, but my spaces are getting trimmed.
            help="Describes raw HeapObject", 
            function=__name__ + ".describe_heap_object",
            name="heapobject"
        )
    )
    print("Script `heapobject` is installed.")

