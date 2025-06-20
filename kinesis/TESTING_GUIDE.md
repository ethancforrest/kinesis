# Kinesis Bug Fix Testing Guide

This guide covers testing all 12 bug fixes implemented in the kinesis-collaboration branch.

## Quick Setup

```bash
# On your norns device
;install https://github.com/ethancforrest/kinesis/tree/kinesis-collaboration

# Load the script - it should start without errors
# Check norns REPL for any startup messages
```

## Bug Fix Test Matrix

### ✅ **Critical Fixes (Bugs 1-6)**

#### **Bug #1: Variable Scoping**
**Fix**: Added `local` keywords to `screen_dirty` and `alt_key`

**Test**:
```lua
-- In norns REPL, these should return nil (not accessible globally)
print(screen_dirty)  -- Should be nil
print(alt_key)       -- Should be nil
print(suns)          -- Should exist (intentionally global for REPL access)
```

**Expected**: No global variable conflicts with other scripts

---

#### **Bug #2: Function Parameters**  
**Fix**: Corrected `init_sun()` calls to use single parameter

**Test**:
- **K1 + K2**: Switch sun 1 modes (1→2→3→4→1...)
- **K1 + K3**: Switch sun 2 modes (1→2→3→4→1...)

**Expected**: Smooth mode switching without errors, see mode numbers update on screen

---

#### **Bug #3: Key Handler Logic**
**Fix**: Removed redundant condition in alt key handling

**Test**:
- Press and hold **K1** - should activate alt mode
- Release **K1** - should deactivate alt mode  
- Press **K1** rapidly - should respond correctly each time

**Expected**: Clean alt key behavior, no stuck states

---

#### **Bug #4: SuperCollider Buffer Parameters**
**Fix**: Changed `\buf_win_start` to `\buf_win_end` in engine

**Test**:
1. Switch to mode 2 (granular): **K1 + K2** until `m2` shows
2. Load audio file: **Parameters → sample → Select audio file**
3. Set mode to recorded: **Parameters → set mode → recorded**
4. Turn **E2** to adjust granular parameters

**Expected**: Proper granular synthesis with correct buffer windowing

---

#### **Bug #5: Clock Cleanup**
**Fix**: Added proper clock cancellation in deinit functions

**Test**:
1. Switch rapidly between modes: **K1+K2**, **K1+K3** repeatedly
2. Monitor norns REPL for messages
3. Switch to mode 1, turn **E2/E3** to start motion, then switch modes

**Expected**: 
- See "deinit sun mode: X" messages
- No clock-related errors
- No orphaned motion after mode switches

---

#### **Bug #6: Division by Zero**
**Fix**: Added safety check in `quotient_remainder()` function

**Test**:
```lua
-- In norns REPL
quotient_remainder(10, 0)  -- Should return 0, 0 (safe)
quotient_remainder(5, 2)   -- Should return 2, 0.5 (normal)
```

**Expected**: No crashes, safe fallback values

---

### ✅ **Additional Fixes (Bugs 7-12)**

#### **Bug #7: Reflector Error Handling**
**Fix**: Added nil checks for reflector operations

**Test**:
1. Switch to mode 2: **K1 + K2** until `m2`
2. Turn **E1** to switch between record/play/loop states
3. Try **K2** in each state to start/stop operations
4. Monitor REPL for any reflector errors

**Expected**: No "attempt to call nil" errors

---

#### **Bug #8: File Loading Error Handling**
**Fix**: Added file existence check in SuperCollider engine

**Test**:
1. Mode 2: **Parameters → sample → Select invalid/missing file**
2. Check SuperCollider log for error messages

**Expected**: Graceful error message, no engine crash

---

#### **Bug #9: Deinit Function Check**
**Fix**: Added existence check before calling deinit

**Test**:
- Rapid mode switching should not cause deinit errors
- Monitor REPL during mode changes

**Expected**: No "attempt to call nil" on deinit

---

#### **Bug #10: Variable Naming Consistency**
**Fix**: Standardized variable names between modes

**Test**:
1. Compare behavior between mode 1 and mode 4
2. Both should handle direction changes similarly
3. Turn **E2** or **E3** back and forth rapidly

**Expected**: Consistent motion behavior across modes

---

#### **Bug #11: Audio Function Documentation**
**Fix**: Added educational comments for audio routing

**Test**:
1. Switch to mode 1
2. Code review: check comments in `sun_mode_1.lua` around lines 63-67

**Expected**: Clear documentation of audio routing purpose

---

#### **Bug #12: Morph Race Condition**
**Fix**: Simplified cancellation to immediate completion

**Test**:
1. Mode 3: **K1 + K3** until `m3`
2. Turn **E2/E3** rapidly to trigger photon morphing
3. Switch modes during active morphs

**Expected**: No timing conflicts, smooth morph cancellation

---

## Comprehensive Integration Tests

### **Mode-Specific Testing**

#### **Mode 1 (Softcut)**
```
1. K1+K2 to mode 1 (m1)
2. Turn E2/E3 - should see sun pulsing
3. Listen for softcut rate changes
4. Check no audio routing errors
```

#### **Mode 2 (Granular)**
```
1. K1+K2 to mode 2 (m2)  
2. Turn E2 - should change granular parameters
3. E1 - switch between record/play/loop
4. K2 - start/stop recording/playing
5. Load audio file and test granulation
```

#### **Mode 3 (Generic)**
```
1. K1+K3 to mode 3 (m3)
2. Turn E2/E3 - should activate photons
3. Test photon movement and morphing
```

#### **Mode 4 (Generic)**
```
1. K1+K3 to mode 4 (m4)
2. Similar to mode 1 but generic
3. Turn E2/E3 for photon velocity
```

### **REPL Testing**
```lua
-- Test documented REPL commands
suns[2]:set_velocity_manual(1)
suns[2]:set_velocity_manual(-10)
suns[2]:set_velocity_manual(0)

-- Test utility functions
quotient_remainder(5, 2)
quotient_remainder(10, 0)
```

### **Stress Testing**
```
1. Rapid mode switching (K1+K2/K3 repeatedly)
2. Multiple encoder movements simultaneously  
3. Load/unload audio files repeatedly
4. Monitor REPL for any errors during stress tests
```

## Error Monitoring Checklist

**Watch for these in norns REPL:**
- ❌ "attempt to call nil" errors
- ❌ Clock cancellation failures  
- ❌ Division by zero crashes
- ❌ File loading errors
- ✅ Clean "deinit sun mode: X" messages
- ✅ Smooth mode transitions
- ✅ Proper audio routing setup

## Performance Validation

**Before/After Comparison:**
- Memory usage should be stable (no leaks)
- Mode switching should be instant
- No orphaned clocks or processes
- Consistent audio behavior

## Success Criteria

✅ **All tests pass without errors**  
✅ **REPL shows clean operation messages**  
✅ **Mode switching is smooth and reliable**  
✅ **Audio functionality works as expected**  
✅ **No resource leaks or timing issues**  
✅ **Educational value maintained/improved**

---

## Quick Verification Script

Run this in norns REPL to verify key fixes:

```lua
-- Test 1: Global variables
print("screen_dirty:", screen_dirty)  -- Should be nil
print("alt_key:", alt_key)           -- Should be nil  
print("suns exists:", suns ~= nil)   -- Should be true

-- Test 2: Utility functions
local q, r = quotient_remainder(5, 2)
print("5/2 =", q, r)  -- Should be 2, 0.5

local q2, r2 = quotient_remainder(10, 0)  
print("10/0 =", q2, r2)  -- Should be 0, 0 (safe)

-- Test 3: REPL access
if suns[2] then
  print("Sun 2 accessible for REPL commands")
end

print("✅ Basic verification complete!")
```

This comprehensive testing ensures all 12 bug fixes work correctly and the kinesis script is robust and educational.