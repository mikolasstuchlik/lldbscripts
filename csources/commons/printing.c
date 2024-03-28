#ifndef PRINTING_C
#define PRINTING_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "lldb_null.h"
#endif /*LLDB_EXPR_ENV*/

void __lldbscript__PutStr(const char * str, uint32_t len) {
    for(uint32_t i = 0; i < len; i++) {
        (int)putchar((int)str[i]);
    }
}

void __lldbscript__PutUnsignedX(uint64_t number, uint8_t bytes) {
    uint64_t buffer;
    for(uint8_t i = 0; i < bytes * 2; i++) {
        buffer = number >> (4 * (bytes * 2 - i));
        buffer = buffer & 0b1111;
        switch(buffer) {
        case 0x0: (int)putchar('0'); break;
        case 0x1: (int)putchar('1'); break;
        case 0x2: (int)putchar('2'); break;
        case 0x3: (int)putchar('3'); break;
        case 0x4: (int)putchar('4'); break;
        case 0x5: (int)putchar('5'); break;
        case 0x6: (int)putchar('6'); break;
        case 0x7: (int)putchar('7'); break;
        case 0x8: (int)putchar('8'); break;
        case 0x9: (int)putchar('9'); break;
        case 0xa: (int)putchar('a'); break;
        case 0xb: (int)putchar('b'); break;
        case 0xc: (int)putchar('c'); break;
        case 0xd: (int)putchar('d'); break;
        case 0xe: (int)putchar('e'); break;
        case 0xf: (int)putchar('f'); break;
        }
    }
}

void __lldbscript__PutUnsignedDecimal(uint64_t number) {
    uint64_t digit = number % 10;
    uint64_t next = number / 10;
    if (next > 0) {
        (void)__lldbscript__PutUnsignedDecimal(next);
    }
    switch (digit) {
    case 0x0: (int)putchar('0'); break;
    case 0x1: (int)putchar('1'); break;
    case 0x2: (int)putchar('2'); break;
    case 0x3: (int)putchar('3'); break;
    case 0x4: (int)putchar('4'); break;
    case 0x5: (int)putchar('5'); break;
    case 0x6: (int)putchar('6'); break;
    case 0x7: (int)putchar('7'); break;
    case 0x8: (int)putchar('8'); break;
    case 0x9: (int)putchar('9'); break;
    case 0xa: (int)putchar('1'); (int)putchar('0'); break;
    }
}

void __lldbscript__PutPtr(void * ptr) {
    __lldbscript__PutStr("0x", 2);
    __lldbscript__PutUnsignedX((uint64_t)ptr, 8);
}

#endif /*PRINTING_C*/
