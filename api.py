import json
import requests
import urllib2

username = ''
password = ''
api_root = 'http://chipselecta.com/eenventory/api'

class Http404(IOError):
    pass

class HTTPError(Exception):
    def __init__(self, message, code):
        Exception.__init__(self, message)
        self.code = code
    
    def __repr__(self):
        return 'HTTPError(' + repr(self.message) + ', code=' + repr(self.code) + ')'

def get(url, data):
    r = requests.get(api_root + url,
                     auth=(username, password),
                     data=data)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 404:
        raise Http404
    else:
        raise HTTPError(r.text, code=r.status_code)

def post(url, data):
    r = requests.post(api_root + url,
                      auth=(username, password),
                      data=data)
    if r.status_code == 200 or r.status_code == 201:
        return r.json()
    elif r.status_code == 404:
        raise Http404
    else:
        raise HTTPError(r.text, code=r.status_code)

def find_distributor(name):
    return get('/distributor/find/',
               {'name': name})

def populate_distributor(name, web_site=''):
    try:
        return get('/distributor/find/',
                   {'name': name})
    except urllib2.HTTPError, e:
        if e.code == 404:
            return post('/distributor/',
                        data={'name': name,
                              'web_site': web_site})
        else:
            raise

def get_part(part_id):
    return get('/part/' + str(part_id) + '/',
               {})

def create_order(dist, order_number, url, date, price):
    return post('/order/',
                {'dist': dist['id'],
                 'order_number': order_number,
                 'url': url,
                 'date': date,
                 'price': price})

def create_order_property(order, name, value):
    return post('/order_property/',
                {'order': order['id'],
                 'name': name,
                 'value': value})

def create_part_history(order, part, quantity, ext_price):
    return post('/part_history/',
                {'part': part['id'],
                 'date': order['date'],
                 'reason': '+',
                 'quantity': quantity,
                 'ext_price': ext_price,
                 'order': order['id']})

def import_digikey_part(dist_part_num):
    return get('/digikey/import/',
                {'dist_part_number': dist_part_num})

def import_mouser_part(dist_part_num):
    return get('/mouser/import/',
                {'dist_part_number': dist_part_num})
