#ifndef RELEASE_INTERPOSER_C
#define RELEASE_INTERPOSER_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "release_override.c"

//https://github.com/apple/swift/blob/05a5bc40238f7dee9aca90b5e10437f631a7e438/include/swift/Runtime/InstrumentsSupport.h#L41
void *_swift_release;
#endif /*LLDB_EXPR_ENV*/

#ifndef LLDB_EXPR_ENV
void interposer() {
#endif /*LLDB_EXPR_ENV*/
    __lldbscript__original_swift_release = (void (*)(void *))_swift_release;
    _swift_release = (void *)&__lldbscript__new_release;
#ifndef LLDB_EXPR_ENV
}
#endif /*LLDB_EXPR_ENV*/

#endif /*RELEASE_INTERPOSER_C*/
