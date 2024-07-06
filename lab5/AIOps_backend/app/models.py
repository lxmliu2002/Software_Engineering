# 导入`connection`用于执行原生sql语句
from django.db import connection, models
from django.db.models import Count, Max

# Create your models here.


# 系统用户user表：【userId，userName，userPassword，userPower，createTime，updateTime】
class User(models.Model):
    # primary_key=True表示该属性为该表的主键，暗示null=False和unique=True。
    id = models.AutoField(primary_key=True)

    userId = models.CharField(max_length=20)
    userName = models.CharField(unique=True, max_length=15)
    userPassword = models.CharField(max_length=20)
    userPower = models.DecimalField(max_digits=3, decimal_places=0, default=10)
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)

    def save(self, **kwargs):
        if not self.id:
            idCount = User.objects.aggregate(Count("id")).get("id__count")
            cursor = connection.cursor()
            if idCount == 0:
                # 要想使用sql原生语句，必须用到execute()函数,然后在里面写入sql原生语句
                cursor.execute("TRUNCATE app_user")
            maxid = User.objects.aggregate(Max("id")).get("id__max")
            # 让主键从什么位置开始排序
            if maxid is not None:
                cursor.execute("ALTER TABLE app_user AUTO_INCREMENT = %s", [maxid + 1])
            self.userId = "{}{:06d}".format(
                "user", (maxid + 1) if maxid is not None else 1
            )
        super().save(*kwargs)
