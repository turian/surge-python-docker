import glob
import os
import random
import surgepy
import json

SR = 44100

# Create a Surge XT instance
synth = surgepy.createSurge(SR)

# Initialize a dictionary to hold metadata for all parameters
metadata = {}

# Function to gather metadata about a parameter
def gather_param_metadata(synth, param):
    param_name = param.getName()
    param_type = synth.getParamValType(param)
    param_min = synth.getParamMin(param)
    param_max = synth.getParamMax(param)
    param_def = synth.getParamDef(param)

    return {
        "name": param_name,
        "type": param_type,
        "min": param_min,
        "max": param_max,
        "default": param_def,
    }

# Dynamically retrieve all control group constants
control_group_constants = {
    name: getattr(surgepy.constants, name)
    for name in dir(surgepy.constants)
    if name.startswith("cg_")
}

# Loop over each control group and collect metadata for the parameters
for cg_id in control_group_constants.values():
    control_group = synth.getControlGroup(cg_id)
    group_name = control_group.getName()
    metadata[group_name] = {"entries": []}

    for entry in control_group.getEntries():
        entry_metadata = {
            "entry": entry.getEntry(),
            "scene": entry.getScene(),
            "params": [],
        }
        for param in entry.getParams():
            param_meta = gather_param_metadata(synth, param)
            entry_metadata["params"].append(param_meta)

            # Handle children parameters for oscillators if applicable
            children = param.getChildren() if hasattr(param, "getChildren") else []
            for child_param in children:
                child_meta = gather_param_metadata(synth, child_param)
                entry_metadata["params"].append(child_meta)

        metadata[group_name]["entries"].append(entry_metadata)

# Retrieve the patch to manipulate scenes, oscillators, etc.
patch = synth.getPatch()

# Collect metadata for oscillators
oscillators = patch["scene"][0]["osc"]
for osc_id, osc_params in enumerate(oscillators):
    osc_metadata = {"oscillator_id": osc_id, "params": []}
    for param_name, param in osc_params.items():
        if isinstance(param, surgepy.SurgeNamedParamId):
            param_meta = gather_param_metadata(synth, param)
            osc_metadata["params"].append(param_meta)

            # Handle children parameters for oscillators if applicable
            children = param.getChildren() if hasattr(param, "getChildren") else []
            for child_param in children:
                child_meta = gather_param_metadata(synth, child_param)
                osc_metadata["params"].append(child_meta)

    metadata[f"oscillator_{osc_id}"] = osc_metadata

# Collect metadata for other parts of the patch (e.g., filter units, effects, etc.)
for scene_id, scene in enumerate(patch["scene"]):
    scene_metadata = {"scene_id": scene_id, "filter_units": [], "lfos": [], "effects": []}

    # Filter units
    for filter_unit in scene["filterunit"]:
        filter_metadata = {"params": []}
        for param in filter_unit.values():
            if isinstance(param, surgepy.SurgeNamedParamId):
                param_meta = gather_param_metadata(synth, param)
                filter_metadata["params"].append(param_meta)
        scene_metadata["filter_units"].append(filter_metadata)

    # LFOs
    for lfo in scene["lfo"]:
        lfo_metadata = {"params": []}
        for param in lfo.values():
            if isinstance(param, surgepy.SurgeNamedParamId):
                param_meta = gather_param_metadata(synth, param)
                lfo_metadata["params"].append(param_meta)
        scene_metadata["lfos"].append(lfo_metadata)

    # Effects
    for fx in patch["fx"]:
        fx_metadata = {"params": []}
        for param in fx.values():
            if isinstance(param, surgepy.SurgeNamedParamId):
                param_meta = gather_param_metadata(synth, param)
                fx_metadata["params"].append(param_meta)
        scene_metadata["effects"].append(fx_metadata)

    metadata[f"scene_{scene_id}"] = scene_metadata

# Save metadata to a JSON file
with open("surge_patch_metadata.json", "w") as json_file:
    json.dump(metadata, json_file, indent=4)

print(f"Metadata JSON saved as 'surge_patch_metadata.json'")

# The rest of your script to generate audio, if needed...

