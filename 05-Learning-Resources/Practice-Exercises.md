# Norns Programming Practice Exercises

## Lua Fundamentals Exercises

### Exercise 1: Basic Variables and Types
Create a Lua script that demonstrates:
```lua
-- Number operations
local a = 10
local b = 3.14
local result = a + b

-- String manipulation  
local name = "Norns"
local message = "Hello " .. name
local length = string.len(message)

-- Boolean logic
local is_ready = true
local is_complete = false
local status = is_ready and not is_complete

-- Print all results
print("Number result:", result)
print("Message:", message)
print("Status:", status)
```

**Challenge**: Add error handling using `pcall()` for division by zero.

---

### Exercise 2: Tables and Functions
```lua
-- Create a scale table
local major_scale = {0, 2, 4, 5, 7, 9, 11}

-- Function to transpose a note
function transpose(note, semitones)
  return note + semitones
end

-- Function to get scale degree
function get_scale_note(root, scale, degree)
  local octave = math.floor((degree - 1) / #scale)
  local scale_index = ((degree - 1) % #scale) + 1
  return root + scale[scale_index] + (octave * 12)
end

-- Test the functions
local root_note = 60  -- Middle C
for i = 1, 15 do
  local note = get_scale_note(root_note, major_scale, i)
  print("Degree " .. i .. ": " .. note)
end
```

**Challenge**: Add functions for different scale types (minor, dorian, etc.).

---

### Exercise 3: Control Flow and Loops
```lua
-- Generate a rhythm pattern
local pattern = {}
local pattern_length = 16

-- Fill pattern with random notes
for i = 1, pattern_length do
  if math.random() > 0.6 then
    pattern[i] = {
      note = 60 + math.random(0, 12),
      velocity = math.random(0.5, 1.0)
    }
  else
    pattern[i] = nil  -- Rest
  end
end

-- Play pattern function
function play_pattern(pattern)
  for i, step in ipairs(pattern) do
    if step then
      print("Step " .. i .. ": Note " .. step.note .. ", Vel " .. step.velocity)
    else
      print("Step " .. i .. ": Rest")
    end
  end
end

play_pattern(pattern)
```

**Challenge**: Add pattern quantization and swing timing.

---

## Norns Scripting Exercises

### Exercise 4: Basic Norns Script Structure
Create a script with proper Norns structure:

```lua
-- minimal_synth.lua
engine.name = "PolyPerc"

local frequency = 440
local amplitude = 0.5
local playing = false

function init()
  print("Minimal synth loaded")
end

function key(n, z)
  if n == 3 then
    if z == 1 then
      -- Key pressed
      engine.hz(frequency)
      playing = true
    else
      -- Key released
      playing = false
    end
    redraw()
  end
end

function enc(n, d)
  if n == 2 then
    frequency = util.clamp(frequency + (d * 10), 100, 1000)
  elseif n == 3 then
    amplitude = util.clamp(amplitude + (d * 0.01), 0, 1)
  end
  redraw()
end

function redraw()
  screen.clear()
  screen.level(15)
  screen.move(10, 20)
  screen.text("MINIMAL SYNTH")
  
  screen.level(10)
  screen.move(10, 35)
  screen.text("Freq: " .. math.floor(frequency) .. " Hz")
  screen.move(10, 45)
  screen.text("Amp: " .. string.format("%.2f", amplitude))
  
  if playing then
    screen.move(10, 60)
    screen.text("PLAYING")
  end
  
  screen.update()
end
```

**Challenge**: Add multiple oscillators with different waveforms.

---

### Exercise 5: Parameter System
Extend the previous script with parameters:

```lua
function init()
  -- Add parameters
  params:add_control("freq", "Frequency", controlspec.new(100, 1000, "exp", 1, 440, "Hz"))
  params:add_control("amp", "Amplitude", controlspec.AMP)
  params:add_option("wave", "Waveform", {"sine", "saw", "square"}, 1)
  
  -- Parameter actions
  params:set_action("freq", function(x)
    frequency = x
    redraw()
  end)
  
  params:set_action("amp", function(x)
    amplitude = x
    redraw()
  end)
  
  print("Parameter synth loaded")
end
```

**Challenge**: Add ADSR envelope parameters and implement envelope control.

---

### Exercise 6: Clock and Sequencing
Create a simple step sequencer:

```lua
-- step_seq.lua
engine.name = "PolyPerc"

local steps = {}
local current_step = 1
local step_count = 8
local playing = false

function init()
  -- Initialize steps
  for i = 1, step_count do
    steps[i] = {
      active = false,
      note = 60 + i
    }
  end
  
  -- Start sequencer clock
  clock.run(sequencer)
  
  params:add_number("tempo", "Tempo", 60, 200, 120)
  params:set_action("tempo", function(x)
    clock.set_tempo(x)
  end)
end

function sequencer()
  while true do
    if playing and steps[current_step].active then
      engine.hz(midi_to_hz(steps[current_step].note))
    end
    
    current_step = (current_step % step_count) + 1
    redraw()
    
    clock.sleep(0.25)  -- 16th notes
  end
end

function key(n, z)
  if n == 2 and z == 1 then
    playing = not playing
  elseif n == 3 and z == 1 then
    steps[current_step].active = not steps[current_step].active
  end
  redraw()
end

function midi_to_hz(note)
  return (440 / 32) * (2 ^ ((note - 9) / 12))
end

function redraw()
  screen.clear()
  screen.level(15)
  screen.move(10, 10)
  screen.text("STEP SEQUENCER")
  
  screen.level(10)
  screen.move(10, 25)
  screen.text("Playing: " .. (playing and "YES" or "NO"))
  
  -- Draw steps
  for i = 1, step_count do
    local x = 10 + (i - 1) * 12
    local y = 40
    
    if i == current_step then
      screen.level(15)
    elseif steps[i].active then
      screen.level(10)
    else
      screen.level(3)
    end
    
    screen.rect(x, y, 8, 8)
    screen.fill()
  end
  
  screen.update()
end
```

**Challenge**: Add step probability and velocity per step.

---

## SuperCollider Engine Exercises

### Exercise 7: Basic SynthDef
Create a simple synthesizer definition:

```supercollider
// In SuperCollider IDE
(
SynthDef(\myBasicSynth, {
    arg freq = 440, amp = 0.1, gate = 1, cutoff = 1000;
    var sig, env, filter;
    
    // Oscillator
    sig = Saw.ar(freq, amp);
    
    // Filter
    filter = LPF.ar(sig, cutoff);
    
    // Envelope
    env = EnvGen.kr(Env.adsr(), gate, doneAction: 2);
    
    // Output
    Out.ar(0, filter * env);
}).add;
)

// Test the SynthDef
x = Synth(\myBasicSynth, [\freq, 440, \amp, 0.2]);
x.set(\gate, 0);  // Release
```

**Challenge**: Add detune, multiple oscillators, and filter envelope.

---

### Exercise 8: Basic Norns Engine
Create a minimal Norns engine:

```supercollider
Engine_BasicSynth : CroneEngine {
    var <synth;
    
    *new { arg context, doneCallback;
        ^super.new(context, doneCallback);
    }
    
    alloc {
        SynthDef(\basicVoice, {
            arg out, freq = 440, amp = 0.1, gate = 1;
            var sig, env;
            
            sig = Saw.ar(freq, amp);
            env = EnvGen.kr(Env.adsr(), gate, doneAction: 2);
            
            Out.ar(out, sig * env);
        }).add;
        
        context.server.sync;
        
        this.addCommand("start", "ff", { arg msg;
            var freq = msg[1];
            var amp = msg[2];
            
            synth = Synth(\basicVoice, [
                \out, context.out_b,
                \freq, freq,
                \amp, amp
            ]);
        });
        
        this.addCommand("stop", "", { arg msg;
            if (synth.notNil) {
                synth.set(\gate, 0);
            };
        });
    }
}
```

**Challenge**: Add polyphony with voice management.

---

### Exercise 9: Effect Processing
Create an engine with built-in effects:

```supercollider
Engine_EffectSynth : CroneEngine {
    alloc {
        SynthDef(\effectVoice, {
            arg out, freq = 440, amp = 0.1, gate = 1,
                delay_time = 0.2, delay_feedback = 0.3, delay_mix = 0.2,
                reverb_room = 0.5, reverb_mix = 0.3;
                
            var sig, env, delayed, reverbed;
            
            // Basic oscillator
            sig = Saw.ar(freq, amp);
            env = EnvGen.kr(Env.adsr(), gate, doneAction: 2);
            sig = sig * env;
            
            // Delay effect
            delayed = DelayN.ar(sig, 1.0, delay_time);
            delayed = delayed + (LocalIn.ar(1) * delay_feedback);
            LocalOut.ar(delayed);
            sig = sig + (delayed * delay_mix);
            
            // Reverb effect
            reverbed = FreeVerb.ar(sig, reverb_mix, reverb_room);
            
            Out.ar(out, reverbed);
        }).add;
        
        // Add commands for effect control
        this.addCommand("set_delay", "fff", { arg msg;
            var time = msg[1];
            var feedback = msg[2];
            var mix = msg[3];
            
            if (synth.notNil) {
                synth.set(
                    \delay_time, time,
                    \delay_feedback, feedback,
                    \delay_mix, mix
                );
            };
        });
    }
}
```

**Challenge**: Add modulation sources (LFOs) and multiple effect types.

---

## Grid Integration Exercises

### Exercise 10: Basic Grid Control
Create a grid-controlled step sequencer:

```lua
-- grid_seq.lua
engine.name = "PolyPerc"

local g = grid.connect(1)
local sequence = {}
local current_step = 1
local playing = false

function init()
  g.key = grid_key
  
  -- Initialize 16-step sequence
  for i = 1, 16 do
    sequence[i] = false
  end
  
  clock.run(step_clock)
  grid_redraw()
end

function grid_key(x, y, z)
  if y == 1 and z == 1 then  -- Top row
    if x <= 16 then
      sequence[x] = not sequence[x]
      grid_redraw()
    end
  elseif y == 8 and z == 1 then  -- Bottom row
    if x == 1 then
      playing = not playing
      grid_redraw()
    end
  end
end

function step_clock()
  while true do
    if playing then
      if sequence[current_step] then
        engine.hz(440)
      end
      
      current_step = (current_step % 16) + 1
      grid_redraw()
    end
    
    clock.sleep(0.25)
  end
end

function grid_redraw()
  g:all(0)
  
  -- Draw sequence
  for i = 1, 16 do
    local level = sequence[i] and 15 or 3
    if i == current_step and playing then
      level = 10
    end
    g:led(i, 1, level)
  end
  
  -- Draw play button
  g:led(1, 8, playing and 15 or 5)
  
  g:refresh()
end
```

**Challenge**: Add multiple tracks and different note values per step.

---

## Project-Based Exercises

### Exercise 11: Mini DAW
Combine multiple concepts into a small digital audio workstation:

**Features to implement:**
- Multiple tracks with different engines
- Basic mixer (volume, pan per track)
- Pattern-based sequencing
- Parameter automation
- Save/load functionality

### Exercise 12: Live Performance Tool
Create a script optimized for live performance:

**Features to implement:**
- Scene-based workflow
- Real-time parameter control
- Loop recording and playback
- MIDI controller integration
- Visual feedback for performance

### Exercise 13: Generative Composition Engine
Build a system that creates music algorithmically:

**Features to implement:**
- Markov chain melody generation
- Probability-based rhythm patterns
- Harmonic progression algorithms
- Real-time evolution of musical parameters
- User influence on generative processes

---

## Debugging and Testing Exercises

### Exercise 14: Error Handling
Practice common debugging scenarios:

```lua
-- Common error patterns and solutions
function safe_engine_call(command, ...)
  local success, error = pcall(engine[command], ...)
  if not success then
    print("Engine error:", error)
    return false
  end
  return true
end

function validate_parameter(value, min, max, name)
  if type(value) ~= "number" then
    print("Warning: " .. name .. " must be a number")
    return false
  end
  
  if value < min or value > max then
    print("Warning: " .. name .. " out of range (" .. min .. "-" .. max .. ")")
    return util.clamp(value, min, max)
  end
  
  return value
end
```

### Exercise 15: Performance Optimization
Learn to identify and fix performance issues:

```lua
-- Efficient screen drawing
function redraw()
  screen.clear()
  
  -- Cache frequently used values
  local tempo = params:get("tempo")
  local playing_status = playing and "PLAYING" or "STOPPED"
  
  -- Minimize screen operations
  screen.level(15)
  screen.move(10, 10)
  screen.text("PERFORMANCE TEST")
  
  screen.level(10)
  screen.move(10, 25)
  screen.text("Tempo: " .. tempo)
  screen.move(10, 35)
  screen.text("Status: " .. playing_status)
  
  screen.update()
end

-- Efficient table operations
function update_sequence_efficient(steps, new_data)
  -- Use table.insert/remove instead of rebuilding tables
  for i, step in ipairs(new_data) do
    if steps[i] then
      steps[i].active = step.active
      steps[i].note = step.note
    else
      table.insert(steps, step)
    end
  end
end
```

---

## Progress Tracking

Mark completed exercises:

**Lua Fundamentals:**
- [ ] Exercise 1: Variables and Types
- [ ] Exercise 2: Tables and Functions  
- [ ] Exercise 3: Control Flow and Loops

**Norns Scripting:**
- [ ] Exercise 4: Basic Script Structure
- [ ] Exercise 5: Parameter System
- [ ] Exercise 6: Clock and Sequencing

**SuperCollider Engines:**
- [ ] Exercise 7: Basic SynthDef
- [ ] Exercise 8: Basic Norns Engine
- [ ] Exercise 9: Effect Processing

**Grid Integration:**
- [ ] Exercise 10: Basic Grid Control

**Projects:**
- [ ] Exercise 11: Mini DAW
- [ ] Exercise 12: Live Performance Tool
- [ ] Exercise 13: Generative Composition Engine

**Advanced:**
- [ ] Exercise 14: Error Handling
- [ ] Exercise 15: Performance Optimization

*Complete these exercises in order, taking time to experiment and modify each one before moving to the next.*