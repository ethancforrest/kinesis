-- Grid Example Script
-- Demonstrates grid integration with Norns

engine.name = "PolyPerc"

-- Global variables
local g = grid.connect(1)
local notes = {}
local scale = {0, 2, 4, 5, 7, 9, 11}  -- Major scale
local root_note = 60
local grid_width = 16
local grid_height = 8

-- Grid state
local step_lights = {}
local playing_notes = {}
local current_step = 1
local sequence_length = 16

-- Initialize
function init()
  -- Initialize grid state
  for x = 1, grid_width do
    step_lights[x] = {}
    for y = 1, grid_height do
      step_lights[x][y] = 0
    end
  end
  
  -- Connect grid
  g.key = grid_key
  
  -- Parameters
  params:add_number("tempo", "Tempo", 60, 200, 120)
  params:add_number("root", "Root Note", 24, 84, 60)
  params:add_number("seq_len", "Sequence Length", 1, 16, 16)
  
  params:set_action("root", function(x)
    root_note = x
  end)
  
  params:set_action("seq_len", function(x)
    sequence_length = x
  end)
  
  -- Start sequencer
  clock.run(sequencer)
  
  -- Initial grid draw
  grid_redraw()
  redraw()
end

-- Grid key handler
function grid_key(x, y, z)
  if z == 1 then  -- Key press
    if x <= sequence_length then
      -- Toggle step
      step_lights[x][y] = step_lights[x][y] == 0 and 15 or 0
      
      -- If this is the current step, play the note
      if x == current_step then
        play_column(x)
      end
    end
  end
  grid_redraw()
end

-- Sequencer coroutine
function sequencer()
  while true do
    -- Clear previous step indicator
    local prev_step = current_step == 1 and sequence_length or current_step - 1
    
    -- Play current step
    play_column(current_step)
    
    -- Advance step
    current_step = current_step % sequence_length + 1
    
    -- Update display
    grid_redraw()
    redraw()
    
    -- Wait for next step
    clock.sync(1/4)  -- 16th notes
  end
end

-- Play notes in a column
function play_column(x)
  -- Stop previous notes
  for note, _ in pairs(playing_notes) do
    engine.note_off(note)
  end
  playing_notes = {}
  
  -- Play new notes
  for y = 1, grid_height do
    if step_lights[x][y] > 0 then
      local scale_degree = grid_height - y + 1
      local note = root_note + scale[((scale_degree - 1) % #scale) + 1] + 
                   math.floor((scale_degree - 1) / #scale) * 12
      
      engine.note_on(note, 0.8)
      playing_notes[note] = true
    end
  end
end

-- Draw grid
function grid_redraw()
  g:all(0)  -- Clear grid
  
  -- Draw sequence steps
  for x = 1, sequence_length do
    for y = 1, grid_height do
      local level = step_lights[x][y]
      
      -- Highlight current step
      if x == current_step then
        level = math.max(level, 4)
      end
      
      g:led(x, y, level)
    end
  end
  
  -- Draw sequence length indicator
  for x = sequence_length + 1, grid_width do
    g:led(x, 1, 2)
  end
  
  g:refresh()
end

-- Key handler
function key(n, z)
  if n == 2 and z == 1 then
    -- Clear all steps
    for x = 1, grid_width do
      for y = 1, grid_height do
        step_lights[x][y] = 0
      end
    end
    grid_redraw()
  elseif n == 3 and z == 1 then
    -- Random pattern
    for x = 1, sequence_length do
      for y = 1, grid_height do
        step_lights[x][y] = math.random() > 0.7 and 15 or 0
      end
    end
    grid_redraw()
  end
  redraw()
end

-- Encoder handler
function enc(n, d)
  if n == 1 then
    params:delta("tempo", d)
  elseif n == 2 then
    params:delta("root", d)
  elseif n == 3 then
    params:delta("seq_len", d)
  end
  redraw()
end

-- Screen drawing
function redraw()
  screen.clear()
  
  screen.level(15)
  screen.move(10, 10)
  screen.text("GRID SEQUENCER")
  
  screen.level(10)
  screen.move(10, 25)
  screen.text("Step: " .. current_step .. "/" .. sequence_length)
  
  screen.move(10, 35)
  screen.text("Tempo: " .. params:get("tempo"))
  
  screen.move(10, 45)
  screen.text("Root: " .. params:get("root"))
  
  screen.level(6)
  screen.move(10, 58)
  screen.text("K2: Clear  K3: Random")
  
  screen.update()
end

-- Cleanup
function cleanup()
  g:all(0)
  g:refresh()
end