import ipaddress

raw_ip = input("Enter an IP address: ")

  try:
    address = ipaddress.ip_address(raw_ip)
    print(f"Valid IP address: {address}")
except ValueError:
    print("Invalid IP address.")



  
