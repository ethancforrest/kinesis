-- tambla: bending rhythmic arpeggio
-- original version from https://github.com/ngwese/tambla
-- this file represents the original code for reference

engine.name = 'wsyn'

local sky = include('tambla/lib/dep/sky')
local model = include('tambla/lib/model')
local pages = include('tambla/lib/pages')
local devices = include('tambla/lib/devices')

local MU = require 'musicutil'

local tambla = model.Tambla()
local ui_pages = pages.UIPages(tambla)
local device_rack = devices.rack()

function init()
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
  end)

  -- set default output
  device_rack:configure(params:string('output'))

  -- arc/grid setup
  if arc.device then
    print('configuring arc')
    arc.device.delta = function(n, delta) ui_pages:arc_delta(n, delta) end
  end

  if grid.device then
    print('configuring grid')
    grid.device.key = function(x, y, z) ui_pages:grid_key(x, y, z) end
  end

  -- engine setup
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

  params:set_action('wsyn_amp', function(x) engine.wsyn_amp(x) end)
  params:set_action('wsyn_hzlag', function(x) engine.wsyn_hzlag(x) end)
  params:set_action('wsyn_amp_attack', function(x) engine.wsyn_amp_attack(x) end)
  params:set_action('wsyn_amp_release', function(x) engine.wsyn_amp_release(x) end)
  params:set_action('wsyn_lpf_hz', function(x) engine.wsyn_lpf_hz(x) end)
  params:set_action('wsyn_lpf_q', function(x) engine.wsyn_lpf_q(x) end)
  params:set_action('wsyn_hpf_hz', function(x) engine.wsyn_hpf_hz(x) end)
  params:set_action('wsyn_hpf_q', function(x) engine.wsyn_hpf_q(x) end)

  params:set_action('delay_time', function(x) engine.delay_time(x) end)
  params:set_action('delay_feedback', function(x) engine.delay_feedback(x) end)
  params:set_action('delay_level', function(x) engine.delay_level(x) end)

  -- set parameter defaults
  params:bang()

  -- load startup set
  tambla:load_set('/home/we/dust/data/tambla/sets/start.tambla')

  tambla:set_tick(function(tick, voice, hz, vel)
    local event = sky.mk_event { type = 'tick', tick = tick, voice = voice, hz = hz, vel = vel }
    device_rack:process(event)
  end)

  clock.run(tambla.run, tambla)

  redraw()
end

function key(n, z)
  ui_pages:key(n, z)
  redraw()
end

function enc(n, d)
  ui_pages:enc(n, d)
  redraw()
end

function redraw()
  ui_pages:draw()
  screen.update()
end

function cleanup()
  tambla:stop()
end

function midi.add()
  print('midi device added')
end

function midi.remove()
  print('midi device removed')
end