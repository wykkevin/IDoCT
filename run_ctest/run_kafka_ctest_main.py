import os
import xml.etree.ElementTree as ET
import json
from subprocess import Popen, PIPE

from run_ctest import run_test_utils


def readInput():
    # Read input
    updated_configs = []
    for fileName in os.listdir("kafka-configs"):
        path = os.path.join("kafka-configs", fileName)
        config_file = open(path, "r")
        config_lines = config_file.readlines()
        conf_xml = ET.Element("config")
        for line in config_lines:
            split_line = line.split(",")
            name = split_line[0]
            value = split_line[1]
            prop = ET.SubElement(conf_xml, "configs")
            n = ET.SubElement(prop, "name")
            v = ET.SubElement(prop, "value")
            n.text = name
            v.text = value
            updated_configs.append(name)

    # Add the file to the kafka project
    inject_path = "../../kafka/clients/src/main/resources/ctest.xml"
    print(">>>>[ctest_core] injecting into file: {}".format(inject_path))
    file = open(inject_path, "wb")
    file.write(str.encode(
        "<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n"))
    file.write(ET.tostring(conf_xml))
    file.close()
    return updated_configs


# Find all the tests that has the changed config.

# From parse_input.py
def extract_mapping(updated_configs):
    """get tests associated with a list of params from mapping"""
    # Read generated json mapping
    json_mapping_path = "../generate_mapping/results/kafka-core/param_unset_getter_map.json"
    mapping_file = open(json_mapping_path, "r")
    mapping = json.loads(mapping_file.read())

    ctest_tests = []
    for test in mapping:
        related_configs = mapping[test]
        for updated_config in updated_configs:
            if updated_config in related_configs:
                ctest_tests.append(test)
                break
    return ctest_tests


# Run each of the tests. Configs are already injected.
def run_all_tests(tests):
    print("testing " + str(len(tests)) + " tests")
    kafka_dir = "../../kafka/"
    os.chdir(kafka_dir)
    print("test dir " + os.getcwd())
    for test in tests:
        print("running test " + test)
        cmd = ["./gradlew", "-Prerun-tests", "core:test", "--tests", test, "-i"]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout = ""
        stderr = ""
        stdout, stderr = process.communicate()

        print_output = run_test_utils.strip_ansi(stdout.decode("ascii", "ignore"))
        print(print_output)


def clean_injected_file():
    inject_path = "../../kafka/clients/src/main/resources/ctest.xml"
    file = open(inject_path, "w")
    file.write("")
    file.close()


def main():
    updated_configs = readInput()
    ctests = extract_mapping(updated_configs)
    run_all_tests(ctests)
    # clean_injected_file()


main()
