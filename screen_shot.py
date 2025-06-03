import time
import pyautogui
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Replace 'your-slack-bot-token' with your actual Slack bot token
# slack_bot_token =
#'xoxb-254106751139-7308664479335-dQw3Qkp7Xh5B2DPGQ7ETQ5gc'
# Replace 'your-channel-id' with the ID of the Slack channel
slack_channel_id = 'C079H6J4Q11'

# Initialize the Slack client
client = WebClient(token=slack_bot_token)

def take_screenshot():
    # Get the current time and format it as a string
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # Define the filename using the timestamp
    filename = f'screenshot_{timestamp}.png'
    # Take the screenshot
    screenshot = pyautogui.screenshot()
    # Save the screenshot
    screenshot.save(filename)
    print(f'Screenshot saved as {filename}')
    return filename

def upload_to_slack(filename):
    try:
        # Upload the file to the specified Slack channel using files_upload_v2
        response = client.files_upload_v2(
            channels=[slack_channel_id],
            file=filename,
            title=filename,
        )
        assert response["file"]  # Ensure the file is uploaded successfully
        print(f'Uploaded {filename} to Slack channel {slack_channel_id}')
    except SlackApiError as e:
        print(f'Error uploading {filename} to Slack: {e.response["error"]}')

def main():
    try:
        while True:
            filename = take_screenshot()
            upload_to_slack(filename)
            # Wait for 60 seconds before taking the next screenshot
            time.sleep(120)
    except KeyboardInterrupt:
        print('Program terminated by user.')

if __name__ == '__main__':
    main()
