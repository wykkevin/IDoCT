# Run this by python3 run_single_kafka_ctest.py test_name configs
# Configs should in the format of "test_config1=test_value1 test_config2=test_value2"
# Example python3 run_single_kafka_ctest.py AclCommandTest.testPatternTypes zookeeper.connect=127.0.0.1:9999

import sys
import xml.etree.ElementTree as ET
import os
from subprocess import Popen, PIPE
import run_test_utils


def parse_input(argv):
    ctestname = argv[1]
    conf_xml = ET.Element("config")
    for i in range(2, len(argv)):
        equal_index = argv[i].index('=')
        param = argv[i][0:equal_index]
        value = argv[i][equal_index + 1:]
        prop = ET.SubElement(conf_xml, "configs")
        n = ET.SubElement(prop, "name")
        v = ET.SubElement(prop, "value")
        n.text = param
        v.text = value
    return ctestname, conf_xml


def inject_configs(conf_xml):
    inject_path = "../../kafka/clients/src/main/resources/ctest.xml"
    print(">>>>[ctest_core] injecting into file: {}".format(inject_path))
    file = open(inject_path, "wb")
    file.write(str.encode(
        "<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n"))
    file.write(ET.tostring(conf_xml))
    file.close()


def run_test(test_name):
    kafka_dir = "../../kafka/"
    os.chdir(kafka_dir)
    print("running test " + test_name)
    cmd = ["./gradlew", "-Prerun-tests", "core:test", "--tests", test_name, "-i"]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr =process.communicate()
    print_output = run_test_utils.strip_ansi(stdout.decode("ascii", "ignore"))
    print(print_output)
    os.chdir("../IDoCT/run_ctest/")


def clean_injected_file():
    inject_path = "../../kafka/clients/src/main/resources/ctest.xml"
    file = open(inject_path, "w")
    file.write("")
    file.close()


def main(argv):
    test_name, conf_xml = parse_input(argv)
    inject_configs(conf_xml)
    run_test(test_name)
    clean_injected_file()


main(sys.argv)
