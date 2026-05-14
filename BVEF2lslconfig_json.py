import argparse
import io
import json
import ntpath
import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict


EXCLUDED_ELECTRODES = set(["GND", "REF", "Fpz Gnd", "FCz Ref"])


def output_name(bvef_name, config_name):
    config_base = re.sub(r"\.(cfg|json)$", "", config_name, flags=re.IGNORECASE)
    bvef_basename = ntpath.basename(bvef_name)
    bvef_base = re.sub(r"\.bvef$", "", bvef_basename, flags=re.IGNORECASE)
    return config_base + "-" + bvef_base + ".json"


def read_electrode_names(bvef_name):
    tree = ET.parse(bvef_name)
    root = tree.getroot()
    names = []

    for electrode in root.findall("Electrode"):
        name_element = electrode.find("Name")
        if name_element is None or name_element.text is None:
            continue

        name = name_element.text
        if name not in EXCLUDED_ELECTRODES:
            names.append(name)

    return names


def read_json_config(config_name):
    with io.open(config_name, "r", encoding="utf-8") as config_file:
        return json.load(config_file, object_pairs_hook=OrderedDict)


def write_json_config(config_name, config):
    with io.open(config_name, "w", encoding="utf-8", newline="\n") as config_file:
        json.dump(config, config_file, indent=4)
        config_file.write("\n")


def eeg_channels(config):
    try:
        channels = config["Amplifier"]["Channels"]
    except KeyError:
        raise ValueError("JSON config must contain Amplifier.Channels")

    return [channel for channel in channels if channel.get("Type") == 0]


def inject_labels(config, labels, allow_count_mismatch=False):
    channels = eeg_channels(config)

    if len(channels) != len(labels) and not allow_count_mismatch:
        raise ValueError(
            "Electrode count ({0}) does not match EEG channel count ({1}). "
            "Use --allow-count-mismatch to update only the overlapping labels.".format(
                len(labels), len(channels)
            )
        )

    update_count = min(len(channels), len(labels))
    for index in range(update_count):
        channels[index]["Label"] = labels[index]

    return update_count


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            "Inject labels from a .bvef file into a tester.cfg-style JSON .cfg file."
        )
    )
    parser.add_argument("bvef", help="Input BrainVision Electrode Format file")
    parser.add_argument("config", help="Input JSON .cfg file")
    parser.add_argument(
        "--allow-count-mismatch",
        action="store_true",
        help="Update only the overlapping BVEF labels and EEG channels",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output .json file. Defaults to <config>-<bvef>.json",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    labels = read_electrode_names(args.bvef)
    config = read_json_config(args.config)
    updated = inject_labels(config, labels, args.allow_count_mismatch)
    configout_name = args.output or output_name(args.bvef, args.config)
    write_json_config(configout_name, config)
    print("Updated {0} EEG channel labels in {1}".format(updated, configout_name))


if __name__ == "__main__":
    main()
