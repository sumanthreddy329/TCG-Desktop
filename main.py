import os
import json
import re

import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit
from qt_material import apply_stylesheet
import openai


class MainWindow(QMainWindow):
    config = {}  # Define config as a class attribute

    def __init__(self):
        super().__init__()

        # Add the reference_method_content attribute
        self.reference_method_content = []
        self.reference_method_content_tc = []
        self.target_method_content = []

        # Set window properties
        self.setWindowTitle("Test Case Generator")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setGeometry(100, 100, 500, 500)

        # Create the central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Create the layout
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Create the OpenAI API key input field
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setPlaceholderText("Enter OpenAI API Key")
        self.openai_key_input.setStyleSheet("color: white;")  # Set text color to white
        layout.addWidget(self.openai_key_input)

        # Create the controller file input field
        self.controller_file_input = QLineEdit()
        self.controller_file_input.setPlaceholderText("Enter Controller File")
        self.controller_file_input.setStyleSheet("color: white;")  # Set text color to white
        layout.addWidget(self.controller_file_input)

        # Create the test file input field
        self.test_file_input = QLineEdit()
        self.test_file_input.setPlaceholderText("Enter Test File")
        self.test_file_input.setStyleSheet("color: white;")  # Set text color to white
        layout.addWidget(self.test_file_input)

        # Create the reference method input field
        self.reference_method_input = QLineEdit()
        self.reference_method_input.setPlaceholderText("Enter Reference Method")
        self.reference_method_input.setStyleSheet("color: white;")  # Set text color to white
        layout.addWidget(self.reference_method_input)

        # Create the target method input field
        self.target_method_input = QLineEdit()
        self.target_method_input.setPlaceholderText("Enter Target Method")
        self.target_method_input.setStyleSheet("color: white;")  # Set text color to white
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
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                self.config = json.load(f)  # Assign loaded config data to self.config
            self.controller_file_input.setText(self.config.get("controller_file_path", ""))
            self.test_file_input.setText(self.config.get("test_file_path", ""))
            self.reference_method_input.setText(self.config.get("reference_method", ""))
            self.target_method_input.setText(self.config.get("target_method", ""))
            self.openai_key_input.setText(self.config.get("openai_key", ""))

    def closeEvent(self, event):
        # Save the entered values to the configuration file
        controller_file_path = self.controller_file_input.text()
        test_file_path = self.test_file_input.text()
        reference_method = self.reference_method_input.text()
        target_method = self.target_method_input.text()
        openai_key = self.openai_key_input.text()

        self.config["controller_file_path"] = controller_file_path
        self.config["test_file_path"] = test_file_path
        self.config["reference_method"] = reference_method
        self.config["target_method"] = target_method
        self.config["openai_key"] = openai_key

        with open("config.json", "w") as f:
            json.dump(self.config, f)  # Save self.config data to the file

        event.accept()

    def log_message(self, message):
        self.log_console.append(message)

    def generate_test_cases(self):
        # Get the input values
        global rmtc_content
        controller_file_path = self.controller_file_input.text()
        test_file_path = self.test_file_input.text()
        reference_method = self.reference_method_input.text()
        target_method = self.target_method_input.text()
        openai_key = self.openai_key_input.text()

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
        for test_case in reference_test_cases:
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

        # Save test cases and reference method content to a file named 'content.txt'
        with open("content.txt", "w") as content_file:
            content_file.write("Test cases for reference method:\n")
            self.log_message("\nTest Cases of reference method:\n")
            for test_case in reference_test_cases:
                self.log_message("- " + test_case + "\n")
                content_file.write("- " + test_case + "\n")

            content_file.write("\nContent of reference method:\n")
            for line in reference_method_content:
                content_file.write(line)

        # Find the target method content in the controller file
        target_method_content = []
        reference_method_content_tc = []
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
            self.log_message("\n Fetching Content of target method from Controller File...")

        # Append target method content to the 'content.txt' file
        with open("content.txt", "a") as content_file:
            content_file.write(f"\nContent of target method '{target_method}':\n")
            for line in target_method_content:
                content_file.write(line)

        self.log_message("\nTarget method content has been printed and appended to 'content.txt'.")

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

            self.log_message("\nFetching Content of reference method testcases from Controller File...\n")

            # Save reference method content to the 'content.txt' file
            with open("content.txt", "a") as content_file:
                content_file.write(
                    f"\nContent of reference method '{test_case}' from ControllerTest file:\n"
                )
                for line in rmtc_content:
                    reference_method_content_tc.append(line)
                    content_file.write(line)

        # Create a statement with content data in 'query.txt' file
        with open("query.txt", "w") as query_file:
            query_file.write("If for this method:\n")
            for line in reference_method_content[1:]:
                if "Mapping" in line:
                    break
                query_file.write(line.strip() + "\n")

            query_file.write("These are test cases:\n")
            query_file.write("\n")
            for line in reference_method_content_tc:
                query_file.write(line.strip() + "\n")

            query_file.write("\n")  # Add a space between reference method test cases and target method content

            query_file.write("Then create similar test cases and additional test cases for the below controller:\n")
            for line in target_method_content:
                query_file.write(line.strip() + "\n")

        self.log_message("The statement with content data has been printed and saved in 'query.txt'.\n")

        # Read the query.txt file and generate a query_string
        query_string = ""
        with open("query.txt", "r") as query_file:
            query_string = query_file.read()

        # Use the ChatGPT model to generate a response
        if openai_key:
            try:
                response = self.generate_response(openai_key, query_string)

                # Save the response to a file named 'response.txt'
                with open("response.txt", "w") as response_file:
                    response_file.write(response)

                self.log_message("Test case generation response has been generated and saved in 'response.txt'.\n")
            except Exception as e:
                self.log_message(f"An error occurred while generating the response: {str(e)}")
        else:
            self.log_message("Error: OpenAI API key is required to generate test cases.\n")

    def generate_response(self, openai_key, query_string):
        # Set up OpenAI API
        openai.api_key = openai_key

        # Define the completion prompt
        prompt = """
        The following is a test case generation scenario:

        Controller File Path: <CONTROLLER_FILE_PATH>
        Test File Path: <TEST_FILE_PATH>
        Reference Method: <REFERENCE_METHOD>
        Target Method: <TARGET_METHOD>

        Content:
        If for this method:
        <REFERENCE_METHOD_CONTENT>
        These are test cases:
        <REFERENCE_METHOD_TEST_CASES>

        Then create similar test cases and additional test cases for the below controller:
        <TARGET_METHOD_CONTENT>

        Test case generation response:
        """

        # Replace the placeholders in the prompt with the actual values
        prompt = prompt.replace("<CONTROLLER_FILE_PATH>", self.controller_file_input.text())
        prompt = prompt.replace("<TEST_FILE_PATH>", self.test_file_input.text())
        prompt = prompt.replace("<REFERENCE_METHOD>", self.reference_method_input.text())
        prompt = prompt.replace("<TARGET_METHOD>", self.target_method_input.text())
        prompt = prompt.replace("<REFERENCE_METHOD_CONTENT>", "\n".join(self.reference_method_content))
        prompt = prompt.replace("<REFERENCE_METHOD_TEST_CASES>", "\n".join(self.reference_method_content_tc))
        prompt = prompt.replace("<TARGET_METHOD_CONTENT>", "\n".join(self.target_method_content))

        # Generate the completion using the ChatGPT model
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt + "\n" + query_string,
            temperature=0.7,
            max_tokens=500,
            n=1,
            stop=None,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Extract the generated response from the API response
        completion_text = response.choices[0].text.strip()

        return completion_text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
