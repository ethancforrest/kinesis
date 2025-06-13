-- tambla: bending rhythmic arpeggio 
-- IMPROVED VERSION with enhanced usability
-- Original by ngwese, improvements for better user experience
-- Version: 1.1.0 - Phase 1 Improvements

engine.name = 'wsyn'

local sky = include('tambla/lib/dep/sky')
local model = include('tambla/lib/model')
local pages = include('tambla/lib/pages')
local devices = include('tambla/lib/devices')

local MU = require 'musicutil'

-- IMPROVEMENT: Add global state tracking for UI enhancements
local UI_STATE = {
  help_mode = false,
  help_timer = 0,
  tooltip_text = "",
  tooltip_timer = 0,
  held_keys = {},
  last_activity = 0,
  version = "1.1.0"
}

local tambla = model.Tambla()
local ui_pages = pages.UIPages(tambla)
local device_rack = devices.rack()

-- IMPROVEMENT: Add help text system
local HELP_TEXT = {
  play = {
    title = "PLAY PAGE - Performance Mode",
    controls = {
      "E1: Select slot (pattern bank)",
      "E2: Select row (1-4)",  
      "E3: Adjust parameter",
      "K2: Switch pages",
      "K3: Start/stop transport",
      "Hold K1: Show this help"
    },
    tips = {
      "Hold MIDI keys to trigger rows",
      "Each row plays different rhythms",
      "Bend < 1.0 = fast→slow timing",
      "Bend > 1.0 = slow→fast timing"
    }
  },
  edit = {
    title = "EDIT PAGE - Step Programming", 
    controls = {
      "E1: Select row (1-4)",
      "E2: Select step",
      "E3: Adjust step value",
      "K3: Toggle step on/off",
      "Hold K1: Show this help"
    },
    tips = {
      "Chance = probability of step",
      "Velocity = note loudness", 
      "Duration = note length",
      "Bright = active step"
    }
  },
  macro = {
    title = "MACRO PAGE - Pattern Management",
    controls = {
      "E1: Select slot",
      "E2: Navigate options",
      "E3: Adjust/browse",
      "K3: Execute action",
      "Hold K1: Show this help"
    },
    tips = {
      "Copy/paste between slots",
      "Save patterns to files",
      "Load pattern collections",
      "Randomize for inspiration"
    }
  }
}

-- IMPROVEMENT: Enhanced initialization with user feedback
function init()
  print("tambla " .. UI_STATE.version .. " - loading...")
  
  local device_graph = {
    ['off'] = {},
    ['midi-1'] = { 
      devices.midi_device(midi.connect(1))
    },
    ['engine'] = { 
      devices.engine_device() 
    },
    ['crow'] = { 
      devices.crow_device() 
    },
    ['midi-1-engine'] = { 
      devices.midi_device(midi.connect(1)),
      devices.engine_device()
    },
    ['midi-1-crow'] = { 
      devices.midi_device(midi.connect(1)),
      devices.crow_device()
    },
    ['engine-crow'] = { 
      devices.engine_device(),
      devices.crow_device()
    },
    ['all'] = { 
      devices.midi_device(midi.connect(1)),
      devices.engine_device(),
      devices.crow_device()
    }
  }

  device_rack:register(device_graph)

  -- global configuration
  params:add_option('output', 'output', 
    { 'off', 'midi-1', 'engine', 'crow', 'midi-1-engine', 'midi-1-crow', 'engine-crow', 'all' }, 3)
  params:set_action('output', function(value)
    local spec = params:string('output')
    device_rack:configure(spec)
    show_tooltip("Output: " .. spec)
  end)

  -- set default output
  device_rack:configure(params:string('output'))

  -- arc/grid setup with improved feedback
  if arc.device then
    print('✓ arc configured')
    arc.device.delta = function(n, delta) 
      ui_pages:arc_delta(n, delta)
      UI_STATE.last_activity = util.time()
    end
  end

  if grid.device then
    print('✓ grid configured')  
    grid.device.key = function(x, y, z) 
      ui_pages:grid_key(x, y, z)
      UI_STATE.last_activity = util.time()
    end
  end

  -- engine setup with improved parameter descriptions
  params:add_control('wsyn_amp', 'amp', controlspec.new(0, 1, 'lin', 0.01, 0.8))
  params:add_control('wsyn_hzlag', 'hz lag', controlspec.new(0.001, 1, 'exp', 0.001, 0.025, 's'))
  params:add_control('wsyn_amp_attack', 'attack', controlspec.new(0.001, 5, 'exp', 0.001, 0.001, 's'))
  params:add_control('wsyn_amp_release', 'release', controlspec.new(0.001, 10, 'exp', 0.001, 0.5, 's'))
  params:add_control('wsyn_lpf_hz', 'lpf hz', controlspec.new(20, 20000, 'exp', 1, 4000, 'Hz'))
  params:add_control('wsyn_lpf_q', 'lpf q', controlspec.new(0.01, 100, 'exp', 0.01, 1))
  params:add_control('wsyn_hpf_hz', 'hpf hz', controlspec.new(20, 20000, 'exp', 1, 20, 'Hz'))
  params:add_control('wsyn_hpf_q', 'hpf q', controlspec.new(0.01, 100, 'exp', 0.01, 1))

  params:add_separator()

  params:add_control('delay_time', 'delay time', controlspec.new(0.0, 0.75, 'lin', 0.01, 0.20, 's'))
  params:add_control('delay_feedback', 'delay feedback', controlspec.new(0.0, 1.0, 'lin', 0.01, 0.1))
  params:add_control('delay_level', 'delay level', controlspec.new(0.0, 1.0, 'lin', 0.01, 0.35))

  -- IMPROVEMENT: Add tooltips for parameter changes
  params:set_action('wsyn_amp', function(x) 
    engine.wsyn_amp(x) 
    show_tooltip("Amp: " .. string.format("%.2f", x))
  end)
  params:set_action('wsyn_hzlag', function(x) 
    engine.wsyn_hzlag(x)
    show_tooltip("Hz Lag: " .. string.format("%.3f", x) .. "s")
  end)
  params:set_action('wsyn_amp_attack', function(x) 
    engine.wsyn_amp_attack(x)
    show_tooltip("Attack: " .. string.format("%.3f", x) .. "s")
  end)
  params:set_action('wsyn_amp_release', function(x) 
    engine.wsyn_amp_release(x)
    show_tooltip("Release: " .. string.format("%.3f", x) .. "s")
  end)
  params:set_action('wsyn_lpf_hz', function(x) 
    engine.wsyn_lpf_hz(x)
    show_tooltip("LPF: " .. math.floor(x) .. "Hz")
  end)
  params:set_action('wsyn_lpf_q', function(x) 
    engine.wsyn_lpf_q(x)
    show_tooltip("LPF Q: " .. string.format("%.2f", x))
  end)
  params:set_action('wsyn_hpf_hz', function(x) 
    engine.wsyn_hpf_hz(x)
    show_tooltip("HPF: " .. math.floor(x) .. "Hz")
  end)
  params:set_action('wsyn_hpf_q', function(x) 
    engine.wsyn_hpf_q(x)
    show_tooltip("HPF Q: " .. string.format("%.2f", x))
  end)

  params:set_action('delay_time', function(x) 
    engine.delay_time(x)
    show_tooltip("Delay: " .. string.format("%.2f", x) .. "s")
  end)
  params:set_action('delay_feedback', function(x) 
    engine.delay_feedback(x)
    show_tooltip("Feedback: " .. math.floor(x * 100) .. "%")
  end)
  params:set_action('delay_level', function(x) 
    engine.delay_level(x)
    show_tooltip("Delay Level: " .. math.floor(x * 100) .. "%")
  end)

  -- set parameter defaults
  params:bang()

  -- load startup set with feedback
  local success = tambla:load_set('/home/we/dust/data/tambla/sets/start.tambla')
  if success then
    show_tooltip("Loaded startup set")
  else
    show_tooltip("Using default patterns")
  end

  tambla:set_tick(function(tick, voice, hz, vel)
    local event = sky.mk_event { type = 'tick', tick = tick, voice = voice, hz = hz, vel = vel }
    device_rack:process(event)
    
    -- IMPROVEMENT: Track note activity for UI feedback
    track_note_activity(voice, hz, vel)
  end)

  clock.run(tambla.run, tambla)
  
  -- IMPROVEMENT: Start UI update timer
  clock.run(ui_timer)

  print("tambla ready! Hold K1 for help")
  show_tooltip("Welcome to tambla " .. UI_STATE.version)
  redraw()
end

-- IMPROVEMENT: Track note activity for visual feedback
function track_note_activity(voice, hz, vel)
  UI_STATE.held_keys[voice] = {
    hz = hz,
    vel = vel,
    time = util.time()
  }
  
  -- Clean up old notes after 1 second
  for v, note in pairs(UI_STATE.held_keys) do
    if util.time() - note.time > 1.0 then
      UI_STATE.held_keys[v] = nil
    end
  end
end

-- IMPROVEMENT: Tooltip system
function show_tooltip(text)
  UI_STATE.tooltip_text = text
  UI_STATE.tooltip_timer = 2.0  -- Show for 2 seconds
end

-- IMPROVEMENT: UI update timer for tooltips and animations
function ui_timer()
  while true do
    clock.sleep(1/30)  -- 30 FPS for smooth UI
    
    -- Update tooltip timer
    if UI_STATE.tooltip_timer > 0 then
      UI_STATE.tooltip_timer = UI_STATE.tooltip_timer - (1/30)
      if UI_STATE.tooltip_timer <= 0 then
        UI_STATE.tooltip_text = ""
      end
    end
    
    -- Update help timer
    if UI_STATE.help_timer > 0 then
      UI_STATE.help_timer = UI_STATE.help_timer - (1/30)
      if UI_STATE.help_timer <= 0 then
        UI_STATE.help_mode = false
      end
    end
    
    -- Redraw if we have active UI elements
    if UI_STATE.tooltip_timer > 0 or UI_STATE.help_mode then
      redraw()
    end
  end
end

-- IMPROVEMENT: Enhanced key handling with help system
function key(n, z)
  UI_STATE.last_activity = util.time()
  
  -- Help system: Long press K1 to show help
  if n == 1 then
    if z == 1 then
      -- Start help timer
      clock.run(function()
        clock.sleep(1.0)  -- Long press threshold
        if UI_STATE.help_timer <= 0 then  -- Only if key still held
          UI_STATE.help_mode = not UI_STATE.help_mode
          UI_STATE.help_timer = UI_STATE.help_mode and 10.0 or 0  -- Show help for 10 seconds
          redraw()
        end
      end)
    else
      -- Key released - cancel help if it was just starting
      if UI_STATE.help_timer <= 0 then
        UI_STATE.help_mode = false
      end
    end
  end
  
  -- Pass through to original handler if not in help mode
  if not UI_STATE.help_mode then
    ui_pages:key(n, z)
  end
  
  redraw()
end

-- IMPROVEMENT: Enhanced encoder handling with activity tracking  
function enc(n, d)
  UI_STATE.last_activity = util.time()
  
  -- Pass through to original handler
  ui_pages:enc(n, d)
  redraw()
end

-- IMPROVEMENT: Enhanced redraw with help overlay and tooltips
function redraw()
  screen.clear()
  
  -- Draw main UI
  ui_pages:draw()
  
  -- IMPROVEMENT: Draw help overlay if active
  if UI_STATE.help_mode then
    draw_help_overlay()
  end
  
  -- IMPROVEMENT: Draw tooltip if active
  if UI_STATE.tooltip_timer > 0 then
    draw_tooltip()
  end
  
  -- IMPROVEMENT: Draw status indicators
  draw_status_indicators()
  
  screen.update()
end

-- IMPROVEMENT: Help overlay system
function draw_help_overlay()
  local current_page = ui_pages:current_page_name() or "play"
  local help = HELP_TEXT[current_page]
  
  if not help then return end
  
  -- Semi-transparent background
  screen.level(8)
  screen.rect(2, 2, 124, 60)
  screen.fill()
  
  -- Border
  screen.level(15)
  screen.rect(2, 2, 124, 60)
  screen.stroke()
  
  -- Title
  screen.level(15)
  screen.move(6, 12)
  screen.text(help.title)
  
  -- Controls
  screen.level(12)
  local y = 22
  for _, control in ipairs(help.controls) do
    screen.move(6, y)
    screen.text(control)
    y = y + 7
  end
  
  -- Tips (if space allows)
  if #help.tips > 0 and y < 50 then
    screen.level(8)
    screen.move(6, y + 2)
    screen.text("Tips:")
    y = y + 9
    
    screen.level(10)
    for i, tip in ipairs(help.tips) do
      if y < 58 then
        screen.move(6, y)
        screen.text("• " .. tip)
        y = y + 7
      end
    end
  end
  
  -- Footer
  screen.level(6)
  screen.move(6, 58)
  screen.text("Release K1 to close help")
end

-- IMPROVEMENT: Tooltip display
function draw_tooltip()
  if UI_STATE.tooltip_text == "" then return end
  
  local text_width = string.len(UI_STATE.tooltip_text) * 4
  local x = 64 - text_width / 2
  local y = 58
  
  -- Background
  screen.level(8)
  screen.rect(x - 2, y - 6, text_width + 4, 8)
  screen.fill()
  
  -- Text
  screen.level(15)
  screen.move(x, y)
  screen.text(UI_STATE.tooltip_text)
end

-- IMPROVEMENT: Status indicators
function draw_status_indicators()
  -- Transport status
  screen.level(6)
  screen.move(120, 8)
  if tambla:is_playing() then
    screen.text("▶")
  else
    screen.text("⏸")
  end
  
  -- Active voice count
  local active_voices = 0
  for _ in pairs(UI_STATE.held_keys) do
    active_voices = active_voices + 1
  end
  
  if active_voices > 0 then
    screen.level(10)
    screen.move(115, 64)
    screen.text(active_voices)
  end
  
  -- Version indicator (subtle)
  screen.level(3)
  screen.move(2, 64)
  screen.text("v" .. UI_STATE.version)
end

function cleanup()
  tambla:stop()
  print("tambla stopped")
end

function midi.add()
  print('✓ midi device added')
  show_tooltip("MIDI device connected")
end

function midi.remove()
  print('⚠ midi device removed')
  show_tooltip("MIDI device disconnected")
end