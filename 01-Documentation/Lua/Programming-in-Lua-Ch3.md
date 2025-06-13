# Programming in Lua - Chapter 3: Expressions

*From the first edition of "Programming in Lua" by Roberto Ierusalimschy*

## What are Expressions?

**Expressions denote values.** In Lua, expressions include:

- **Numeric constants** - literal numbers like `42`, `3.14`
- **String literals** - text in quotes like `"hello"`
- **Variables** - named references to values
- **Unary operations** - single-operand operations like `-x`
- **Binary operations** - two-operand operations like `x + y`
- **Function calls** - invoking functions like `print("hello")`

## Types of Expressions

### 1. Literals
```lua
42          -- numeric constant
3.14159     -- floating-point constant
"hello"     -- string literal
'world'     -- string literal (single quotes)
```

### 2. Variables
```lua
x           -- variable reference
name        -- variable reference
```

### 3. Operations
```lua
-- Unary operations
-x          -- negation
not x       -- logical not

-- Binary operations
x + y       -- addition
x - y       -- subtraction
x * y       -- multiplication
x / y       -- division
x == y      -- equality
x ~= y      -- inequality
```

### 4. Function Calls
```lua
print("hello")      -- function call
math.sin(x)         -- method call
table.insert(t, v)  -- library function call
```

## Expression Evaluation

Expressions are evaluated to produce values:
- Numeric expressions produce numbers
- String expressions produce strings
- Boolean expressions produce true/false
- Function calls return their result values

## Combining Expressions

Expressions can be combined to form more complex expressions:

```lua
x + y * z           -- arithmetic combination
f(x) + g(y)         -- function calls in arithmetic
x > 0 and y < 10    -- logical combination
```

## Key Points

1. **Everything has a value** - All expressions evaluate to some value
2. **Composable** - Simple expressions can build complex ones
3. **Flexible** - Same operators work with different types when appropriate
4. **Functional** - Function calls are expressions that return values

## Next Steps

Understanding expressions is fundamental to Lua programming. They form the building blocks for:
- Variable assignments
- Function arguments
- Control flow conditions
- Return values

*Note: This content is from the first edition (Lua 5.0). The fourth edition targeting Lua 5.3 is available through Amazon.*

*Source: https://www.lua.org/pil/3.html*