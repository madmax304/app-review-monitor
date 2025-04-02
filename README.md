# App Review Monitor

A Python script that monitors App Store Connect reviews and sends them to a Slack channel.

## Features

- Fetches recent reviews from App Store Connect
- Sends formatted review notifications to Slack
- Runs on a scheduled basis (9 AM PST daily)
- Automated deployment via GitHub Actions
- Comprehensive logging and error handling
- Unit tests for reliability

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/madmax304/app-review-monitor.git
cd app-review-monitor
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### GitHub Actions Deployment

1. Fork this repository to your GitHub account

2. Add the following secrets to your repository (Settings > Secrets and variables > Actions):
   - `APP_ID`: Your App Store Connect App ID
   - `ISSUER_ID`: Your App Store Connect Issuer ID
   - `KEY_ID`: Your App Store Connect Key ID
   - `PRIVATE_KEY`: Your App Store Connect Private Key
   - `SLACK_WEBHOOK_URL`: Your Slack Webhook URL

3. The workflow will automatically run at 9 AM PST daily
   - You can also manually trigger the workflow from the Actions tab

## Usage

### Local Development

To run the script manually:
```bash
python app_review_monitor.py
```

To run tests:
```bash
pytest tests/
```

### GitHub Actions

The script runs automatically at 9 AM PST daily. You can:
- View execution logs in the Actions tab
- Download logs as artifacts after each run
- Manually trigger the workflow from the Actions tab

## Configuration

- The script fetches reviews from the last 24 hours
- Reviews are formatted with emojis and markdown for better readability
- The Slack channel name can be modified in the `app_review_monitor.py` file
- Logs are stored in the `logs` directory with rotation enabled

## Security

- All sensitive credentials are stored as GitHub Secrets
- The `.env` file is excluded from version control
- Make sure to keep your private key and webhook URL secure
- Logs are automatically uploaded as artifacts and retained for 7 days

## License

MIT License 