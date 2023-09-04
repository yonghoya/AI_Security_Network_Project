# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
import socket
import requests



def index(request):
    return HttpResponse("안녕하세요  test에 오신것을 환영합니다.")


def checkurl_main(request):
    if request.method == 'POST':
        url_string = request.POST.get('input_string', '')
        if url_string:
            context = information(url_string)
            return render(request, 'checkurl/output.html', context)

    return render(request, 'checkurl/input.html')


def information(input_string):
    AI_output, url_type = AI(input_string)
    ip, country = get_ip(input_string)

    context = {'url': input_string, 'AI_output': AI_output, 'url_type': url_type, 'ip': ip, 'country': country}
    return context


def AI(input_string):
    ##코드 추가 필요
    return 1, "Phishing" ##test를 위한 하드코딩. 향후 삭제






def get_ip(input_string):
    def get_ip_address(domain):
        ip_address = socket.gethostbyname(domain)
        return ip_address

    def get_country(ip_address):
        url = f"https://ipapi.co/{ip_address}/country_name/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return response.text.strip()  # Remove leading/trailing whitespace
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    domain = input_string

    try:
        ip_address = get_ip_address(domain)
        country = get_country(ip_address)
    except socket.gaierror as e:
        print(f"An error occurred: {e}")
        return None

    return ip_address, country




