# Network Node Manager Bot

## About This Project

I started this project to tackle a personal issue. At home, I run a mini server with a bunch of self-hosted services.
But sometimes, the power goes out, and since I don’t have a UPS, the server shuts down, and I can’t do anything about it
when I’m away.

So I thought—why not use other devices, like old Android phones, to keep an eye on the server and wake it up when the
power comes back? That’s how this project was born, and it works pretty well now! It even sends me updates on Telegram
when something happens.

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

**General Advice for Nodes:**
To ensure stability, it's highly recommended to set up **static IP addresses** for your nodes via your home router. This
way, if anything goes wrong, they will always reconnect using the same IP addresses once everything is back to normal.

The bot uses **Google Spreadsheets** to store data online, outside the home network, in case of a power failure. Here's
how to set it up:

1. **Google Cloud Setup:**
    - Create a project in Google Cloud Platform.
    - Generate credentials to let nodes write to the spreadsheet.
    - Save the credentials file as **`google_credentials.json`** in the project folder.

2. **Spreadsheet Configuration:**
   The spreadsheet contains several key columns used by the nodes to adjust their behavior:
    - **NODE_ID:** Sequential numbers from 1 to N, identifying each node.
    - **NODE_LAN_IP:** Identifies the node on the network, allowing other nodes to ping it.
    - **NODE_MAC_ADDRESS:** Stores the MAC address of the network interface for nodes that support Wake-on-LAN.
    - **CHECK:** Determines if the node should be contacted for pings and Wake-on-LAN. This is useful for devices like
      my personal tablet, which I take on trips and disable via a Telegram command.
    - **WOL:** Indicates if the node supports Wake-on-LAN.

   The spreadsheet must be uploaded to **Google Drive**, and sharing permissions should be set to allow **anyone with
   the link to edit**, ensuring that all nodes can access and update it.

   The initial configuration might seem tricky, but I've included Telegram bot commands to simplify adjustments later.

3. **Node Data Writing:**
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
   source .venv/bin/activate   # Android/Linux/macOS
   .venv\Scripts\activate      # Windows
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Place the `google_credentials.json` file in the correct directory.
7. On Android, macOS, and Linux, run the following command to make the start script executable:
   ```bash
   chmod +x start.sh
   ```
   **Note:** On macOS and Linux, use `sudo` to run the command.

## Telegram Configuration and Bot Commands

1. Set up a Telegram bot via **BotFather**.
2. Save your new Telegram Token for next steps.

The bot comes with several commands to help manage nodes:

```plaintext
/reboot - Reboots the node.
/enable - Enables the contacted node to be verified.
/disable - Disables the contacted node to prevent it from being verified.
/enable_nodes - Enables the nodes sent as arguments from another node.
/disable_nodes - Disables the nodes sent as arguments from another node.
/check - Checks the operation of the node.
```

When creating the bot in BotFather, you can copy and paste this list to have all commands readily available in the chat.
I personally added the nodes to a group to send the same command to all bots and get all responses in a single chat.

## .env File Configuration

1. Configure the **.env** file with the following:
   ```plaintext
   TELEGRAM_TOKEN=your-telegram-token
   TELEGRAM_MAIN_GROUP=chat-id-or-group-id
   NODE_ID=node-id
   NODE_HAS_BATTERY=node-battery-for-laptop-or-smartphones integer 1-0
   SPREADSHEET_URL=google-spreadsheet-url-like https://docs.google.com/spreadsheets/d/1
   MAIN_SHEET_ID=main-sheet-id-usually-0
   NODE_SHEET_ID=node-sheet-id
   NODE_DEBUG=debug-mode integer 1-0
   ```

## Android Setup

Follow the same steps but with some extra setup:

**Pro Tip:** Typing commands on a phone can be tricky. Use SSH from your PC instead! Change the password with `passwd`,
run `sshd`, and follow [this guide](https://wiki.termux.com/wiki/Remote_Access).

1. Make sure your device runs **Android >= 6.0**.
2. Install **Termux** from **F-Droid** (don’t use the Play Store version as it's outdated). Download
   from [here](https://f-droid.org).
3. Get **Termux-API** from F-Droid to access phone features (like battery status).
4. Open Termux and execute:
   ```bash
   pkg update && pkg upgrade
   termux-setup-storage
   pkg install cronie termux-api python clang cmake make libffi-dev openssl-dev libxml2 libxslt ninja autoconf automake build-essential libtool patchelf
   ```

**Pro Tip:** On Android I recommend to install pip packages using the -v option, because it can happen that the device
is not very performant so it looks like it froze.

Just run command like this:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -v
chmod +x start.sh
./start.sh
```

## Automating Restarts (Android/Linux/macOS)

To keep the bot running smoothly, set up a cron job:

```bash
* * * * * cd /path/to/network-node-manager-bot && python3 nnm_check.py
```

### Windows Task Scheduler Setup

On Windows, use Task Scheduler to automate running the bot:

1. Open **Task Scheduler** and create a new task.
2. Set it to run at startup or at regular intervals.
3. Choose "Start a program" and set the path to `python.exe`.
4. Add arguments to run the bot, e.g., `C:\path\to\network-node-manager-bot\nnm_check.py`.
5. Save and activate the task.

This runs the script every minute, ensuring everything stays monitored.

## What's Next?

- Better logging and analytics.
- Support for more messaging platforms.
- A self-hosted data storage alternative to Google.

