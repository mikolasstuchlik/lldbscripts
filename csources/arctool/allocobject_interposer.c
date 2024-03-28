#ifndef ALLOCOBJECT_INTERPOSER_C
#define ALLOCOBJECT_INTERPOSER_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>

#include "allocobject_override.c"

//https://github.com/apple/swift/blob/05a5bc40238f7dee9aca90b5e10437f631a7e438/include/swift/Runtime/InstrumentsSupport.h#L30
void * _swift_allocObject;
#endif /*LLDB_EXPR_ENV*/

#ifndef LLDB_EXPR_ENV
void interposer() {
#endif /*LLDB_EXPR_ENV*/
    __lldbscript__original_swift_allocObject = (void *(*)(void *, size_t, size_t))_swift_allocObject;
    _swift_allocObject = (void *)&__lldbscript__new_swift_allocObject;
#ifndef LLDB_EXPR_ENV
}
#endif /*LLDB_EXPR_ENV*/

#endif /*ALLOCOBJECT_INTERPOSER_C*/
