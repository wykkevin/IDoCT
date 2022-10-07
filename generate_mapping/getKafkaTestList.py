import os


def get_class_name(lines):
    for line in lines:
        split_line = line.split()
        if len(split_line) >= 2 and split_line[0] == "class":
            return split_line[1]
    return ""


def get_test_methods(lines):
    isNextLineTest = False
    method_list = []
    for line in lines:
        if "@Test" in line:
            isNextLineTest = True
        elif isNextLineTest:
            split_line = line.split()
            if len(split_line) > 2 and split_line[0] == "def":
                isNextLineTest = False
                method = split_line[1]
                method_list.append(method[0:len(method) - 3])
    return method_list


root = "../../kafka/core/src/test/scala/unit/kafka"
output = "["
for path, subdirs, files in os.walk(root):
    for name in files:
        f = open(os.path.join(path, name), "r")
        file_content = f.readlines()
        class_name = get_class_name(file_content)
        method_list = get_test_methods(file_content)
        for method in method_list:
            output += "\"" + class_name + "." + method + "\", "
output = output[0:len(output) - 2]
output += "]"
f = open("./results/kafka-core/test_method_list.json", "x")
f.write(output)
