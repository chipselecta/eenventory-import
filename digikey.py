from decimal import *
from bs4 import BeautifulSoup
import re
import urlparse
import datetime
import time

import urllib2

from utils import wget
from api import (Http404, get, find_distributor, populate_distributor,
                 create_order, create_order_property, create_part_history,
                 import_digikey_part, get_part)

def is_table_gvList(tag):
    return tag.name == 'table' and tag.has_attr('id') and tag['id'].endswith('_gvList')

def parse_orders(url, file):
    soup = BeautifulSoup(open(file))
    
    t = soup.find(is_table_gvList)
    tbody = t.tbody
    if tbody:
        t = tbody
    
    orders = []
    first = True
    for r in t.children:
        if r.name != 'tr':
            continue
        if first:
            first = False
            continue
        print '**r', r
        order_url = urlparse.urljoin (url, r.a['href'])
        
        order = []
        for d in r.children:
            if d.name != 'td':
                continue
            order.append(d.get_text(strip=True))
        orders.append((order, order_url))
    
    return orders

def is_table_ordOrderDetails(tag):
    return tag.name == 'table' and tag.has_attr('id') and tag['id'].endswith('_ordOrderDetails')

def parse_order(url, soup):
    t = soup.find(is_table_ordOrderDetails)
    tbody = t.tbody
    if tbody:
        t = tbody
    
    items = []
    for r in t.children:
        if r.name != 'tr':
            continue

        item = []
        for d in r.children:
            if d.name != 'td':
                continue

            item.append(d.get_text(strip=True))
        items.append(item)

    return items

def is_span_lblWebID(tag):
    return tag.name == 'span' and tag.has_attr('id') and tag['id'].endswith('_lblWebID')

def is_span_lblSalesorderNumber(tag):
    return tag.name == 'span' and tag.has_attr('id') and tag['id'].endswith('_lblSalesorderNumber')

def is_span_lblSubmitted(tag):
    return tag.name == 'span' and tag.has_attr('id') and tag['id'].endswith('_lblSubmitted')

def import_order(url):
    digikey = find_distributor('Digi-Key')
    
    file = '/tmp/order.html'
    wget(url, file)
    
    soup = BeautifulSoup(open(file))
    
    web_id_tag = soup.find(is_span_lblWebID)
    web_id = web_id_tag.get_text(strip=True)
    
    salesorder_number_tag = soup.find(is_span_lblSalesorderNumber)
    salesorder_number = salesorder_number_tag.get_text(strip=True)
    
    submitted_tag = soup.find(is_span_lblSubmitted)
    submitted = submitted_tag.get_text(strip=True)
    
    order = parse_order(url, soup)
    items = [item for item in order if len(item) == 9]
    
    print web_id, salesorder_number, submitted, items
    
    # FIX replace by populate_order
    try:
        return get('/order/find/',
                   {'dist': digikey['id'],
                    'order_number': salesorder_number})
    except Http404:
        price = None
        for item in order:
            if len(item) == 3:
                if item[1] == 'Subtotal':
                    subtotal = item[2].replace ('$', '')
                elif item[1] == 'Total':
                    m = re.match(r'\$([0-9]+.[0-9]+)', item[2])
                    if m:
                        price = m.group(1)
        
        # %m/%d/%Y
        m = re.search(r'([0-9]+)/([0-9]+)/([0-9]+)', submitted)
        
        o = create_order(dist=digikey,
                         order_number=salesorder_number,
                         url=url,
                         date=m.group(3) + '-' + m.group(1) + '-' + m.group(2),
                         price=price if price else subtotal)

        if not price:
            create_order_property(order=o,
                                  name='Import Note',
                                  value='Total missing, used Subtotal for Order Price')
    
    create_order_property(order=o,
                          name='Salesorder Number',
                          value=salesorder_number)
                
    create_order_property(order=o, 
                          name='Web ID',
                          value=web_id)

    import_failures = []
    for item in items:
        (index, quantity, dist_part_num, desc, _, _, _, unit_price, ext_price) = item
        
        try:
            unit_price = Decimal(unit_price.replace('$', ''))
            ext_price = Decimal(ext_price.replace('$', ''))
            quantity = int(quantity.replace('NCNR', ''))
            
            print 'importing ' + dist_part_num
            dp = import_digikey_part(dist_part_num)
            
            p = get_part(dp['part'])
            
            create_part_history(order=o,
                                part=p,
                                quantity=quantity,
                                ext_price=ext_price)
        except Exception, e:
            print 'import failed:', repr(e)
            import_failures.append(dist_part_num)
    
    if import_failures:
        create_order_property(order=o,
                              name='Failed to Import',
                              value=', '.join(import_failures))

def import_orders():
    url = 'https://www.digikey.com/classic/registereduser/WebOrderHistory.aspx'
    file = '/tmp/orders.html'
    wget(url, file)
    
    orders = parse_orders(url, file)
    
    for order in orders:
        (cols, url) = order
        import_order(url)
