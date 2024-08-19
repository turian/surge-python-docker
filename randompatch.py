import glob
import os
import random

import soundfile as sf
import surgepy

SR = 44100
# Grand piano
NOTE_RANGE = [21, 108]

DURATION = 4
MAX_VELOCITY = 127

note = 64
velocity = 100
hold = 1.5


# Directory containing wavetables
FACTORY_WAVETABLES = glob.glob(
    "/home/surge/surge/resources/data/wavetables*/**/*.wav", recursive=True
)


# Function to randomize a parameter's value within its range
def randomize_param(synth, param):
    param_min = synth.getParamMin(param)
    param_max = synth.getParamMax(param)
    random_value = random.uniform(param_min, param_max)
    return random_value


# Create a Surge XT instance
synth = surgepy.createSurge(SR)

# Dynamically retrieve all control group constants
control_group_constants = {
    name: getattr(surgepy.constants, name)
    for name in dir(surgepy.constants)
    if name.startswith("cg_")
}

# Loop over each control group and randomize the parameters
for cg_id in control_group_constants.values():
    control_group = synth.getControlGroup(cg_id)
    for entry in control_group.getEntries():
        for param in entry.getParams():
            random_value = randomize_param(synth, param)
            synth.setParamVal(param, random_value)

# Retrieve the patch to manipulate scenes, oscillators, etc.
patch = synth.getPatch()

# Randomize the number of oscillators to use (between 1 and the maximum available)
oscillators = patch["scene"][0]["osc"]
num_oscillators = len(oscillators)
num_oscillators_to_use = random.randint(1, num_oscillators)

# Randomize the parameters of the selected oscillators
for osc_id in range(num_oscillators_to_use):
    osc_params = oscillators[osc_id]
    for param_name, param in osc_params.items():
        if isinstance(param, surgepy.SurgeNamedParamId):
            if "wavetable" in param_name.lower():
                # Select and load a random wavetable if available
                wavetable_path = random.choice(FACTORY_WAVETABLES)
                if wavetable_path:
                    synth.loadWavetable(0, osc_id, wavetable_path)
            else:
                random_value = randomize_param(synth, param)
                synth.setParamVal(param, random_value)

            # Handle children parameters for oscillators if applicable
            children = param.getChildren() if hasattr(param, "getChildren") else []
            for child_param in children:
                random_value = randomize_param(synth, child_param)
                synth.setParamVal(child_param, random_value)

# Randomize other parts of the patch (e.g., filter units, effects, etc.)
for scene in patch["scene"]:
    for filter_unit in scene["filterunit"]:
        for param in filter_unit.values():
            if isinstance(param, surgepy.SurgeNamedParamId):
                random_value = randomize_param(synth, param)
                synth.setParamVal(param, random_value)

    for lfo in scene["lfo"]:
        for param in lfo.values():
            if isinstance(param, surgepy.SurgeNamedParamId):
                random_value = randomize_param(synth, param)
                synth.setParamVal(param, random_value)

    # Randomize effects
    effects = patch["fx"]
    for fx in effects:
        for param in fx.values():
            if isinstance(param, surgepy.SurgeNamedParamId):
                random_value = randomize_param(synth, param)
                synth.setParamVal(param, random_value)

onesec = synth.getSampleRate() / synth.getBlockSize()
buf = synth.createMultiBlock(int(round(DURATION * onesec)))

chd = [note]
for n in chd:
    synth.playNote(0, n, velocity, 0)
synth.processMultiBlock(buf, 0, int(round(hold * onesec)))

for n in chd:
    synth.releaseNote(0, n, 0)
synth.processMultiBlock(buf, int(round((DURATION - hold) * onesec)))

slug = "output/random.wav"
# WHY? float round
sf.write(slug, buf.T, int(round(synth.getSampleRate())))
# osynth.system(f"oggenc --quality 10 {slug}")
os.system(f"oggenc -Q {slug} && rm {slug}")


## Save the randomized patch to a file
# output_path = "/path/to/save/random_patch.fxp"
# synth.savePatch(output_path)
# print(f"Random patch saved to {output_path}")
