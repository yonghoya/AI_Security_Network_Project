
from django.http import HttpResponse
from django.shortcuts import render
import socket
import requests
import multiprocessing
import csv

from checkurl import multi
from checkurl.models import url_judge
from checkurl.models import URLManager

from django.utils.safestring import mark_safe
from checkurl.models import white_list



"""
def make_white_DB():
    num = 1
    with open('C:/projects/sixproject/checkurl/top500Domains.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            root_domain = row[1]
            new_white = white_list(num, root_domain)
            new_white.save()
            num += 1
"""

"""
def asdf():
    new1 = URLManager(1, "Benign", "악의적인 목적이나 위협을 갖지 않는 일반적인 웹 페이지 주소입니다.", False)
    new2 = URLManager(2, "Defacement", "웹 사이트나 웹 페이지의 외관을 공격자가 변경하여 피해자나 방문자에게 악의적인 메시지나 그래픽을 노출하는 URL입니다.", True)
    new3 = URLManager(3, "Phishing", "피해자를 속여 개인 정보나 금융 정보를 탈취하려는 악의적인 목적으로 설계된 URL입니다.", True)
    new4 = URLManager(4, "Malware", "악성 코드 또는 악성 소프트웨어를 다운로드하거나 실행하도록 설계된 URL입니다.", True)

    new1.save()
    new2.save()
    new3.save()
    new4.save()
"""



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
    AI_output, url_type = multi_processing(input_string)
    print(AI_output)
    print(url_type)
    ip, country, country_img = get_ip(input_string)
    print(country_img)
    type_explanation = url_manager_view(url_type)
    insert_db(AI_output, url_type, input_string, ip, country)

    context = {'url': input_string, 'AI_output': AI_output, 'url_type': url_type, 'type_explanation': type_explanation, 'ip': ip, 'country': country, 'country_img': mark_safe(country_img)}
    ## url : 클라이언트가 입력한 url(str), AI_output : 악성여부(bool), url_type : AI가 판단한 해당 url의 타입(str), type_explanation : 해당 type에 대한 설명(str), ip(str), country : 국가명(str)
    return context




def multi_processing(input_string):

    print("multi_process in!")
    return_queue = multiprocessing.JoinableQueue()
    AI_process = multiprocessing.Process(target=multi.AI, args=(input_string, return_queue))
    DB_process = multiprocessing.Process(target=multi.scan_DB, args=(input_string, return_queue))
    AI_process.start()
    DB_process.start()


    DB_process.join()
    result_DB = return_queue.get()
    if result_DB[1] != "Null": ##db에 해당 url 정보가 존재한다면
        return result_DB[0], result_DB[1]


    AI_process.join()
    result_AI = return_queue.get()
    print("multi_process finished!")
    return result_AI[0], result_AI[1]









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

    def get_country_image_url(country_name):
        base_url = "https://restcountries.com/v3.1/name/"
        url = f"{base_url}{country_name}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()[0]  # Assuming the first result is the correct one
            flag_url = data["flags"]["png"]

            # Append query parameters to the image URL to resize it
            resized_flag_url = f"{flag_url}?width=50&height=50"  # You can adjust width and height as needed

            return resized_flag_url
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching country image: {e}")
            return None
        except (IndexError, KeyError) as e:
            print(f"Country data format error: {e}")
            return None

    domain = input_string

    try:
        ip_address = get_ip_address(domain)
        country = get_country(ip_address)
        country_image_url = get_country_image_url(country)
    except socket.gaierror as e:
        print(f"An error occurred: {e}")
        return None

    return ip_address, country, country_image_url




def url_manager_view(type):
    type_upper = type.capitalize()
    url_manager_data = URLManager.objects.filter(url_type=type_upper)
    type_explanation = ""
    if url_manager_data:
        type_explanation = url_manager_data[0].type_explanation

    return type_explanation





