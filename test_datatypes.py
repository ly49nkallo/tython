import tython_compiler as tc
from tython_compiler.interpreter import *
print(i1 := Integer32(0))
print(i2 := Integer32(0xFFFFFFFF))
print(i1 + i2)
print(i3 := Integer64(0))
print(i4 := Integer64(0xFFFFFFFFFF))
print(i3 + i4)
print(i2 + i4)

