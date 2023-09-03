from django.shortcuts import render, redirect

def index(request):
    if request.method == 'POST':
        input_string = request.POST.get('input_string')
        if input_string:
            return redirect('output', keyword=input_string)
    return render(request, 'main/input.html')
    
def output(request, keyword):
    if request.method == 'POST':
        return redirect('index')

    context = {'keyword': keyword}
    return render(request, 'main/output.html', context)
