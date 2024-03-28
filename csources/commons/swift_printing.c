#ifndef SWIFT_PRINTING_C
#define SWIFT_PRINTING_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "printing.c"
#include "lldb_null.h"

// https://github.com/apple/swift/blob/fc6011c1803dbd539561e7f96ed02210ebb1ce7f/include/swift/Runtime/InstrumentsSupport.h#L47
size_t swift_retainCount(void *);

// https://github.com/apple/swift/blob/fc6011c1803dbd539561e7f96ed02210ebb1ce7f/stdlib/public/runtime/ReflectionMirror.cpp#L1072
char * swift_OpaqueSummary(void *);

// https://github.com/apple/swift/blob/fc6011c1803dbd539561e7f96ed02210ebb1ce7f/stdlib/public/runtime/Casting.cpp#L179
char * swift_getTypeName(void *, bool);
#endif /*LLDB_EXPR_ENV*/

void __lldbscript__MetadataName(void * metadata) { 
    if (metadata != NULL) { 
        char * result = NULL;
        result = (char *)swift_OpaqueSummary(metadata); 
        if (result != NULL) {
            (int)printf("%s\n", result);
            return;
        }
        result = (char *)swift_getTypeName(metadata, true); 
        if (result != NULL) {
            (int)printf("%s\n", result);
            return;
        }
        (int)printf("<no description>\n");
    }
}

void __lldbscript__PrintRetainCount(void * ptr, const char * prefix, uint32_t prefix_len) {
    if (ptr == NULL) {
        (void)__lldbscript__PutStr(prefix, prefix_len);
        (void)__lldbscript__PutStr("NULL\n", 5);
    } else {
        uint64_t retains = (size_t)swift_retainCount(ptr);
        (void)__lldbscript__PutStr(prefix, prefix_len);
        (void)__lldbscript__PutPtr(ptr);
        (void)__lldbscript__PutStr(" retains(", 9);
        (void)__lldbscript__PutUnsignedDecimal(retains);
        (void)__lldbscript__PutStr(")\n", 2);
    }
}

#endif /*SWIFT_PRINTING_C*/
