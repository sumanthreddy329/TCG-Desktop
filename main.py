import re
import os
import threading
import json
import PySimpleGUI as sg

# Configuration file path
config_file = "config.json"

# Create an empty configuration file if it doesn't exist
if not os.path.isfile(config_file):
    with open(config_file, "w") as f:
        json.dump({}, f)

# GUI layout
layout = [
    [sg.Text("Java Controller File:"), sg.Input(key="-CONTROLLER_FILE-"), sg.FileBrowse()],
    [sg.Text("Test File:"), sg.Input(key="-TEST_FILE-"), sg.FileBrowse()],
    [sg.Button("Submit")],
    [sg.Text("Log Console")],
    [sg.Output(size=(80, 20), key="-LOG_CONSOLE-")]
]

window = sg.Window("Test Case Generator", layout, finalize=True)

def generate_test_cases():
    # Read Java controller file
    controller_file_path = values["-CONTROLLER_FILE-"]
    with open(controller_file_path, "r") as controller_file:
        controller_content = controller_file.read()

    # Read Test file of the controller
    test_file_path = values["-TEST_FILE-"]
    with open(test_file_path, "r") as test_file:
        test_content = test_file.read()

    # Find methods without test cases
    method_pattern = r"public\s+[\w<>,]+\s+(\w+)\s*\([^)]*\)\s*{"
    methods = re.findall(method_pattern, controller_content)

    test_method_pattern = r"@Test\s+public\s+void\s+(\w+)\s*\([^)]*\)\s*{"
    test_methods = re.findall(test_method_pattern, test_content)

    methods_without_tests = [method for method in methods if method not in test_methods]

    # Remove methods with an additional suffix starting with '_'
    methods_without_tests = [method for method in methods_without_tests if not method.endswith('_')]

    # Print methods without test cases
    print("Methods without test cases:")
    for method in methods_without_tests:
        print(method)

    # Find test cases with method names
    test_cases = re.findall(r"@Test\s+public\s+void\s+(\w+)\s*\([^)]*\)\s*{", test_content)
    methods_with_tests = [method for method in methods if f"{method}_works" in test_cases]

    # Print methods with test cases
    print("\nMethods with test cases:")
    for method in methods_with_tests:
        print(method)

    # Find methods without test cases
    methods_without_tests = [method for method in methods if method not in methods_with_tests]

    # Print methods without test cases
    print("\nMethods without test cases:")
    for method in methods_without_tests:
        print(method)

def update_openai_key():
    pass

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Submit":
        threading.Thread(target=generate_test_cases).start()

window.close()
