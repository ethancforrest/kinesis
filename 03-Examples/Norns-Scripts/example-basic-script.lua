-- Basic Norns Script Template
-- A simple example showing core Norns scripting concepts

engine.name = "PolyPerc"

-- Global variables
local position = 0
local notes = {}
local playing = false

-- Initialize script
function init()
  -- Set up parameters
  params:add_number("tempo", "Tempo", 60, 200, 120)
  params:add_number("note", "Base Note", 24, 84, 60)
  params:add_control("amp", "Amplitude", controlspec.AMP)
  params:set("amp", 0.5)
  
  -- Parameter actions
  params:set_action("tempo", function(x)
    clock.set_tempo(x)
  end)
  
  -- Start the clock
  clock.run(sequencer)
  
  print("Basic script loaded!")
end

-- Sequencer coroutine
function sequencer()
  while true do
    if playing then
      local note = params:get("note") + math.random(0, 12)
      engine.hz(midi_to_hz(note))
      position = (position + 1) % 8
    end
    clock.sleep(0.25)  -- 16th notes
  end
end

-- Key handler
function key(n, z)
  if n == 2 and z == 1 then
    -- Key 2: toggle playback
    playing = not playing
    redraw()
  elseif n == 3 and z == 1 then
    -- Key 3: manual trigger
    local note = params:get("note") + math.random(0, 12)
    engine.hz(midi_to_hz(note))
  end
end

-- Encoder handler
function enc(n, d)
  if n == 1 then
    -- Encoder 1: tempo
    params:delta("tempo", d)
  elseif n == 2 then
    -- Encoder 2: base note
    params:delta("note", d)
  elseif n == 3 then
    -- Encoder 3: amplitude
    params:delta("amp", d / 100)
  end
  redraw()
end

-- Screen drawing
function redraw()
  screen.clear()
  
  -- Title
  screen.level(15)
  screen.move(10, 10)
  screen.text("BASIC SCRIPT")
  
  -- Status
  screen.level(10)
  screen.move(10, 25)
  screen.text("Status: " .. (playing and "PLAYING" or "STOPPED"))
  
  -- Position indicator
  screen.move(10, 35)
  screen.text("Position: " .. position)
  
  -- Parameters
  screen.move(10, 50)
  screen.text("Tempo: " .. params:get("tempo"))
  screen.move(10, 60)
  screen.text("Note: " .. params:get("note"))
  
  screen.update()
end

-- Utility function
function midi_to_hz(note)
  return (440 / 32) * (2 ^ ((note - 9) / 12))
end

-- Cleanup
function cleanup()
  print("Basic script cleaned up!")
end