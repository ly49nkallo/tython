# TYTHON Compiler/interpreter

Compiled language. Simple. Fast. Democratic.

Rules:

1. The ZEN of Tython : LESS FEATURES >> READABILITY & LINE COUNT!
2. Variables are one letter and, optionally, one number. (e.g. X, A0, Y1)
   1. This means there are 2 \* 26 \* 11 = 572 unique variable names, choose wisely!
3. All variables have an implicit type.
   1. Types include:
      1. INT (32 bit integer) (INT32, INT64, INT128)
      2. REAL (32 bit float) (REAL32, REAL64)
      3. CHAR (8 bit integer)
   2. Variables I, J, K, L, M, N, are INTEGERS. Otherwise, it is REAL.
   3. If these do not work for you, you can specify the type EXPLICITLY or use the implicit keyword to remap the implicit types for the program
   4. There is no boolean type, just integers!
   5. Any variable prefixed with an _ is automatically an vector
   6. An array is homogeneous in type
   7. Strings are represented as arrays or characters
   8. Lists are indexed with _square brackets_ (unlike TI-83/4)
4. There are litterally **no loops**; but there are GOTO statements!
5. No functions! Only Programs and labels! You can envoke a label with a goto statement or execute a program
   1. The compiler will check for circular executions, don't even try. The callstack is also limited to 100. **Any and all recursion is strictly prohibited!!!**
6. The langauge will not depend on any way choice of code format besides newlines.
   1. If statements are paired with an 'end' keyword
7. THE STATE OF VARIABLES PERSISTS ACROSS ENVOKED PROGRAM EXECUTIONS!
   1. Tython refuses to align with either functional or object oriented programming techniques!
8. 

Ex.

``` tython1
# Comment
program "squareroot" #name of program. Must match the filename.

# x = (-b +- sqrt(b**2 - 4*a*c)) / 2a
prompt a #Prompt a
prompt b #Prompt b
prompt c #Prompt c

v = sqrt(b**2 - 4*a*c)
o1 = (-b + v) / (2*a)
o2 = (-b - v) / (2*a)

disp "x1=", o1 #Display o2 in terminal
disp "x2=", o2 #Display o3 in terminal
```

``` tython1
# A simple bank system
# @RESERVED i, B
program "bank"
version 1 2 3

lbl M
disp "1. View balance"
disp "2. Withdraw"
disp "3. Deposit"

prompt i #Prompt selection
if i=1 then
goto M1
if i=2 then
goto M2
if i=3 then
goto M3

lbl M1
INT32 B
disp "Your current balance is " B/100 "." B%100
goto M

lbl M2
INT32 D
disp "How much do you want to deposit?"
prompt D
B = B + D
goto M

lbl M3
INT32 D
disp "How much do you want to withdraw?"
prompt D
B = B - D
goto M

```

```tython1
# program to compute fibonacii sequence
program "fibonacii_sequence"

INT32 @I
dim(I) = 20
@I[0] = 1
@I[1] = 1
i = 2
lbl A
@I[i] = @I[i-1] + @I[i-2]
i = i + 1
if i < 20 then
goto A

```
