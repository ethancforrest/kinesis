
local tabutil = require "tabutil"

-- Try to load bit library for Lua 5.1 compatibility
local bit = bit or bit32 or {}

-- Add bit operations for Lua 5.1 compatibility
if not bit.lshift then
  function bit.lshift(a, n)
    return a * (2 ^ n)
  end
end

if not bit.rshift then
  function bit.rshift(a, n)
    return math.floor(a / (2 ^ n))
  end
end

if not bit.band then
  function bit.band(a, b)
    local result = 0
    local bitval = 1
    while a > 0 and b > 0 do
      if a % 2 == 1 and b % 2 == 1 then
        result = result + bitval
      end
      bitval = bitval * 2
      a = math.floor(a / 2)
      b = math.floor(b / 2)
    end
    return result
  end
end

if not bit.bnot then
  function bit.bnot(a)
    return (-a - 1)
  end
end

if not bit.bxor then
  function bit.bxor(a, b)
    if a == 0 or a == 1 then
      return a == 0 and b or 0
    end
    local result = 0
    local bitval = 1
    while a > 0 or b > 0 do
      local abit = a % 2
      local bbit = b % 2
      if abit ~= bbit then
        result = result + bitval
      end
      bitval = bitval * 2
      a = math.floor(a / 2)
      b = math.floor(b / 2)
    end
    return result
  end
end

local mp = {}
mp.__index = mp

mp.SIGN = {{0,0,0,0,0,0,0,0},-- o
{0,24,24,126,126,24,24,0}, -- +
{0,0,0,126,126,0,0,0}, -- -
{0,96,96,126,126,96,96,0}, -- >
{0,6,6,126,126,6,6,0}, -- <
{0,102,102,24,24,102,102,0}, -- * rnd
{0,120,120,102,102,30,30,0}, -- <> up/down
{0,126,126,102,102,126,126,0}} -- [] sync2 = 12

mp.MODE_POSITION = 0
mp.MODE_SPEED = 1
mp.MODE_RULES = 2

mp.L0 = 4
mp.L1 = 8
mp.L2 = 12

local gridbuf = require "gridbuf"
local gbuf = gridbuf.new(16, 8)

function mp.new()
	local m = {}
	setmetatable(m, mp)
	m.edit_row = 0
	m.key_count = 0
	m.mode = 0
	m.prev_mode = 0
	m.kcount = 0
	m.scount = {}
	m.state = {}
	m.clear = {}

	m.count = {}
	m.position = {}
	m.speed = {}
	m.tick = {}
	m.min = {}
	m.max = {}
	m.trigger = {}
	m.toggle = {}
	m.rules = {}
	m.rule_dests = {}
	m.sync = {}
	m.sound = 0
	m.pushed = {}
	m.rule_dest_targets = {}
	m.smin = {}
	m.smax = {}

	for i=1,8 do
		m.count[i] = 8+i
		m.position[i] = 8+i
		m.speed[i] = 0
		m.tick[i] = 0
		m.max[i] = 8+i
		m.min[i] = 8+i
		m.trigger[i] = bit.lshift(1, i)
		m.toggle[i] = 0
		m.rules[i] = 2 -- inc
		m.rule_dests[i] = i
		m.sync[i] = bit.lshift(1, i)
		m.rule_dest_targets[i] = 3
		m.smin[i] = 0
		m.smax[i] = 0
		m.pushed[i] = 0
		m.scount[i] = 0
	end

	m.mp_event = function(row, state) end 
	return m
end

function mp:apply_rule(i)
	local rd = self.rule_dests[i]

	if self.rules[i] == 2 then -- inc
		if bit.band(self.rule_dest_targets[i], 1) > 0 then
			self.count[rd] = self.count[rd] + 1
			if self.count[rd] > self.max[rd] then self.count[rd] = self.min[rd] end
		end

		if bit.band(self.rule_dest_targets[i], 2) > 0 then
			self.speed[rd] = self.speed[rd] + 1
			if self.speed[rd] > self.smax[rd] then self.speed[rd] = self.smin[rd] end
		end

	elseif self.rules[i] == 3 then -- dec
		if bit.band(self.rule_dest_targets[i], 1) > 0 then
			self.count[rd] = self.count[rd] - 1
			if self.count[rd] < self.min[rd] then self.count[rd] = self.max[rd] end
		end

		if bit.band(self.rule_dest_targets[i], 2) > 0 then
			self.speed[rd] = self.speed[rd] - 1
			if self.speed[rd] < self.smin[rd] then self.speed[rd] = self.smax[rd] end
		end

	elseif self.rules[i] == 4 then -- max
		if bit.band(self.rule_dest_targets[i], 1) > 0 then self.count[rd] = self.max[rd] end

		if bit.band(self.rule_dest_targets[i], 2) > 0 then self.speed[rd] = self.smax[rd] end

	elseif self.rules[i] == 5 then -- min
		if bit.band(self.rule_dest_targets[i], 1) > 0 then self.count[rd] = self.min[rd] end

		if bit.band(self.rule_dest_targets[i], 2) > 0 then self.speed[rd] = self.smin[rd] end

	elseif self.rules[i] == 6 then -- rnd
		if bit.band(self.rule_dest_targets[i], 1) > 0 then
			self.count[rd] = math.random(self.min[rd], self.max[rd])
		end

		if bit.band(self.rule_dest_targets[i], 2) > 0 then
			self.speed[rd] = math.random(self.smin[rd], self.smax[rd])
		end

	elseif self.rules[i] == 7 then -- pole
		if bit.band(self.rule_dest_targets[i], 1) > 0 then
			if math.abs(self.count[rd] - self.min[rd]) < math.abs(self.count[rd] - self.max[rd]) then
				self.count[rd] = self.max[rd]
			else
				self.count[rd] = self.min[rd]
			end
		end

		if bit.band(self.rule_dest_targets[i], 2) > 0 then
			if math.abs(self.speed[rd] - self.smin[rd]) < math.abs(self.speed[rd] - self.smax[rd]) then
				self.speed[rd] = self.smax[rd]
			else
				self.speed[rd] = self.smin[rd]
			end
		end

	elseif self.rules[i] == 8 then -- stop
		if bit.band(self.rule_dest_targets[i], 1) > 0 then
			self.position[rd] = -1
		end
	end
end

function mp:clock()
	for i=1,8 do
		if self.pushed[i] == 1 then
			for n=1,8 do
				if bit.band(self.sync[i], bit.lshift(1, n)) > 0 then
					self.position[n] = self.count[n]
					self.tick[n] = self.speed[n]
				end

				if bit.band(self.trigger[i], bit.lshift(1, n)) > 0 then
					self.state[n] = 1
					self.clear[n] = 1
				end

				if bit.band(self.toggle[i], bit.lshift(1, n)) > 0 then
					self.state[n] = bit.bxor(self.state[n], 1)
				end
			end

			self.pushed[i] = 0
		end

		if self.tick[i] == 0 then
			self.tick[i] = self.speed[i]

			if self.position[i] == 1 then 
				self:apply_rule(i) 

				self.position[i] = self.position[i] - 1

				for n=1,8 do
					if bit.band(self.sync[i], bit.lshift(1, n)) > 0 then
						self.position[n] = self.count[n]
						self.tick[n] = self.speed[n]
					end

					if bit.band(self.trigger[i], bit.lshift(1, n)) > 0 then
						self.state[n] = 1
						self.clear[n] = 1
					end

					if bit.band(self.toggle[i], bit.lshift(1, n)) > 0 then
						self.state[n] = bit.bxor(self.state[n], 1)
					end
				end
			elseif self.position[i] > 1 then
				self.position[i] = self.position[i] - 1
			end
		else
			self.tick[i] = self.tick[i] - 1
		end
	end

	for i=1,8 do
		local row = math.abs(i - 9) -- inverse so that index 1 is bottom row
		self.mp_event(row, self.state[i])
		if self.clear[i] == 1 then self.state[i] = 0 end
		self.clear[i] = 0
	end
end

function mp:gridevent(x, y, z)
	self.prev_mode = self.mode

	if x == 1 then
		self.kcount = self.kcount + (bit.lshift(z, 1)-1)

		if self.kcount < 0 then self.kcount = 0 end

		if self.kcount == 1 and z == 1 then
			self.mode = mp.MODE_SPEED
		elseif self.kcount == 0 then
			self.mode = mp.MODE_POSITION
			self.scount[y] = 0
		end

		if self.mode == mp.MODE_SPEED and z == 1 then 
			self.edit_row = y 
		end

	elseif x == 2 and self.mode ~= mp.MODE_POSITION then
		if self.mode == mp.MODE_SPEED and z == 1 then 
			self.mode = mp.MODE_RULES
			self.edit_row = y
		elseif self.mode == mp.MODE_RULES and z == 0 then
			self.mode = mp.MODE_SPEED
		end

	elseif self.mode == mp.MODE_POSITION then
		self.scount[y] = self.scount[y] + (bit.lshift(z, 1) - 1)
		if self.scount[y] < 0 then self.scount[y] = 0 end

		if z == 1 and self.scount[y] == 1 then
			self.position[y] = x
			self.count[y] = x
			self.min[y] = x
			self.max[y] = x
			self.tick[y] = self.speed[y]

			if self.sound == 1 then self.pushed[y] = 1 end

		elseif z == 1 and self.scount[y] == 2 then
			if x < self.count[y] then
				self.min[y] = x
				self.max[y] = self.count[y]
			else
				self.max[y] = x
				self.min[y] = self.count[y]
			end
		end
	elseif self.mode == mp.MODE_SPEED then
		self.scount[y] = self.scount[y] + (bit.lshift(z, 1) - 1)
		if self.scount[y] < 0 then self.scount[y] = 0 end

		if z == 1 then
			if x > 8 then
				if self.scount[y] == 1 then
					self.smin[y] = x - 9
					self.smax[y] = x - 9
					self.speed[y] = x - 9
					self.tick[y] = self.speed[y]
				elseif self.scount[y] == 2 then
					if x-8 < self.smin[y] then
						self.smax[y] = self.smin[y]
						self.smin[y] = x - 9
					else
						self.smax[y] = x - 9
					end
				end
			elseif x == 6 then
				self.toggle[self.edit_row] = bit.bxor(self.toggle[self.edit_row], bit.lshift(1, y))
				self.trigger[self.edit_row] = bit.band(self.trigger[self.edit_row], bit.bnot(bit.lshift(1, y)))
			elseif x == 7 then
				self.trigger[self.edit_row] = bit.bxor(self.trigger[self.edit_row], bit.lshift(1, y))
				self.toggle[self.edit_row] = bit.band(self.toggle[self.edit_row], bit.bnot(bit.lshift(1, y)))
			elseif x == 5 then
				self.sound = bit.bxor(self.sound, 1)
			elseif x == 3 then
				if self.position[y] == -1 then 
					self.position[y] = self.count[y]
				else
					self.position[y] = -1
				end
			elseif x == 4 then
				self.sync[self.edit_row] = bit.bxor(self.sync[self.edit_row], bit.lshift(1, y))
			end
		end
	elseif self.mode == mp.MODE_RULES and z == 1 then
		if x > 4 and x < 8 then
			self.rule_dests[self.edit_row] = y
			self.rule_dest_targets[self.edit_row] = x - 4
		elseif x > 7 then
			self.rules[self.edit_row] = y
		end
	end
end

function mp:gridredraw(g)
	gbuf:led_level_all(0)

	if self.mode == mp.MODE_POSITION then
		for i=1,8 do
			for j=self.min[i],self.max[i] do
				gbuf:led_level_set(j, i, mp.L0)
			end

			gbuf:led_level_set(self.count[i], i, mp.L1)

			if self.position[i] >= 1 then
				gbuf:led_level_set(self.position[i], i, mp.L2)
			end
		end
	elseif self.mode == mp.MODE_SPEED then
		for i=1,8 do 
			if self.position[i] >= 1 then gbuf:led_level_set(self.position[i], i, mp.L0) end

			if self.position[i] ~= -1 then gbuf:led_level_set(3, i, 2) end

			for j=self.smin[i],self.smax[i] do
				gbuf:led_level_set(j+9, i, mp.L0)
			end

			gbuf:led_level_set(self.speed[i]+9, i, mp.L1)

			if self.sound == 1 then gbuf:led_level_set(5, i, 2) end

			if bit.band(self.toggle[self.edit_row], bit.lshift(1, i)) > 0 then
				gbuf:led_level_set(6, i, mp.L2)
			else
				gbuf:led_level_set(6, i, mp.L0)
			end

			if bit.band(self.trigger[self.edit_row], bit.lshift(1, i)) > 0 then
				gbuf:led_level_set(7, i, mp.L2)
			else
				gbuf:led_level_set(7, i, mp.L0)
			end

			if bit.band(self.sync[self.edit_row], bit.lshift(1, i)) > 0 then
				gbuf:led_level_set(4, i, mp.L1)
			else
				gbuf:led_level_set(4, i, mp.L0)
			end
		end

		gbuf:led_level_set(1, self.edit_row, mp.L2)
	elseif self.mode == mp.MODE_RULES then 
		for i=1,8 do 
			if self.position[i] >= 1 then gbuf:led_level_set(self.position[i], i, mp.L0) end
		end

		gbuf:led_level_set(1, self.edit_row, mp.L1)
		gbuf:led_level_set(2, self.edit_row, mp.L1)

		local rd = self.rule_dests[self.edit_row]
		if self.rule_dest_targets[self.edit_row] == 1 then
			gbuf:led_level_set(5, rd, mp.L2)
			gbuf:led_level_set(6, rd, mp.L0)
			gbuf:led_level_set(7, rd, mp.L0)
		elseif self.rule_dest_targets[self.edit_row] == 2 then
			gbuf:led_level_set(5, rd, mp.L0)
			gbuf:led_level_set(6, rd, mp.L2)
			gbuf:led_level_set(7, rd, mp.L0)
		else
			gbuf:led_level_set(5, rd, mp.L2)
			gbuf:led_level_set(6, rd, mp.L2)
			gbuf:led_level_set(7, rd, mp.L0)
		end

		for i=8,16 do
			gbuf:led_level_set(i, self.rules[self.edit_row], mp.L0)
		end

		for i=1,8 do
			local k = mp.SIGN[self.rules[self.edit_row]][i]
			for j=1,8 do
				if bit.band(k, bit.lshift(1, j)) ~= 0 then
					gbuf:led_level_set(9+j, i, mp.L2) 
				end
			end
		end
	end

	gbuf:render(g)
	if g then g:refresh() end
end

function mp.loadornew(f)
	local m
	m = tabutil.load(f)

	if m == nil then
		m = mp.new()
	else
		setmetatable(m, mp)
	end

	return m
end

function mp:save(f)
	print("saving mp")

	for k,v in ipairs(self) do
		print("saving mp." .. k)
	end

	tabutil.save(self, f)
end

return mp
