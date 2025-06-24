-- meadowphysics
-- midi out capability
-- engine PolyPerc
--
-- key2  toggle scale mode^
-- key3  save meadowphysics
-- key3^ save scales
-- enc1  volume
-- enc2  root note
-- enc3  bpm
--

engine.name = "PolyPerc"

-- Optional halfsecond library for advanced timing (from awake script)
local hs
local halfsecond_available = pcall(function() 
  hs = include("awake/lib/halfsecond")
end)
if not halfsecond_available then
  print("Note: halfsecond library not available (requires awake script)")
  hs = nil
end

local data_dir = _path.code .. "meadowphysics/data/"

local shift = 0

local MeadowPhysics = require "lib/meadowphysics"
local mp

local GridScales = require "lib/gridscales"
local gridscales

local MusicUtil = require "musicutil"

local g = grid.connect()
if not g then
  print("Warning: No grid device found")
end

local BeatClock = require "beatclock"

local options = {}
options.OUTPUT = {"audio", "midi", "audio + midi"}
options.STEP_LENGTH_NAMES = {"1 bar", "1/2", "1/3", "1/4", "1/6", "1/8", "1/12", "1/16", "1/24", "1/32", "1/48", "1/64"}
options.STEP_LENGTH_DIVIDERS = {1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64}

local midi_out_device
local midi_out_channel
local midi_channel_offset

local notes = {}
local row_notes = {1, 2, 3, 4, 5, 6, 7, 8} -- Per-row note tables
local active_notes = {}
local row_active_notes = {1, 2, 3, 4, 5, 6, 7, 8} -- Per-row active notes

-- Initialize per-row tables
for i = 1, 8 do
  row_notes[i] = {}
  row_active_notes[i] = {}
end

local clk = BeatClock.new()
local clk_midi = midi.connect()
if clk_midi then
  clk_midi.event = function(data) clk:process_midi(data) end
else
  print("Warning: Could not connect MIDI for clock")
end

local notes_off_metro = metro.init()

local function all_notes_off()
  if (params:get("output") == 2 or params:get("output") == 3) then
    for row = 1, 8 do
      local channel = midi_channel_offset + row - 1
      if channel <= 16 then
        for _,a in pairs(row_active_notes[row]) do
          midi_out_device:note_off(a.note, nil, channel)
        end
        row_active_notes[row] = {}
      end
    end
    -- Legacy single channel notes off
    for _,a in pairs(active_notes) do
      midi_out_device:note_off(a, nil, midi_out_channel)
    end
  end
  active_notes = {}
  for i = 1, 8 do
    row_active_notes[i] = {}
  end
end

local function step()
	all_notes_off()

	mp:clock()
	
	-- Process per-row notes with individual MIDI channels
	for row = 1, 8 do
		local channel = midi_channel_offset + row - 1
		if channel <= 16 then
			for _,n in pairs(row_notes[row]) do
				local f = MusicUtil.note_num_to_freq(n)
				if (params:get("output") == 1 or params:get("output") == 3) then
					engine.hz(f)
				end

				if (params:get("output") == 2 or params:get("output") == 3) then
					midi_out_device:note_on(n, 96, channel)
					table.insert(row_active_notes[row], {note = n, channel = channel})
				end
			end
		end
		row_notes[row] = {}
	end
	
	-- Legacy single channel notes (for backwards compatibility)
	for _,n in pairs(notes) do
		local f = MusicUtil.note_num_to_freq(n)
		if (params:get("output") == 1 or params:get("output") == 3) then
			engine.hz(f)
		end

    if (params:get("output") == 2 or params:get("output") == 3) then
      midi_out_device:note_on(n, 96, midi_out_channel)
      table.insert(active_notes, n)
		end
	end
	notes = {}

	if params:get("note_length") < 4 then
		notes_off_metro:start((60 / clk.bpm / clk.steps_per_beat / 4) * params:get("note_length"), 1)
	end
end

local function stop()
	all_notes_off()
end

local function reset_pattern()
	clk:reset()
end

local grid_clk 

local screen_clk 

function init()
	-- meadowphysics
	local success, result = pcall(function()
		return MeadowPhysics.loadornew(data_dir .. "mp.data")
	end)
	if success then
		mp = result
		mp.mp_event = event
		print("Meadowphysics data loaded")
	else
		print("Error loading meadowphysics data, using defaults")
		mp = MeadowPhysics.new()
		mp.mp_event = event
	end
	
	-- gridscales
	local success2, result2 = pcall(function()
		return GridScales.loadornew(data_dir .. "gridscales.data")
	end)
	if success2 then
		gridscales = result2
		print("Gridscales data loaded")
	else
		print("Error loading gridscales data, using defaults")
		gridscales = GridScales.new()
	end
	gridscales:add_params()

	-- metro / midi
	midi_out_device = midi.connect(1)
	if midi_out_device then
		midi_out_device.event = function() end
	else
		print("Warning: Could not connect MIDI output device")
	end

	clk.on_step = step
	clk.on_stop = stop
	clk.on_select_internal = function() clk:start() end
	clk.on_select_external = reset_pattern
	clk:add_clock_params()
	params:set("bpm", 120)
	
	-- Initialize MIDI channel offset
	midi_channel_offset = 1

	notes_off_metro.event = all_notes_off
	
	params:add {
		type = "option",
		id = "output",
		name = "output",
		options = options.OUTPUT,
		action = all_notes_off
	}

	params:add {
		type = "number",
		id = "midi_out_device",
		name = "midi out device",
		min = 1, max = 4, default = 1,
		action = function(value) 
			midi_out_device = midi.connect(value)
			if not midi_out_device then
				print("Warning: Could not connect to MIDI device " .. value)
			end
		end
	}

	params:add {
		type = "number",
		id = "midi_out_channel",
		name = "midi out channel",
		min = 1, max = 16, default = 1,
		action = function(value)
			all_notes_off()
			midi_out_channel = value
		end
	}

	params:add {
		type = "number",
		id = "midi_channel_offset",
		name = "row 1 midi channel",
		min = 1, max = 16, default = 1,
		action = function(value)
			all_notes_off()
			midi_channel_offset = value
		end
	}
	
	params:add_separator()

	params:add {
		type = "option",
		id = "step_length",
		name = "step length",
		options = options.STEP_LENGTH_NAMES,
		default = 4,
		action = function(value)
			clk.ticks_per_step = 96 / options.STEP_LENGTH_DIVIDERS[value]
			clk.steps_per_beat = options.STEP_LENGTH_DIVIDERS[value] / 4
			clk:bpm_change(clk.bpm)
		end
	}

	params:add {
		type = "option",
		id = "note_length",
		name = "note length",
		options = {"25%", "50%", "75%", "100%"},
		default = 4
	}

	-- metro
	grid_clk = metro.init()
	grid_clk.event = gridredraw 
	grid_clk.time = 1 / 30

	screen_clk = metro.init()
	screen_clk.event = function() redraw() end
	screen_clk.time = 1 / 15

	-- engine 
  params:add {
		type = "control",
		id = "amp",
		controlspec = controlspec.new(0,1,'lin',0,0.5,''),
    action = function(x) engine.amp(x) end
	}

  params:add {
		type = "control",
		id = "pw",
		controlspec = controlspec.new(0,100,'lin',0,50,'%'),
    action = function(x) engine.pw(x/100) end
	}

	params:add {
		type = "control",
		id = "release",
		controlspec = controlspec.new(0.1,3.2,'lin',0,1.2,'s'),
    action = function(x) engine.release(x) end
	}

  params:add {
		type = "control",
		id = "cutoff",
		controlspec = controlspec.new(50,5000,'exp',0,555,'hz'),
    action = function(x) engine.cutoff(x) end
	}

  params:add {
		type = "control",
		id = "gain",
		controlspec = controlspec.new(0,4,'lin',0,1,''),
    action = function(x) engine.gain(x) end
	}

	params:default()
	params:add_separator()

	-- grid
	if g then mp:gridredraw(g) end

	screen_clk:start()
	grid_clk:start()
	clk:start()

  if hs then hs.init() end
end

function event(row, state)
	if state == 1 then
		local note = params:get("root_note") + gridscales:note(row)
		
		-- Route to per-row notes for multi-channel MIDI
		if row >= 1 and row <= 8 then
			table.insert(row_notes[row], note)
		end
		
		-- Also add to legacy notes table for backwards compatibility
		table.insert(notes, note)
	end
end

function redraw()
	if shift == 1 then
		draw_gridscales()
	else
		draw_mp()
	end
end

function draw_gridscales()
	gridscales:redraw()
end

function draw_mp()
	screen.clear()
	screen.aa(1)

	for i=1,8 do
		if mp.position[i] >= 1 then
			local y = (i-1)*8
			local x = 0

			x = (mp.position[i]-1)*8
			screen.level(15)
			screen.move(x, y)
			screen.rect(x, y, 8, 8)
			screen.fill()
			screen.stroke()
		end
	end

	screen.level(4)
	for i=0,8 do
		local y = i*8
		screen.move(0,y)
		screen.line(128,y)
		screen.stroke()
		screen.close()
	end

	for i=0,16 do
		local x = i*8
		screen.move(x, 0)
		screen.line(x, 64)
		screen.stroke()
		screen.close()
	end

	screen.update()
end

function draw_bpm()
	screen.clear()
	screen.aa(1)

	screen.move(64,32)
	screen.font_size(32)
	screen.text(params:get("bpm"))
	screen.stroke()

	screen.update()
end

function g.key(x, y, z)
	if shift == 1 then
		gridscales:gridevent(x, y, z)
	else
		mp:gridevent(x, y, z)
	end
end

function gridredraw()
	if shift == 1 then
		gridscales:gridredraw(g)
	else
		mp:gridredraw(g)
	end
end

function enc(n, d)
	if n == 1 then
		params:delta("output", d)
	elseif n == 2 then
		params:delta("root_note", d)
		draw_gridscales()
	elseif n == 3 then
		params:delta("bpm", d)
		draw_bpm()
	end
end

function key(n, z)
	if n == 1 and z == 1 then
		gridscales:set_scale(8)
	end
	if n == 2 and z == 1 then 
		shift = 1 - shift
	elseif n == 3 and z == 1 then
		if shift == 1 then
			local success, err = pcall(function()
				gridscales:save(data_dir .. "gridscales.data")
			end)
			if not success then
				print("Error saving gridscales: " .. (err or "unknown error"))
			else
				print("Gridscales saved")
			end
		else
			local success, err = pcall(function()
				mp:save(data_dir .. "mp.data")
			end)
			if not success then
				print("Error saving meadowphysics: " .. (err or "unknown error"))
			else
				print("Meadowphysics saved")
			end
		end
	end
end

-- Cleanup function to properly manage resources
function cleanup()
  print("meadowphysics cleanup")
  
  -- Stop all active clocks and metros
  if clk then
    clk:stop()
  end
  
  if notes_off_metro then
    notes_off_metro:stop()
  end
  
  -- Send all notes off to prevent stuck MIDI notes
  all_notes_off()
  
  -- Disconnect MIDI
  if midi_out_device then
    midi_out_device.event = nil
  end
  
  if clk_midi then
    clk_midi.event = nil
  end
  
  -- Clear any remaining state
  if mp then
    mp:stop()
  end
  
  print("meadowphysics cleanup complete")
end

