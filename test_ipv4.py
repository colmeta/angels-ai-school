import socket
from urllib.parse import urlparse

# Test DATABASE_URL parsing and IPv4 resolution
test_url = "postgresql://postgres:password@db.hsmfffgszcgmmyynaeqi.supabase.co:5432/postgres"

parsed = urlparse(test_url)
print(f"Hostname: {parsed.hostname}")
print(f"Port: {parsed.port}")

# Try IPv4 resolution
try:
    addr_info = socket.getaddrinfo(
        parsed.hostname,
        parsed.port or 5432,
        socket.AF_INET,  # Force IPv4
        socket.SOCK_STREAM
    )
    print(f"\nIPv4 Resolution successful:")
    for info in addr_info:
        print(f"  Address: {info[4][0]}")
except Exception as e:
    print(f"\nIPv4 Resolution failed: {e}")
