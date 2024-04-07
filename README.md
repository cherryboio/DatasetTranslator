# Dataset Translation Script

## Overview
This script translates datasets using an asynchronous API, specifically designed to work with the Ollama API. The script interfaces with a specific model that is configured to handle language to language translations while maintaining the original text length and enclosing the translated text within `<edited_text>` tags.
The json parsing is specifically designed for dataautogpt3/flan1m-alpaca-uncensored. Change it if necessary for your usecase.

## Model Configuration
The script is configured to work with a model that has the following settings in its model file:

- FROM *model*
- PARAMETER stop </edited_text>
- PARAMETER stop </edited_Text>
- PARAMETER stop </Edited_Text>
- PARAMETER stop </Edited_text>
- PARAMETER stop </EditedText>

SYSTEM *Translating system message must include -put translated text in <edited_text> tags.-*

These parameters ensure the model operates with specific constraints tailored to the script.

## Setup
- Install Python 3.8 or higher.
- Clone or download the script from the GitHub repository to your local machine.
- Navigate to the script's directory in your terminal or command prompt.
- Install required libraries: `pip install -r requirements.txt`.

## Configuration
- Open the script in a text editor or IDE.
- Modify the `API_ENDPOINT`, `MODEL`, and file path constants (`INPUT_FILE`, `OUTPUT_FILE`, `LOG_FILE`) at the top of the script to match your setup and the Ollama API endpoint you intend to use.
- If your JSON structure differs from the expected `input`, `instruction`, and `output` fields, adjust the `parse_json_line` function accordingly.

## Usage
- Ensure your input file is in the same directory as the script or provide the correct path in the `INPUT_FILE` constant.
- Run the script using `python main.py`.
- Monitor the script's progress in the terminal. Log messages and progress will be displayed.
- After the script completes, follow the provided Python snippet in a separate Python file or an interactive session to remove lines with 'null' values:
  ```python
  import json
  
  input_file_path = 'output_dataset.jsonl'  # Adjust to your output file path
  output_file_path = 'cleaned_dataset.jsonl'  # Adjust to your desired cleaned output file path
  
  with open(input_file_path, 'r', encoding='utf-8') as input_file, open(output_file_path, 'w', encoding='utf-8') as output_file:
      for line in input_file:
          try:
              data = json.loads(line)  # Parse the line as JSON
              if data.get('input') is not None and data.get('output') is not None and data.get('instruction') is not None:
                  output_file.write(line)
          except json.JSONDecodeError:
              print(f"Skipping invalid JSON line: {line}")
  
  print("Dataset cleaned. Lines with 'null' values in 'input' or 'output' have been removed.")
    ```
## Features
- Asynchronous API calls
- Progress tracking with TQDM
- Error handling and retries
