# Programming in Lua - Chapter 1: Getting Started

*From the first edition of "Programming in Lua" by Roberto Ierusalimschy*
*Note: This is for Lua 5.0. Fourth edition available targeting Lua 5.3*

## Introduction

Lua is a simple programming language that's easy to learn and use. This chapter introduces basic Lua programming through two example programs.

## Example 1: Hello World

The simplest Lua program:

```lua
print("Hello World")
```

To run this program:
1. Save it as `hello.lua`
2. Run with: `lua hello.lua`

## Example 2: Factorial Function

A more complex program that calculates factorials:

```lua
-- defines a factorial function
function fact (n)
    if n == 0 then
        return 1
    else
        return n * fact(n-1)
    end
end

print("enter a number:")
a = io.read("*number")        -- read a number
print(fact(a))
```

This program demonstrates:
- Function definition with `function`
- Conditional logic with `if-then-else`
- Recursion
- User input with `io.read()`
- Comments with `--`

## Running Lua Programs

For beginners, use the stand-alone Lua interpreter:
- Save your program to a file (e.g., `program.lua`)
- Run with: `lua program.lua`

## Key Takeaways

- Lua syntax is clean and readable
- Functions are defined with the `function` keyword
- Comments begin with `--`
- The `print()` function outputs to the console
- `io.read()` can read user input

*Source: https://www.lua.org/pil/1.html*