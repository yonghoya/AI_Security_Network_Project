# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
import socket
import requests
from checkurl.models import URLManager
from checkurl.models import url_judge



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
    type_explanation = url_manager_view(url_type)
    insert_db(AI_output, url_type, input_string, ip, country)

    context = {'url': input_string, 'AI_output': AI_output, 'url_type': url_type, 'type_explanation': type_explanation, 'ip': ip, 'country': country}
    return context




def AI(url):
    try:
        data = {"url": url}
        response = requests.post("http://3.34.52.88:8000/predict", json=data) ##유동ip
        response.raise_for_status()  # Raise an exception if the request fails
        result = response.json()
        malicious_result = False
        type_result = result['predict_result']
        if type_result != "benign":
            malicious_result = True
        return malicious_result, type_result
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return 0, "Error",


def insert_db(AI_output, url_type, input_string, ip, country):
    try:
        new_test_entry = url_judge(AI_output, url_type, input_string, ip, country)
        new_test_entry.save()
        print("데이터가 저장되었습니다.")
    except Exception as e:
        print(f"Database Exception: {e}")





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




def url_manager_view(type):
    type_upper = type.capitalize()
    url_manager_data = URLManager.objects.filter(url_type=type_upper)
    type_explanation = ""
    if url_manager_data:
        type_explanation = url_manager_data[0].type_explanation
        print(type_explanation)

    return type_explanation





