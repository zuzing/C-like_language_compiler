---
A compiler for a C-like language that supports code execution and printing of the program's abstract syntax tree (AST).


---
Example programs that the compiler can execute:

```C
for n = 2:100 {
    p = 1;
    for d = 2:n-1 {
        nc = n;
        while (nc > 0) nc -= d;
        if (nc == 0) {
            p = 0;
            break;
        }
    }
    if (p == 1) {
        print n;
    }
}
```

```C
A = eye(3);
B = ones(3);
C = A .+ B;
print C;

D = zeros(3, 4);
D[0, 0] = 42;
print D;
print D[2, 2];
```

More examples in ./tests/test_data/interpreter_example

Specific syntax is specified in Parser.py
