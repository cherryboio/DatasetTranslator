import json
import asyncio
import aiohttp
import aiofiles
from tqdm import tqdm

# Constants defining API endpoint, file paths, model details, and retry configurations.
# These can be modified to fit the specific use case or setup.
API_ENDPOINT = "http://your-api-endpoint.com/api/chat"
INPUT_FILE = "input_dataset.jsonl"
OUTPUT_FILE = "output_dataset.jsonl"
LOG_FILE = "process_log.txt"
MODEL = "your_model_identifier"
MAX_RETRIES = 3  # Maximum number of retries for a single request in case of failures.
RETRY_DELAY = 5  # Delay (in seconds) between retries.
TIMEOUT_DURATION = 30  # Timeout duration for API requests in seconds.
DEFAULT_TEMP = 0  # Default temperature setting for the API request.
MAX_TEMP = 0.8  # Maximum temperature setting for the API.
TEMP_INCREMENT = 0.1  # Incremental temperature increase for retries.

def remove_start_tag(text):
    """Remove predefined start tags from the text."""
    # Modify these tags according to your API's response format.
    start_tag_variations = ["<edited_text>", "<edited_text>", "<edited_Text>", "<edited_Text>", "<Edited_Text>", "<Edited_text>", "<EditedText>"]
    for start_tag in start_tag_variations:
        if start_tag in text:
            return text[text.index(start_tag) + len(start_tag):].strip()
    return text.strip()

async def log_status(message):
    """Asynchronously log a message to a log file."""
    async with aiofiles.open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        await log_file.write(f"{message}\n")

def parse_json_line(line):
    """Parse a JSON line and return the relevant fields for processing."""
    data = json.loads(line)
    # These fields can be adjusted based on the JSON structure of your input file.
    return data.get("instruction", ""), data.get("input", ""), data.get("output", "")

def create_payload(role, content, temperature):
    """Create the payload for the API request based on the role, content, and temperature."""
    # Adjust the payload structure according to the API's expected format.
    return {
        "model": MODEL,
        "system": "Your system instructions here...",
        "messages": [{'role': role, 'content': f'"{content}"'}],
        "stream": False,
        "temperature": temperature
    }

async def get_translated_text(session, role, content, line_number, retries=0, temperature=DEFAULT_TEMP):
    """Get translated text from the API, handling retries and temperature adjustments."""
    payload = create_payload(role, content, temperature)
    try:
        response = await asyncio.wait_for(session.post(API_ENDPOINT, json=payload), TIMEOUT_DURATION)
        if response.status == 200:
            response_json = await response.json()
            translated_content = remove_start_tag(response_json['message']['content'])
            await log_status(f"Line {line_number}: Successfully translated.")
            return translated_content
        else:
            raise Exception(f"API returned non-200 status code: {response.status}")
    except asyncio.TimeoutError:
        await log_status(f"Line {line_number}: Timeout. Retrying...")
        if retries < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAY)
            return await get_translated_text(session, role, content, line_number, retries + 1, temperature)
        else:
            await log_status(f"Line {line_number}: Max retries reached. Skipping.")
    except Exception as e:
        await log_status(f"Line {line_number}: Error - {str(e)}. Retrying...")
        if retries < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAY)
            return await get_translated_text(session, role, content, line_number, retries + 1, temperature)
        else:
            await log_status(f"Line {line_number}: Max retries reached. Skipping.")

async def process_line(session, line_number, line):
    """Process a single line from the input file, translating various components."""
    instruction, input_text, output_text = parse_json_line(line)
    # Parallel processing of different parts of the line to enhance efficiency.
    translated_instruction = await get_translated_text(session, 'user', instruction, line_number)
    translated_input = await get_translated_text(session, 'user', input_text, line_number)
    translated_output = await get_translated_text(session, 'user', output_text, line_number)
    return {"instruction": translated_instruction, "input": translated_input, "output": translated_output}

async def main():
    """Main function to orchestrate the translation process."""
    async with aiohttp.ClientSession() as session, aiofiles.open(INPUT_FILE, 'r', encoding='utf-8') as input_file, aiofiles.open(OUTPUT_FILE, 'a', encoding='utf-8') as output_file:
        total_lines = sum(1 for _ in open(INPUT_FILE))
        with tqdm(total=total_lines) as pbar:
            line_number = 0
            async for line in input_file:
                line_number += 1
                translated_data = await process_line(session, line_number, line)
                await output_file.write(json.dumps(translated_data, ensure_ascii=False) + "\n")
                pbar.update(1)
    print("Translation completed. Output saved to", OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(main())
