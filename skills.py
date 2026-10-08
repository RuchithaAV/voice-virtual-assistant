import ctypes
import os
import re
import subprocess
import urllib.parse
import webbrowser

# Windows Virtual-Key codes for volume control
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
KEYEVENTF_KEYUP = 0x0002

# Application name mapping to executable or shell command
APP_MAPPINGS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "calc": ["calc.exe"],
    "explorer": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
    "files": ["explorer.exe"],
    "task manager": ["taskmgr.exe"],
    "terminal": ["cmd.exe"],
    "command prompt": ["cmd.exe"],
    "cmd": ["cmd.exe"],
    "paint": ["mspaint.exe"],
    "chrome": ["cmd.exe", "/c", "start chrome"],
    "google chrome": ["cmd.exe", "/c", "start chrome"],
    "edge": ["cmd.exe", "/c", "start msedge"],
    "microsoft edge": ["cmd.exe", "/c", "start msedge"],
    "code": ["cmd.exe", "/c", "code"],
    "vs code": ["cmd.exe", "/c", "code"],
    "visual studio code": ["cmd.exe", "/c", "code"],
    "spotify": ["cmd.exe", "/c", "start spotify:"],
}

# Website name and abbreviation mapping to full URLs
WEBSITE_MAPPINGS = {
    "yt": "https://www.youtube.com",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "wikipedia": "https://www.wikipedia.org",
    "wiki": "https://www.wikipedia.org",
    "reddit": "https://www.reddit.com",
    "chatgpt": "https://chatgpt.com",
    "chat gpt": "https://chatgpt.com",
    "gmail": "https://mail.google.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://www.instagram.com",
    "insta": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "kaggle": "https://www.kaggle.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
}


def _send_key_event(vk_code: int, times: int = 1) -> None:
    """Simulates pressing and releasing a virtual key in Windows."""
    user32 = ctypes.windll.user32
    for _ in range(times):
        user32.keybd_event(vk_code, 0, 0, 0)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def adjust_volume(action: str, steps: int = 5) -> str:
    """Adjusts Windows system volume."""
    if action == "up":
        _send_key_event(VK_VOLUME_UP, steps)
        return "Increased system volume."
    elif action == "down":
        _send_key_event(VK_VOLUME_DOWN, steps)
        return "Decreased system volume."
    elif action in ("mute", "unmute"):
        _send_key_event(VK_VOLUME_MUTE, 1)
        return "Toggled volume mute."
    return "Volume command not recognized."


def launch_url(url: str) -> bool:
    """Robustly opens a URL in Windows using native ShellExecute, browser executables, and cmd."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # 1. Native Windows ShellExecute
    try:
        os.startfile(url)
        return True
    except Exception:
        pass

    # 2. Windows start command
    try:
        subprocess.Popen(f'start "" "{url}"', shell=True)
        return True
    except Exception:
        pass

    # 3. Direct browser binaries (Chrome, Brave, Edge)
    known_browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for browser_path in known_browsers:
        if os.path.exists(browser_path):
            try:
                subprocess.Popen([browser_path, url])
                return True
            except Exception:
                continue

    # 4. Python standard webbrowser fallback
    try:
        return webbrowser.open(url, new=2)
    except Exception:
        return False


def launch_application(target: str) -> tuple[bool, str]:
    """Attempts to launch a registered desktop application."""
    target_clean = target.strip().lower()
    for name, cmd in APP_MAPPINGS.items():
        if name in target_clean:
            try:
                subprocess.Popen(cmd)
                return True, f"Opening {name.title()}."
            except Exception as error:
                return False, f"Failed to open {name.title()}: {error}"
    return False, f"Could not find application matching '{target}'."


def perform_web_search(query: str, platform: str = "google") -> tuple[str, str]:
    """Opens browser for Google or YouTube search and returns response text and URL."""
    encoded_query = urllib.parse.quote_plus(query.strip())
    if platform in ("youtube", "yt"):
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        launch_url(url)
        return f"Searching YouTube for '{query}'.", url
    else:
        url = f"https://www.google.com/search?q={encoded_query}"
        launch_url(url)
        return f"Searching Google for '{query}'.", url


def open_website(site_name: str) -> tuple[bool, str, str | None]:
    """Opens a predefined website or arbitrary domain in the default browser."""
    site_clean = site_name.strip().lower()

    # Check known mappings
    for name, url in WEBSITE_MAPPINGS.items():
        if site_clean == name or site_clean.startswith(name + " ") or site_clean.endswith(" " + name):
            launch_url(url)
            return True, f"Opening {name.title()} in your browser.", url

    # Check for direct domains (e.g. 'google.com', 'kaggle.com', 'news.ycombinator.com')
    if re.search(r"\b[a-zA-Z0-9-]+\.(com|org|net|io|in|co|edu|gov|ai|app|dev)\b", site_clean):
        target_url = site_clean
        if not target_url.startswith(("http://", "https://")):
            target_url = f"https://{target_url}"
        launch_url(target_url)
        return True, f"Opening {site_clean} in your browser.", target_url

    return False, f"Website '{site_name}' not recognized.", None


def execute_skill(command: str) -> tuple[bool, str | None, str | None]:
    """
    Evaluates command against automation skills.
    
    Returns:
        (is_handled: bool, response_message: str | None, opened_url: str | None)
    """
    text = command.strip().lower()

    # Clean leading punctuation/fillers if any
    text = re.sub(r"^[,\.\?\!\s]+", "", text)

    # 1. Volume Controls
    if any(phrase in text for phrase in ("volume up", "increase volume", "turn up volume", "raise volume", "increase sound")):
        return True, adjust_volume("up", 6), None

    if any(phrase in text for phrase in ("volume down", "decrease volume", "turn down volume", "lower volume", "reduce volume", "decrease sound")):
        return True, adjust_volume("down", 6), None

    if any(phrase in text for phrase in ("mute volume", "mute audio", "unmute volume", "unmute audio", "mute sound", "unmute sound")) or text in ("mute", "unmute"):
        return True, adjust_volume("mute"), None

    # 2. YouTube Search & Play Commands
    if "youtube" in text or " on yt" in text or text.startswith("yt "):
        for pattern in (
            r"search youtube for (.+)",
            r"search for (.+) on youtube",
            r"search (.+) on youtube",
            r"play (.+) on youtube",
            r"play (.+) on yt",
            r"search yt for (.+)",
            r"search on youtube (.+)",
            r"youtube search for (.+)",
            r"youtube (.+)",
        ):
            match = re.match(pattern, text)
            if match:
                query = match.group(1).strip()
                if query and query not in ("for", "on", "youtube", "yt"):
                    msg, url = perform_web_search(query, platform="youtube")
                    return True, msg, url

    # 3. Google & General Web Searches
    for pattern in (
        r"search google for (.+)",
        r"search for (.+) on google",
        r"search (.+) on google",
        r"google for (.+)",
        r"search for (.+)",
        r"google (.+)",
    ):
        match = re.match(pattern, text)
        if match:
            query = match.group(1).strip()
            if query and query not in ("for", "on", "google"):
                msg, url = perform_web_search(query, platform="google")
                return True, msg, url

    # 4. Direct Website Opening
    for prefix in ("open ", "go to ", "visit ", "launch "):
        if text.startswith(prefix):
            target = text[len(prefix):].strip()
            is_site, site_resp, target_url = open_website(target)
            if is_site:
                return True, site_resp, target_url

            is_app, app_resp = launch_application(target)
            if is_app:
                return True, app_resp, None

    # 5. Direct single-word website aliases (e.g. "youtube", "yt", "github")
    if text in WEBSITE_MAPPINGS:
        is_site, site_resp, target_url = open_website(text)
        return True, site_resp, target_url

    # Not an automation skill command
    return False, None, None


