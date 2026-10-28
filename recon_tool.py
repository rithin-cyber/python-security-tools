import socket
import urllib.request
import urllib.error

hostname = input("Enter an authorized hostname: ").strip()

if not hostname:
    print("Please enter a hostname.")
    raise SystemExit(1)

if hostname.lower().startswith("https://") or hostname.lower().startswith("http://"):
    print("Enter hostname only, such as example.com.")
    raise SystemExit(1)

if "/" in hostname:
    print("Enter hostname only, without a path, such as example.com.")
    raise SystemExit(1)

if " " in hostname:
    print("Hostname cannot contain spaces.")
    raise SystemExit(1)

if "?" in hostname or "#" in hostname:
    print("Enter hostname only, without a query string or fragment.")
    raise SystemExit(1)

# Step 1: Resolve the hostname.
try:
    ip_address = socket.gethostbyname(hostname)
    print(f"Hostname: {hostname}")
    print(f"IPv4 address: {ip_address}")

except socket.gaierror:
    print("DNS resolution failed.")
    raise SystemExit(1)

# Step 2: Make one HTTPS request.
url = f"https://{hostname}/"

try:
    with urllib.request.urlopen(url, timeout=5) as response:
        print(f"HTTPS status: {response.status}")
        print(f"Final URL: {response.geturl()}")

except urllib.error.HTTPError as error:
    print(f"HTTPS status: {error.code}")

except urllib.error.URLError as error:
    print(f"HTTPS request failed: {error.reason}")
