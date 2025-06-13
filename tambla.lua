-- bending rhythmic arpeggio
-- 1.2.0 @ngwese
--
-- pages: macro <play> edit
--
-- E1 select horizontal/column
-- E2 row param
-- E3 row param value
--
-- K1 = ALT
-- ALT-E1 = select row
-- ALT-K2 = page left
-- ALT-K3 = page right
--

include('sky/unstable')
sky.use('device/make_note')
sky.use('device/arp')
sky.use('device/switcher')
sky.use('device/transform')
sky.use('lib/device/linn') -- TODO: publish local fixes
sky.use('io/norns')
sky.use('lib/io/grid') -- TODO: publish local fixes
sky.use('lib/io/crow')
sky.use('io/arc')
sky.use('engine/polyperc')

local halfsecond = include('lib/halfsecond')

local model = include('lib/model')
local pages = include('lib/pages')
local devices = include('lib/devices')
local wsyn = include('lib/wsyn')

tambla = model.Tambla{
  tick_period = 1/64,
  slots = {
    model.Pattern():randomize(),
    model.Pattern():randomize(),
    model.Pattern(),
    model.Pattern()
  }
}

main_logger = sky.Logger{
  bypass = true,
  filter = function(e)
    return tambla.is_tick(e) or sky.is_clock(e) -- or sky.is_type(e, sky.types.CONTROL_CHANGE)
  end,
}

--
-- midi outputs
--

local function build_midi_out(n)
  local out = sky.Chain{
    sky.Channel{ channel = n },
    sky.Output{
      device = midi.connect(2)
    }
  }
  return out
end

midi_a = build_midi_out(1)
midi_b = build_midi_out(2)
midi_c = build_midi_out(3)
midi_d = build_midi_out(4)

--
-- internal audio engine
--

engine_out = sky.Chain{
  sky.Random{
    chance = 0.5,
    transform = function(e) e.hz = e.hz * 2 end
  },
  sky.Output{
    device = sky.NornsAudioEngine{
      hz_to_engine_fn = function(hz) return mu.hz_to_note_num(hz) end,
      engine = engine,
      engine_name = 'PolyPerc',
      amp = 0.5,
      source = 'internal',
    }
  }
}

--
-- crow
--

crow_out = sky.Chain{
  devices.Scale{},
  sky.Switch{
    pos = 1,
    outputs = {
      sky.Output{
        device = sky.CrowCV{ n = 1 },
      },
      sky.Output{
        device = sky.CrowCV{ n = 2 },
      },
    }
  }
}

crow_clock_out = sky.Chain{
  sky.Transform{
    transform = function(e)
      e.state = 1
      e.duration = 0.1
      return e
    end
  },
  sky.Output{
    device = sky.CrowGate{ n = 3 },
  }
}

crow_gate_out = sky.Chain{
  sky.Transform{
    transform = function(e)
      e.state = e.gate and 1 or 0
      e.duration = e.gate and e.dur_s or 0.1
      return e
    end
  },
  sky.Output{
    device = sky.CrowGate{ n = 4 },
  }
}

--
-- w/syn
--

wsyn_out = wsyn.output()

--
-- arc
--

arc_controller = sky.Chain{
  sky.ArcInput{
    device = arc.connect(1),
    n = 1,
    sensitivity = 5/32,
  },
  sky.Transform{
    transform = function(e)
      if e.type == sky.types.CONTROL_CHANGE then
        e.param = 'gain'
        e.value = util.clamp(e.value, 0, 1)
      end
      return e
    end
  },
  sky.Output{
    bypass = false,
    device = tambla
  },
}

--
-- routing
--

arp_a = sky.ArpEngine{ hold = true }
arp_b = sky.ArpEngine{ hold = false }

linn_a = sky.LinnEngine{ name = 'a', n = 16 }
linn_b = sky.LinnEngine{ name = 'b', n = 16 }

global_switch = sky.Switch{
  pos = 1,
  outputs = {
    midi_a,
    engine_out,
    crow_out,
    wsyn_out
  }
}

tambla_out = sky.Chain{
  devices.TamblaNoteGen{ model = tambla },
  devices.Route{},
  devices.Random{},
  devices.Scale{},
  -- global_switch,
  sky.Switcher{
    pos = 1,
    slots = {
      arp_a,
      arp_b,
      linn_a,
      linn_b,
      sky.Chain{
        sky.NoteOn{},
        global_switch
      },
    }
  }
}

tambla_clock_out = sky.Chain{
  sky.Filter{
    filter = function(e) return tambla.is_tick(e) and (e.nth % 16 == 0) end
  },
  crow_clock_out
}

tambla_gate_out = sky.Chain{
  sky.Filter{
    filter = function(e) return sky.is_type(e, sky.types.NOTE_ON, sky.types.NOTE_OFF) end
  },
  crow_gate_out
}

clock_in = sky.Chain{
  sky.Input{
    device = sky.NornsClock{ source = 'internal', period = tambla.tick_period },
  },
  sky.Broadcaster{
    destinations = {
      tambla_out,
      tambla_clock_out,
      tambla_gate_out,
      main_logger,
    }
  }
}

--
-- grid
--

grid_controller = sky.Chain{
  sky.GridInput{
    device = grid.connect(1),
  },
  sky.Output{
    bypass = false,
    device = tambla
  },
}

--
-- norns
--

norns_controller = sky.Chain{
  sky.NornsInput{},
  sky.Output{
    bypass = false,
    device = tambla
  },
}

--
-- controller and device setup
--

controller = pages.Controller{
  pages = {
    pages.MacroPage{ model = tambla },
    pages.PlayPage{ model = tambla },
    pages.EditPage{ model = tambla },
  }
}

tambla_device = devices.TamblaNoteGen{
  model = tambla,
  controller = controller
}

function init()
  -- clock_in:start() -- allow sky to clock itself?
  clock.run(function()
    clock.sync(1/64)
    while true do
      local e = tambla:mk_tick()
      tambla_out:push(e)
      tambla_clock_out:push(e)
      tambla_gate_out:push(e)
      main_logger:push(e)
      clock.sync(1/64)
    end
  end)

  -- setup controller
  controller:set_device(tambla)
  controller:set_page(1)

  -- TODO: this may become the default behavior for devices
  tambla.process_event = function(self, e)
    controller:process_event(e)
  end

  -- grid setup
  tambla.grid_event = function(self, e)
    controller:grid_event(e)
  end

  -- start devices
  clock_in:start()
  norns_controller:start()
  grid_controller:start()
  arc_controller:start()

  -- params setup
  halfsecond.init()
end

function cleanup()
  clock_in:stop()
  norns_controller:stop()
  grid_controller:stop()
  arc_controller:stop()
end

-- norns hooks

function enc(n, d)
  controller:enc(n, d)
end

function key(n, z)
  controller:key(n, z)
end

function redraw()
  controller:redraw()
end