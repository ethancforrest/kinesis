# SuperCollider Quick Reference for Norns

## Basic Syntax

### Comments
```supercollider
// Single line comment

/*
Multi-line comment
can span multiple lines
*/
```

### Variables
```supercollider
// Variables
var freq = 440;
var amp = 0.5;

// Environment variables (global)
~freq = 440;
~synth = Synth(\default);

// Arguments in functions
arg freq=440, amp=0.1;
```

## Data Types

### Numbers
```supercollider
x = 42;           // Integer
y = 3.14159;      // Float
z = 1.23e-4;      // Scientific notation
```

### Arrays
```supercollider
// Array creation
arr = [1, 2, 3, 4, 5];
notes = [60, 64, 67, 72];

// Access elements (0-indexed!)
first = arr[0];
last = arr[arr.size - 1];

// Array operations
arr.add(6);           // Add element
arr.insert(2, 99);    // Insert at index
arr.reverse;          // Reverse array
```

### Symbols and Strings
```supercollider
// Symbols (immutable identifiers)
\default
\sine
\polyPerc

// Strings
"Hello World"
"This is a string"
```

## SynthDefs and UGens

### Basic SynthDef Structure
```supercollider
SynthDef(\mysynth, {
    arg freq=440, amp=0.1, gate=1;
    var sig, env;
    
    // Generate signal
    sig = SinOsc.ar(freq, 0, amp);
    
    // Apply envelope
    env = EnvGen.kr(Env.adsr(), gate, doneAction: 2);
    sig = sig * env;
    
    // Output
    Out.ar(0, sig);
}).add;
```

### Common UGens

#### Oscillators
```supercollider
SinOsc.ar(freq, phase, mul, add)     // Sine wave
Saw.ar(freq, mul, add)               // Sawtooth
Pulse.ar(freq, width, mul, add)      // Square/pulse wave
LFNoise0.ar(freq, mul, add)          // Random noise
WhiteNoise.ar(mul, add)              // White noise
```

#### Filters
```supercollider
LPF.ar(input, freq, mul, add)        // Low-pass filter
HPF.ar(input, freq, mul, add)        // High-pass filter
BPF.ar(input, freq, rq, mul, add)    // Band-pass filter
Resonz.ar(input, freq, rq, mul, add) // Resonant filter
```

#### Envelopes
```supercollider
EnvGen.kr(envelope, gate, doneAction: 2)

// Envelope types
Env.adsr(attackTime, decayTime, sustainLevel, releaseTime)
Env.perc(attackTime, releaseTime)
Env.triangle(duration, level)
```

#### Effects
```supercollider
DelayN.ar(input, maxdelaytime, delaytime)  // Simple delay
CombN.ar(input, maxdelaytime, delaytime, decaytime)  // Comb filter
Reverb.ar(input, mix, room, damp)          // Reverb
Distortion.ar(input, gain)                 // Distortion
```

## Control Structures

### Conditionals
```supercollider
if(condition, {
    // true case
}, {
    // false case
});

// Select (like switch/case)
value.switch(
    0, { "zero" },
    1, { "one" },
    2, { "two" },
    { "other" }  // default case
);
```

### Loops
```supercollider
// Do loop
10.do({ arg i;
    i.postln;
});

// For loop
for(1, 10, { arg i;
    i.postln;
});

// Array iteration
[1, 2, 3, 4].do({ arg item, index;
    [index, item].postln;
});
```

## Functions

### Function Definition
```supercollider
// Basic function
f = { arg x, y;
    x + y
};

// Call function
result = f.value(3, 4);

// Function with multiple arguments
g = { arg freq=440, amp=0.1;
    SinOsc.ar(freq, 0, amp)
};
```

## Norns Engine Structure

### Basic Engine Template
```supercollider
Engine_MyEngine : CroneEngine {
    
    // Constructor
    *new { arg context, doneCallback;
        ^super.new(context, doneCallback);
    }
    
    // Initialize
    alloc {
        
        // Define SynthDefs
        SynthDef(\mysynth, {
            arg out, freq=440, amp=0.1, gate=1;
            var sig, env;
            sig = SinOsc.ar(freq, 0, amp);
            env = EnvGen.kr(Env.adsr(), gate, doneAction: 2);
            Out.ar(out, sig * env);
        }).add;
        
        // Define commands (callable from Lua)
        this.addCommand("note_on", "ff", { arg msg;
            var freq = msg[1];
            var amp = msg[2];
            Synth(\mysynth, [\freq, freq, \amp, amp]);
        });
        
        this.addCommand("note_off", "", { arg msg;
            // Note off logic
        });
    }
}
```

### Commands and Communication

```supercollider
// Add command (callable from Lua)
this.addCommand("commandName", "argumentTypes", { arg msg;
    // msg[1], msg[2], etc. contain the arguments
});

// Argument type codes:
// "i" = integer
// "f" = float  
// "s" = string

// Send data to Lua
this.sendReply("/replyName", [value1, value2]);
```

## Common Patterns

### Polyphonic Voice Management
```supercollider
var voices;

// Initialize voice array
voices = Array.newClear(8);

// Find free voice
findFreeVoice = {
    var freeVoice = nil;
    voices.do({ arg voice, i;
        if(voice.isNil, {
            freeVoice = i;
        });
    });
    freeVoice;
};

// Play note
playNote = { arg freq, amp;
    var voiceIndex = findFreeVoice.value;
    if(voiceIndex.notNil, {
        voices[voiceIndex] = Synth(\mysynth, [
            \freq, freq,
            \amp, amp
        ]);
    });
};
```

### Parameter Mapping
```supercollider
// Map MIDI note to frequency
freq = msg[1].midicps;

// Linear scaling
value = msg[1].linlin(0, 127, 20, 20000);

// Exponential scaling  
value = msg[1].linexp(0, 127, 20, 20000);

// Clip values
value = msg[1].clip(0, 1);
```

### Audio Routing
```supercollider
// Simple stereo output
Out.ar(0, [left, right]);

// Send to specific bus
Out.ar(context.out_b, signal);

// Audio input
input = In.ar(context.in_b, 2);
```

## Best Practices

1. **Use doneAction: 2** - Prevents synth accumulation
2. **Initialize variables** - Set default values for arguments
3. **Check for nil** - Validate inputs in commands
4. **Use proper scaling** - Map control values to appropriate ranges
5. **Free resources** - Clean up synths and busses when done

## Common Gotchas

- **0-indexed arrays** - Unlike Lua, SuperCollider arrays start at 0
- **Parentheses in function calls** - Often optional but good for clarity
- **UGen rate mismatch** - Make sure audio rate (.ar) and control rate (.kr) match usage
- **Argument order** - Pay attention to UGen argument order
- **Scope of variables** - Use `var` for local variables

## Useful Methods

```supercollider
// Math
value.abs            // Absolute value
value.sqrt           // Square root
value.pow(exponent)  // Power
value.wrap(lo, hi)   // Wrap around range

// Arrays
array.size           // Length
array.reverse        // Reverse
array.scramble       // Randomize order
array.choose         // Random element

// Debug
value.postln         // Print to console
value.poll           // Monitor value changes
```

*This reference covers the essential SuperCollider concepts needed for Norns engine development.*