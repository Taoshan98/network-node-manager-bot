# Network Node Manager Bot

## About This Project

I started this project to tackle a personal issue. At home, I run a mini server with a bunch of self-hosted services. But sometimes, the power goes out, and since I don’t have a UPS, the server shuts down, and I can’t do anything about it when I’m away.

So I thought—why not use other devices, like old Android phones, to keep an eye on the server and wake it up when the power comes back? That’s how this project was born, and it works pretty well now! It even sends me updates on Telegram when something happens.

## Features

- **Device Monitoring:** Keeps tabs on network devices.
- **Power Handling:** Detects power return and wakes devices up.
- **Telegram Alerts:** Sends updates straight to your phone.
- **Easy Setup:** Simple steps to get started.

## How It Works

1. The bot runs on devices in your network (like an old phone).
2. If the power goes out, it waits.
3. When power is back, it sends a wake-on-LAN signal to turn the server on.
4. You get a Telegram message with the node status.

## Setting Up Nodes

The bot uses **Google Spreadsheets** to store data online, outside the home network, in case of a power failure. Here's how to set it up:

1. **Google Cloud Setup:**
   - Create a project in Google Cloud Platform.
   - Generate credentials to let nodes write to the spreadsheet.
   - Save the credentials file as **`google_credentials.json`** in the project folder.

2. **Node Data Writing:**
   - Each node logs its status in the spreadsheet.
   - To avoid Google API limits, nodes write at different intervals.

This method works for now, but I plan to move away from Google to something more flexible.

## Installation Guide

### Windows, macOS, and Linux

1. Install **Python** (make sure it’s added to the PATH).
2. Clone the project:
   ```bash
   git clone https://github.com/Taoshan98/network-node-manager-bot.git
   ```
3. Move into the project directory:
   ```bash
   cd network-node-manager-bot
   ```
4. Set up a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Configure the **.env** file with the following:
   ```plaintext
   TELEGRAM_TOKEN=your-telegram-token
   TELEGRAM_MAIN_GROUP=chat-id-or-group-id
   NODE_ID=node-id
   NODE_HAS_BATTERY=node-battery-for-laptop-or-smartphones integer 1-0
   SPREADSHEET_URL=google-spreadsheet-url like-https://docs.google.com/spreadsheets/d/1
   MAIN_SHEET_ID=main-sheet-id-usually-0
   NODE_SHEET_ID=node-sheet-id
   NODE_DEBUG=debug-mode integer 1-0
   ```
7. Set up a Telegram bot via **BotFather** and create a Google Spreadsheet using the provided template.
8. Place the `google_credentials.json` file in the correct directory.

#### Windows Task Scheduler Setup

On Windows, use Task Scheduler to automate running the bot:

1. Open **Task Scheduler** and create a new task.
2. Set it to run at startup or at regular intervals.
3. Choose "Start a program" and set the path to `python.exe`.
4. Add arguments to run the bot, e.g., `C:\path\to\network-node-manager-bot\nnm_check.py`.
5. Save and activate the task.

### Android Setup

Follow the same steps but with some extra setup:

**Pro Tip:** Typing commands on a phone can be tricky. Use SSH from your PC instead! Change the password with `passwd`, run `sshd`, and follow [this guide](https://wiki.termux.com/wiki/Remote_Access).

1. Make sure your device runs **Android >= 6.0**.
2. Install **Termux** from **F-Droid** (don’t use the Play Store version as it's outdated). Download from [here](https://f-droid.org).
3. Get **Termux-API** from F-Droid to access phone features (like battery status).
4. Open Termux and run:
   ```bash
   pkg update && pkg upgrade
   pkg install termux-api python clang cmake make libffi-dev openssl-dev libxml2 libxslt ninja autoconf automake build-essential libtool patchelf
   ```
   This installs the required tools to run the bot.

5. Follow the same steps as other systems.
6. Install **cronie** to replace cron jobs:
   ```bash
   pkg install cronie
   ```
7. Set up the cron job using:
   ```bash
   crontab -e
   ```
   Run `pwd` to find your working directory, usually `/data/data/com.termux/files/home`.

## Automating Restarts (Linux/macOS)

To keep the bot running smoothly, set up a cron job:

```bash
* * * * * cd /path/to/network-node-manager-bot && python3 nnm_check.py
```

This runs the script every minute, ensuring everything stays monitored.
