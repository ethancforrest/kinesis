// Simple SuperCollider Engine for Norns
// A basic polyphonic synthesizer engine

Engine_SimpleEngine : CroneEngine {

	var <synths;
	var <synthDef;

	*new { arg context, doneCallback;
		^super.new(context, doneCallback);
	}

	alloc {
		// Initialize voice management
		synths = Array.newClear(16);  // 16 voice polyphony

		// Define the main synthesis SynthDef
		synthDef = SynthDef(\simpleVoice, {
			arg out, gate = 1, freq = 440, amp = 0.1, 
			    attack = 0.01, decay = 0.3, sustain = 0.5, release = 1.0,
			    cutoff = 1000, resonance = 0.1, 
			    lfo_rate = 5, lfo_amount = 0;

			var sig, env, filter_env, lfo;

			// LFO for modulation
			lfo = SinOsc.kr(lfo_rate, 0, lfo_amount);

			// Main oscillator (saw wave with slight detuning for richness)
			sig = Saw.ar([freq + lfo, freq * 1.007 + lfo], amp * 0.5);
			sig = Mix(sig);

			// Envelope
			env = EnvGen.kr(
				Env.adsr(attack, decay, sustain, release), 
				gate, 
				doneAction: 2
			);

			// Filter envelope (opens with note)
			filter_env = EnvGen.kr(
				Env.adsr(attack * 0.5, decay * 0.8, sustain * 0.8, release * 2), 
				gate
			);

			// Low-pass filter
			sig = LPF.ar(sig, cutoff + (filter_env * cutoff * 2));
			sig = RLPF.ar(sig, cutoff, resonance.linlin(0, 1, 1, 0.1));

			// Apply amplitude envelope
			sig = sig * env;

			// Output
			Out.ar(out, sig);
		}).add;

		// Wait for SynthDef to be added, then define commands
		context.server.sync;

		// Commands that can be called from Lua

		// Play a note
		this.addCommand("note_on", "iff", { arg msg;
			var voice = msg[1].asInteger;
			var freq = msg[2];
			var amp = msg[3];

			if (synths[voice].notNil) {
				synths[voice].release;
			};

			synths[voice] = Synth(\simpleVoice, [
				\out, context.out_b,
				\freq, freq,
				\amp, amp,
				\gate, 1
			]);
		});

		// Release a note
		this.addCommand("note_off", "i", { arg msg;
			var voice = msg[1].asInteger;
			if (synths[voice].notNil) {
				synths[voice].set(\gate, 0);
				synths[voice] = nil;
			};
		});

		// Set envelope parameters
		this.addCommand("set_envelope", "ffff", { arg msg;
			var attack = msg[1];
			var decay = msg[2];
			var sustain = msg[3];
			var release = msg[4];

			synths.do({ arg synth;
				if (synth.notNil) {
					synth.set(
						\attack, attack,
						\decay, decay,
						\sustain, sustain,
						\release, release
					);
				};
			});
		});

		// Set filter parameters
		this.addCommand("set_filter", "ff", { arg msg;
			var cutoff = msg[1];
			var resonance = msg[2];

			synths.do({ arg synth;
				if (synth.notNil) {
					synth.set(
						\cutoff, cutoff,
						\resonance, resonance
					);
				};
			});
		});

		// Set LFO parameters
		this.addCommand("set_lfo", "ff", { arg msg;
			var rate = msg[1];
			var amount = msg[2];

			synths.do({ arg synth;
				if (synth.notNil) {
					synth.set(
						\lfo_rate, rate,
						\lfo_amount, amount
					);
				};
			});
		});

		// Release all notes
		this.addCommand("all_off", "", { arg msg;
			synths.do({ arg synth, i;
				if (synth.notNil) {
					synth.set(\gate, 0);
					synths[i] = nil;
				};
			});
		});

		// Set master amplitude
		this.addCommand("amp", "f", { arg msg;
			var amp = msg[1];
			synths.do({ arg synth;
				if (synth.notNil) {
					synth.set(\amp, amp);
				};
			});
		});

		("SimpleEngine loaded").postln;
	}

	free {
		synths.do({ arg synth;
			if (synth.notNil) {
				synth.free;
			};
		});
	}
}