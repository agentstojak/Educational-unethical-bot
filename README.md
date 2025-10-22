# Educational-unethical-bot


This bot was created for educational purposes, showcasing various techniques and functionalities that can be implemented using different AI models. The models utilized include Google Gemini, v0, ChatGPT, DeepSeek, and GitHub Copilot. This README provides an overview of the bot's capabilities and the code structure. 📚

Features 🌟
System Information 💻
System Info: Retrieves and displays detailed system information. 📊
Screenshot: Takes a screenshot and sends it to the Discord channel. 📸
Shutdown/Restart: Allows the bot to shutdown or restart the system. ⏹️⏺️
Persistence and Protection 🔒
Startup Persistence: Ensures the bot runs on system startup by adding it to the Windows startup folder and registry. 🔄
Anti-Deletion Protection: Hides the bot process and file attributes to make it harder to kill or delete. 🛡️
Self-Heal: If the original bot is deleted, it recreates itself from the startup copy. 🔄
Monitoring and Theft 🕵️‍♂️
Keylogger: Records keystrokes and sends them to a specified Discord channel. 🔑
Screen Recording: Records the screen for a specified duration and sends the video to a Discord channel. 🎥
Microphone Recording: Records audio from the microphone and sends it to a Discord channel. 🎤
Discord Token Dump: Extracts and sends Discord tokens and account information. 🔑
Browser Credential Dump: Extracts and sends saved passwords from browsers like Chrome, Edge, and Brave. 🔑
Game Data Dump: Steals data from Minecraft and Epic Games launchers. 🎮
File Operations 📂
Download: Allows downloading files from the system. 📤
Upload: Supports uploading files to the Discord channel. 📥
Process Management 🖥️
List Processes: Lists all running processes on the system. 📋
Kill Process: Terminates a process by its PID. ❌
Network and System 🌐
Network Connections: Displays active network connections. 🔗
Message Box: Displays a message box on the user's screen. 📢
User Info: Retrieves and displays user information and environment variables. 👤
Webcam: Takes a photo using the webcam and sends it to the Discord channel. 📸
Additional Commands 🛠️
Build: Compiles the bot into a standalone .exe file. 🛠️
Geolocate: Geolocates an IP address and provides location details. 🌍
Open URL: Opens a specified URL in the default web browser. 🌐
Play Sound: Plays a sound from a given URL. 🔊
Installation and Setup 🔧
Clone the Repository:

bash
git clone https://github.com/yourusername/educational-unethical-bot.git
cd educational-unethical-bot
Install Dependencies:

bash
pip install -r requirements.txt
Set Up Discord Bot:

Create a new application on the Discord Developer Portal.
Copy the bot token and replace YOUR-OWN-TOKEN in the code with your token. 🔑
Run the Bot:

bash
python your_bot_script.py
Commands 📜
System Commands
!systeminfo: Show system information. 📊
!screenshot: Take a screenshot. 📸
!shutdown: Shutdown the computer. ⏹️
!restart: Restart the computer. ⏺️
!listprocesses: List running processes. 📋
!kill [PID]: Kill a process by ID. ❌
!exec [command]: Execute a shell command. 💻
File Operations
!download [path]: Download a file. 📤
!upload: Upload attached files. 📥
!clipread: Read clipboard. 📋
!clipwrite [text]: Write to clipboard. ✏️
Monitoring
!startrecording [duration]: Start screen recording. 🎥
!stoprecording: Stop recording. ⏹️
!keylog: Start keylogger. 🔑
!stopkl: Stop keylogger. ❌
!webcam: Take webcam photo. 📸
!connections: Show network connections. 🔗
Persistence
!persist: Make bot launch on startup. 🔄
!stopstartup: Remove startup persistence. ❌
!selfdestruct: Delete bot and all traces. 💣
Credential Theft
!dumpcreds: Dump saved passwords. 🔑
!dumpdiscord: Steal Discord tokens. 🔑
!dumpgames: Steal game launcher data. 🎮
Builder
!build: Compiles the bot into a distributable .exe. 🛠️
Other
!message [text]: Show message box. 📢
!userinfo: Show user info. 👤
!cmds: Show this help menu. 📜
!geolocate [port]: Locates the user. 🌍
!openurl [url]: Open a URL in the browser. 🌐
!playsound [url]: Play sound from URL. 🔊
Contributing 🤝
Contributions are welcome! Feel free to fork the repository and submit pull requests. 🛠️

License 📜
This project is licensed under the MIT License. See the LICENSE file for details. 🔍

Disclaimer ⚠️
This bot is for educational purposes only and should be used responsibly. Unauthorized access to systems or data may be illegal and unethical. 🚫
