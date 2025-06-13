# Norns API Quick Reference

## Script Structure

### Essential Functions
```lua
-- Engine selection (place at top of script)
engine.name = "PolyPerc"

-- Called when script loads
function init()
  -- Initialize variables, parameters, etc.
end

-- Called when script is reloaded (Ctrl+R)
function cleanup()
  -- Clean up resources
end

-- Handle key presses
function key(n, z)
  -- n = key number (1, 2, 3)
  -- z = 1 for press, 0 for release
end

-- Handle encoder turns
function enc(n, d)
  -- n = encoder number (1, 2, 3) 
  -- d = delta (-1 for CCW, 1 for CW)
end

-- Screen drawing
function redraw()
  screen.clear()
  -- Drawing commands
  screen.update()
end
```

## Screen API

### Basic Drawing
```lua
-- Clear screen
screen.clear()

-- Update display
screen.update()

-- Set pixel
screen.pixel(x, y)

-- Draw line
screen.line(x1, y1, x2, y2)

-- Draw rectangle
screen.rect(x, y, width, height)

-- Draw circle
screen.circle(x, y, radius)
```

### Text
```lua
-- Move cursor to position
screen.move(x, y)

-- Draw text at cursor
screen.text("Hello")

-- Draw text at specific position
screen.text_center("Centered text")
screen.text_right("Right aligned")

-- Set font size
screen.font_size(8)    -- 8, 16, or custom
screen.font_face(1)    -- 1-25 for different fonts
```

### Graphics Properties
```lua
-- Set drawing level (0-15, 15 = brightest)
screen.level(15)

-- Set line width
screen.line_width(1)

-- Anti-aliasing
screen.aa(1)  -- 1 = on, 0 = off
```

## Parameters

### Creating Parameters
```lua
-- In init() function
params:add_number("tempo", "Tempo", 60, 200, 120)
params:add_option("scale", "Scale", {"major", "minor", "dorian"}, 1)
params:add_control("filter", "Filter", controlspec.FREQ)
params:add_separator()

-- Parameter callbacks
params:set_action("tempo", function(x)
  clock.set_tempo(x)
end)
```

### Parameter Types
```lua
-- Number with min, max, default
params:add_number("id", "Name", min, max, default)

-- Option list
params:add_option("id", "Name", {"opt1", "opt2"}, default_index)

-- Control with controlspec
params:add_control("id", "Name", controlspec.AMP)

-- File picker
params:add_file("id", "Name", path)

-- Trigger (momentary button)
params:add_trigger("id", "Name")

-- Text input
params:add_text("id", "Name", "default_text")
```

### Using Parameters
```lua
-- Get parameter value
value = params:get("parameter_id")

-- Set parameter value
params:set("parameter_id", value)

-- Delta (relative change)
params:delta("parameter_id", delta)
```

## Clock and Timing

### Clock Functions
```lua
-- Set tempo
clock.set_tempo(120)

-- Get current tempo
tempo = clock.get_tempo()

-- Sleep for beats
clock.sleep(1)  -- Sleep for 1 beat

-- Sleep for seconds
clock.sleep(1/clock.get_tempo() * 60)  -- 1 second

-- Get beat position
beat = clock.get_beats()
```

### Coroutines
```lua
-- Start a clock coroutine
function sequence()
  while true do
    -- Do something
    engine.hz(math.random(200, 800))
    clock.sleep(0.25)
  end
end

-- Start the coroutine
clock.run(sequence)
```

## Audio Engine

### Engine Commands
```lua
-- Send command to engine
engine.command_name(arg1, arg2)

-- Common engine patterns
engine.hz(frequency)        -- Set frequency
engine.amp(amplitude)       -- Set amplitude
engine.note_on(note, vel)   -- MIDI-style note on
engine.note_off(note)       -- MIDI-style note off
```

### Engine Polls
```lua
-- Create poll to get data from engine
level_poll = poll.set("level", function(value)
  current_level = value
  redraw()
end)

-- Start/stop polling
level_poll.start()
level_poll.stop()
```

## MIDI

### MIDI Setup
```lua
-- In init()
midi_device = midi.connect(1)  -- Connect to device 1
midi_device.event = midi_event  -- Set event handler

function midi_event(data)
  local msg = midi.to_msg(data)
  if msg.type == "note_on" then
    engine.note_on(msg.note, msg.vel / 127)
  elseif msg.type == "note_off" then
    engine.note_off(msg.note)
  end
end
```

## Grid Integration

### Grid Setup
```lua
-- In init()
g = grid.connect(1)
g.key = grid_key

function grid_key(x, y, z)
  -- x, y = grid coordinates (1-indexed)
  -- z = 1 for press, 0 for release
  if z == 1 then
    -- Key pressed
    g:led(x, y, 15)  -- Light up LED
  else
    -- Key released  
    g:led(x, y, 0)   -- Turn off LED
  end
  g:refresh()
end
```

### Grid Display
```lua
-- Set single LED
g:led(x, y, level)  -- level 0-15

-- Set all LEDs
g:all(level)

-- Set row/column
g:led_row(y, level_table)
g:led_col(x, level_table)

-- Update display
g:refresh()
```

## Utilities

### Math Utilities
```lua
-- Clamp value between min and max
value = util.clamp(value, min, max)

-- Linear interpolation
result = util.linlin(input, in_min, in_max, out_min, out_max)

-- Exponential interpolation  
result = util.linexp(input, in_min, in_max, out_min, out_max)

-- Wrap value in range
result = util.wrap(value, min, max)

-- Round to nearest step
result = util.round(value, step)
```

### Table Utilities
```lua
-- Print table contents (debug)
tab.print(table)

-- Save/load tables
tab.save(table, path)
loaded_table = tab.load(path)

-- Table length
length = #table
```

### File Operations
```lua
-- Check if file exists
exists = util.file_exists(path)

-- Ensure directory exists
util.make_dir(path)

-- Path joining
path = path.join(directory, filename)
```

## Control Specs

### Common Control Specs
```lua
controlspec.UNIPOLAR     -- 0 to 1
controlspec.BIPOLAR      -- -1 to 1  
controlspec.FREQ         -- 20 to 20000 Hz
controlspec.AMP          -- 0 to 1 (amplitude)
controlspec.PAN          -- -1 to 1 (pan)
controlspec.DELAY        -- 0 to 2 seconds
controlspec.MIDI         -- 0 to 127
```

### Custom Control Specs
```lua
-- Create custom controlspec
my_spec = controlspec.new(
  min,           -- minimum value
  max,           -- maximum value  
  warp,          -- 'lin', 'exp', 'db', etc.
  step,          -- step size
  default,       -- default value
  units          -- unit string
)
```

## Common Patterns

### Parameter Menu Navigation
```lua
function enc(n, d)
  if n == 1 then
    -- Mix between parameter pages or menu levels
    mix.delta("param_focus", d)
  elseif n == 2 then
    -- Select parameter
    params:delta("selected_param", d)
  elseif n == 3 then
    -- Adjust selected parameter
    params:delta(selected_param_id, d)
  end
end
```

### State Management
```lua
-- Global state
local mode = 1
local page = 1

function key(n, z)
  if n == 1 then
    if z == 1 then
      -- Mode/shift key held
      mode = 2
    else
      mode = 1
    end
  elseif n == 2 and z == 1 then
    -- Toggle page
    page = page % 3 + 1
    redraw()
  end
end
```

### Screen Pages
```lua
function redraw()
  screen.clear()
  
  if page == 1 then
    draw_main_page()
  elseif page == 2 then
    draw_settings_page()  
  elseif page == 3 then
    draw_info_page()
  end
  
  screen.update()
end
```

*This reference covers the most commonly used Norns API functions for script development.*