# Norns Programming Learning Roadmap

## Phase 1: Foundation (Weeks 1-2)

### Prerequisites Setup
- [ ] Install Norns (hardware) or Norns Shield (DIY)
- [ ] Connect to WiFi and access Maiden (http://norns.local)
- [ ] Understand basic Norns navigation (keys, encoders, screen)
- [ ] Install a few community scripts to understand capabilities

### Basic Lua Programming
- [ ] Read Programming in Lua Chapters 1-3 (in this repo)
- [ ] Complete basic Lua exercises:
  - [ ] Variables and types
  - [ ] Functions and control flow
  - [ ] Tables as arrays and objects
- [ ] Practice with Lua REPL/interactive interpreter

### Norns Fundamentals
- [ ] Read official Norns documentation overview
- [ ] Complete Norns Study 1 ("first light")
- [ ] Understand script structure (init, key, enc, redraw)
- [ ] Create your first simple script using the template

**Milestone**: Create a basic script that responds to keys and encoders

---

## Phase 2: Norns Scripting (Weeks 3-4)

### Core Norns Concepts
- [ ] Complete Norns Study 2 ("many tomorrows")
- [ ] Master the parameter system
- [ ] Understand screen drawing API
- [ ] Learn clock and timing functions

### Practice Projects
- [ ] Build a simple step sequencer
- [ ] Create a parameter-controlled synthesizer interface
- [ ] Implement basic menu navigation
- [ ] Add MIDI input/output to a script

### Tools and Workflow
- [ ] Master Maiden editor and file management
- [ ] Learn debugging techniques (print statements, error handling)
- [ ] Understand script loading and reloading workflow

**Milestone**: Build a functional musical tool (sequencer, controller, or instrument)

---

## Phase 3: Advanced Scripting (Weeks 5-6)

### Advanced Norns Features
- [ ] Complete Norns Studies 3-4 ("patterning", "spacetime")
- [ ] Integrate Grid (if available) or simulate grid interactions
- [ ] Work with softcut (sampling and looping)
- [ ] Implement complex state management

### Lua Deep Dive
- [ ] Advanced Lua concepts (metatables, closures, coroutines)
- [ ] File I/O and data persistence
- [ ] Performance optimization techniques
- [ ] Error handling and robustness

### Community Integration
- [ ] Study existing community scripts
- [ ] Contribute to discussions on llllllll.co
- [ ] Share your work and get feedback

**Milestone**: Create a substantial script worthy of community sharing

---

## Phase 4: SuperCollider Basics (Weeks 7-8)

### SuperCollider Fundamentals
- [ ] Install SuperCollider IDE
- [ ] Complete official SuperCollider "Getting Started" tutorial
- [ ] Understand client-server architecture
- [ ] Learn basic synthesis (SinOsc, Saw, Pulse, etc.)

### Audio Programming Concepts
- [ ] Read DSP Fundamentals (in this repo)
- [ ] Understand sample rates, buffers, and audio routing
- [ ] Learn about envelopes, filters, and effects
- [ ] Practice with basic UGens

### SuperCollider for Norns
- [ ] Study existing Norns engines
- [ ] Understand the CroneEngine class
- [ ] Learn command/message system between Lua and SuperCollider

**Milestone**: Understand how Norns engines work and modify an existing engine

---

## Phase 5: Engine Development (Weeks 9-10)

### Building Your First Engine
- [ ] Start with the simple engine template (in this repo)
- [ ] Add commands for note on/off
- [ ] Implement basic polyphony
- [ ] Add parameter control from Lua

### Advanced Engine Concepts
- [ ] Voice management and allocation
- [ ] Audio effects integration
- [ ] Performance optimization
- [ ] Memory management

### Testing and Integration
- [ ] Create Lua scripts that use your engine
- [ ] Test polyphony and parameter changes
- [ ] Debug audio issues and performance problems

**Milestone**: Build a complete, working Norns engine with accompanying Lua script

---

## Phase 6: Specialization (Weeks 11-12)

Choose one or more areas to focus on:

### Option A: Grid Programming
- [ ] Complete Norns Study 5 ("physical")
- [ ] Learn grid interaction patterns
- [ ] Build grid-based sequencers or controllers
- [ ] Study grid-centric community scripts

### Option B: Sampling and Audio Processing
- [ ] Master softcut API
- [ ] Implement real-time audio effects
- [ ] Build sampling and looping tools
- [ ] Study audio analysis techniques

### Option C: Generative and Algorithmic Music
- [ ] Study probability and randomness in music
- [ ] Implement L-systems or cellular automata
- [ ] Create adaptive and responsive systems
- [ ] Build AI-assisted composition tools

### Option D: Hardware Integration
- [ ] MIDI controller integration
- [ ] CV and modular synth connectivity (Crow)
- [ ] Custom hardware interfaces
- [ ] OSC and network communication

**Milestone**: Become proficient in your chosen specialization area

---

## Phase 7: Mastery and Contribution (Ongoing)

### Advanced Projects
- [ ] Build complex, multi-faceted instruments
- [ ] Contribute engines or libraries to the community
- [ ] Mentor newcomers on llllllll.co
- [ ] Document and share your techniques

### Community Involvement
- [ ] Participate in community events and collaborations
- [ ] Submit scripts to the community catalog
- [ ] Write tutorials or documentation
- [ ] Help with Norns core development

### Continuous Learning
- [ ] Stay updated with Norns software updates
- [ ] Explore new SuperCollider techniques
- [ ] Study computer music research and papers
- [ ] Experiment with new musical concepts

**Milestone**: Become a valued contributor to the Norns community

---

## Daily Practice Recommendations

### Week 1-2 (Foundation)
- 30 minutes Lua programming practice
- 30 minutes exploring existing Norns scripts
- 15 minutes reading documentation

### Week 3-6 (Scripting)
- 45 minutes coding your own scripts
- 30 minutes studying community code
- 15 minutes documentation/theory

### Week 7-10 (SuperCollider)
- 30 minutes SuperCollider practice
- 30 minutes Norns engine work
- 30 minutes integration and testing

### Week 11+ (Specialization)
- 60 minutes focused project work
- 30 minutes community engagement
- 30 minutes exploration and experimentation

---

## Resources Checklist

### Essential Reading (in this repo)
- [ ] Programming in Lua Chapters 1-3
- [ ] SuperCollider tutorials overview
- [ ] DSP Fundamentals
- [ ] All quick reference guides

### External Resources
- [ ] Official Norns Studies (complete all 6)
- [ ] Programming in Lua (full book, 4th edition recommended)
- [ ] SuperCollider community tutorials
- [ ] Lines forum (llllllll.co) regular participation

### Tools Setup
- [ ] Norns device or Shield
- [ ] SuperCollider IDE (for engine development)
- [ ] Grid (optional but recommended)
- [ ] MIDI controller (optional)
- [ ] Audio interface (if needed)

---

## Assessment and Milestones

### Self-Assessment Questions

After Phase 2:
- Can you create a basic Norns script from scratch?
- Do you understand the parameter system?
- Can you implement key/encoder handlers effectively?

After Phase 4:
- Can you read and understand SuperCollider code?
- Do you understand basic synthesis concepts?
- Can you modify existing Norns engines?

After Phase 6:
- Have you built something unique and functional?
- Are you comfortable debugging audio and timing issues?
- Can you help others with Norns questions?

### Portfolio Projects
By the end of this roadmap, you should have:
1. **3-5 Norns scripts** showcasing different techniques
2. **1-2 SuperCollider engines** demonstrating synthesis skills
3. **1 substantial project** in your area of specialization
4. **Documentation** of your learning journey
5. **Community contributions** (forum posts, shared code, etc.)

---

*This roadmap is designed to take you from complete beginner to advanced Norns programmer in approximately 3 months of consistent practice. Adjust the timeline based on your available time and prior programming experience.*