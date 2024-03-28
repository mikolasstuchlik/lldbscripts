#ifndef RETAIN_INTERPOSER_C
#define RETAIN_INTERPOSER_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "retain_override.c"

//https://github.com/apple/swift/blob/05a5bc40238f7dee9aca90b5e10437f631a7e438/include/swift/Runtime/InstrumentsSupport.h#L35
void *_swift_retain;
#endif /*LLDB_EXPR_ENV*/

#ifndef LLDB_EXPR_ENV
void interposer() {
#endif /*LLDB_EXPR_ENV*/
    __lldbscript__original_swift_retain = (void *(*)(void *))_swift_retain;
    _swift_retain = (void *)&__lldbscript__new_retain;
#ifndef LLDB_EXPR_ENV
}
#endif /*LLDB_EXPR_ENV*/

#endif /*RETAIN_INTERPOSER_C*/
