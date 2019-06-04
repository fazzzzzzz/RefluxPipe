# Create your models here.
import datetime

from djongo import models


class User(models.Model):
    username = models.TextField(unique=True)
    alias = models.TextField(unique=True)
    password = models.TextField()
    totp = models.TextField()
    api_token = models.TextField()
    is_admin = models.BooleanField()


class DnsLog(models.Model):
    username = models.TextField()
    domain = models.TextField()
    host = models.TextField()
    type = models.TextField()
    logtime = models.DateTimeField(default=datetime.datetime.utcnow)


class HttpLog(models.Model):
    username = models.TextField()
    host = models.TextField()
    url = models.TextField()
    method = models.TextField()
    useragent = models.TextField()
    body = models.TextField()
    contenttype = models.TextField()
    referer = models.TextField()
    logtime = models.DateTimeField(default=datetime.datetime.utcnow)


class InviteCode(models.Model):
    code = models.TextField(unique=True)
    status = models.BooleanField()
