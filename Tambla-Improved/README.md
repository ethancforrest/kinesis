# Tambla Improved

**Enhanced version of tambla with improved usability and user experience**

Original tambla by [ngwese](https://github.com/ngwese) - A semi-generative rhythmic arpeggiator with bendable playheads  
Improvements focused on accessibility and user guidance while preserving all original functionality.

## What's New in Version 1.1.0

### 🆘 Context-Sensitive Help System
- **Long press K1** on any page to see relevant help
- Page-specific controls and tips
- Auto-dismiss or manual close
- No more guessing what controls do

### 💬 Real-Time Parameter Feedback  
- **Tooltips for all parameter changes** via encoders
- Shows current values with proper units
- 2-second display duration
- Immediate feedback for audio engine parameters

### 📊 Status Indicators
- **Transport state** (▶/⏸) always visible
- **Active voice count** when notes are playing
- **Version indicator** for troubleshooting
- Clear visual feedback for system state

### ✨ Enhanced User Experience
- **Informative startup** with progress indicators
- **Device connection feedback** for MIDI/Grid/Arc
- **Welcome tooltips** for first-time users
- **Better error messages** throughout

## Installation

### Option 1: Direct Replace (Recommended)
1. Backup your existing tambla script
2. Replace `tambla.lua` with the improved version
3. All existing patterns and settings preserved

### Option 2: Side-by-Side
1. Install as new script (rename to `tambla-improved.lua`)
2. Test improvements alongside original
3. Switch when comfortable

## Quick Start

### First Time Users
1. **Load the script** and see the welcome message
2. **Press K3** to start the transport
3. **Hold K1** for 1 second to see contextual help
4. **Hold MIDI keys** to trigger rhythmic patterns
5. **Use encoders** and watch tooltips for guidance

### Existing Users
- **Everything works exactly the same**
- **Long press K1** to discover new help system
- **Watch for tooltips** when adjusting parameters
- **Notice status indicators** in corners

## Improvements Detail

### Help System
```
Long Press K1 → Context Help
├── PLAY PAGE: Performance controls & MIDI tips
├── EDIT PAGE: Step programming guidance
└── MACRO PAGE: Pattern management help
```

### Tooltip Examples
- `"Amp: 0.65"` when adjusting amplitude
- `"LPF: 2400Hz"` for filter frequency  
- `"Delay: 0.25s"` for delay time
- `"Feedback: 45%"` for delay feedback

### Status Indicators
- **Top Right**: ▶ (playing) or ⏸ (stopped)
- **Bottom Right**: Active voice count (when > 0)
- **Bottom Left**: Version number (subtle)

## Compatibility

### 100% Backwards Compatible
- ✅ All existing patterns load unchanged
- ✅ All keyboard shortcuts preserved
- ✅ All original features intact
- ✅ Performance characteristics maintained

### Enhanced, Not Replaced
- **Additive improvements** only
- **No workflow changes** required
- **Optional assistance** available when needed
- **Expert users** unimpeded

## What Problems This Solves

### Before Improvements
- ❌ **No guidance** for complex interface
- ❌ **Silent parameter changes**
- ❌ **Invisible system state**
- ❌ **Steep learning curve**
- ❌ **Cryptic error messages**

### After Improvements  
- ✅ **Contextual help** on every page
- ✅ **Real-time feedback** for all changes
- ✅ **Clear status indicators**
- ✅ **Gentler learning curve**
- ✅ **Informative feedback**

## Technical Details

### Implementation Approach
- **Non-breaking additions** to original code
- **Overlay-based UI enhancements**
- **Event-driven tooltip system**
- **Modular help content**

### Performance Impact
- **Minimal CPU overhead** (UI timer only when needed)
- **Memory efficient** (static help text)
- **Smooth 30fps** UI updates
- **No audio performance impact**

### Code Quality
- **Clean integration** with original architecture
- **Defensive programming** for edge cases
- **Consistent code style** throughout
- **Comprehensive error handling**

## Known Limitations

### Current Scope
- **Phase 1 focus**: Critical usability only
- **Help system**: Text-based (no interactive tutorials yet)
- **Tooltips**: Basic formatting (no rich graphics)
- **Status**: Essential indicators only

### Future Improvements (Planned)
- **Preset pattern library** for quick start
- **Interactive tutorial mode** for guided learning
- **Visual timing curves** for bend parameters
- **Pattern morphing** and advanced copy/paste

## Troubleshooting

### Help Not Showing
- **Check K1**: Must hold for full 1 second
- **Page context**: Help content varies by page
- **Release timing**: Let go to close help

### Tooltips Missing
- **Parameter changes**: Only shows for encoder adjustments
- **Timing**: May appear briefly (2 seconds)
- **Content**: Not all actions have tooltips yet

### Performance Issues
- **Disable UI timer**: Modify `clock.run(ui_timer)` if needed
- **Reduce frequency**: Change `1/30` to `1/10` for slower updates
- **Check original**: Compare with unmodified version

## Contributing

### Feedback Welcome
- **User experience reports**: What works/doesn't work?
- **Feature requests**: What would help most?
- **Bug reports**: Any issues or edge cases?
- **Performance data**: Measurements on your hardware

### Development
- **Clean commit history** maintained
- **Test plan** included for validation
- **Documentation** updated with changes
- **Community review** encouraged

## Credits

### Original tambla
- **Author**: Nathan Wese ([@ngwese](https://github.com/ngwese))
- **Repository**: https://github.com/ngwese/tambla
- **License**: MIT

### Improvements
- **Focus**: Usability and user experience enhancements
- **Approach**: Respectful additions, no breaking changes
- **Goal**: Make powerful tool accessible to more users

## License

Same as original tambla (MIT License) - improvements contributed back to community.

---

*"The goal is not to change tambla, but to help users discover what it can already do."*