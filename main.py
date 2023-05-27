import os
import json
import re

import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication
from qt_material import apply_stylesheet


class MainWindow(QMainWindow):
    config = {}  # Define config as a class attribute

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Test Case Generator")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setGeometry(100, 100, 500, 350)

        # Create the central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Create the layout
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Create the controller file input field
        self.controller_file_input = QtWidgets.QLineEdit()
        self.controller_file_input.setPlaceholderText("Enter Controller File")
        layout.addWidget(self.controller_file_input)

        # Create the test file input field
        self.test_file_input = QtWidgets.QLineEdit()
        self.test_file_input.setPlaceholderText("Enter Test File")
        layout.addWidget(self.test_file_input)

        # Create the reference method input field
        self.reference_method_input = QtWidgets.QLineEdit()
        self.reference_method_input.setPlaceholderText("Enter Reference Method")
        layout.addWidget(self.reference_method_input)

        # Create the target method input field
        self.target_method_input = QtWidgets.QLineEdit()
        self.target_method_input.setPlaceholderText("Enter Target Method")
        layout.addWidget(self.target_method_input)

        # Create the buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()

        # Create the submit button
        submit_button = QtWidgets.QPushButton("Submit")
        submit_button.clicked.connect(self.generate_test_cases)
        buttons_layout.addWidget(submit_button)

        layout.addLayout(buttons_layout)

        # Create the log console
        self.log_console = QtWidgets.QTextEdit()
        self.log_console.setReadOnly(True)
        layout.addWidget(self.log_console)

        # Apply the Material Design style
        apply_stylesheet(self, theme='dark_teal.xml')

        # Load values from config.json if it exists
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.config = json.load(f)  # Assign loaded config data to self.config
            self.controller_file_input.setText(self.config.get("controller_file_path", ""))
            self.test_file_input.setText(self.config.get("test_file_path", ""))
            self.reference_method_input.setText(self.config.get("reference_method", ""))
            self.target_method_input.setText(self.config.get("target_method", ""))

    def closeEvent(self, event):
        # Save the entered values to the configuration file
        controller_file_path = self.controller_file_input.text()
        test_file_path = self.test_file_input.text()
        reference_method = self.reference_method_input.text()
        target_method = self.target_method_input.text()

        self.config["controller_file_path"] = controller_file_path
        self.config["test_file_path"] = test_file_path
        self.config["reference_method"] = reference_method
        self.config["target_method"] = target_method

        with open(config_file, "w") as f:
            json.dump(self.config, f)  # Save self.config data to the file

        event.accept()

    def log_message(self, message):
        self.log_console.append(message)

    def generate_test_cases(self):
        # Get the input values
        controller_file_path = self.controller_file_input.text()
        test_file_path = self.test_file_input.text()
        reference_method = self.reference_method_input.text()
        target_method = self.target_method_input.text()

        # Read Java controller file
        try:
            with open(controller_file_path, "r") as controller_file:
                controller_content = controller_file.readlines()
            with open(test_file_path, "r") as controllertest_file:
                controllertest_content = controllertest_file.readlines()
        except FileNotFoundError:
            self.log_message("Error: Controller file not found.")
            return

        # Read Java controller test file
        try:
            with open(test_file_path, "r") as test_file:
                test_content = test_file.read()
        except FileNotFoundError:
            self.log_message("Error: Test file not found.")
            return

        # Find methods with test cases in controller test file
        test_method_pattern = r"@Test\s+public\s+void\s+(\w+)\s*\([^)]*\)\s*{"
        test_methods = re.findall(test_method_pattern, test_content)

        # Retrieve test cases for reference method from controller test file
        reference_test_cases = [
            test_method
            for test_method in test_methods
            if test_method.lower().startswith(reference_method.lower())
        ]

        # Print test cases for reference method
        self.log_message("\nTest cases for reference method:")
        for test_case in reference_test_cases:
            self.log_message("- " + test_case)

            # Find the reference method content in the controller file
            reference_method_content = []
            reference_method_start = False
            mapping_start = False
            for line in controller_content:
                if "Mapping" in line:
                    if reference_method_start:
                        break
                    mapping_start = True
                if reference_method in line:
                    reference_method_start = True
                if reference_method_start and mapping_start:
                    reference_method_content.append(line)
                if reference_method_start and "Mapping" in line:
                    mapping_start = True

            # Print reference method content
            self.log_message(
                f"\nContent of reference method '{reference_method}' from Controller file:"
            )
            for line in reference_method_content[1:]:
                if "Mapping" in line:
                    break
                self.log_message(line.strip())

        # Save test cases and reference method content to a file named 'testcases.txt'
        with open("testcases.txt", "w") as test_case_file:
            test_case_file.write("Test cases for reference method:\n")
            for test_case in reference_test_cases:
                test_case_file.write("- " + test_case + "\n")

            test_case_file.write("\nContent of reference method:\n")
            for line in reference_method_content:
                test_case_file.write(line)

        self.log_message("Test cases and reference method content have been printed and saved.")

        # Find the target method content in the controller file
        target_method_content = []
        target_method_start = False
        prev_line_empty = True  # Variable to track if the previous line was empty
        for i, line in enumerate(controller_content):
            if target_method in line:
                target_method_start = True
                if i > 0 and "@" in controller_content[i - 1]:
                    target_method_content.append(controller_content[i - 1])
                if not prev_line_empty:
                    target_method_content.append(line)  # Include the current line
            elif target_method_start:
                if "@" in line:
                    target_method_start = False
                    break
                target_method_content.append(line)

            prev_line_empty = line.strip() == ""  # Check if the current line is empty

        if target_method_content:
            self.log_message(
                f"\nContent of target method '{target_method}' from Controller file:"
            )
            for line in target_method_content:
                self.log_message(line.strip())

        # Append target method content to the 'testcases.txt' file
        with open("testcases.txt", "a") as test_case_file:
            test_case_file.write(f"\nContent of target method '{target_method}':\n")
            for line in target_method_content:
                test_case_file.write(line)

        self.log_message("Target method content has been printed and appended to 'testcases.txt'.")

        # Find the reference method content in the ControllerTest file
        for test_case in reference_test_cases:
            rmtc_content = []
            rmtc_start = False
            prev_line_empty = True  # Variable to track if the previous line was empty
            for i, line in enumerate(controllertest_content):
                if test_case in line:
                    rmtc_start = True
                    if i > 0 and "@" in controllertest_content[i - 1]:
                        rmtc_content.append(controllertest_content[i - 1])
                    if not prev_line_empty:
                        rmtc_content.append(line)  # Include the current line
                elif rmtc_start:
                    if "@" in line:
                        rmtc_start = False
                        break
                    rmtc_content.append(line)

                prev_line_empty = line.strip() == ""  # Check if the current line is empty

            # Print reference method content
            self.log_message(
                f"\nContent of reference method '{test_case}' from ControllerTest file:"
            )
            for line in rmtc_content:
                self.log_message(line.strip())

            # Save reference method content to the 'testcases.txt' file
            with open("testcases.txt", "a") as test_case_file:
                test_case_file.write(
                    f"\nContent of reference method '{test_case}' from ControllerTest file:\n"
                )
                for line in rmtc_content:
                    test_case_file.write(line)

# Configuration file path
config_file = "config.json"

# Check if the configuration file exists
if not os.path.exists(config_file):
    # Create an empty configuration file if it doesn't exist
    with open(config_file, "w") as f:
        json.dump({}, f)

# Create the application instance
app = QApplication(sys.argv)

# Set the application style to the Material Design style
app.setStyle("Fusion")

# Create the main window
window = MainWindow()
window.show()

# Run the event loop
sys.exit(app.exec_())
