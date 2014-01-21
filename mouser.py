from decimal import *
from bs4 import BeautifulSoup
import re
import urlparse
from subprocess import call
import datetime
import urllib2

import requests

from utils import wget
from api import (Http404, get, find_distributor, populate_distributor,
                 create_order, create_order_property, create_part_history,
                 import_mouser_part, get_part)

def is_cart_row(tag):
    return tag.name == 'tr' and tag.has_attr('class') and re.match('^(cartRow|alt-grey)', tag['class'][0])

def is_span_SalesOrderNumber(tag):
    return tag.name == 'span' and tag.has_attr('id') and re.search('lblSalesOrderNumber$', tag['id'])

def is_span_WebOrderNumber(tag):
    return tag.name == 'span' and tag.has_attr('id') and re.search('lblWebOrderNumber$', tag['id'])

def is_span_OrderDate(tag):
    return tag.name == 'span' and tag.has_attr('id') and re.search('lblOrderDateHeader$', tag['id'])

def is_tr_OrderTotal(tag):
    return tag.name == 'tr' and tag.has_attr('id') and re.search('trOrderTotal$', tag['id'])

def parse_order(url, file):
    soup = BeautifulSoup(open(file))
    
    t = soup.find(is_span_SalesOrderNumber)
    sales_order_num = re.sub('\n', '', t.get_text ())
    
    t = soup.find(is_span_WebOrderNumber)
    web_order_num = re.sub('\n', '', t.get_text ())
    
    t = soup.find(is_span_OrderDate)
    order_date = re.sub('\n', '', t.get_text ())
    
    t = soup.find(is_tr_OrderTotal)
    i = 0
    for d in t.children:
        if d.name != 'td':
            continue
        
        i = i + 1
        if i == 2:
            break
    
    # \xa0 is &nbsp;
    price = re.sub('[\n\xa0$]', '', d.get_text ())
    
    items = []
    for r in soup.find_all(is_cart_row):
        i = 0
        item = []
        for d in r.children:
            
            if d.name != 'td' or (d.has_attr('class') and d['class'] == ['td-select']):
                continue
            
            if i == 0:
                a = d.a
                item.append((urlparse.urljoin (url, a['href']),
                             re.sub('\n', '', a.get_text ())))
            else:
                item.append(re.sub('\n', '', d.get_text ()))
            i = i + 1
        items.append(item)
        
    return (sales_order_num, web_order_num, order_date, items, price)

def import_order(url):
    mouser = populate_distributor('Mouser',
                                  'http://mouser.com/')
    
    file = '/tmp/order.html'
    wget(url, file)
    
    (sales_order_num, web_order_num, order_date, items, price) = parse_order(url, file)
    
    try:
        return get('/order/find/',
                   {'dist': mouser['id'],
                    'order_number': sales_order_num})
    except Http404:
        # %m/%d/%Y
        m = re.search(r'([0-9]+)/([0-9]+)/([0-9]+)', order_date)
        
        o = create_order(dist=mouser,
                         order_number=sales_order_num,
                         url=url,
                         date=m.group(3) + '-' + m.group(1) + '-' + m.group(2),
                         price=price)
    
    create_order_property(order=o,
                          name='Sales Order Number',
                          value=sales_order_num)
    create_order_property(order=o,
                          name='Web Order Number',
                          value=web_order_num)
    
    import_failures = []
    for item in items:
        (part_url, dist_part_num) = item[0]
        
        quantity = item[2]
        price = item[3].replace('$', '')
        ext_price = item[4].replace('$', '')

        try:
            print 'importing ' + dist_part_num
            dp = import_mouser_part(dist_part_num)
            
            p = get_part(dp['part'])
            
            create_part_history(order=o,
                                part=p,
                                quantity=quantity,
                                ext_price=ext_price)
        except Exception, e:
            print 'import failed:', repr(e)
            import_failures.append (dist_part_num)
    
    if import_failures:
        create_order_property(order=o,
                              name='Failed to Import',
                              value=', '.join(import_failures))

def is_orders_data_table(tag):
    return tag.name == 'table' and tag.has_attr('id') and re.search("mkr:dataTbl.hdn$", tag['id'])

def parse_orders(url, file):
    soup = BeautifulSoup(open(file))
    
    orders = []
    
    t = soup.find(is_orders_data_table)
    for r in t.find_all('tr'):
        o = []
        o_url = urlparse.urljoin (url, r.a['href'])
        for d in r.find_all('td'):
            o.append(re.sub('\n', '', d.get_text ()))
        orders.append ((o, o_url))
    
    return orders

def import_orders():
    url = 'https://mouser.com/OrderHistory/OrdersView.aspx'
    file = '/tmp/orders.html'
    wget(url, file)
    
    orders = parse_orders(url, file)
    
    for order in orders:
        (cols, url) = order
        import_order(url)
