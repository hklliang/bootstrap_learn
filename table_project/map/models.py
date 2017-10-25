from django.db import models

# Create your models here.
class HotelMapSuggest(models.Model):
    id = models.AutoField(primary_key=True)
    supplier=models.CharField(max_length=255,default='')
    gf_id = models.IntegerField(default=0,db_index=True)
    supp_id = models.CharField(max_length=20,db_index=True)
    gf_name = models.CharField(max_length=255,default='')
    supp_name = models.CharField(max_length=255,default='')
    name_score = models.IntegerField(default=0)
    gf_address = models.CharField(max_length=255,default='')
    supp_address = models.CharField(max_length=255,default='')
    address_score = models.IntegerField(default=0)
    gf_city = models.CharField(max_length=255,default='')
    supp_city = models.CharField(max_length=255,default='')
    country=models.CharField(max_length=255,default='')
    status=models.IntegerField(default=-1)
    createDate=models.DateTimeField(auto_now_add=True)
    lastDate=models.DateTimeField(auto_now=True)

    class Meta:
        # 数据库中生成的表名称 默认 app名称 + 下划线 + 类名
        db_table = "HotelMapSuggest"