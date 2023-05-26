import re
import openai
import PySimpleGUI as sg
import json
import os
import threading

# Configuration file path
config_file = "config.json"

# Create an empty configuration file if it doesn't exist
if not os.path.isfile(config_file):
    with open(config_file, "w") as f:
        json.dump({}, f)

# Load OpenAI API key from configuration file
try:
    with open(config_file, "r") as f:
        config = json.load(f)
        openai_key = config.get("openai_key", "")
except FileNotFoundError:
    openai_key = ""

# GUI layout
layout = [
    [sg.Text("OpenAI API Key:"), sg.Input(default_text=openai_key, key="-OPENAI_KEY-")],
    [sg.Text("Java Controller File:"), sg.Input(key="-CONTROLLER_FILE-"), sg.FileBrowse()],
    [sg.Text("Test File:"), sg.Input(key="-TEST_FILE-"), sg.FileBrowse()],
    [sg.Button("Submit"), sg.Button("Reset OpenAI Key")],
    [sg.Text("Log Console")],
    [sg.Output(size=(80, 20), key="-LOG_CONSOLE-")]
]

window = sg.Window("Test Case Generator", layout, finalize=True)

def generate_test_cases():
    global openai_key

    # Update OpenAI API key in the configuration file
    config = {"openai_key": openai_key}
    with open(config_file, "w") as f:
        json.dump(config, f)

    # Set the OpenAI API key
    openai.api_key = openai_key

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

    # Generate test cases for methods without test cases
    generated_methods = []
    for method in methods_without_tests:
        # Find the method in the controller file
        method_regex = rf"public\s+[\w<>,]+\s+{method}\s*\([^)]*\)\s*{{[\s\S]*?}}"
        method_content = re.search(method_regex, controller_content, re.MULTILINE)
        if method_content:
            method_content = method_content.group(0)
            # Generate method using OpenAI/ChatGPT
            prompt = f"Please generate a test method for the '{method}' method:\n\n{method_content}\n\nTest method:"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.7,
            )
            generated_method = response.choices[0].text.strip()
            generated_methods.append(generated_method)

    # Write generated methods to the text file on the desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    test_cases_file_path = os.path.join(desktop_path, "GPT_TestCases.txt")
    with open(test_cases_file_path, "w") as test_cases_file:
        for method in generated_methods:
            test_cases_file.write(method + "\n")

    print("Test methods generated and saved to the 'GPT_TestCases.txt' file on the desktop.")

def update_openai_key():
    global openai_key
    openai_key = values["-OPENAI_KEY-"]

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Submit":
        update_openai_key()
        threading.Thread(target=generate_test_cases).start()
    elif event == "Reset OpenAI Key":
        window["-OPENAI_KEY-"].update("")

window.close()
