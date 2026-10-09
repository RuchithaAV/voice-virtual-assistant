import ctypes
import datetime
import os
import re
import subprocess
import urllib.parse
import webbrowser
import psutil
import requests

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

# Weather code descriptions from WMO
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
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


def get_current_time_date(request_type: str = "all") -> str:
    """Returns the current formatted system time and date."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")

    if request_type == "time":
        return f"The current time is {time_str}."
    elif request_type == "date":
        return f"Today is {date_str}."
    return f"It is {time_str} on {date_str}."


def get_system_diagnostics() -> str:
    """Returns current CPU, RAM, and Battery status."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        ram_percent = ram.percent

        battery = psutil.sensors_battery()
        if battery:
            plugged = "plugged in" if battery.power_plugged else "on battery"
            battery_info = f"Battery is at {battery.percent}% ({plugged})."
        else:
            battery_info = "Running on desktop AC power."

        return (
            f"{battery_info} "
            f"CPU usage is {cpu_percent}%, and RAM usage is {ram_percent}%."
        )
    except Exception as error:
        return f"Unable to fetch system metrics: {error}"


def get_live_weather(city_query: str = "London") -> tuple[bool, str, str | None]:
    """Fetches real-time weather information using Open-Meteo free API."""
    city_clean = city_query.strip()
    if not city_clean or city_clean.lower() in ("today", "now", "here", "outside", "current"):
        city_clean = "London"

    headers = {"User-Agent": "VoiceVirtualAssistant/1.0"}
    try:
        # Step 1: Geocoding
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={urllib.parse.quote_plus(city_clean)}&count=1&language=en&format=json"
        )
        geo_resp = requests.get(geo_url, headers=headers, timeout=8).json()

        if not geo_resp.get("results"):
            return False, f"Could not find weather data for location '{city_clean}'.", None

        result = geo_resp["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        city_name = result.get("name", city_clean)
        country = result.get("country", "")

        # Step 2: Forecast
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        )
        weather_resp = requests.get(weather_url, headers=headers, timeout=8).json()
        current = weather_resp.get("current", {})

        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code", 0)
        condition = WEATHER_CODES.get(code, "Clear")

        loc_label = f"{city_name}, {country}" if country else city_name
        summary = (
            f"The current weather in {loc_label} is {condition} with a temperature of {temp}°C, "
            f"humidity of {humidity}%, and wind speed of {wind} km/h."
        )
        online_url = f"https://www.google.com/search?q=weather+{urllib.parse.quote_plus(city_name)}"
        return True, summary, online_url
    except Exception as error:
        return False, f"Failed to retrieve weather data: {error}", None



def get_wikipedia_summary(topic: str) -> tuple[bool, str, str | None]:
    """Retrieves a direct encyclopedic summary from Wikipedia REST API."""
    topic_clean = topic.strip().replace(" ", "_")
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic_clean)}"
        headers = {"User-Agent": "VoiceVirtualAssistant/1.0 (academic_project)"}
        resp = requests.get(url, headers=headers, timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract", "")
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page")
            if extract:
                # Trim extract to first 2 sentences for voice brevity
                sentences = re.split(r"(?<=[.!?])\s+", extract)
                concise_extract = " ".join(sentences[:2])
                return True, concise_extract, page_url

        return False, f"Could not find a Wikipedia summary for '{topic}'.", None
    except Exception as error:
        return False, f"Wikipedia lookup error: {error}", None


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
    Evaluates command against automation and real-time knowledge skills.
    
    Returns:
        (is_handled: bool, response_message: str | None, opened_url: str | None)
    """
    text = command.strip().lower()

    # Clean leading/trailing punctuation/fillers if any
    text = re.sub(r"^[,\.\?\!\s]+", "", text)
    text = re.sub(r"[,\.\?\!\s]+$", "", text)

    # 1. Volume Controls
    if any(phrase in text for phrase in ("volume up", "increase volume", "turn up volume", "raise volume", "increase sound")):
        return True, adjust_volume("up", 6), None

    if any(phrase in text for phrase in ("volume down", "decrease volume", "turn down volume", "lower volume", "reduce volume", "decrease sound")):
        return True, adjust_volume("down", 6), None

    if any(phrase in text for phrase in ("mute volume", "mute audio", "unmute volume", "unmute audio", "mute sound", "unmute sound")) or text in ("mute", "unmute"):
        return True, adjust_volume("mute"), None

    # 2. Time & Date
    if any(phrase in text for phrase in ("what time is it", "current time", "tell me the time", "what is the time")):
        return True, get_current_time_date("time"), None

    if any(phrase in text for phrase in ("what is the date", "today's date", "what day is today", "what is today's date", "what's the date")):
        return True, get_current_time_date("date"), None

    # 3. System Diagnostics & Battery
    if any(phrase in text for phrase in ("battery status", "battery level", "battery percentage", "cpu usage", "ram usage", "system status", "system health", "system diagnostics")):
        return True, get_system_diagnostics(), None

    # 4. Live Weather
    if "weather" in text or "temperature" in text:
        city = "London"
        loc_match = re.search(r"(?:in|for|at|of)\s+([a-zA-Z\s]+)", text)
        if loc_match:
            candidate = loc_match.group(1).strip()
            candidate = re.sub(r"\b(today|now|currently|outside|right now|please|like|report|forecast)\b", "", candidate).strip()
            if candidate:
                city = candidate
        else:
            clean_phrase = re.sub(r"\b(what|what's|is|the|weather|temperature|now|today|currently|report|how)\b", "", text).strip()
            if clean_phrase:
                city = clean_phrase

        ok, weather_msg, weather_url = get_live_weather(city)
        if ok:
            return True, weather_msg, weather_url

    # 5. Direct Wikipedia Knowledge Lookup
    # Avoid routing time, date, weather, or conversational prompts to Wikipedia
    if not any(k in text for k in ("weather", "temperature", "time", "date", "battery", "cpu", "ram", "volume", "open ", "play ")):
        for pattern in (
            r"^who is (.+)",
            r"^who was (.+)",
            r"^what is (.+)",
            r"^what was (.+)",
            r"^tell me about (.+)",
            r"^define (.+)",
            r"^explain (.+)",
        ):
            match = re.match(pattern, text)
            if match:
                topic = match.group(1).strip()
                if topic not in ("your name", "my name", "you", "this", "that", "it"):
                    ok, wiki_msg, wiki_url = get_wikipedia_summary(topic)
                    if ok:
                        return True, wiki_msg, wiki_url


    # 6. YouTube Search & Play Commands
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

    # 7. Google & General Web Searches
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

    # 8. Direct Website & Application Opening
    for prefix in ("open ", "go to ", "visit ", "launch "):
        if text.startswith(prefix):
            target = text[len(prefix):].strip()
            is_site, site_resp, target_url = open_website(target)
            if is_site:
                return True, site_resp, target_url

            is_app, app_resp = launch_application(target)
            if is_app:
                return True, app_resp, None

    # 9. Direct single-word website aliases (e.g. "youtube", "yt", "github")
    if text in WEBSITE_MAPPINGS:
        is_site, site_resp, target_url = open_website(text)
        return True, site_resp, target_url

    # Not an automation skill command
    return False, None, None



