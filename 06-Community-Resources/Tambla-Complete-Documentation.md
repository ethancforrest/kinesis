# Tambla: Complete User Documentation

*Semi-generative rhythmic arpeggiator with bendable playheads*

## Table of Contents
1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Interface Guide](#interface-guide)
4. [Musical Applications](#musical-applications)
5. [Technical Reference](#technical-reference)
6. [Troubleshooting](#troubleshooting)
7. [Improvement Recommendations](#improvement-recommendations)

---

## Quick Start

### Minimum Setup
1. **Install Tambla** via Maiden package manager
2. **Connect MIDI keyboard** to Norns
3. **Load the script** and select "Play" page
4. **Hold a key** on your MIDI keyboard - you'll hear rhythmic patterns

### First Pattern
1. Navigate to **Edit page** (K2 from Play page)
2. Use **E2** to select different steps
3. Use **E3** to adjust step velocity (brightness = velocity)
4. Use **K3** to toggle steps on/off
5. Return to **Play page** (K2) and hold keys to hear your pattern

---

## Core Concepts

### The Four-Row System
Tambla organizes rhythm into **four independent rows**:
```
Row 1: ████░░██░░░█░░██    (16 steps)
Row 2: ██░░██░░██░░        (12 steps)  
Row 3: █░█░█░█░            (8 steps)
Row 4: █░░█░░░█            (7 steps)
```

Each row can have:
- **2-16 steps** (different lengths create polyrhythm)
- **Independent timing** (bend, offset, resolution)
- **Per-step parameters** (velocity, duration, chance)

### Bendable Playheads
Traditional arpeggiators move at constant speed. Tambla's playheads can:
- **Speed up then slow down** (bend < 1.0, logarithmic)
- **Slow down then speed up** (bend > 1.0, exponential)  
- **Move at constant speed** (bend = 1.0, linear)

This creates organic, breathing rhythms within precise synchronization.

### Key-Triggered Performance
- **First key held** → triggers Row 1 pattern
- **Second key held** → triggers Row 2 pattern
- **Third key held** → triggers Row 3 pattern  
- **Fourth key held** → triggers Row 4 pattern

Notes start from the **current playhead position**, not the beginning, maintaining rhythmic coherence.

---

## Interface Guide

### Navigation
- **K1**: Shift/modifier key
- **K2**: Navigate between pages
- **K3**: Context-dependent action
- **E1**: Page/section navigation
- **E2**: Parameter/item selection
- **E3**: Value adjustment

### Play Page (Main Performance Interface)

#### Display Elements
```
TAMBLA          [Tempo: 120]
Slot: 1/8       Pattern: A
Row: 1/4        [●●○●] ○○●○

Bend: 0.50      Offset: 0
Res: 1/1        Count: 16
```

#### Controls
- **E1**: Select slot (1-8) - different pattern banks
- **E2**: Select row (1-4) - which rhythmic voice to edit
- **E3**: Adjust current parameter (depends on cursor position)
- **K3**: Start/stop transport
- **K1+E1**: Navigate parameter categories
- **K1+E2**: Fine adjustment mode
- **K1+E3**: Reset parameter to default

#### Parameters (per row)
- **Bend**: Timing curve (-2.0 to +2.0)
  - < 1.0: Fast start, slow end
  - > 1.0: Slow start, fast end
- **Offset**: Phase shift (0-15 steps)
- **Resolution**: Clock division (1/4, 1/2, 1/1, 2/1, 4/1)
- **Count**: Number of steps (2-16)

### Edit Page (Step Programming)

#### Display Elements
```
EDIT - Row 1/4
Step: 8/16      [●●○●●○○●]

Velocity: 85    ████████▌
Duration: 1.0   ████████
Chance: 75%     ██████░░
```

#### Controls
- **E1**: Select row (1-4)
- **E2**: Select step (1-16)
- **E3**: Adjust parameter value
- **K3**: Toggle step on/off
- **K1+E1**: Parameter category selection
- **K1+E2**: Copy current step
- **K1+K3**: Paste to current step

#### Step Parameters
- **Velocity**: MIDI velocity (0-127)
- **Duration**: Note length multiplier (0.1-4.0)
- **Chance**: Probability of triggering (0-100%)
- **Aux**: Auxiliary parameter for future use

#### Visual Feedback
- **Bright squares**: Active steps
- **Dim squares**: Inactive steps
- **Current step**: Highlighted with cursor
- **Playhead**: Moving indicator during playback

### Macro Page (Pattern Management)

#### Display Elements
```
MACRO
Slot: 1/8       [Copy] [Paste]
Pattern: A      [Load] [Save]

File: patterns/tambla_001.ptn
```

#### Controls
- **E1**: Select slot (1-8)
- **E2**: Select pattern within slot (A-H planned)
- **E3**: Navigate file browser when loading/saving
- **K3**: Execute selected action
- **K1+K2**: Quick copy current pattern
- **K1+K3**: Quick paste to current slot

#### Operations
- **Copy**: Store current pattern in clipboard
- **Paste**: Load clipboard pattern to current slot
- **Load**: Browse and load pattern files
- **Save**: Save current pattern to file
- **Randomize**: Generate random pattern (K1+K3)
- **Clear**: Empty current pattern (K1+E1+K3)

---

## Musical Applications

### Practice Accompaniment
**Original design goal**: Generate rhythmic patterns for djembe/handpan practice

#### Setup
1. **Set different row lengths**: Row 1=16, Row 2=12, Row 3=8, Row 4=7
2. **Add subtle bend**: 0.9-1.1 for organic feel
3. **Use chance parameters**: 80-90% for slight variation
4. **Hold one key**: Let pattern evolve while you practice

#### Tips
- Start with simple patterns (few active steps)
- Use lower velocities for background patterns
- Longer durations create sustained accompaniment

### Polyrhythmic Composition
**Create complex interlocking rhythms**

#### Basic Polyrhythm
1. **Row 1**: 16 steps (4/4 time)
2. **Row 2**: 12 steps (3/4 time)
3. **Row 3**: 15 steps (5/4 time)
4. **Hold multiple keys** to hear relationships

#### Advanced Techniques
- **Phase shifting**: Use offset to stagger pattern starts
- **Clock division**: Different resolutions create metric modulation
- **Bend variation**: Each row can have different timing curves

### Live Performance
**Real-time pattern manipulation**

#### Performance Setup
1. **Map MIDI controller** to key parameters:
   - Bend (continuous controller)
   - Chance (performance variation)
   - Velocity (dynamics)
2. **Prepare pattern variations** in different slots
3. **Use key combinations** for quick parameter access

#### Performance Techniques
- **Gradual bend changes**: Create builds and releases
- **Chance modulation**: Add/remove rhythmic complexity
- **Pattern switching**: Use different slots for song sections
- **Live step editing**: Modify patterns while performing

### Generative Exploration
**Let the algorithm surprise you**

#### Discovery Process
1. **Start with random patterns**: Use randomize function
2. **Listen for interesting moments**: What catches your ear?
3. **Isolate and develop**: Turn off other rows, focus on one
4. **Add controlled variation**: Adjust chance parameters
5. **Build complexity gradually**: Add rows back in

---

## Technical Reference

### MIDI Implementation

#### Input
- **Note On/Off**: Triggers pattern playback
- **Velocity**: Affects output note velocity (if row velocity > 0)
- **Channel**: All channels accepted
- **Controller**: Mappable via Norns parameter system

#### Output  
- **Note On/Off**: Generated by step triggers
- **Velocity**: Combined from step velocity + input velocity
- **Timing**: Determined by bend/resolution/offset calculations
- **Channel**: Configurable per output device

### Timing Algorithm

#### Bend Calculation
```lua
-- Simplified timing calculation
local progress = current_step / total_steps
local bent_progress

if bend < 1.0 then
  -- Logarithmic: fast start, slow end
  bent_progress = math.log(1 + progress * (math.exp(bend) - 1)) / bend
else
  -- Exponential: slow start, fast end  
  bent_progress = (math.exp(progress * bend) - 1) / (math.exp(bend) - 1)
end

local actual_time = bent_progress * pattern_duration
```

#### Clock Synchronization
- **Master clock**: Driven by Norns transport
- **Row clocks**: Derived from master with resolution division
- **Playhead updates**: Calculated each clock tick
- **Note scheduling**: Queued for precise timing

### File Format

#### Pattern Files (.ptn)
```lua
-- Simplified structure
{
  version = "1.0",
  rows = {
    {
      count = 16,
      resolution = 1,
      bend = 1.0,
      offset = 0,
      steps = {
        {velocity = 80, duration = 1.0, chance = 1.0, aux = 0},
        -- ... more steps
      }
    },
    -- ... more rows
  }
}
```

### Device Routing

#### Supported Outputs
- **MIDI**: Standard MIDI note events
- **Engine**: Norns internal synthesis engines
- **Crow**: CV/Gate output for modular systems

#### Configuration
```lua
-- Device setup (simplified)
devices = {
  midi = midi.connect(1),      -- MIDI device 1
  engine = engine,             -- Current Norns engine
  crow = crow                  -- Crow module
}
```

---

## Troubleshooting

### Common Issues

#### No Sound Output
**Symptoms**: Patterns play but no audio
**Solutions**:
1. Check MIDI connections and device settings
2. Verify Norns engine is loaded and responding
3. Confirm step velocities are > 0
4. Check chance parameters (100% = always trigger)

#### Timing Feels Wrong
**Symptoms**: Rhythm doesn't match expectation
**Solutions**:
1. Check bend settings (1.0 = linear timing)
2. Verify resolution settings (1/1 = normal speed)
3. Confirm offset values (0 = no phase shift)
4. Check if multiple rows are interfering

#### Patterns Don't Save
**Symptoms**: Changes lost when reloading
**Solutions**:
1. Use Macro page save function explicitly
2. Check file permissions in dust directory
3. Verify sufficient storage space
4. Check for valid filename characters

#### MIDI Input Not Responding
**Symptoms**: Keys don't trigger patterns
**Solutions**:
1. Check MIDI device connection in Norns system menu
2. Verify MIDI channel settings
3. Confirm script is on Play page
4. Check if transport is running (K3 to start)

### Performance Optimization

#### CPU Usage
- **Limit simultaneous rows**: More active rows = more CPU
- **Reduce step counts**: 16-step patterns use more CPU than 8-step
- **Moderate bend calculations**: Extreme bend values require more computation

#### Memory Management
- **Clear unused patterns**: Use clear function in Macro page
- **Limit pattern count**: 8 slots × 4 rows × 16 steps = significant memory
- **Save frequently**: Prevent loss of work

---

## Improvement Recommendations

### Critical Missing Features

#### 1. Comprehensive Documentation
**Current Issue**: User manual is missing
**Recommended Solutions**:
- In-script help system (K1+K1+K1)
- Parameter tooltips on screen
- Quick reference card (printable PDF)
- Video tutorials for key concepts

#### 2. Better Visual Feedback
**Current Issues**: 
- Playhead position unclear during playback
- Parameter relationships not obvious
- No indication of which keys are held

**Recommended Solutions**:
```lua
-- Enhanced visual feedback
function draw_playhead_indicators()
  for row = 1, 4 do
    local x = 10 + (current_step[row] * 6)
    local y = 20 + (row * 8)
    screen.level(15)
    screen.circle(x, y, 2)
    screen.fill()
  end
end

function draw_held_keys()
  screen.level(6)
  screen.move(10, 60)
  screen.text("Keys: " .. table.concat(held_keys, " "))
end
```

#### 3. Parameter Visualization
**Current Issue**: Bend and timing effects are abstract
**Recommended Solutions**:
- Visual timing curves showing bend effects
- Polyrhythm visualization (overlapping circles)
- Real-time step highlighting during playback

### Usability Improvements

#### 4. Onboarding Experience
**Current Issue**: Complex interface with no guidance
**Recommended Solutions**:
- Tutorial mode with guided examples
- Preset patterns for different musical styles
- "Demo mode" that shows capabilities

#### 5. Parameter Organization
**Current Issue**: Too many parameters on single page
**Recommended Solutions**:
```lua
-- Hierarchical parameter organization
local param_groups = {
  timing = {"bend", "offset", "resolution"},
  pattern = {"count", "velocity", "duration"},
  performance = {"chance", "aux", "swing"}
}
```

#### 6. Copy/Paste Workflow
**Current Issue**: Limited pattern manipulation tools
**Recommended Solutions**:
- Step-level copy/paste
- Pattern templates and favorites
- Undo/redo functionality
- Pattern morphing between slots

### Musical Enhancements

#### 7. Scale and Harmony Support
**Current Issue**: Only chromatic note output
**Recommended Solutions**:
```lua
-- Scale quantization
local scales = {
  major = {0, 2, 4, 5, 7, 9, 11},
  minor = {0, 2, 3, 5, 7, 8, 10},
  pentatonic = {0, 2, 4, 7, 9}
}

function quantize_to_scale(note, scale_type, root)
  -- Implementation here
end
```

#### 8. Advanced Timing Features
**Current Capabilities**: Basic bend curves
**Recommended Additions**:
- Swing/shuffle parameters per row
- Micro-timing adjustments per step
- Groove templates from acoustic performances
- Polyrhythmic alignment tools

#### 9. Pattern Evolution
**Current Issue**: Static patterns unless manually changed
**Recommended Solutions**:
- Gradual pattern mutation over time
- Probabilistic step evolution
- Pattern breeding/genetic algorithms
- Environmental response (tempo-based changes)

### Technical Improvements

#### 10. Performance Optimization
**Current Issues**: CPU spikes with complex patterns
**Recommended Solutions**:
```lua
-- Optimized timing calculations
local timing_cache = {}

function get_bent_timing(step, bend, total_steps)
  local cache_key = step .. "_" .. bend .. "_" .. total_steps
  if timing_cache[cache_key] then
    return timing_cache[cache_key]
  end
  
  -- Calculate and cache result
  local result = calculate_bent_timing(step, bend, total_steps)
  timing_cache[cache_key] = result
  return result
end
```

#### 11. Extended Hardware Support
**Current Support**: Basic MIDI, limited Grid/Arc
**Recommended Additions**:
- Full Grid integration with visual feedback
- Arc support for continuous parameter control
- Crow integration for modular systems
- OSC support for network control

#### 12. File Management
**Current Issue**: Basic save/load functionality
**Recommended Solutions**:
- Pattern libraries and collections
- Auto-save and crash recovery
- Export to standard MIDI files
- Sharing via cloud/network

### Code Architecture Improvements

#### 13. Error Handling
**Current Issue**: Limited error recovery
**Recommended Solutions**:
```lua
-- Robust error handling
function safe_pattern_load(filename)
  local success, result = pcall(load_pattern_file, filename)
  if not success then
    print("Pattern load failed: " .. result)
    return get_default_pattern()
  end
  return result
end
```

#### 14. Modularity Enhancement
**Current State**: Good separation, could be better
**Recommended Improvements**:
- Plugin architecture for new timing algorithms
- Modular device drivers
- Customizable UI layouts
- Third-party pattern generators

#### 15. Testing and Validation
**Current Issue**: No automated testing
**Recommended Solutions**:
- Unit tests for timing calculations
- Pattern validation functions
- Performance benchmarking
- Regression test suite

### Documentation Improvements

#### 16. Interactive Help System
```lua
-- In-script help
local help_topics = {
  bend = {
    description = "Controls playhead timing curve",
    range = "-2.0 to +2.0",
    examples = {
      "0.5: Fast start, slow end",
      "1.5: Slow start, fast end"
    }
  }
}

function show_help(topic)
  -- Display contextual help
end
```

#### 17. Musical Examples
**Current Issue**: No practical examples provided
**Recommended Additions**:
- Genre-specific pattern collections
- Famous polyrhythm recreations
- Step-by-step composition tutorials
- Performance technique demonstrations

---

## Implementation Priority

### High Priority (Core Usability)
1. **Visual feedback improvements** (playhead, held keys)
2. **In-script help system** (parameter tooltips)
3. **Better onboarding** (tutorial mode, presets)
4. **Error handling** (graceful failure recovery)

### Medium Priority (Musical Features)
1. **Scale quantization** (harmonic support)
2. **Advanced copy/paste** (pattern manipulation)
3. **Pattern evolution** (generative features)
4. **Extended hardware support** (Grid, Arc, Crow)

### Low Priority (Polish)
1. **Performance optimization** (caching, efficiency)
2. **File management** (libraries, export)
3. **Testing framework** (automated validation)
4. **Modular architecture** (plugin system)

---

*This documentation addresses the missing user manual while identifying specific areas for improvement. The script shows exceptional technical and musical sophistication but would benefit significantly from better user experience design and more comprehensive documentation.*