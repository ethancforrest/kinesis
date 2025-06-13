# Lua Quick Reference for Norns

## Basic Syntax

### Comments
```lua
-- Single line comment

--[[
Multi-line comment
can span multiple lines
--]]
```

### Variables and Assignment
```lua
local x = 10        -- Local variable (preferred)
y = 20             -- Global variable
name = "hello"     -- String
flag = true        -- Boolean
nothing = nil      -- Nil value
```

## Data Types

### Numbers
```lua
x = 42            -- Integer
y = 3.14159       -- Float
z = 1.23e-4       -- Scientific notation
```

### Strings
```lua
str1 = "double quotes"
str2 = 'single quotes'
str3 = [[multi-line
string content]]

-- String concatenation
result = "hello" .. " " .. "world"
```

### Booleans
```lua
flag = true
condition = false

-- Falsy values: false, nil
-- Truthy values: everything else (including 0 and "")
```

## Tables (Arrays and Objects)

### Arrays (indexed tables)
```lua
-- Array creation
arr = {1, 2, 3, 4, 5}
empty = {}

-- Access elements (1-indexed!)
first = arr[1]
last = arr[#arr]

-- Add elements
table.insert(arr, 6)        -- Append
table.insert(arr, 2, 99)    -- Insert at position 2
```

### Objects (key-value tables)
```lua
-- Object creation
person = {
  name = "Alice",
  age = 30,
  city = "Portland"
}

-- Access properties
print(person.name)      -- Dot notation
print(person["age"])    -- Bracket notation

-- Add/modify properties
person.email = "alice@example.com"
person["phone"] = "555-1234"
```

## Control Flow

### Conditionals
```lua
if x > 10 then
  print("big")
elseif x > 5 then
  print("medium")
else
  print("small")
end

-- Ternary-like
result = condition and "yes" or "no"
```

### Loops
```lua
-- For loop (numeric)
for i = 1, 10 do
  print(i)
end

for i = 10, 1, -1 do  -- Count down
  print(i)
end

-- For loop (table iteration)
for i, value in ipairs(array) do
  print(i, value)
end

for key, value in pairs(table) do
  print(key, value)
end

-- While loop
while condition do
  -- code
end

-- Repeat-until loop
repeat
  -- code
until condition
```

## Functions

### Function Definition
```lua
-- Basic function
function greet(name)
  return "Hello, " .. name
end

-- Anonymous function
local add = function(a, b)
  return a + b
end

-- Multiple return values
function divmod(a, b)
  return math.floor(a/b), a % b
end

local quotient, remainder = divmod(17, 5)
```

### Variable Arguments
```lua
function sum(...)
  local total = 0
  for i, v in ipairs({...}) do
    total = total + v
  end
  return total
end

result = sum(1, 2, 3, 4, 5)
```

## Common Patterns

### Error Handling
```lua
-- Using pcall (protected call)
local success, result = pcall(risky_function, arg1, arg2)
if success then
  print("Result:", result)
else
  print("Error:", result)
end
```

### Table Utilities
```lua
-- Check if table contains value
function contains(table, value)
  for _, v in pairs(table) do
    if v == value then
      return true
    end
  end
  return false
end

-- Table length
length = #array  -- Only works for arrays
```

### String Utilities
```lua
-- String formatting
message = string.format("Hello %s, you are %d years old", name, age)

-- String manipulation
upper = string.upper("hello")    -- "HELLO"
lower = string.lower("WORLD")    -- "world"
sub = string.sub("hello", 2, 4)  -- "ell"
```

## Norns-Specific Lua Patterns

### Script Structure
```lua
-- Engine selection
engine.name = "PolyPerc"

-- Global variables
local position = 0
local notes = {}

-- Init function (called when script loads)
function init()
  -- Setup code here
end

-- Key handler
function key(n, z)
  if n == 3 and z == 1 then
    -- Key 3 pressed
  end
end

-- Encoder handler  
function enc(n, d)
  if n == 2 then
    position = util.clamp(position + d, 0, 100)
  end
end

-- Redraw screen
function redraw()
  screen.clear()
  screen.text("Position: " .. position)
  screen.update()
end
```

### Common Norns Functions
```lua
-- Utilities
util.clamp(value, min, max)    -- Constrain value
util.linlin(x, min1, max1, min2, max2)  -- Linear mapping

-- Math
math.random()                  -- Random 0-1
math.random(n)                 -- Random 1-n
math.random(min, max)          -- Random in range

-- Tables
tab.print(table)              -- Debug print table contents
```

## Best Practices

1. **Use local variables** - Faster and avoids global namespace pollution
2. **Check for nil** - Use `if value then` rather than `if value ~= nil then`
3. **Use ipairs for arrays** - `ipairs()` for indexed tables, `pairs()` for all
4. **Cache table lookups** - Store `table.function` in local variable if called repeatedly
5. **Consistent naming** - Use snake_case for variables, PascalCase for "classes"

## Common Gotchas

- **1-indexed arrays** - Lua arrays start at index 1, not 0
- **String concatenation** - Use `..` not `+`
- **Truthiness** - Only `false` and `nil` are falsy, everything else is truthy
- **Global by default** - Variables are global unless declared with `local`
- **Table length** - `#table` only works reliably with array-like tables

*This reference covers the most commonly used Lua features in Norns scripting.*