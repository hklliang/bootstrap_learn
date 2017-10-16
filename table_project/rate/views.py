from django.shortcuts import render, HttpResponse, redirect
from util.qunar import Mysql_db, QunarSpider
from util.pkfare import PkfareRate
from django.views.generic import View
import re, MySQLdb
import pandas as pd
import datetime
rateparms = dict(
    login_url='https://www.pkfare.com/platform-gateway/user/login',
    login_data={
        'password': "a25352089",
        'username': "kevin_mpt",
    },
    rate_url='https://www.pkfare.com/hotel/rates?time={time}',
    uri="mongodb://hoteluser:Hotelgfuser2016@112.124.12.40:27017/?authSource=admin&authMechanism=SCRAM-SHA-1"
)
# 112.124.12.40 生产环境
# 101.37.20.31 测试环境
pkfarerate = PkfareRate(**rateparms)

# Create your views here.
mysql_db = Mysql_db()
pattern = re.compile('\D+')


def qunar_room(request):
    if request.method == 'POST':
        output = [['来源', '订单号', '房型', '官网房型比较', '早餐', '退订政策', '酒店名', '地址', '与pk的跑分']]
        order_rows = mysql_db.do_fetch()

        qunarspider = QunarSpider()
        for row, order in enumerate(order_rows):
            # print(order['SOURCE_ORDER_NUM'])

            (url_area,
             qunar_hotel_name,
             gf_hotel_name,
             name_score,
             qunar_hotel_address,
             gf_hotel_address,
             address_score,
             pk_room_type,
             qunar_room_type,
             qunar_breadfast,
             qunar_refund,
             perDayPrice) = qunarspider(order['SOURCE_ORDER_NUM'])

            conditions = eval(order['CONDITIONS'])
            for condition in conditions:
                if 'MEAL' in condition.values():
                    gf_hotel_breadfast = condition['name']

            cancel_type = order['cancel_type']
            if cancel_type == 'NONE_REFUNDABLE':
                gf_hotel_refund = '取消扣款'
            elif cancel_type == None:
                gf_hotel_refund = ''
            else:
                gf_hotel_refund = '限时取消'
            gf_hotel_room = order['room_type']
            supplier = order.get('supplier','')
            supp_hotel_address = order.get('supp_hotel_address','')or ''
            supp_hotel_name = order.get('supp_hotel_name','') or ''
            supp_name_score = order.get('supp_name_score','') or ''
            supp_address_score = order.get('supp_address_score','')or ''



            qunar_order_url = 'http://hota.qunar.com/confirm/ohtml/detail?orderNum={orderNum}'.format(
                orderNum=order['SOURCE_ORDER_NUM'])
            pk_order_url = 'https://www.pkfare.com/modules/view/hotelSearch/operateDetail.html?orderNum={orderNum}'.format(
                orderNum=order['ORDER_NUM'])
            num = row % 2
            pk_order = '<a href={url} class="color-{num}" target="_blank">{order_num}</a>'.format(url=pk_order_url,
                                                                                                  order_num=order[
                                                                                                      'ORDER_NUM'],
                                                                                                  num=num)
            qunar_order = '<a href={url} class="color-{num}" target="_blank">{order_num}</a>'.format(
                url=qunar_order_url,
                order_num=order['SOURCE_ORDER_NUM'], num=num)
            qunar_room = '<a href={url} target="_blank">{qunar_room_type}</a>'.format(
                url=url_area,
                qunar_room_type=qunar_room_type)
            output.extend([['PKFARE', pk_order, gf_hotel_room, pk_room_type, gf_hotel_breadfast,
                            gf_hotel_refund, gf_hotel_name, gf_hotel_address, ''],
                           ['QUNAR', qunar_order, '%s(价格)' % perDayPrice, qunar_room, qunar_breadfast, qunar_refund,
                            qunar_hotel_name,qunar_hotel_address, '%s(Name)/%s(Ad)' % (name_score, address_score)],
                           [supplier, '', '', '', '', '',supp_hotel_name,supp_hotel_address, '%s(Name)/%s(Ad)' % (supp_name_score, supp_address_score)]])

        return HttpResponse(str(output))
    return redirect('/index')


def index(request):
    return render(request, 'index.html')


def hotelRate(request):

    return render(request, 'hotelRate.html')


def getHotelRate(request):

    # checkInDate=(datetime.datetime.now()+ datetime.timedelta(days = 2)).strftime('%Y-%m-%d')
    # checkOutDate = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')

    if request.method == 'POST':
        checkInDate=request.POST.get('Check_in')
        checkOutDate = request.POST.get('Check_out')
        Adult_nums=request.POST.get('Adult_nums')
        Room_nums=request.POST.get('Room_nums')
        hotel_list =pattern.split(request.POST.get('Hotel_id'))
        # print(checkInDate,checkOutDate,Adult_nums,Room_nums,Hotel_list)

        All_room_list = [['Hotel_id', 'Supplier', 'Room_type', 'Price', 'Breakfast', 'Refund']]
        # hotel_list = pattern.split(request.body.decode("utf-8"))
        for row, hotel_id in enumerate(hotel_list):
            room_list = pkfarerate.get_pkfare_rate(row, hotel_id, checkInDate, checkOutDate, Adult_nums, Room_nums, 0)
            if room_list:
                All_room_list.extend(room_list)

    return HttpResponse(str(All_room_list))


def initial():
    con = MySQLdb.connect(
        host='127.0.0.1',
        db='data',
        user='root',
        passwd='123456',
        charset='utf8',
        use_unicode=True)

    sql = """
            select gf_hotel_id,hotelseq,linkStatus,`status`,country_name,city,address1,gf_hotel_name from qunar_gf_hotel a join ht_hotel_address b
           on a.gf_hotel_id=b.hotel_id
order by `linkStatus`
           """
    hotels = pd.read_sql(sql, con=con)
    return hotels


# hotels = initial()


# class HotelSearch(View):
#     def get(self, request):
#         return render(request, 'hotelSearch.html')
#
#     def post(self, request):
#         # keys=re.sub('\s+','',request.body.decode("utf-8")).splitlines()
#         keys = request.body.decode("utf-8").splitlines()
#         pat_keys = '(%s)' % ')|('.join(keys)
#         title = ['hotel_id', 'hotelseq', 'linkStatus', 'status', 'country', 'city', 'address', 'hotel_name']
#         title.extend(list(range(len(keys))))
#         All_hotel_list = [title]
#         match_hotels = hotels['gf_hotel_name'].str.extract(pat_keys, flags=re.IGNORECASE, expand=True)
#         hotels_data = hotels.join(match_hotels).dropna(subset=list(range(len(keys))), how='all').fillna('')
#         hotels_list = hotels_data.values.tolist()
#         All_hotel_list.extend(hotels_list)
#
#         return HttpResponse(str(All_hotel_list[:300]))
