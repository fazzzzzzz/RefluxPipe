import socketserver
import struct

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings


class SinDNSQuery:
    def __init__(self, data):
        i = 1
        self.name = ''
        while True:
            d = ord(chr(data[i]))
            if d == 0:
                break
            if d < 32:
                self.name = self.name + '.'
            else:
                self.name = self.name + chr(d)
            i = i + 1
        self.querybytes = data[0:i + 1]
        (self.type, self.classify) = struct.unpack('>HH', data[i + 1:i + 5])
        self.len = i + 5

    def getbytes(self):
        return self.querybytes + struct.pack('>HH', self.type, self.classify)


class SinDNSAnswer:
    def __init__(self, ip):
        self.name = 49164
        self.type = 1
        self.classify = 1
        self.timetolive = 190
        self.datalength = 4
        self.ip = ip

    def getbytes(self):
        res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
        s = self.ip.split('.')
        res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        return res


class SinDNSFrame:
    def __init__(self, data):
        (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH',
                                                                                                     data[0:12])
        self.query = SinDNSQuery(data[12:])

    def getname(self):
        return self.query.name

    def setip(self, ip):
        self.answer = SinDNSAnswer(ip)
        self.answers = 1
        self.flags = 33152

    def getbytes(self):
        res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
        res = res + self.query.getbytes()
        if self.answers != 0:
            res = res + self.answer.getbytes()
        return res


def get_dns_type(type):
    type_list = {
        1: 'A',
        2: 'NS',
        3: 'MD',
        4: 'MF',
        5: 'CNAME',
        6: 'SOA',
        7: 'MB',
        8: 'MG',
        9: 'MR',
        10: 'NULL',
        11: 'WKS',
        12: 'PTR',
        13: 'HINFO',
        14: 'MINFO',
        15: 'MX',
        16: 'TXT',
        28: 'AAAA',
        100: 'UINFO',
        101: 'UID',
        102: 'GID',
        255: 'ANY',
    }
    return type_list[type]


class SinDNSUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        dns = SinDNSFrame(data)
        socket = self.request[1]
        try:
            name = dns.getname()
            dns_type = get_dns_type(dns.query.type)
        except:
            print("\033[31mDNS type=" + dns.query.type + " error [" + str(self.client_address[0]) + ":" + str(
                self.client_address[1]) + "]\033[0m")
            return 0
        if dns_type != 'A':
            print("\033[31mDNS " + dns_type + " " + name + " error [" + str(self.client_address[0]) + ":" + str(
                self.client_address[1]) + "]\033[0m")
            return 0
        print("\033[31mDNS " + dns_type + " " + name + " success [" + str(self.client_address[0]) + ":" + str(
            self.client_address[1]) + "]\033[0m")
        if len(name.split(".")) <= len(settings.SERVER_DOMAIN.split(".")) or name[-1 - len(
                settings.SERVER_DOMAIN):] != "." + settings.SERVER_DOMAIN:
            dns.setip("0.0.0.0")
            socket.sendto(dns.getbytes(), self.client_address)
            return 0
        useralias = name.split(".")[-1 - len(settings.SERVER_DOMAIN.split('.'))]
        if useralias == 'registe':
            dns.setip(settings.SERVER_IP)
            socket.sendto(dns.getbytes(), self.client_address)
            return 0
        from Web.models import User, DnsLog
        if User.objects.filter(alias=useralias).count() != 1:
            dns.setip("0.0.0.0")
            socket.sendto(dns.getbytes(), self.client_address)
            return 0
        else:
            DnsLog(username=User.objects.filter(alias=useralias).first().username, domain=name,
                   host=self.client_address[0],
                   type="A").save()
            async_to_sync(get_channel_layer().group_send)(
                'group_%s' % User.objects.filter(alias=useralias).first().username,
                {
                    'type': 'client_message',
                    'message': 'dnslog_update'
                }
            )
            dns.setip(settings.SERVER_IP)
            socket.sendto(dns.getbytes(), self.client_address)
            return 0


def dnsinit():
    try:
        print('Starting the DNS service...')
        server = socketserver.UDPServer(("0.0.0.0", 53), SinDNSUDPHandler)
        server.serve_forever()
    except:
        print('Failed to start the DNS service.')
