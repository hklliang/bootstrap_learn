# -*- coding:utf-8 -*-  
__author__ = 'hklliang'
__date__ = '2017-07-20 17:03'

import MySQLdb
import requests, json
import re, os
import pickle
from fuzzywuzzy import fuzz
import pprint
import MySQLdb.cursors

class Mysql_db(object):
    def __init__(self):
        self.conn = MySQLdb.connect(
            host='rr-bp1ig5ki4ov0e7lseo.mysql.rds.aliyuncs.com',
            db='hotel',
            user='hotel_r',
            passwd='HotMPT207',
            charset='utf8',
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def do_fetch(self):
        order_sql = """

   SELECT
    oi.hotel_id,
	o.ORDER_NUM,
	SOURCE_ORDER_NUM,
	ra.room_type,
	CONDITIONS,
	cancel_type,
	supp_hotel_name,
	oi.supplier,
name_score supp_name_score,
supp_hotel_address,
address_score  supp_address_score
FROM
	or_order_new o
JOIN or_order_item oi ON O.ORDER_NUM = OI.ORDER_NUM
AND OI.DISPLAY = 1
LEFT JOIN `order_hotel_snapshot` sn ON o.order_num = SN.order_num
LEFT JOIN order_rate_snapshot ra ON sn.SNAPSHOT_ID = ra.SNAPSHOT_ID
LEFT JOIN order_cancel_detail de ON o.order_num = de.order_num AND de.type = 'supplier'
left JOIN hotel_mapping hm on oi.hoteL_id=hm.gf_hotel_id and oi.supplier=hm.supplier


WHERE
	     (ORDER_STATUS + PAY_STATUS = 100 AND operator_status = 1000)
	     OR operator_status = 1500
	-- or o.order_num = 5000146935
	-- (SOURCE_ORDER_NUM='101284838518'
	-- or SOURCE_ORDER_NUM='101299846173')
	and order_by='Qunar Api'
            """
        self.cursor.execute(order_sql)
        result = self.cursor.fetchall()
        return result


class QunarSpider():
    def __init__(self, *args, **kwargs):

        self.cookies = ''

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'cookie': 'QN99=9727; QunarGlobal=192.168.31.102_-34b99509_15a0cb24da4_-677b|1486271814249; QN601=3b186652b845384bf1e5885594802c36; QN48=tc_3a1cc1d2dd1fe604_15a94e59c08_d33e; pgv_pvi=8106185728; _jzqx=1.1488556771.1489334945.2.jzqsr=hotel%2Equnar%2Ecom|jzqct=/city/singapore_city/q-%e6%a8%9f%e5%ae%9c%e5%9b%bd%e9%99%85%e6%9c%ba%e5%9c%ba.jzqsr=hotel%2Equnar%2Ecom|jzqct=/city/singapore_city/; __utma=183398822.1661238889.1488556770.1488556770.1489334942.2; __utmz=183398822.1488556770.1.1.utmcsr=hotel.qunar.com|utmccn=(referral)|utmcmd=referral|utmcct=/city/singapore_city/q-%E6%A8%9F%E5%AE%9C%E5%9B%BD%E9%99%85%E6%9C%BA%E5%9C%BA; _jzqa=1.236856397460736200.1488556771.1488556771.1489334945.2; QN621=fr%3Dqunarindex%261490067914133%3DDEFAULT; QN43=2; QN42=hulling; _q=U.tsopxek7035; _t=24999300; csrfToken=XOSVzn1cEMtbnZBGk2i6fOayyzSHjcBq; _s=s_TJCTK3FPH6UEICP4L62REN4EEM; _v=aqxL6BnURxGcrvYK9N869wIzVfHQfsCuzhi6IIKcKWdqeU1r4z-lDbXCkwcp8Z2BAX3anCG03scZUVD9Igh0nB44Qc-phoYqKYwzHAqGYgyWqgI-qvKa6uU9euOH4pZvlWu3gCDESjgEjmj5jegMasBhy4aZyZrOKQZ6o8duw4n5; QN269=A9D3F670244A11E796A9FA163EBE0F8B; QN1=O5cv5llTHBIgwxg1pfPfAg==; flowidList=.2-1.3-1.4-1.1-3.; QN205=organic; Hm_lvt_75154a8409c0f82ecd97d538ff0ab3f3=1498547820,1498612222,1498698668,1498785624; QN70=19b7163d015d061a4314; pgv_si=s9622859776; QN73=2842-2843; QN44=tsopxek7035; RT_CACLPRICE=1; _i=RBTjeLwDDC-7sruRsm_SQndFh-bx; _vi=Z8pleTfkN1vKqMvoFEZNoJoIUuINQp4C8PmoB3z3TIKgubJWis7lYp1UmYtm1tjtkcChu4Z-IKpR6uNh2cCs-p7fTX6YExnNvAQc4JGtAlGvevntH1CZ2QTr05zKjC7gXTxi91eUUnZl75A71HnXPEKbr0Y01jCA39Ii8uBFCefA; QN268=1499046776993_240ef54385a5318c|1499046804645_82ae561263a89301'

        }

    def __call__(self, qunar_order_num):
        # 通过订单获得房型id
        qunar_room_id, hotelid, check_in_date, check_out_date,perDayPrice = self.get_qunar_room(qunar_order_num)

        # 通过hotelid获得seq
        qunar_hotel_name, qunar_hotel_address = self.get_seq(hotelid)
        hotelseq,gf_hotel_name, gf_hotel_address = self.get_gf_info(hotelid)
        _pos = hotelseq.rindex('_')
        dt_id = hotelseq[_pos + 1:]
        city = hotelseq[:_pos]

        # 通过hotelid获得酒店名和酒店地址

        # 计算相似度

        name_score = fuzz.ratio(qunar_hotel_name, gf_hotel_name)
        address_score = fuzz.partial_ratio(qunar_hotel_address, gf_hotel_address)
        # 获得房型
        roomtype = self.get_room_type(qunar_room_id, hotelseq, city, dt_id, check_in_date,
                                      check_out_date)

        # 返回json数据

        url_area, pk_room, qunar_room, qunar_breadfast, qunar_refund = roomtype
        return (
            url_area,
            qunar_hotel_name,
            gf_hotel_name,
            name_score,
            qunar_hotel_address,
            gf_hotel_address,
            address_score,
            pk_room,
            qunar_room,
            qunar_breadfast,
            qunar_refund,
            perDayPrice
        )



    def get_seq(self, hotelid):
        seq_url = 'http://hota.qunar.com/confirm/oapi/hotel/hotelInfo?hotelId={hotelid}'.format(hotelid=hotelid)
        res = requests.get(seq_url, cookies=self.cookies)
        try:
            hotel_dict = json.loads(res.text)
        except Exception as e:
            hotel_dict = {}
            print(hotelid,e)

        data = hotel_dict.get('data')
        if data:
            qunar_hotel_name = data.get("sHotelName")
            qunar_hotel_address = data.get('hotelAddress').replace('\xa0', ' ')
        else:
            qunar_hotel_name=''
            qunar_hotel_address=''

        return qunar_hotel_name, qunar_hotel_address

    def login_qunar(self):
        login_data = {
            'username': 'ha7yy:admin',
            'password': 'GFtrip2016',
            'captcha': '',
            'remember': 'true',
            'ret': 'http%3A%2F%2Fhota.qunar.com%2Fstats%2Fohtml%2Fannouncement%2FqueryAnnouncements',
        }
        login_url = 'https://shanghu.qunar.com/passport/doLogin'
        r = requests.post(url=login_url, data=login_data)
        with open('qunar_cookie', 'wb') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(r.cookies), f)
        return r.cookies

    def get_cookies(self):
        if not os.path.exists('qunar_cookie'):
            return self.login_qunar()
        try:
            with open('qunar_cookie', 'rb') as f:
                return requests.utils.cookiejar_from_dict(pickle.load(f))
        except Exception as e:
            return self.login_qunar()

    def get_qunar_room(self, qunar_order_num):

        url_room = 'http://hota.qunar.com/confirm/oapi/allorder/queryOrderDetail?orderNum={order_num}'.format(
            order_num=qunar_order_num)

        res = requests.get(url_room, cookies=self.cookies)
        if res.status_code!=200:
            self.cookies = self.login_qunar()
            res = requests.get(url_room, cookies=self.cookies)
        try:
            room_dict = json.loads(res.text)
        except json.JSONDecodeError as e:
            print(res.text)
            print(e)
            return '','','','',''
        data = room_dict['data']
        qunar_room_id = data['roomId']

        hotelid = data['hotelId']
        check_in_date = data['fromDate']
        check_out_date = data['toDate']
        perDayPrice = data['perDayPrice'][0]['price']['amount']

        return qunar_room_id, hotelid, check_in_date, check_out_date,perDayPrice

    def get_gf_info(self, hotelid):

        url_info = 'http://hota.qunar.com/baseinfo/oapi/shotel/detail/{hotelid}'.format(hotelid=hotelid)
        res_info = requests.get(url_info, cookies=self.cookies)
        hotel_info = json.loads(res_info.text)
        hotel_data = hotel_info['data']
        propInfo=hotel_data['propInfo']
        name=propInfo['name']
        address = propInfo['address']
        hotelSeq=hotel_data['hotelSeq']
        # qunar_address = hotel_data['hotelAddress'].replace('\xa0', ' ')

        return hotelSeq,name, address

    def get_room_type(self, qunar_room_id, qunar_hotel_id, city, dt_id, check_in_date, check_out_date):

        url_area = 'http://hotel.qunar.com/city/{city}/dt-{dt_id}/?_=1#fromDate={check_in_date}' \
                   '&toDate={check_out_date}'.format(city=city, dt_id=dt_id, check_in_date=check_in_date,
                                                     check_out_date=check_out_date)
        requests.get(url_area, headers=self.headers)

        room_url = 'http://te.hotel.qunar.com/render/detailV2.jsp?HotelSEQ={buyer_hotel_id}&cityurl={city}&' \
                   'fromDate={check_in_date}&toDate={check_out_date}' \
            .format(buyer_hotel_id=qunar_hotel_id, city=city, check_in_date=check_in_date,
                    check_out_date=check_out_date)
        res = requests.get(room_url, headers=self.headers)
        # print(room_url,qunar_room_id)
        pk_room, qunar_room, qunar_breadfast, qunar_refund=self.parse_room_type(res, qunar_room_id)
        return url_area,pk_room, qunar_room, qunar_breadfast, qunar_refund

    def parse_room_type(self, res, qunar_room_id):

        regex = re.compile(r'\\(?![/u"])')
        if 'hta1023i85i' in res.text:
            str = res.text[1:-2]
            try:
                rooms = json.loads(str)['result']
            except:
                rooms = json.loads(regex.sub(r"\\\\", str))['result']
            room_id = '{qunar_room_id}_930099'.format(qunar_room_id=qunar_room_id)
            for k, v in rooms.items():
                if 'hta1023i85i' in k and v[22] == room_id:

                    pk_room = v[2]
                    qunar_room = v[3]

                    qunar_breadfast = v[25]

                    if v[-12] == '0':
                        qunar_refund = '取消扣款'
                    else:
                        qunar_refund = '限时取消'

                    return pk_room, qunar_room, qunar_breadfast, qunar_refund
        return '','','',''


def run():
    mysql_db = Mysql_db()
    order_rows = mysql_db.do_fetch()

    qunarspider = QunarSpider()


    for order in order_rows:
        # print(order['SOURCE_ORDER_NUM'])
        gf_room = {}
        (url_area,
         qunar_hotel_name,
         gf_hotel_name,
         name_score,
         qunar_hotel_address,
         gf_hotel_address,
         address_score,
         pk_room,
         qunar_room,
         qunar_breadfast,
         qunar_refund,
         perDayPrice) = qunarspider(order['SOURCE_ORDER_NUM'])
        gf_room['1_gf_ORDER'] = order['ORDER_NUM']
        gf_room['2_gf_name'] = gf_hotel_name
        gf_room['3_gf_address'] = gf_hotel_address
        gf_hotel_breadfast=''
        conditions = eval(order['CONDITIONS'])
        for condition in conditions:
            if 'MEAL' in condition.values():
                gf_hotel_breadfast = condition['name']

        cancel_type = order['cancel_type']
        if cancel_type == 'NONE_REFUNDABLE':
            gf_hotel_refund = '取消扣款'
        elif cancel_type == None:
            gf_hotel_refund= ''
        else:
            gf_hotel_refund = '限时取消'
        gf_hotel_room = order['room_type']

        qunar_room_dict = {}
        qunar_room_dict['1_qunar_order']=order['SOURCE_ORDER_NUM']
        qunar_room_dict['2_qunar_name']=qunar_hotel_name
        qunar_room_dict['3_qunar_address']=qunar_hotel_address
        qunar_room_dict['4_qunar_breakfast'] = qunar_breadfast
        qunar_room_dict['5_qunar_refund'] = qunar_refund
        qunar_room_dict['6_pk_room'] = pk_room
        qunar_room_dict['6_qunar_room'] = qunar_room
        qunar_room_dict['7_name_score'] = name_score
        qunar_room_dict['8_address_score'] = address_score
        qunar_room_dict['9_perDayPrice'] = perDayPrice

        qunar_order_url = 'http://hota.qunar.com/confirm/ohtml/detail?orderNum={orderNum}'.format(
            orderNum=order['SOURCE_ORDER_NUM'])
        pk_order_url = 'https://www.pkfare.com/modules/view/hotelSearch/operateDetail.html?orderNum={orderNum}'.format(
            orderNum=order['ORDER_NUM'])

        print(url_area, qunar_order_url, pk_order_url, sep='\n')
        [[order['ORDER_NUM'], gf_hotel_name, gf_hotel_address, gf_hotel_breadfast,
         gf_hotel_refund,gf_hotel_room,pk_room,pk_order_url,name_score,address_score,],[order['SOURCE_ORDER_NUM'],qunar_hotel_name, qunar_hotel_address,
                                         qunar_breadfast,qunar_refund, qunar_room, qunar_order_url,url_area,                ]]




if __name__ == '__main__':
    run()
