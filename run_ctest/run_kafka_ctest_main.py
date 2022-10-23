import os
import xml.etree.ElementTree as ET
import json
from subprocess import Popen, PIPE


def read_input_by_line():
    updated_configs = []
    path = "./kafka-configs/kafka-ctest-config.csv"
    config_file = open(path, "r")
    config_lines = config_file.readlines()
    for line in config_lines:
        split_line = line.split(",")
        name = split_line[0]
        value = split_line[1]

        conf_xml = ET.Element("config")
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
        ctests = extract_mapping(updated_configs)
        test_results = run_all_tests(ctests)
        config_pairs = {}
        config_pairs[name] = value
        store_test_results(test_results, config_pairs, "kafka-ctest-config.csv")


def read_input():
    # Read input
    updated_configs = []
    for file_name in os.listdir("kafka-configs"):
        path = os.path.join("kafka-configs", file_name)
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
        ctests = extract_mapping(updated_configs)
        test_results = run_all_tests(ctests)
        store_test_results(test_results, file_name)


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
    mapping_file.close()
    return ctest_tests


# Run each of the tests. Configs are already injected.
def run_all_tests(tests):
    print("testing " + str(len(tests)) + " tests")
    kafka_dir = "../../kafka/"
    os.chdir(kafka_dir)
    results = {}
    print("test dir " + os.getcwd())
    for test in tests:
        print("running test " + test)
        cmd = ["./gradlew", "-Prerun-tests", "core:test", "--tests", test]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if "PASSED" in str(stdout):
            results[test] = True
            print(test + " is passed")
        else:
            results[test] = False
            print(test + " is failed")
    os.chdir("../IDoCT/run_ctest/")
    return results


def store_test_results(test_results, config_pairs, config_file_name):
    result_file_name = config_file_name.split(".csv")[0] + "_result.txt"
    result_path = "./kafka-configs/" + result_file_name
    file = open(result_path, "a")
    file.write("Testing with " + str(len(config_pairs)) + " configs\n")
    for config in config_pairs:
        file.write(config + ":" + str(config_pairs[config]) + "\n")
    file.write(str(len(test_results)) + " tests run for this config\n")
    for result in test_results:
        file.write(result + "," + str(test_results[result]) + "\n")
    file.write("End of a Ctest\n")
    file.close()


def clean_injected_file():
    inject_path = "../../kafka/clients/src/main/resources/ctest.xml"
    file = open(inject_path, "w")
    file.write("")
    file.close()


def main():
    # read_input()  # Run ctest with multiple config changes
    read_input_by_line()  # Run ctest with one config change, but the changes are stored in a single file
    clean_injected_file()


main()
