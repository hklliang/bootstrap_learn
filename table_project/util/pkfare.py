# -*- coding:utf-8 -*-  
__author__ = 'hklliang'
__date__ = '2017-09-19 17:08'
import requests
import json, os
import pickle
import time
from pymongo import MongoClient
from bson import ObjectId


class PkfareRate():
    def __init__(self, login_url, login_data, rate_url, uri):
        self.time = int(time.time() * 1000)

        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
        }

        self.login_data = login_data
        self.login_url = login_url
        self.rate_url = rate_url
        self.uri = uri
        self.rate = None
        if uri:
            self.mongo_db_rate()

    def mongo_db_rate(self):
        client = MongoClient(self.uri)
        self.rate = client.hotel.rate

    def get_rate_supplier(self, rate_id):

        supplier = self.rate.find_one({'_id': ObjectId(rate_id)})['supplier']
        return supplier

    def login_pkfare(self):

        login_headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
        }
        r = requests.post(url=self.login_url, headers=login_headers, data=json.dumps(self.login_data))
        print('logining')
        with open("pkfare_cookie", "wb") as f:
            pickle.dump(requests.utils.dict_from_cookiejar(r.cookies), f)
        return r.cookies

    # 酒店
    def get_pkfare_rate(self,row, hotel_id, checkInDate, checkOutDate, numberOfAdults, numberOfRooms,numberOfChildren):


        if not os.path.exists("pkfare_cookie"):
            self.login_pkfare()
        try:
            with open("pkfare_cookie", "rb") as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
        except Exception as e:
            print(e)
            cookies = self.login_pkfare()

        try:

            data = 'checkInDate={checkInDate}&checkOutDate={checkOutDate}&hotelId={hotel_id}&numberOfAdults={numberOfAdults}&numberOfChildren={numberOfChildren}&tt=1505466748062&numberOfRooms={numberOfRooms}'.format(
                checkInDate=checkInDate, checkOutDate=checkOutDate, numberOfAdults=numberOfAdults,
                numberOfRooms=numberOfRooms, hotel_id='{hotel_id}',numberOfChildren=numberOfChildren
            )
            res = requests.post(self.rate_url.format(time=self.time), cookies=cookies,
                                data=data.format(hotel_id=hotel_id), headers=self.headers)

            json_res = json.loads(res.text)

            if 'login' in json_res['message']:
                cookies = self.login_pkfare()
                res = requests.post(self.rate_url, cookies=cookies, data=data.format(hotel_id=hotel_id),
                                    headers=self.headers)
                print('login')
                json_res = json.loads(res.text)
            if json_res['data'] != None:
                pk_url = 'https://www.pkfare.com/modules/view/hotelSearch/hotelDetail.html?checkInDate%3D{checkInDate}%26checkOutDate%3D{checkOutDate}%26hotelId%3D{hotel_id}%26numberOfAdults%3D{numberOfAdults}%26numberOfRooms%3D{numberOfRooms}%26numberOfChildren%3D{numberOfChildren}'.format(
                    checkInDate=checkInDate, checkOutDate=checkOutDate, numberOfAdults=numberOfAdults,
                    numberOfRooms=numberOfRooms, hotel_id='{hotel_id}',numberOfChildren=numberOfChildren
                )
                return self.parse_json(row,hotel_id,json_res,pk_url)


        except TimeoutError  as e:
            print(hotel_id, e)

    def parse_json(self, row,hotel_id, data,pk_url):
        room_list = []
        roomInfos = data['data']['roomInfos']
        for room_types in roomInfos:
            for room in room_types['roomRateInfos']:
                rateId = room['rateId']
                if self.rate:
                    supplier = self.get_rate_supplier(rateId)
                else:
                    supplier = rateId

                roomType = room_types['roomType']
                base = room['base']
                breakfast = room['conditions'][0]['name']

                if len(room['conditions']) > 1:
                    refund = room['conditions'][1]['name']
                else:
                    refund = '无'
                num=row%2
                format_pk_url=pk_url.format(hotel_id=hotel_id)
                hotel_a = '<a href="{format_pk_url}" target="_blank" class="color-{num}">{hotel_id}</a>'.format(format_pk_url=format_pk_url,hotel_id=hotel_id,num=num)
                room_list.append([hotel_a, supplier, roomType, base, breakfast, refund])

        return room_list
