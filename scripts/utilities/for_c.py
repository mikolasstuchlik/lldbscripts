from typing import Optional
import lldb

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
