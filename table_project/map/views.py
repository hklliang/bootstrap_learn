from django.shortcuts import render,HttpResponse
from django.views.generic import View
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import HotelMapSuggest
import json
import datetime
# Create your views here.
class HotelMap(View):

    def get(self,request):

        return render(request,'hotelMap.html')

    def post(self,request):
        cPage=int(request.POST.get('cPage'))
        if cPage<=0:
            cPage=1
        pSize=int(request.POST.get('pSize'))

        gf_id=request.POST.get('gf_id')
        supp_id=request.POST.get('supp_id')
        supp_name = request.POST.get('supp_id')
        status=request.POST.get('status')

        sort_name_score=request.POST.get('sort_name_score')

        sort_address_score = request.POST.get('sort_address_score')
        sort_createDate = request.POST.get('sort_createDate')
        sort_lastDate = request.POST.get('sort_lastDate')
        sort=[]
        if sort_name_score:
            if sort_name_score=='1':
                sort.append('name_score')
            else:
                sort.append('-name_score')
        if sort_address_score:
            if sort_address_score == '1':
                sort.append('address_score')
            else:
                sort.append('-address_score')

        if sort_createDate:
            if sort_createDate == '1':
                sort.append('createDate')
            else:
                sort.append('-createDate')
        if sort_lastDate:
            if sort_lastDate == '1':
                sort.append('lastDate')
            else:
                sort.append('-lastDate')



        filter={}
        if gf_id:
            filter['gf_id'] = gf_id
        if supp_id:
            filter['supp_id'] = supp_id
        if supp_name:
            filter['supp_name__icontains'] = supp_name
        if status:
            filter['status'] = status
#"这种惰性利用了 Python 的分片（slicing）功能。下面的代码并没有先请求所有的记录，然后对所需要的记录进行分片，而是在实际的查询中使用了 5 作为 OFFSET、10 作为 LIMIT，这可以极大地提高性能。"
        all_data=HotelMapSuggest.objects.all()
        data=list(all_data.filter(**filter).order_by(*sort).values()[(cPage-1)*pSize:cPage*pSize])

        # json_data = serializers.serialize("json", data)
        totals=len(all_data)
        hotelmap_dict_str=json.dumps(dict(data=data,totals=totals), cls=DjangoJSONEncoder)
        return HttpResponse(hotelmap_dict_str)

class EditHotelMap(View):
    def post(self,request):

        id=request.POST.get('id')
        status=int(request.POST.get('status'))

        obj=HotelMapSuggest.objects.filter(id=id).update(status=-status)#不用save


        return JsonResponse({'status_code':obj})