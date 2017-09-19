from django.shortcuts import render,HttpResponse,redirect
import time

# Create your views here.
def hotel_rate(request):
    if request.method=='POST':
        output=[['a','b','c','e','f','g','h','i','k']]
        for i in range(10):
            output.append(['1','2','3','4','5','6','7','8','9095555555888855999'])


        return HttpResponse(str(output))
    return redirect('/index')

def index(request):


    return render(request,'index.html')
