#ifndef RETAIN_INTERPOSER_C
#define RETAIN_INTERPOSER_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "retain_override.c"

//https://github.com/apple/swift/blob/05a5bc40238f7dee9aca90b5e10437f631a7e438/include/swift/Runtime/InstrumentsSupport.h#L35
void *_swift_retain;
//https://github.com/apple/swift/blob/07eb52a80dee5a196fc7ad573aacc63c62434fc9/include/swift/Runtime/InstrumentsSupport.h#L37
void *_swift_retain_n;
//HeapObject *(*SWIFT_RT_DECLARE_ENTRY _swift_tryRetain)(HeapObject *object);
void *_swift_tryRetain;
#endif /*LLDB_EXPR_ENV*/

#ifndef LLDB_EXPR_ENV
void interposer() {
#endif /*LLDB_EXPR_ENV*/
    __lldbscript__original_swift_retain = (void *(*)(void *))_swift_retain;
    _swift_retain = (void *)&__lldbscript__new_retain;

    __lldbscript__original_swift_retain_n = (void *(*)(void *, uint32_t))_swift_retain_n;
    _swift_retain_n = (void *)&__lldbscript__new_retain_n;

    __lldbscript__original_swift_tryRetain = (void *(*)(void *))_swift_tryRetain;
    _swift_tryRetain = (void *)&__lldbscript__new_tryRetain;
#ifndef LLDB_EXPR_ENV
}
#endif /*LLDB_EXPR_ENV*/

#endif /*RETAIN_INTERPOSER_C*/
