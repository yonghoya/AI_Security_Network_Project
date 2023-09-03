import socket
import requests

def get_ip(input_string):
    def get_ip_address(domain):
        ip_address = socket.gethostbyname(domain)
        return ip_address

    def get_country(ip_address):
        response = requests.get(f"https://ipapi.co/{ip_address}/country_name/").text
        return response.strip()  # Remove leading/trailing whitespace

    domain = input_string

    ip_address = get_ip_address(domain)
    country = get_country(ip_address)

    print(f"The IP address of {domain} is: {ip_address}")
    print(f"The country of {ip_address} is: {country}")

    return ip_address, country

a, b = get_ip("www.naver.com")