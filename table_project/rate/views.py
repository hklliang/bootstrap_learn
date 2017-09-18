from django.shortcuts import render,HttpResponse,redirect
import time

# Create your views here.
def hotel_rate(request):
    if request.method=='POST':
        output=[['a','b','c'],['1','2','3'],['1','2','3']]
        time.sleep(3)
        return HttpResponse(str(output))
    return redirect('/index')

def index(request):


    return render(request,'index.html')
