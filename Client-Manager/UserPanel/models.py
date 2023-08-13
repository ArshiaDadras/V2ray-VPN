from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=32, unique=True)
    payment_code = models.CharField(max_length=16, unique=True)
    destination_card = models.CharField(max_length=16)
    mobile = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    plan = models.CharField(max_length=16)
    verified = models.BooleanField(default=False)

    def to_json(self):
        return {
            'name': self.name,
            'payment_code': self.payment_code,
            'destination_card': self.destination_card,
            'mobile': self.mobile,
            'email': self.email,
            'plan': self.plan,
        }

class Inbound(models.Model):
    user_id = models.IntegerField()
    up = models.IntegerField()
    down = models.IntegerField()
    total = models.IntegerField()
    remark = models.TextField()
    enable = models.BooleanField()
    expiry_time = models.IntegerField()
    autoreset = models.BooleanField()
    ip_alert = models.BooleanField()
    ip_limit = models.IntegerField()
    listen = models.TextField()
    port = models.IntegerField()
    protocol = models.TextField()
    settings = models.TextField()
    stream_settings = models.TextField()
    tag = models.TextField()
    sniffing = models.TextField()

    class Meta:
        db_table = 'inbounds'
        managed = False

    def to_json(self):
        return {
            'remark': self.remark,
            'up': self.up,
            'down': self.down,
            'total': self.total,
            'enable': self.enable,
            'expiry_time': self.expiry_time,
        }
    
class Client(models.Model):
    inbound_id = models.IntegerField()
    enable = models.BooleanField()
    email = models.TextField()
    up = models.IntegerField()
    down = models.IntegerField()
    total = models.IntegerField()
    expiry_time = models.IntegerField()

    class Meta:
        db_table = 'client_infos'
        managed = False

    def to_json(self):
        return {
            'name': self.email,
            'up': self.up,
            'down': self.down,
            'total': self.total,
            'enable': self.enable,
            'expiry_time': self.expiry_time,
        }