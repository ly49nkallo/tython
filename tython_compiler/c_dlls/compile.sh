#!/bin/bash
gcc -fPIC -shared -o integer_operators.so integer_operators.c -O3
gcc -fPIC -shared -o float_operators.so float_operators.c -O3
