/* Define c standard operations on floats */
typedef float f32;
typedef double f64;


f64 f64_add(f64 f1, f64 f2) {
    return f1 + f2;
}
f64 f64_subtract(f64 f1, f64 f2) {
    return f1 - f2;
}
f64 f64_negate(f64 f) {
    return -f;
}
f64 f64_multiply(f64 f1, f64 f2) {
    return f1 * f2;
}
f64 f64_divide(f64 f1, f64 f2) {
    return f1 / f2;
}

f32 f32_add(f32 f1, f32 f2) {
    return f1 + f2;
}
f32 f32_subtract(f32 f1, f32 f2) {
    return f1 - f2;
}
f32 f32_negate(f32 f) {
    return -f;
}
f32 f32_multiply(f32 f1, f32 f2) {
    return f1 * f2;
}
f32 f32_divide(f32 f1, f32 f2) {
    return f1 / f2;
}