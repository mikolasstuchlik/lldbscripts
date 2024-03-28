#ifndef RELEASE_INTERPOSER_C
#define RELEASE_INTERPOSER_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "release_override.c"

//https://github.com/apple/swift/blob/05a5bc40238f7dee9aca90b5e10437f631a7e438/include/swift/Runtime/InstrumentsSupport.h#L41
void *_swift_release;

//https://github.com/apple/swift/blob/07eb52a80dee5a196fc7ad573aacc63c62434fc9/include/swift/Runtime/InstrumentsSupport.h#L43C31-L43C47
void *_swift_release_n;
#endif /*LLDB_EXPR_ENV*/

#ifndef LLDB_EXPR_ENV
void interposer() {
#endif /*LLDB_EXPR_ENV*/
    __lldbscript__original_swift_release = (void (*)(void *))_swift_release;
    _swift_release = (void *)&__lldbscript__new_release;

    __lldbscript__original_swift_release_n = (void (*)(void *, uint32_t))_swift_release_n;
    _swift_release_n = (void *)&__lldbscript__new_release_n;
#ifndef LLDB_EXPR_ENV
}
#endif /*LLDB_EXPR_ENV*/

#endif /*RELEASE_INTERPOSER_C*/
