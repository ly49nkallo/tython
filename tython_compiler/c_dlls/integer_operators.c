/* Define c standard operations on integers */
#include "inttypes.h"
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;

i64 i64_add(i64 i1, i64 i2) {
    return i1 + i2;
}
i64 i64_subtract(i64 i1, i64 i2) {
    return i1 - i2;
}
i64 i64_negate(i64 i) {
    return -i;
}
i64 i64_multiply(i64 i1, i64 i2) {
    return i1 * i2;
}
i64 i64_divide(i64 i1, i64 i2) {
    return i1 / i2;
}

i32 i32_add(i32 i1, i32 i2) {
    return i1 + i2;
}
i32 i32_subtract(i32 i1, i32 i2) {
    return i1 - i2;
}
i32 i32_negate(i32 i) {
    return -i;
}
i32 i32_multiply(i32 i1, i32 i2) {
    return i1 * i2;
}
i32 i32_divide(i32 i1, i32 i2) {
    return i1 / i2;
}

i16 i16_add(i16 i1, i16 i2) {
    return i1 + i2;
}
i16 i16_subtract(i16 i1, i16 i2) {
    return i1 - i2;
}
i16 i16_negate(i16 i) {
    return -i;
}
i16 i16_multiply(i16 i1, i16 i2) {
    return i1 * i2;
}
i16 i16_divide(i16 i1, i16 i2) {
    return i1 / i2;
}