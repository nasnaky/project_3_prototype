from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=66)
    money = models.IntegerField(default=0)
    accessToken = models.CharField(max_length=1000,null=True,blank=True)
    max_day = models.DateField(null=True,blank=True)

    def __str__(self):
        return self.name

    def __int__(self):
        return self.id


class auction_object(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    img = models.TextField()
    purchase = models.IntegerField()
    max_money = models.IntegerField(default=0,null=True,blank=True)
    auction = models.IntegerField()
    term = models.DateField()
    Kinds = models.TextField(null=True,blank=True)
    purchase_check = models.BooleanField(default=False)
    create_user = models.ForeignKey("User", on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def __int__(self):
        return self.id


class auction_participation(models.Model):
    auction_user = models.ForeignKey("User", on_delete=models.CASCADE)
    auction_source = models.ForeignKey("auction_object", on_delete=models.PROTECT)
    auction_purchase = models.IntegerField()


class purchasing_execution(models.Model):
    purchase_user = models.ForeignKey("User", on_delete=models.CASCADE)
    purchase_source = models.ForeignKey("auction_object", on_delete=models.PROTECT)
