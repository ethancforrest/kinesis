# Programming in Lua - Chapter 2: Types and Values

*From the first edition of "Programming in Lua" by Roberto Ierusalimschy*

## Lua's Type System

Lua is a **dynamically typed** programming language. This means:
- Variables have no predefined types
- Any variable may contain values of any type
- Types are associated with values, not variables

## The Eight Basic Types

Lua has eight basic types:

1. **nil** - represents the absence of a value
2. **boolean** - true or false
3. **number** - represents real (double-precision floating-point) numbers
4. **string** - sequence of characters
5. **userdata** - allows arbitrary C data to be stored in Lua variables
6. **function** - functions are first-class values
7. **thread** - represents independent threads of execution (coroutines)
8. **table** - implements arrays, sets, records, and more

## Key Characteristics

### Functions as First-Class Values
Functions can be:
- Assigned to variables
- Passed as arguments to other functions
- Returned as results from functions
- Stored in data structures

### Dynamic Typing
```lua
-- The same variable can hold different types
x = 10        -- x is a number
x = "hello"   -- now x is a string
x = nil       -- now x is nil
```

## The type() Function

Use `type()` to determine the type of a value at runtime:

```lua
print(type("Hello world"))   --> string
print(type(10.4*3))         --> number
print(type(print))          --> function
print(type(type))           --> function
print(type(true))           --> boolean
print(type(nil))            --> nil
print(type(type(X)))        --> string
```

## Practical Considerations

### Flexibility vs. Structure
- Dynamic typing provides flexibility
- Can sometimes lead to messy code if not used carefully
- Useful for indicating exceptional conditions with `nil`

### nil as a Special Value
- `nil` is often used to represent "no value" or exceptional conditions
- Different from other "empty" values like empty strings or zero

## Programming Style Tips

While Lua's flexible typing system allows for creative solutions, it's important to:
- Use consistent patterns in your code
- Document expected types in comments
- Use `nil` meaningfully to represent absence of values

*Source: https://www.lua.org/pil/2.html*