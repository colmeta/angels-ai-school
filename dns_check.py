import socket
import urllib.parse

def check_dns(hostname):
    print(f"Checking DNS for {hostname}")
    try:
        print(f"gethostbyname: {socket.gethostbyname(hostname)}")
    except Exception as e:
        print(f"gethostbyname failed: {e}")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for info in addr_info:
            family = "IPv4" if info[0] == socket.AF_INET else "IPv6"
            print(f"getaddrinfo: {family} -> {info[4][0]}")
    except Exception as e:
        print(f"getaddrinfo failed: {e}")

if __name__ == "__main__":
    check_dns("db.hsmfffgszcgmmyynaeqi.supabase.co")
    check_dns("google.com")
