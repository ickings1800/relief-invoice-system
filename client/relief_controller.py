import requests
from enum import Enum
from datetime import datetime, date, time
from json import dumps


def get_customer_data():
    customers = requests.get('http://localhost:8000/pos/api/customers/')
    data = []
    for c in customers.json():
        row = list()
        row.append(c.get('id'))
        row.append(c.get('name'))
        row.append(c.get('address'))
        row.append(c.get('postal_code'))
        row.append(c.get('tel_no'))
        row.append(c.get('fax_no'))
        row.append(c.get('term'))
        row.append(c.get('gst'))
        data.append(row)
    return data


def get_customer_detail_data(customer_id):
    customer = requests.get('http://localhost:8000/pos/api/customers/{0}/'.format(customer_id))
    data = {}
    customer_json = customer.json()
    data['id'] = customer_json.get('id')
    data['address'] = customer_json.get('address')
    data['name'] = customer_json.get('name')
    data['postal_code'] = customer_json.get('postal_code')
    data['tel_no'] = customer_json.get('tel_no')
    data['fax_no'] = customer_json.get('fax_no')
    data['term'] = customer_json.get('term')
    data['gst'] = customer_json.get('gst')
    return data


def update_customer_data(customer_id, address, name, postal_code, tel_no, fax_no, term, gst):
    data = {
        'address': address,
        'name': name,
        'postal_code': postal_code,
        'tel_no': tel_no,
        'fax_no': fax_no,
        'term': term,
        'gst': gst
    }
    r = requests.put('http://localhost:8000/pos/api/customer/update/{0}/'.format(customer_id), data)
    return r



def get_product_data():
    data = []
    products = requests.get('http://localhost:8000/pos/api/products/')
    for p in products.json():
        row = list()
        row.append(p.get('id'))
        row.append(p.get('name'))
        row.append(p.get('specification'))
        data.append(row)
    return data


def get_product_detail_data(product_id):
    data = {}
    product = requests.get('http://localhost:8000/pos/api/products/{0}/'.format(product_id))
    print(product)
    product_json = product.json()
    data['id'] = product_json.get('id')
    data['name'] = product_json.get('name')
    data['specification'] = product_json.get('specification')
    return data


def get_trip_data():
    data = []
    trips = requests.get('http://localhost:8000/pos/api/trips/')
    for t in trips.json():
        row = list()
        row.append(t.get('id'))
        row.append(t.get('date'))
        row.append(t.get('notes'))
        data.append(row)
    return data


def get_trip_detail_data(trip_id):
    data = {}
    trip = requests.get('http://localhost:8000/pos/api/trips/{0}/'.format(trip_id))
    trip_json = trip.json()
    data['id'] = trip_json.get('id')
    data['date'] = trip_json.get('date')
    data['notes'] = trip_json.get('notes')
    data['packaging_methods'] = trip_json.get('packaging_methods')
    return data


def update_trip_data(trip_id, date, notes, packaging_methods):
    data = {
        'date': date,
        'notes': notes,
        'packaging_methods': packaging_methods
    }
    r = requests.put('http://localhost:8000/pos/api/trip/update/{0}/'.format(trip_id), data)
    return r


def post_customer_data(name, address, postal_code, tel_no, fax_no, term, gst):
    data = {
        'name': name,
        'address': address,
        'postal_code': postal_code,
        'tel_no': tel_no,
        'fax_no': fax_no,
        'term': term,
        'gst': gst
    }
    r = requests.post('http://localhost:8000/pos/api/customer/create', data)
    return r


def post_product_data(name, specification):
    data = {
        'name': name,
        'specification': specification
    }
    r = requests.post('http://localhost:8000/pos/api/product/create', data)
    return r


def update_product_data(id, name, specification):
    data = {
        'name': name,
        'specification': specification
    }
    r = requests.put('http://localhost:8000/pos/api/product/update/{0}/'.format(id), data)
    return r


def post_trip_data(date, notes):
    data = {
        'date': date,
        'notes': notes
    }
    r = requests.post('http://localhost:8000/pos/api/trip/create', data)
    return r


def get_customerproduct_data(customer_id):
    data = []
    customerproducts = requests.get('http://localhost:8000/pos/api/customers/{0}/products/'.format(customer_id))
    customerproducts_json = customerproducts.json()
    for cp in customerproducts_json:
        row = list()
        row.append(cp.get('id'))
        row.append(cp.get('product'))
        row.append(cp.get('quote_price'))
        data.append(row)
    return data


def post_customerproduct_data(quote_price, customer_id, product_id):
    data = dict()
    data['quote_price'] = quote_price
    data['customer'] = customer_id
    data['product'] = product_id
    r = requests.post('http://localhost:8000/pos/api/customers/{0}/products/create/'.format(customer_id), data)
    return r


def update_customerproduct_data(customerproduct_id, quote_price):
    data = dict()
    data['quote_price'] = quote_price
    r = requests.put('http://localhost:8000/pos/api/customerproduct/{0}/update/'.format(customerproduct_id), data)
    return r


def get_detail_customerproduct(customerproduct_id):
    data = {}
    customerproduct = requests.get('http://localhost:8000/pos/api/customerproduct/{0}/'.format(customerproduct_id))
    customerproduct_json = customerproduct.json()
    data['id'] = customerproduct_json.get('id')
    data['quote_price'] = customerproduct_json.get('quote_price')
    data['product'] = customerproduct_json.get('product')
    return data


def get_customer_routes(customer_id):
    data = []
    routes = requests.get('http://localhost:8000/pos/api/customers/{0}/routes/'.format(customer_id))
    routes_json = routes.json()
    for r in routes_json:
        row = list()
        row.append(r.get('index'))
        row.append(r.get('do_number'))
        row.append(r.get('note'))
        row.append(r.get('invoice_number'))
        row.append(r.get('trip_date'))
        data.append(row)
    return data


def get_customer_invoices(customer_id):
    data = []
    invoices = requests.get('http://localhost:8000/pos/api/customers/{0}/invoices/'.format(customer_id))
    invoices_json = invoices.json()
    for r in invoices_json:
        row = list()
        row.append(r.get('id'))
        row.append(r.get('invoice_year'))
        row.append(r.get('invoice_number'))
        row.append(r.get('start_date'))
        row.append(r.get('end_date'))
        row.append(r.get('minus'))
        row.append(r.get('gst'))
        row.append(r.get('original_total'))
        row.append(r.get('net_total'))
        row.append(r.get('net_gst'))
        row.append(r.get('total_incl_gst'))
        row.append(r.get('remark'))
        row.append(r.get('date_generated'))
        data.append(row)
    return data


def get_all_invoices():
    data = []
    invoices = requests.get('http://localhost:8000/pos/api/invoices/')
    invoices_json = invoices.json()
    for r in invoices_json:
        row = list()
        row.append(r.get('id'))
        row.append(r.get('invoice_year'))
        row.append(r.get('invoice_number'))
        row.append(r.get('start_date'))
        row.append(r.get('end_date'))
        row.append(r.get('minus'))
        row.append(r.get('gst'))
        row.append(r.get('original_total'))
        row.append(r.get('net_total'))
        row.append(r.get('net_gst'))
        row.append(r.get('total_incl_gst'))
        row.append(r.get('remark'))
        row.append(r.get('date_generated'))
        data.append(row)
    return data


def delete_customer_invoice(invoice_id):
    r = requests.delete('http://localhost:8000/pos/api/invoices/{0}/delete/'.format(invoice_id))
    return r


def get_trip_detail_list(trip_id):
    trip = requests.get('http://localhost:8000/pos/api/trips/{0}/detail/routes/'.format(trip_id))
    trip_json = trip.json()
    return trip_json


def delete_trip(trip_id):
    r = requests.delete('http://localhost:8000/pos/api/trip/{0}/delete/'.format(trip_id))
    return r


def post_route(trip_id, customer_id=None, note=None):
    data = dict()
    data['customer'] = customer_id
    data['note'] = note
    r = requests.post('http://localhost:8000/pos/api/trips/{0}/detail/routes/add/'.format(trip_id), data)
    return r


def get_detail_route(route_id):
    data = {}
    route = requests.get('http://localhost:8000/pos/api/routes/{0}/'.format(route_id))
    route_json = route.json()
    data['note'] = route_json.get('note')
    return data


def update_route(route_id, note):
    data = dict()
    data['note'] = note
    r = requests.put('http://localhost:8000/pos/api/routes/{0}/update/'.format(route_id), data)
    return r


def delete_route(route_id):
    r = requests.delete('http://localhost:8000/pos/api/routes/{0}/delete/'.format(route_id))
    return r


def get_detail_orderitem(orderitem_id):
    data = {}
    orderitem = requests.get('http://localhost:8000/pos/api/orderitem/{0}/'.format(orderitem_id))
    orderitem_json = orderitem.json()
    data['quantity'] = orderitem_json.get('quantity')
    data['note'] = orderitem_json.get('note')
    data['packing'] = orderitem_json.get('packing')
    return data


def update_orderitem(orderitem_id, driver_quantity=None, quantity=None, note=None, packing=None):
    data = dict()
    data['driver_quantity'] = driver_quantity
    data['quantity'] = quantity
    data['note'] = note
    data['packing'] = dumps(packing)
    r = requests.put('http://localhost:8000/pos/api/orderitem/{0}/update/'.format(orderitem_id), data)
    print(r.text)
    return r


def arrange_route_trip(trip_id, id_arrangement):
    data = dict()
    data['id_arrangement'] = id_arrangement
    r = requests.post('http://localhost:8000/pos/api/trips/{0}/routes/arrange/'.format(trip_id), data)
    return r