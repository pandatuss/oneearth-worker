import asyncio
import aiohttp
import time

# URLs
LOGIN_URL = "https://www.oneearthtmaproject.com/login"
PICK_URL = "https://www.oneearthtmaproject.com/mainGamePick"

# Login POST body (replace with your data)
LOGIN_PAYLOAD_RAW = (
    "loginData=%7b%22user%22%3a%7b%22id%22%3a6704048301%2c%22first_name%22%3a%22Black%22"
    "%2c%22last_name%22%3a%22Hound%22%2c%22username%22%3a%22blackhoundz%22%2c%22language_code%22%3a%22en%22"
    "%2c%22allows_write_to_pm%22%3atrue%2c%22photo_url%22%3a%22https%3a%2f%2ft.me%2fi%2fuserpic%2f320"
    "%2fxG7f8T7e8DNPvb9bowEbWCJqXeH_xpCYFBk79uC4hJM2j4fv5fjkN4_1O6Y8CYb_.svg%22%7d%2c%22chat_instance%22"
    "%3a%22686730004733806821%22%2c%22chat_type%22%3a%22sender%22%2c%22auth_date%22%3a%221762648758%22"
    "%2c%22signature%22%3a%22QBObEjO2FYznehrGPiklPUsdblgh9x32WlACw87T2QJ0yQCpOkXESvqyGnoMkbtEhCTi7iBrWfgxNpn-T0x7DA%22"
    "%2c%22hash%22%3a%226ab6ed0f4d9e7e9043cdac87bb273ac0520776e279b1861ee62982ca8e960590%22%7d"
)

# Login headers
LOGIN_HEADERS = {
    "Host": "www.oneearthtmaproject.com",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "Accept": "*/*",
    "Origin": "https://www.oneearthtmaproject.com",
    "Referer": "https://www.oneearthtmaproject.com/"
}

# Pick POST body (example)
PICK_BODY = "userID=6704048301&playerID=2436&pickCount=1&isFever=0"

# Pick headers template
def pick_headers(token):
    return {
        "Host": "www.oneearthtmaproject.com",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
        "Accept": "*/*",
        "Origin": "https://www.oneearthtmaproject.com",
        "Referer": "https://www.oneearthtmaproject.com/"
    }

# Function to login and get access token (updated to parse JSON)
async def get_api_key():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(LOGIN_URL, data=LOGIN_PAYLOAD_RAW, headers=LOGIN_HEADERS, timeout=12) as resp:
                json_resp = await resp.json()
                # Extract accessToken from JSON response
                token = json_resp.get('data', {}).get('accessToken')
                if token:
                    print(f"[+] API key obtained: {token}")
                    return token
                else:
                    print("[!] Could not find accessToken in JSON response.")
                    print(f"[!] JSON Response: {json_resp}")
        except Exception as e:
            print(f"[!] Error during login request: {e}")
    return None

# Function to send pick request
async def send_pick(session, token):
    headers = pick_headers(token)
    try:
        async with session.post(PICK_URL, data=PICK_BODY, headers=headers, timeout=12) as resp:
            text = await resp.text()
            print(f"[+] Pick sent. Response snippet: {text[:100]}")
            return True
    except Exception as e:
        print(f"[!] Pick request error: {e}")
        return False

# Main worker loop
async def main_worker():
    token = await get_api_key()
    if not token:
        print("[!] Cannot start worker without API key.")
        return

    count = 0
    async with aiohttp.ClientSession() as session:
        while True:
            success = await send_pick(session, token)
            count += 1

            if not success:
                print("[!] Error occurred. Waiting 10 minutes before refreshing token...")
                await asyncio.sleep(600)  # 10 minutes
                token = await get_api_key()
                if not token:
                    print("[!] Failed to refresh token. Exiting.")
                    return
                count = 0  # reset count after error

            # Refresh token after 500 picks
            if count >= 500:
                print("[*] 500 picks done. Refreshing token...")
                token = await get_api_key()
                if not token:
                    print("[!] Failed to refresh token. Exiting.")
                    return
                count = 0

            await asyncio.sleep(0.5)  # 0.5 second interval

if __name__ == "__main__":
    print("[*] Starting worker...")
    asyncio.run(main_worker())
