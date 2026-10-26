import ipaddress

# Ask the user for an IP address.
raw_ip = input("Enter an IP address: ")

try:
    # Validate the input as an IPv4 or IPv6 address.
    address = ipaddress.ip_address(raw_ip)

    # Display the validated address.
    print(f"Valid IP address: {address}")

except ValueError:
    # Handle input that is not a valid IP address.
    print("Invalid IP address.")

  
