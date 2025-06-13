// Drum Engine for Norns
// A simple drum machine engine with multiple drum sounds

Engine_DrumEngine : CroneEngine {

	*new { arg context, doneCallback;
		^super.new(context, doneCallback);
	}

	alloc {

		// Kick drum SynthDef
		SynthDef(\kick, {
			arg out, freq = 60, amp = 0.8, attack = 0.01, decay = 0.3, 
			    pitch_decay = 0.15, drive = 0.1;

			var sig, env, pitch_env;

			// Pitch envelope for kick thump
			pitch_env = EnvGen.kr(
				Env.perc(0.001, pitch_decay), 
				doneAction: 0
			);

			// Main envelope
			env = EnvGen.kr(
				Env.perc(attack, decay), 
				doneAction: 2
			);

			// Generate kick sound using sine wave with pitch envelope
			sig = SinOsc.ar(freq + (pitch_env * freq * 2), 0, amp);

			// Add some click for punch
			sig = sig + (WhiteNoise.ar(0.1) * EnvGen.kr(Env.perc(0.001, 0.01)));

			// Soft distortion
			sig = (sig * (1 + drive)).tanh;

			// Apply envelope
			sig = sig * env;

			Out.ar(out, sig ! 2);
		}).add;

		// Snare drum SynthDef
		SynthDef(\snare, {
			arg out, freq = 200, amp = 0.6, attack = 0.01, decay = 0.15, 
			    noise_ratio = 0.7, tone_decay = 0.1;

			var sig, env, tone_env, noise, tone;

			// Main envelope
			env = EnvGen.kr(
				Env.perc(attack, decay), 
				doneAction: 2
			);

			// Tone envelope (shorter for snare crack)
			tone_env = EnvGen.kr(
				Env.perc(attack, tone_decay), 
				doneAction: 0
			);

			// Noise component
			noise = WhiteNoise.ar(amp * noise_ratio);
			noise = BPF.ar(noise, freq * 2, 0.5);

			// Tone component
			tone = SinOsc.ar([freq, freq * 1.6], 0, amp * (1 - noise_ratio));
			tone = Mix(tone) * tone_env;

			// Mix noise and tone
			sig = noise + tone;

			// Apply envelope
			sig = sig * env;

			Out.ar(out, sig ! 2);
		}).add;

		// Hi-hat SynthDef
		SynthDef(\hihat, {
			arg out, freq = 8000, amp = 0.4, attack = 0.01, decay = 0.1, 
			    resonance = 0.1, open = 0;

			var sig, env;

			// Envelope - longer for open hi-hat
			env = EnvGen.kr(
				Env.perc(attack, decay * (1 + (open * 3))), 
				doneAction: 2
			);

			// Generate hi-hat using filtered noise
			sig = WhiteNoise.ar(amp);
			sig = BPF.ar(sig, freq, resonance.linlin(0, 1, 0.1, 0.9));
			sig = HPF.ar(sig, freq * 0.5);

			// Apply envelope
			sig = sig * env;

			Out.ar(out, sig ! 2);
		}).add;

		// Clap SynthDef
		SynthDef(\clap, {
			arg out, amp = 0.5, decay = 0.15;

			var sig, env;

			// Multiple short bursts for clap effect
			env = EnvGen.kr(
				Env.new(
					[0, 1, 0, 0.6, 0, 0.4, 0],
					[0.001, 0.013, 0.001, 0.01, 0.001, decay],
					[0, -3, 0, -3, 0, -4]
				), 
				doneAction: 2
			);

			// Filtered noise
			sig = WhiteNoise.ar(amp);
			sig = BPF.ar(sig, 1000, 0.1);

			// Apply envelope
			sig = sig * env;

			Out.ar(out, sig ! 2);
		}).add;

		// Wait for SynthDefs to be added
		context.server.sync;

		// Commands callable from Lua

		// Trigger kick
		this.addCommand("kick", "f", { arg msg;
			var amp = msg[1];
			Synth(\kick, [
				\out, context.out_b,
				\amp, amp
			]);
		});

		// Trigger snare
		this.addCommand("snare", "f", { arg msg;
			var amp = msg[1];
			Synth(\snare, [
				\out, context.out_b,
				\amp, amp
			]);
		});

		// Trigger hi-hat
		this.addCommand("hihat", "ff", { arg msg;
			var amp = msg[1];
			var open = msg[2];
			Synth(\hihat, [
				\out, context.out_b,
				\amp, amp,
				\open, open
			]);
		});

		// Trigger clap
		this.addCommand("clap", "f", { arg msg;
			var amp = msg[1];
			Synth(\clap, [
				\out, context.out_b,
				\amp, amp
			]);
		});

		// Set kick parameters
		this.addCommand("kick_params", "fff", { arg msg;
			var freq = msg[1];
			var decay = msg[2];
			var drive = msg[3];
			
			// These would affect future kick hits
			// For real-time control, you'd need to use buses or global variables
		});

		// Set snare parameters
		this.addCommand("snare_params", "fff", { arg msg;
			var freq = msg[1];
			var decay = msg[2];
			var noise_ratio = msg[3];
			
			// These would affect future snare hits
		});

		// Set hi-hat parameters
		this.addCommand("hihat_params", "fff", { arg msg;
			var freq = msg[1];
			var decay = msg[2];
			var resonance = msg[3];
			
			// These would affect future hi-hat hits
		});

		("DrumEngine loaded").postln;
	}
}