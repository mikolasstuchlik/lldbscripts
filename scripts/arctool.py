# https://github.com/apple/swift/blob/main/include/swift/Runtime/InstrumentsSupport.h
import lldb
import os
import argparse
import shlex
from typing import Any, Optional, Union
from utilities.for_lldb import dump_expr_error
from utilities.for_c import evaluate_c_expression
from utilities.cloader import CFiles, load_c_file

class ArcTool:
    key: str = "ArcToolContext"

    def __init__(self):
        self.context_initialized: bool = False
        self.breakpoint: Optional[lldb.SBBreakpoint] = None
    
    def lazy_initialize_context(self, frame: lldb.SBFrame):
        if self.context_initialized == True:
            return
        
        self.context_initialized = True
        self.__inject_supporting_c_routines(frame)
        self.__inject_arctool_resolution(frame)
        self.__override_swift_retain(frame)
        self.__override_swift_release(frame)
        self.__override_swift_allocObject(frame)
    
    def __inject_arctool_resolution(self, frame: lldb.SBFrame):
        dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.acrtool_resolution), top_level=True))
        dump_expr_error(evaluate_c_expression(frame, "(void)__lldbscript__initialize_buffer();"))

    def __inject_supporting_c_routines(self, frame: lldb.SBFrame):
        dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.printing), top_level=True))
        dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.swift_printing), top_level=True))

    def __override_swift_retain(self, frame: lldb.SBFrame) -> Optional[int]:
        if dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.retain_override), top_level=True)) == None:
            return None
        result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.retain_interpose)))
        if result == None:
            return None
        return result.GetValueAsAddress()

    def __override_swift_release(self, frame: lldb.SBFrame) -> Optional[int]:
        if dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.release_override), top_level=True)) == None:
            return None
        result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.release_interpose)))
        if result == None:
            return None
        return result.GetValueAsAddress()
    
    def __override_swift_allocObject(self, frame: lldb.SBFrame) -> Optional[int]:
        if dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.alloc_override), top_level=True)) == None:
            return None
        result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, load_c_file(CFiles.alloc_interpose)))
        if result == None:
            return None
        return result.GetValueAsAddress()
    
    def monitor(self, frame: lldb.SBFrame, name: str):
        length = len(name)
        expression: str = '(bool)__lldbscript__insert("{name}", {len})'.format(
            name=name,
            len=length
        )
        dump_expr_error(evaluate_c_expression(frame, expression))
    
    def stop_monitoring(self, frame: lldb.SBFrame, name: str):
        length = len(name)
        expression: str = '(void)__lldbscript__remove("{name}", {len})'.format(
            name=name,
            len=length
        )
        dump_expr_error(evaluate_c_expression(frame, expression))
 
    def list(self, frame: lldb.SBFrame):
        dump_expr_error(evaluate_c_expression(frame, "(void)__lldbscript__print_buffer();"))

    def toggle_breakpoint(self, target: lldb.SBTarget, frame: lldb.SBFrame):
        if self.breakpoint == None:
            result: Optional[lldb.SBValue] = dump_expr_error(evaluate_c_expression(frame, "&__lldbscript__breakpoint_slot"))
            if result == None:
                print("Could not create breakpoint")
                return
            self.breakpoint = target.BreakpointCreateByAddress(result.GetValueAsAddress())
            print("Breakpoint set")
            return

        if self.breakpoint.IsEnabled():
            self.breakpoint.SetEnabled(False)
            print("Breakpoint toggled off")
        else:
            self.breakpoint.SetEnabled(True)
            print("Breakpoint toggled on")

    def defragment(self, frame: lldb.SBFrame):
        dump_expr_error(evaluate_c_expression(frame, "(void)__lldbscript__defragment();"))
        

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

    parser: argparse.ArgumentParser = generateOptionParser()
    args = parser.parse_args(shlex.split(command))
    
    tool_instance: ArcTool = lazy_init(dict)

    if args.command == "init":
        tool_instance.lazy_initialize_context(selected_frame)
    elif args.command == "monitor":
        print(args)
        if args.stop_monitoring == True:
            tool_instance.stop_monitoring(selected_frame, args.monitor_name)
        else:
            tool_instance.monitor(selected_frame, args.monitor_name)
    elif args.command == "list":
        tool_instance.list(selected_frame)
    elif args.command == "toggle":
        tool_instance.toggle_breakpoint(target, selected_frame)
    elif args.command == "defragment":
        tool_instance.defragment(selected_frame)
    else:
        pass

def generateOptionParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(usage='arctool [command]')
    subparsers = parser.add_subparsers(title='Available commands', dest='command')

    subparsers.add_parser('init', help='Initializes the arctool. Use when process is running.')

    monitor_parser = subparsers.add_parser('monitor', help='Print events related to a specific type.')
    monitor_parser.add_argument(
        "-n", "--name", 
        type=str, 
        action="store", 
        dest="monitor_name", 
        required=True,
        help="Full name of a type (or it's description)"
        )
    monitor_parser.add_argument(
        '-s', 
        '--stop', 
        action='store_true',
        dest="stop_monitoring",
        help="Stops monitoring this type."
        )

    subparsers.add_parser('list', help='Lists currently observed types')

    subparsers.add_parser('toggle', help='Toggles the breakpoint or on off')

    subparsers.add_parser('defragment', help='Optimizes the resolution buffer.')

    return parser

def __lldb_init_module(
        debugger: lldb.SBDebugger, 
        internal_dict: dict[str, Any]
        ):
    # install script
    helpText: str = generateOptionParser().format_help()
    debugger.HandleCommand(
        'command script add --help "{help}" --function {function} {name}'.format(
            # escape quotes
            # I don't know why, but my spaces are getting trimmed.
            help=helpText.replace(" ", "\xa0").replace('"', '\\"'), 
            function=__name__ + ".arctool",
            name="arctool"
        )
    )
    print("Script `arctool` is installed.")

