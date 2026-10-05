# main.py
import network
import uasyncio as asyncio
from machine import Pin
import server
import urequests  # Built-in, takes 0 extra storage space

# --- CONFIGURATION ---
SSID = "CS-Students"
PASSWORD = "nirmala@sep26"
#SSID = "Athuldev"
#PASSWORD = "qwertyuiop"

# --- CONFIGURATION ---
BOT_TOKEN = "8995755794:AAE5DvWm-Zx9wn1LUfFyO4H_gRvbC-fAynQ"
CHAT_ID = "1112521696"  # Replace with the ID from @userinfobot
# ---------------------
# ---------------------

led = Pin(2, Pin.OUT)

# Tiny, memory-efficient Telegram function
def send_telegram_ip(ip):
    print("Sending IP to Telegram...")
    # Use %20 for spaces to avoid importing URL-encoding libraries
    text = f"🟢%20GhostNode%20Online!%0AIP:%20{ip}"
    
    # Corrected line: Use the variables BOT_TOKEN and CHAT_ID here!
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
    
    try:
        r = urequests.get(url)
        r.close() # CRITICAL: Closes connection to free up RAM
        print("Telegram alert sent!")
    except Exception as e:
        print("Telegram failed:", e)

async def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="ESP32-HUB", authmode=network.AUTH_OPEN)
    print("Hotspot active:", ap.ifconfig()[0])

async def blink_led(state):
    # Safe toggle logic for the LED
    toggle = 0
    while state["is_connecting"]:
        toggle = 1 if toggle == 0 else 0
        led.value(toggle)
        await asyncio.sleep_ms(200) # Fast blink while searching

async def main():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.disconnect() 
    
    state = {"is_connecting": True}
    asyncio.create_task(blink_led(state)) # Start blinking!
    
    print(f"Connecting to WiFi '{SSID}'...")
    sta.connect(SSID, PASSWORD)
    
    for _ in range(150): 
        if sta.isconnected():
            ip = sta.ifconfig()[0]
            print("Connected! IP:", ip)
            
            # 1. Stop the blinking task
            state["is_connecting"] = False
            await asyncio.sleep_ms(300) # Give it a millisecond to stop
            
            # 2. Force the LED to SOLID ON (Stable)
            led.value(1) 
            
            # 3. Send the IP to your phone!
            send_telegram_ip(ip)
            break
            
        await asyncio.sleep_ms(100)
    else:
        print("WiFi Timeout. Starting Hotspot...")
        state["is_connecting"] = False
        sta.active(False)
        await start_ap()
        
        # Force LED to SOLID ON for Hotspot mode too
        led.value(1) 

    print("Starting Server...")
    await server.start_server()
    
    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped.")
    led.value(0) # Turn off if crashed/stopped
