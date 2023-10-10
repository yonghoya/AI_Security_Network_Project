from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import multiprocessing
import csv
import socket
import requests
import json
import re
from checkurl import multi
from checkurl.models import url_judge
from checkurl.models import URLManager
from checkurl.models import white_list
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
@csrf_exempt 
def checkurl_main(request):
    if request.method == 'POST':
        url_string = request.POST.get('input_string', '')  # url_string 초기화
        if url_string:  # url_string이 비어있지 않은 경우에만 실행
            context = information(url_string)
            return render(request, 'checkurl/output.html', context)
    return render(request, 'checkurl/input.html')

'''
def checkurl_main(request):
    if request.method == 'POST':
        url_string = request.POST.get('input_string', '')  # url_string 초기화
        if url_string:  # url_string이 비어있지 않은 경우에만 실행
            context = information(url_string)
            return render(request, 'checkurl/output.html', context)
    return render(request, 'checkurl/input.html')
'''

def information(input_string):
    try:
        pattern = r"(https?://)"
        input_string = re.sub(pattern, "", input_string)
        input_string = input_string.rstrip("/")
        # Assuming these functions can raise exceptions
        AI_output, url_type = multi_processing(input_string)
        ip, country, country_img = get_ip(input_string)
        type_explanation = url_manager_view(url_type)

        # Assuming insert_db can raise exceptions as well
        insert_db(AI_output, url_type, input_string, ip, country)

        context = {
            'url': input_string,
            'AI_output': AI_output,
            'url_type': url_type,
            'type_explanation': type_explanation,
            'ip': ip,
            'country': country,
            'country_img': mark_safe(country_img),
        }
        return context
    except Exception as e:
        return {'error': str(e)}
@csrf_exempt
def url_check_endpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url_to_check = data.get('url')
            if url_to_check is None:
                return JsonResponse({'error': 'Missing "url" key in JSON data'}, status=400)

            try:
                AI_output, url_type = multi_processing(url_to_check)
                return JsonResponse({'predict_result': url_type})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

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
    except Exception as e:
        raise Exception(f"An error occurred while inserting data to the database: {str(e)}")

def get_ip(input_string):
    print(input_string)
    def get_ip_address(domain):
        try:
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except socket.gaierror:
            return None

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
    if not urlparse(domain).scheme:
        domain = "http://" + domain
         
    parsed_url = urlparse(domain)
    host = parsed_url.netloc

    try:
        ip_address = get_ip_address(host)
        country = get_country(ip_address)
        country_image_url = get_country_image_url(country)
    except socket.gaierror as e:
        print(f"An error occurred: {e}")
        return None

    return ip_address, country, country_image_url

def url_manager_view(type):
    try:
        type_upper = type.capitalize()
        url_manager_data = URLManager.objects.filter(url_type=type_upper)
        type_explanation = ""
        if url_manager_data:
            type_explanation = url_manager_data[0].type_explanation
        return type_explanation
    except Exception as e:
        raise Exception(f"An error occurred in url_manager_view: {str(e)}")

