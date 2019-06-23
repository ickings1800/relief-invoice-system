from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from enum import Enum
from datetime import datetime, date, time
from relief_controller import get_customer_data, get_product_data, get_trip_data, post_customer_data, \
    post_product_data, post_trip_data, get_product_detail_data, get_trip_detail_data, update_product_data, \
    update_trip_data, get_customer_detail_data, update_customer_data, get_customerproduct_data, \
    get_detail_customerproduct, post_customerproduct_data, update_customerproduct_data, get_customer_routes, \
    get_customer_invoices, delete_customer_invoice, get_all_invoices, get_trip_detail_list, post_route, delete_route, \
    update_route, update_orderitem, get_detail_orderitem, get_detail_route, get_packing_sum, get_customer_routes_by_date,\
    convert_customer_route_json_to_dict, get_new_invoice_number, create_invoice, get_invoice_detail
import PySimpleGUI as sg
import requests


class RELIEF_BUTTON_EVENT(Enum):
    CANCEL = 'CANCEL'
    ADD_CUSTOMER = 'ADD_CUSTOMER'
    SUBMIT_CUSTOMER = 'SUBMIT_CUSTOMER'
    SAVE_CUSTOMER = 'SAVE_CUSTOMER'
    EDIT_CUSTOMER = 'EDIT_CUSTOMER'
    CUSTOMER_DETAIL_REFRESH = 'CUSTOMER_DETAIL_REFRESH'
    ADD_PRODUCT = 'ADD_PRODUCT'
    SUBMIT_PRODUCT = 'SUBMIT_PRODUCT'
    SAVE_PRODUCT = 'SAVE_PRODUCT'
    ADD_TRIP = 'ADD_TRIP'
    SUBMIT_TRIP = 'SUBMIT_TRIP'
    SAVE_TRIP = 'SAVE_TRIP'
    CALENDAR_TRIP = 'CALENDAR_TRIP'
    REFRESH_CUSTOMER = 'REFRESH_CUSTOMER'
    REFRESH_PRODUCT = 'REFRESH_PRODUCT'
    REFRESH_TRIP = 'REFRESH_TRIP'
    EDIT_TRIP = 'EDIT_TRIP'
    ADD_CUSTOMERPRODUCT = 'ADD_CUSTOMERPRODUCT'
    REFRESH_CUSTOMERPRODUCT = 'REFRESH_CUSTOMERPRODUCT'
    ADD_INVOICE = 'ADD_INVOICE'
    DELETE_INVOICE = 'DELETE_INVOICE'
    REFRESH_INVOICE = 'REFRESH_INVOICE'
    CREATE_INVOICE = 'CREATE_INVOICE'
    VIEW_CUSTOMER = 'VIEW_CUSTOMER'
    SUBMIT_CUSTOMERPRODUCT = 'SUBMIT_CUSTOMERPRODUCT'
    SAVE_CUSTOMERPRODUCT = 'SAVE_CUSTOMERPRODUCT'
    ADD_ROUTE = 'ADD_ROUTE'
    SUBMIT_ROUTE = 'SUBMIT_ROUTE'
    # deleting route will be dynamically generated, appending route id to the back of string.
    DELETE_ROUTE = 'DELETE_ROUTE_'
    ARRANGE_ROUTE = 'ARRANGE_ROUTE'
    REFRESH_TRIP_ROUTE = 'REFRESH_TRIP_ROUTE'
    SAVE_TRIP_ROUTE = 'SAVE_TRIP_ROUTE'
    SAVE_ORDERITEM = 'SAVE_ORDERITEM'
    EDIT_ROUTE = 'EDIT_ROUTE'
    SAVE_PDF = 'SAVE_PDF'
    INVOICE_START_DATE = 'INVOICE_START_DATE'
    INVOICE_END_DATE = 'INVOICE_END_DATE'
    SUBMIT_INVOICE = 'SUBMIT_INVOICE'
    SUBMIT_EDIT_DO = 'SUBMIT_EDIT_DO'
    SUBMIT_EDIT_ORDERITEM = 'SUBMIT_EDIT_ORDERITEM'
    ADD_INVOICE_ORDER = 'ADD_INVOICE_ORDER'
    SUBMIT_INVOICE_ORDER  = 'SUBMIT_INVOICE_ORDER'
    SUBMIT_INVOICE_TRIP_DATE = 'SUBMIT_INVOICE_TRIP_DATE'
    SUBMIT_INVOICE_REDUCTION = 'SUBMIT_INVOICE_REDUCTION'
    SUBMIT_INVOICE_NUMBER = 'SUBMIT_INVOICE_NUMBER'
    SAVE_INVOICE = 'SAVE_INVOICE'


class RELIEF_INPUT_FIELDS(Enum):
    INPUT_CUSTOMER_NAME = 'INPUT_CUSTOMER_NAME'
    INPUT_CUSTOMER_ADDRESS = 'INPUT_CUSTOMER_ADDRESS'
    INPUT_CUSTOMER_POSTAL = 'INPUT_CUSTOMER_POSTAL'
    INPUT_CUSTOMER_TEL = 'INPUT_CUSTOMER_TEL'
    INPUT_CUSTOMER_FAX = 'INPUT_CUSTOMER_FAX'
    INPUT_CUSTOMER_TERM = 'INPUT_CUSTOMER_TERM'
    INPUT_CUSTOMER_GST = 'INPUT_CUSTOMER_GST'
    INPUT_PRODUCT_NAME = 'INPUT_PRODUCT_NAME'
    INPUT_PRODUCT_SPECIFICATIONS = 'INPUT_PRODUCT_SPECIFICATIONS'
    INPUT_TRIP_DATE = 'INPUT_TRIP_DATE'
    INPUT_TRIP_HOURS = 'INPUT_TRIP_HOUR'
    INPUT_TRIP_MINUTE = 'INPUT_TRIP_MINUTE'
    INPUT_TRIP_NOTES = 'INPUT_TRIP_NOTES'
    INPUT_TRIP_PACKAGING_METHODS = 'INPUT_TRIP_PACKAGING_METHODS'
    INPUT_CUSTOMERPRODUCT_PRODUCT = 'INPUT_CUSTOMERPRODUCT_PRODUCT'
    INPUT_CUSTOMERPRODUCT_QUOTE = 'INPUT_CUSTOMERPRODUCT_QUOTE'
    INPUT_ROUTE_CUSTOMER = 'INPUT_ROUTE_CUSTOMER'
    INPUT_ROUTE_NOTE = 'INPUT_ROUTE_NOTE'
    INPUT_ORDERITEM_QTY = 'INPUT_ORDERITEM_QTY_'
    INPUT_EDIT_ROUTE = 'INPUT_EDIT_ROUTE'
    INPUT_INVOICE_START_DATE = 'INPUT_INVOICE_START_DATE'
    INPUT_INVOICE_END_DATE = 'INPUT_INVOICE_END_DATE'
    INPUT_INVOICE_EDIT_DO = 'INPUT_INVOICE_EDIT_DO'
    INPUT_INVOICE_ORDERITEM = 'INPUT_INVOICE_ORDERITEM'
    INPUT_INVOICE_REDUCTION = 'INPUT_INVOICE_REDUCTION'
    INPUT_INVOICE_NUMBER = 'INPUT_INVOICE_NUMBER'
    INPUT_INVOICE_YEAR = 'INPUT_INVOICE_YEAR'


class RELIEF_VIEW_ELEMENTS(Enum):
    CUSTOMER_VIEW_TABLE = 'CUSTOMER_VIEW_TABLE'
    PRODUCT_VIEW_TABLE = 'PRODUCT_VIEW_TABLE'
    TRIP_VIEW_TABLE = 'TRIP_VIEW_TABLE'
    CUSTOMERPRODUCT_VIEW_TABLE = 'CUSTOMERPRODUCT_VIEW_TABLE'
    ORDER_VIEW_TABLE = 'ORDER_VIEW_TABLE'
    INVOICE_VIEW_TABLE = 'INVOICE_VIEW_TABLE'
    CUSTOMER_INVOICE_VIEW_TABLE = 'CUSTOMER_INVOICE_VIEW_TABLE'
    CUSTOMER_NAME_TEXT = 'CUSTOMER_NAME_TEXT'
    CUSTOMER_ADDRESS_TEXT = 'CUSTOMER_ADDRESS_TEXT'
    CUSTOMER_POSTAL_TEXT = 'CUSTOMER_POSTAL_TEXT'
    CUSTOMER_TEL_TEXT = 'CUSTOMER_TEL_TEXT'
    CUSTOMER_FAX_TEXT = 'CUSTOMER_FAX_TEXT'
    CUSTOMER_TERM_TEXT = 'CUSTOMER_TERM_TEXT'
    CUSTOMER_GST_TEXT = 'CUSTOMER_GST_TEXT'
    ORDERITEM_QTY_TEXT = 'ORDERITEM_QTY_TEXT'
    INVOICE_ROUTE_ID = 'INVOICE_ROUTE_ID_'
    INVOICE_ORDERITEM_ID = 'INVOICE_ORDERITEM_ID_'
    INVOICE_REDUCTION = 'INVOICE_REDUCTION'
    INVOICE_NUMBER = 'INVOICE_NUMBER'


def main():
    customer_headings = ['ID', 'Name', 'Address', 'Postal', 'Tel', 'Fax', 'Term', 'GST']
    blank_customer_data = [['' for i in range(len(customer_headings))]]
    customer_data = get_customer_data()
    customer_layout = [[sg.Button('Add', key=RELIEF_BUTTON_EVENT.ADD_CUSTOMER),
                        sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_CUSTOMER)],
                       [sg.Table(values=customer_data if len(customer_data) > 0 else blank_customer_data,
                                 headings=customer_headings,
                                 justification='left',
                                 auto_size_columns=True,
                                 enable_events=True,
                                 vertical_scroll_only=False,
                                 key=RELIEF_VIEW_ELEMENTS.CUSTOMER_VIEW_TABLE)]]

    product_headings = ['ID', 'Name', 'Specification']
    blank_product_data = [['' for i in range(len(product_headings))]]
    product_data = get_product_data()
    product_layout = [[sg.Button('Add', key=RELIEF_BUTTON_EVENT.ADD_PRODUCT),
                       sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_PRODUCT)],
                      [sg.Table(values=product_data if len(product_data) > 0 else blank_product_data,
                                headings=product_headings,
                                justification='left',
                                auto_size_columns=True,
                                enable_events=True,
                                vertical_scroll_only=False,
                                key=RELIEF_VIEW_ELEMENTS.PRODUCT_VIEW_TABLE)]]

    trip_headings = ['ID', 'Date', 'Notes']
    trip_data = get_trip_data()
    blank_trip_data = [['' for i in range(len(trip_headings))]]
    trip_layout = [[sg.Button('Add', key=RELIEF_BUTTON_EVENT.ADD_TRIP),
                    sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_TRIP)],
                   [sg.Table(values=trip_data if len(trip_data) > 0 else blank_trip_data,
                             headings=trip_headings,
                             justification='left',
                             auto_size_columns=True,
                             enable_events=True,
                             vertical_scroll_only=False,
                             key=RELIEF_VIEW_ELEMENTS.TRIP_VIEW_TABLE)]]

    invoice_select = None
    invoice_heading = ['ID',
                       'Year',
                       'Number',
                       'Start Date',
                       'End Date',
                       'Minus',
                       'GST',
                       'Original Total',
                       'Net Total',
                       'Net GST',
                       'Total with GST',
                       'Remark',
                       'Date Generated']

    invoices = get_all_invoices()
    blank_invoice_data = [['' for i in range(len(invoice_heading))]]
    invoice_layout = [[sg.Button('Delete', key=RELIEF_BUTTON_EVENT.DELETE_INVOICE),
                       sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_INVOICE)],
                      [sg.Table(values=invoices if len(invoices) > 0 else blank_invoice_data,
                                headings=invoice_heading,
                                justification='center',
                                enable_events=True,
                                vertical_scroll_only=False,
                                key=RELIEF_VIEW_ELEMENTS.INVOICE_VIEW_TABLE)]]

    layout = [[sg.TabGroup([[sg.Tab('Customer', customer_layout),
                             sg.Tab('Product', product_layout),
                             sg.Tab('Trip', trip_layout),
                             sg.Tab('Invoice', invoice_layout)]])],
              [sg.T('Status: ')]]

    window = sg.Window('Relief Temp GUI', default_element_size=(12, 1), resizable=True).Layout(layout)

    while True:  # Event Loop
        event, values = window.Read()
        # print(event, values)
        if event is None or event == 'Exit':
            break
        if event == RELIEF_BUTTON_EVENT.ADD_CUSTOMER:
            print(RELIEF_BUTTON_EVENT.ADD_CUSTOMER)
            show_add_customer_window()
        if event == RELIEF_BUTTON_EVENT.ADD_PRODUCT:
            print(RELIEF_BUTTON_EVENT.ADD_PRODUCT)
            show_add_product_window()
        if event == RELIEF_BUTTON_EVENT.ADD_TRIP:
            print(RELIEF_BUTTON_EVENT.ADD_TRIP)
            show_add_trip_window()
        if event == RELIEF_BUTTON_EVENT.REFRESH_CUSTOMER:
            print(RELIEF_BUTTON_EVENT.REFRESH_CUSTOMER)
            customer_data = get_customer_data()
            window.FindElement(RELIEF_VIEW_ELEMENTS.CUSTOMER_VIEW_TABLE) \
                .Update(values=customer_data if len(customer_data) > 0 else blank_customer_data)
        if event == RELIEF_BUTTON_EVENT.REFRESH_PRODUCT:
            print(RELIEF_BUTTON_EVENT.REFRESH_PRODUCT)
            product_data = get_product_data()
            window.FindElement(RELIEF_VIEW_ELEMENTS.PRODUCT_VIEW_TABLE) \
                .Update(values=product_data if len(product_data) > 0 else blank_product_data)
        if event == RELIEF_BUTTON_EVENT.REFRESH_TRIP:
            print(RELIEF_BUTTON_EVENT.REFRESH_TRIP)
            trip_data = get_trip_data()
            window.FindElement(RELIEF_VIEW_ELEMENTS.TRIP_VIEW_TABLE) \
                .Update(values=trip_data if len(trip_data) > 0 else blank_trip_data)
        if event == RELIEF_BUTTON_EVENT.VIEW_CUSTOMER:
            print(RELIEF_BUTTON_EVENT.VIEW_CUSTOMER)
        if event == RELIEF_VIEW_ELEMENTS.CUSTOMER_VIEW_TABLE:
            print(RELIEF_VIEW_ELEMENTS.CUSTOMER_VIEW_TABLE)
            customer_id = customer_data[values.get(RELIEF_VIEW_ELEMENTS.CUSTOMER_VIEW_TABLE)[0]][0]
            if type(customer_id) is int:
                show_customer_detail_window(customer_id)
        if event == RELIEF_VIEW_ELEMENTS.PRODUCT_VIEW_TABLE:
            print(RELIEF_VIEW_ELEMENTS.PRODUCT_VIEW_TABLE)
            # Take the first element of selection for now
            product_id = product_data[values.get(RELIEF_VIEW_ELEMENTS.PRODUCT_VIEW_TABLE)[0]][0]
            if type(product_id) is int:
                show_edit_product_window(product_id)
        if event == RELIEF_VIEW_ELEMENTS.TRIP_VIEW_TABLE:
            print(RELIEF_VIEW_ELEMENTS.TRIP_VIEW_TABLE)
            trip_id = trip_data[values.get(RELIEF_VIEW_ELEMENTS.TRIP_VIEW_TABLE)[0]][0]
            if type(trip_id) is int:
                show_trip_detail_window(trip_id)
        if event == RELIEF_VIEW_ELEMENTS.INVOICE_VIEW_TABLE:
            index = values.get(RELIEF_VIEW_ELEMENTS.INVOICE_VIEW_TABLE)[0]
            if type(index) is int:
                invoice_select = invoices[index]
                invoice_id = invoice_select[0]
                show_save_invoice_window(invoice_id)

        if event == RELIEF_BUTTON_EVENT.DELETE_INVOICE:
            invoice_id = invoice_select[0]
            if type(invoice_id) is int:
                show_delete_invoices_window(invoice_id)
        if event == RELIEF_BUTTON_EVENT.REFRESH_INVOICE:
            invoices = get_all_invoices()
            window.FindElement(RELIEF_VIEW_ELEMENTS.INVOICE_VIEW_TABLE) \
                .Update(values=invoices if len(invoices) > 0 else blank_invoice_data)
        # print(event)


    window.Close()


def show_add_customer_window():
    add_customer_layout = [
        [sg.Text('Add a customer')],
        [sg.Text('Name', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_NAME)],
        [sg.Text('Address', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_ADDRESS)],
        [sg.Text('Postal', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_POSTAL)],
        [sg.Text('Tel', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TEL)],
        [sg.Text('Fax', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_FAX)],
        [sg.Text('Term', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TERM)],
        [sg.Text('GST', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_GST)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMER), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]

    add_customer_window = sg.Window('Add Customer').Layout(add_customer_layout)
    while True:
        add_customer_event, add_customer_val = add_customer_window.Read()
        if add_customer_event is None or \
                add_customer_event == 'Exit' or \
                add_customer_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            add_customer_window.Close()

        if add_customer_event == RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMER:
            print(RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMER)
            name = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_NAME)
            address = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_ADDRESS)
            postal = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_POSTAL)
            tel = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TEL)
            fax = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_FAX)
            term = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TERM)
            gst = add_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_GST)

            response = post_customer_data(name, address, postal, tel, fax, term, gst)
            if response.status_code == requests.codes.created:
                add_customer_window.Close()
                break
            else:
                add_customer_window.Fill(add_customer_val)
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)


def show_edit_customer_window(customer_id):
    customer = get_customer_detail_data(customer_id)
    # Populate text fields with retrieved data
    edit_customer_layout = [
        [sg.Text('Edit a customer')],
        [sg.Text('Name', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_NAME,
                                                     default_text=customer.get('name'),
                                                     do_not_clear=True)],
        [sg.Text('Address', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_ADDRESS,
                                                        default_text=customer.get('address'),
                                                        do_not_clear=True)],
        [sg.Text('Postal', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_POSTAL,
                                                       default_text=customer.get('postal_code'),
                                                       do_not_clear=True)],
        [sg.Text('Tel', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TEL,
                                                    default_text=customer.get('tel_no'),
                                                    do_not_clear=True)],
        [sg.Text('Fax', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_FAX,
                                                    default_text=customer.get('fax_no'),
                                                    do_not_clear=True)],
        [sg.Text('Term', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TERM,
                                                     default_text=customer.get('term'),
                                                     do_not_clear=True)],
        [sg.Text('GST', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_GST,
                                                    default_text=customer.get('gst'),
                                                    do_not_clear=True)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SAVE_CUSTOMER), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    edit_customer_window = sg.Window('Edit Customer').Layout(edit_customer_layout)
    while True:
        edit_customer_event, edit_customer_val = edit_customer_window.Read()
        if edit_customer_event is None or \
                edit_customer_event == 'Exit' or \
                edit_customer_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            edit_customer_window.Close()
            break
        if edit_customer_event == RELIEF_BUTTON_EVENT.SAVE_CUSTOMER:
            name = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_NAME)
            address = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_ADDRESS)
            postal = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_POSTAL)
            tel = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TEL)
            fax = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_FAX)
            term = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_TERM)
            gst = edit_customer_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMER_GST)

            response = update_customer_data(customer_id, address, name, postal, tel, fax, term, gst)
            if response.status_code == requests.codes.ok:
                edit_customer_window.Close()
                break
            else:
                edit_customer_window.Fill(edit_customer_val)
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)


def show_add_product_window():
    add_product_layout = [
        [sg.Text('Add a product')],
        [sg.Text('Name', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_PRODUCT_NAME)],
        [sg.Text('Specifications', size=(15, 1)),
         sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_PRODUCT_SPECIFICATIONS)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_PRODUCT), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    add_product_window = sg.Window('Add Product').Layout(add_product_layout)
    while True:
        add_product_event, add_product_val = add_product_window.Read()

        if add_product_event is None or \
                add_product_event == 'Exit' or \
                add_product_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            add_product_window.Close()
            break

        if add_product_event == RELIEF_BUTTON_EVENT.SUBMIT_PRODUCT:
            print(RELIEF_BUTTON_EVENT.SUBMIT_PRODUCT)
            name = add_product_val.get(RELIEF_INPUT_FIELDS.INPUT_PRODUCT_NAME)
            specification = add_product_val.get(RELIEF_INPUT_FIELDS.INPUT_PRODUCT_SPECIFICATIONS)
            response = post_product_data(name, specification)
            if response.status_code == requests.codes.created:
                add_product_window.Close()
                break
            else:
                add_product_window.Fill(add_product_val)
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)


def show_edit_product_window(product_id):
    product = get_product_detail_data(product_id)
    edit_product_layout = [
        [sg.Text('Edit a product')],
        [sg.Text('Name', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_PRODUCT_NAME,
                                                     default_text=product.get('name'))],
        [sg.Text('Specifications', size=(15, 1)),
         sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_PRODUCT_SPECIFICATIONS,
                      default_text=product.get('specification'))],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SAVE_PRODUCT), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    edit_product_window = sg.Window('Edit Product').Layout(edit_product_layout)
    while True:
        edit_product_event, edit_product_val = edit_product_window.Read()
        if edit_product_event is None or \
                edit_product_event == 'Exit' or \
                edit_product_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            edit_product_window.Close()
            break
        if edit_product_event == RELIEF_BUTTON_EVENT.SAVE_PRODUCT:
            print(RELIEF_BUTTON_EVENT.SAVE_PRODUCT)
            print(product.get('id'))
            print(edit_product_val.get(RELIEF_INPUT_FIELDS.INPUT_PRODUCT_NAME))
            print(edit_product_val.get(RELIEF_INPUT_FIELDS.INPUT_PRODUCT_SPECIFICATIONS))
            product_id = product.get('id')
            product_name = edit_product_val.get(RELIEF_INPUT_FIELDS.INPUT_PRODUCT_NAME)
            product_spec = edit_product_val.get(RELIEF_INPUT_FIELDS.INPUT_PRODUCT_SPECIFICATIONS)
            response = update_product_data(product_id, product_name, product_spec)
            if response.status_code == requests.codes.ok:
                edit_product_window.Close()
                break
            else:
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)


def show_add_trip_window():
    add_trip_layout = [
        [sg.Text('Add a trip')],
        [sg.Text('Date', size=(15, 1)),
         sg.Input('', size=(15, 1), key=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE), do_not_clear=True),
         sg.CalendarButton('Choose Date', key=RELIEF_BUTTON_EVENT.CALENDAR_TRIP,
                           target=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE)),
         sg.InputCombo(["%02d" % hour for hour in range(0, 24)], key=RELIEF_INPUT_FIELDS.INPUT_TRIP_HOURS),
         sg.InputCombo(["%02d" % minute for minute in range(0, 60, 15)], key=RELIEF_INPUT_FIELDS.INPUT_TRIP_MINUTE)],
        [sg.Text('Notes', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_TRIP_NOTES, do_not_clear=True)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_TRIP), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]

    add_trip_window = sg.Window('Add Trip').Layout(add_trip_layout)
    while True:
        add_trip_event, add_trip_val = add_trip_window.Read()
        if add_trip_event is None or \
                add_trip_event == 'Exit' or \
                add_trip_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            add_trip_window.Close()
            break
        if add_trip_event == RELIEF_BUTTON_EVENT.SUBMIT_TRIP:
            print(RELIEF_BUTTON_EVENT.SUBMIT_TRIP)
            try:
                # date_input hours and minutes will be zero returned by calendar.
                date_input = add_trip_val.get(str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE))
                hour = int(add_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_HOURS))
                minutes = int(add_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_MINUTE))
                d = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S").date()
                t = time(hour, minutes)
                datetime_combine = datetime.combine(d, t).strftime("%d-%m-%Y %H:%M")
                notes = add_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_NOTES)
                response = post_trip_data(datetime_combine, notes)
                if response.status_code == requests.codes.created:
                    add_trip_window.Close()
                    break
                else:
                    sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
                print(date, hour, minutes)
            except ValueError as e:
                sg.Popup('Error', str(e), button_type=sg.POPUP_BUTTONS_OK)


def show_edit_trip_window(trip_id):
    print(trip_id)
    trip = get_trip_detail_data(trip_id)
    trip_date_str = trip.get('date')
    print(trip_date_str)
    trip_date = datetime.strptime(trip_date_str, "%d-%m-%Y %H:%M")
    trip_hour = "%02d" % trip_date.hour
    trip_minute = "%02d" % trip_date.minute
    edit_trip_layout = [
        [sg.Text('Edit a trip')],
        [sg.Text('Date', size=(15, 1)),
         sg.Input(size=(15, 1), key=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE), default_text=trip_date_str,
                  do_not_clear=True),
         sg.CalendarButton('Choose Date', key=RELIEF_BUTTON_EVENT.CALENDAR_TRIP,
                           target=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE)),
         sg.InputCombo(["%02d" % hour for hour in range(0, 24)], key=RELIEF_INPUT_FIELDS.INPUT_TRIP_HOURS,
                       default_value=trip_hour),
         sg.InputCombo(["%02d" % minute for minute in range(0, 60, 15)], key=RELIEF_INPUT_FIELDS.INPUT_TRIP_MINUTE,
                       default_value=trip_minute)],
        [sg.Text('Notes', size=(15, 1)),
         sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_TRIP_NOTES, default_text=trip.get('notes'), do_not_clear=True)],
        [sg.Text('Packing', size=(15, 1)),
         sg.Multiline(size=(35, 3), key=RELIEF_INPUT_FIELDS.INPUT_TRIP_PACKAGING_METHODS,
                      default_text=trip.get('packaging_methods'), do_not_clear=True)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SAVE_TRIP), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    edit_trip_window = sg.Window('Edit trip').Layout(edit_trip_layout)
    while True:
        edit_trip_event, edit_trip_val = edit_trip_window.Read()
        if edit_trip_event is None or \
                edit_trip_event == 'Exit' or \
                edit_trip_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            edit_trip_window.Close()
            break
        if edit_trip_event == RELIEF_BUTTON_EVENT.SAVE_TRIP:
            try:
                # date_input hours and minutes will be zero returned by calendar.
                date_input = edit_trip_val.get(str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE))
                hour = int(edit_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_HOURS))
                minutes = int(edit_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_MINUTE))
                try:
                    d = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S").date()
                except ValueError:
                    d = datetime.strptime(date_input, "%d-%m-%Y %H:%M").date()
                t = time(hour, minutes)
                datetime_combine = datetime.combine(d, t).strftime("%d-%m-%Y %H:%M")
                notes = edit_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_NOTES)
                packaging_methods = edit_trip_val.get(RELIEF_INPUT_FIELDS.INPUT_TRIP_PACKAGING_METHODS)
                response = update_trip_data(trip_id, datetime_combine, notes, packaging_methods)
                if response.status_code == requests.codes.ok:
                    edit_trip_window.Close()
                    break
                else:
                    sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
                print(date, hour, minutes)
            except ValueError as e:
                sg.Popup('Error', str(e), button_type=sg.POPUP_BUTTONS_OK)


def show_customer_detail_window(customer_id):
    customer = get_customer_detail_data(customer_id)
    customer_detail_layout = [
        [sg.Button('Edit', key=RELIEF_BUTTON_EVENT.EDIT_CUSTOMER),
         sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.CUSTOMER_DETAIL_REFRESH)],
        [sg.Text('Name: ' + str(customer.get('name')), size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_NAME_TEXT)],
        [sg.Text('Address: ' + str(customer.get('address')), size=(45, 1),
                 key=RELIEF_VIEW_ELEMENTS.CUSTOMER_ADDRESS_TEXT)],
        [sg.Text('Postal: ' + str(customer.get('postal_code')), size=(45, 1),
                 key=RELIEF_VIEW_ELEMENTS.CUSTOMER_POSTAL_TEXT)],
        [sg.Text('Tel: ' + str(customer.get('tel_no')), size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_TEL_TEXT)],
        [sg.Text('Fax: ' + str(customer.get('fax_no')), size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_FAX_TEXT)],
        [sg.Text('Term: ' + str(customer.get('term')), size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_TERM_TEXT)],
        [sg.Text('GST: ' + str(customer.get('gst')), size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_GST_TEXT)]
    ]

    customerproduct_headings = ['ID', 'Product', 'Quote']
    customerproducts = get_customerproduct_data(customer_id)
    blank_customerproducts = [['' for i in range(len(customerproduct_headings))]]
    customerproduct_layout = [[sg.Button('Add', key=RELIEF_BUTTON_EVENT.ADD_CUSTOMERPRODUCT),
                               sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_CUSTOMERPRODUCT)],
                              [sg.Table(
                                  values=customerproducts if len(customerproducts) > 0 else blank_customerproducts,
                                  headings=customerproduct_headings,
                                  auto_size_columns=True,
                                  justification='left',
                                  enable_events=True,
                                  vertical_scroll_only=False,
                                  key=RELIEF_VIEW_ELEMENTS.CUSTOMERPRODUCT_VIEW_TABLE)]]

    order_headings = ['Index', 'D/O', 'Note', 'Invoice', 'Trip']
    blank_orders = [['' for i in range(len(order_headings))]]
    orders = get_customer_routes(customer_id)
    order_layout = [[sg.Table(values=orders if len(orders) > 0 else blank_orders,
                              headings=order_headings,
                              auto_size_columns=True,
                              justification='left',
                              enable_events=True,
                              vertical_scroll_only=False,
                              key=RELIEF_VIEW_ELEMENTS.ORDER_VIEW_TABLE)]]

    invoice_select = None

    invoice_headings = ['ID',
                        'Year',
                        'Number',
                        'Start Date',
                        'End Date',
                        'Minus',
                        'GST',
                        'Original Total',
                        'Net Total',
                        'Net GST',
                        'Total with GST',
                        'Remark',
                        'Date Generated']

    invoices = get_customer_invoices(customer_id)
    blank_invoices = [['' for i in range(len(invoice_headings))]]
    invoice_layout = [[sg.Button('Delete', key=RELIEF_BUTTON_EVENT.DELETE_INVOICE),
                       sg.Button('Create', key=RELIEF_BUTTON_EVENT.CREATE_INVOICE)],
                      [sg.Table(values=invoices if len(invoices) > 0 else blank_invoices,
                                headings=invoice_headings,
                                justification='center',
                                enable_events=True,
                                vertical_scroll_only=False,
                                key=RELIEF_VIEW_ELEMENTS.CUSTOMER_INVOICE_VIEW_TABLE)]]

    layout = [[sg.TabGroup([[sg.Tab('Customer', customer_detail_layout),
                             sg.Tab('Product', customerproduct_layout),
                             sg.Tab('Order', order_layout),
                             sg.Tab('Invoice', invoice_layout)]])],
              [sg.T('Status: ')]]

    customer_window = sg.Window('Customer Detail', default_element_size=(12, 1), resizable=True).Layout(layout)

    while True:
        event, values = customer_window.Read()

        # print(event, values)
        if event is None or event == 'Exit':
            break
        if event == RELIEF_VIEW_ELEMENTS.CUSTOMERPRODUCT_VIEW_TABLE:
            print(RELIEF_VIEW_ELEMENTS.CUSTOMERPRODUCT_VIEW_TABLE)
            customerproduct_row = values.get(RELIEF_VIEW_ELEMENTS.CUSTOMERPRODUCT_VIEW_TABLE)[0]
            customerproduct_id = customerproducts[customerproduct_row][0]
            if type(customerproduct_id) is int:
                show_edit_customer_product(customerproduct_id)
        if event == RELIEF_VIEW_ELEMENTS.ORDER_VIEW_TABLE:
            print(RELIEF_VIEW_ELEMENTS.ORDER_VIEW_TABLE)
        if event == RELIEF_VIEW_ELEMENTS.CUSTOMER_INVOICE_VIEW_TABLE:
            print(RELIEF_VIEW_ELEMENTS.CUSTOMER_INVOICE_VIEW_TABLE)
            # get the first element only for now.
            index = values.get(RELIEF_VIEW_ELEMENTS.CUSTOMER_INVOICE_VIEW_TABLE)[0]
            if type(index) is int:
                invoice_select = invoices[index]
        if event == RELIEF_BUTTON_EVENT.ADD_CUSTOMERPRODUCT:
            print(RELIEF_BUTTON_EVENT.ADD_CUSTOMERPRODUCT)
            if type(customer_id) is int:
                show_add_customer_product(customer_id)
        if event == RELIEF_BUTTON_EVENT.EDIT_CUSTOMER:
            if type(customerproduct_id) is int:
                show_edit_customer_window(customer_id)
        if event == RELIEF_BUTTON_EVENT.CUSTOMER_DETAIL_REFRESH:
            if type(customer_id) is int:
                customer = get_customer_detail_data(customer_id)
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_NAME_TEXT).Update('Name: ' + customer.get('name'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_ADDRESS_TEXT).Update(
                    'Address: ' + customer.get('address'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_POSTAL_TEXT).Update(
                    'Postal: ' + customer.get('postal_code'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_TEL_TEXT).Update('Tel: ' + customer.get('tel_no'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_FAX_TEXT).Update('Fax: ' + customer.get('fax_no'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_TERM_TEXT).Update(
                    'Term: ' + str(customer.get('term')))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_GST_TEXT).Update(
                    'GST: ' + str(customer.get('gst')))
        if event == RELIEF_BUTTON_EVENT.REFRESH_CUSTOMERPRODUCT:
            print(RELIEF_BUTTON_EVENT.REFRESH_CUSTOMERPRODUCT)
            if type(customerproduct_id) is int:
                customerproducts = get_customerproduct_data(customer_id)
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMERPRODUCT_VIEW_TABLE) \
                    .Update(values=customerproducts if len(customerproducts) > 0 else blank_customerproducts)
        if event == RELIEF_BUTTON_EVENT.DELETE_INVOICE:
            print(RELIEF_BUTTON_EVENT.DELETE_INVOICE)
            invoice_id = invoice_select[0]
            if type(invoice_id) is int:
                show_delete_invoices_window(invoice_id)

        if event == RELIEF_BUTTON_EVENT.CREATE_INVOICE:
            print(RELIEF_BUTTON_EVENT.CREATE_INVOICE)
            date_range = show_create_invoice_daterange_window()
            show_create_invoice_window(customer_id, date_range)


    customer_window.Close()


def show_create_invoice_daterange_window():
    print('Showing daterange')
    daterange_layout = [
        [sg.Text('Set invoice date range')],
        [sg.Text('Start Date', size=(15, 1)),
         sg.Input('', size=(15, 1), key=str(RELIEF_INPUT_FIELDS.INPUT_INVOICE_START_DATE), do_not_clear=True),
         sg.CalendarButton('Set', key=RELIEF_BUTTON_EVENT.CALENDAR_TRIP,
                           target=str(RELIEF_INPUT_FIELDS.INPUT_INVOICE_START_DATE))],
        [sg.Text('End Date', size=(15, 1)),
         sg.Input('', size=(15, 1), key=str(RELIEF_INPUT_FIELDS.INPUT_INVOICE_END_DATE), do_not_clear=True),
         sg.CalendarButton('Set', key=RELIEF_BUTTON_EVENT.CALENDAR_TRIP,
                           target=str(RELIEF_INPUT_FIELDS.INPUT_INVOICE_END_DATE))],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_INVOICE), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]

    daterange_window = sg.Window('Set invoice date range').Layout(daterange_layout)
    while True:
        daterange_event, daterange_val = daterange_window.Read()
        if daterange_event is None or daterange_event == 'Exit' or daterange_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            break
        if daterange_event == RELIEF_BUTTON_EVENT.SUBMIT_INVOICE:
            print(RELIEF_BUTTON_EVENT.SUBMIT_INVOICE)
            # TODO: date range validation
            daterange_window.Close()
            break

    date_start = daterange_val.get(str(RELIEF_INPUT_FIELDS.INPUT_INVOICE_START_DATE))
    date_end = daterange_val.get(str(RELIEF_INPUT_FIELDS.INPUT_INVOICE_END_DATE))
    print(date_start, date_end)
    return {'date_start': date_start, 'date_end': date_end}


def show_save_invoice_window(invoice_id):
    invoice = get_invoice_detail(invoice_id)
    invoice_name = sg.PopupGetFile("Save Invoice", save_as=True, file_types=(("PDF File", "*.pdf"),)) + ".pdf"
    print(invoice_name)
    export_invoice_to_pdf(invoice, invoice_name)


def export_invoice_to_pdf(invoice, save_as_location):
    customer_name = invoice.get('customer_name')
    customer_term = invoice.get('customer_term')
    customer_gst = invoice.get('gst')
    customer_id = invoice.get('customer_id')
    invoice_number = invoice.get('invoice_number')
    invoice_year = invoice.get('invoice_year')
    start_date = invoice.get('start_date')
    end_date = invoice.get('end_date')
    minus = invoice.get('minus')
    gst = invoice.get('gst')
    original_total = invoice.get('original_total')
    net_total = invoice.get('net_total')
    net_gst = invoice.get('net_gst')
    total_incl_gst = invoice.get('total_incl_gst')
    remark = invoice.get('remark')
    date_generated = invoice.get('date_generated')
    routes = invoice.get('route_set')

    customerproducts = get_customerproduct_data(customer_id)
    customerproduct_headings = [cp[1] for cp in customerproducts]
    quantity_row = {cp: 0 for cp in customerproduct_headings}
    unit_price_row = {cp[1]: cp[2] for cp in customerproducts}
    nett_amt_row = {cp: 0 for cp in customerproduct_headings}

    pdf_location = save_as_location
    doc = SimpleDocTemplate(pdf_location, pagesize=A4, rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm,
                            bottomMargin=2 * cm)

    # container for the "Flowable" objects
    elements = list()

    # Make heading for each column and start data list

    top_table_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9)])

    top_table_data = list()
    top_table_data.append(["SUN-UP BEAN FOOD MFG PTE LTD", "TAX INVOICE"])
    address_invoice_number_row = ["TUAS BAY WALK #02-30 SINGAPORE 637780"]
    if float(customer_gst) > 0:
        address_invoice_number_row.append("INVOICE NUMBER:")
        address_invoice_number_row.append(invoice_year + " " + invoice_number)
    top_table_data.append(address_invoice_number_row)
    top_table_data.append(["TEL: 68639035 FAX: 68633738", "DATE: ", "{0}".format(end_date)])
    top_table_data.append(["REG NO: 200302589N", "TERMS: ", str(customer_term) + " DAYS"])
    top_table_data.append(["BILL TO"])
    top_table_data.append([customer_name])

    top_table = Table(top_table_data, [12 * cm, 4 * cm, 3 * cm])
    top_table.setStyle(top_table_style)

    # Assemble data for each column using simple loop to append it into data list

    product_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                                ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
                                ('FONTSIZE', (0, 0), (-1, -1), 9)])

    product_data = [["DATE"] + customerproduct_headings + ["D/O"]]
    table_width = (19 / len(product_data[0])) * cm

    for r in routes:
        # Remove time part of trip date
        row_date = r.get('trip_date')[:-5]
        row = [row_date]
        print(r)
        for cp_heading in customerproduct_headings:
            orderitem_qty = r.get(cp_heading)
            if orderitem_qty:
                print(cp_heading, orderitem_qty)
                quantity_row[cp_heading] += orderitem_qty
                row.append(str(orderitem_qty))
            else:
                row.append("")

        row_do_number = r.get('do_number')
        row.append(row_do_number)
        product_data.append(row)
    print(product_data)
    product_table = Table(product_data, [table_width for i in range(len(product_data))], repeatRows=1, rowHeights=16)
    product_table.hAlign = 'CENTER'
    product_table.setStyle(product_style)

    quantity_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                 ('FONTSIZE', (0, 0), (-1, -1), 9)])

    for cp in customerproduct_headings:
        quantity = quantity_row.get(cp)
        unit_price = float(unit_price_row.get(cp))
        nett_amt = quantity * unit_price
        nett_amt_row[cp] = round(nett_amt, 4)

    quantity_data = list()

    quantity_data.append(["QUANTITY"] + [quantity_row.get(cp) for cp in customerproduct_headings] + [""])
    quantity_data.append(["UNIT PRICE ($)"] + [unit_price_row.get(cp) for cp in customerproduct_headings] + [""])
    quantity_data.append(["NETT AMOUNT ($)"] + ['%.4f' % nett_amt_row.get(cp) for cp in customerproduct_headings] + [""])
    quantity_table = Table(quantity_data, [table_width for i in range(len(product_data))])
    quantity_table.hAlign = 'CENTER'
    quantity_table.setStyle(quantity_style)

    total_data_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9),
                                   ('GRID', (1, 0), (-1, -1), 0.5, colors.black)])
    total_data = list()
    total_data.append(["SUB-TOTAL ($)", "{0}".format(original_total)])
    total_data.append(["MINUS ($)", "{0}".format(minus)])
    total_data.append(["GST ({0}%)".format(gst), "{0}".format(net_gst)])
    total_data.append(["TOTAL (inc. GST) ($)", "{0}".format(total_incl_gst)])
    total_data_table = Table(total_data)
    total_data_table.hAlign = 'RIGHT'
    total_data_table.setStyle(total_data_style)

    elements.append(top_table)
    elements.append(product_table)
    elements.append(quantity_table)
    elements.append(total_data_table)

    doc.build(elements)


def get_edit_invoice_layout(customer, customerproducts, routes, reduction_calculation=0, invoice_year='', invoice_number=''):
    customer_name = customer.get('name')
    customer_address = customer.get('address')
    customer_postal = customer.get('postal_code')
    customer_term = customer.get('term')
    customer_gst = customer.get('gst')

    customerproduct_headings = [cp[1] for cp in customerproducts]
    customerproduct_widget_lists = {heading: [sg.Text(heading, size=(15, 1))] for heading in customerproduct_headings}

    subtotal_calculation = 0
    size_offset = (15 * len(customerproduct_headings)) + 60
    print(size_offset)
    company_column_widget_list = []
    company_column_widget_list.append(sg.Button('Save', key=str(RELIEF_BUTTON_EVENT.SAVE_INVOICE)))
    company_column_widget_list.append(sg.Text('BILL TO ', size=(15, 1)))
    company_column_widget_list.append(sg.Text(customer_name, size=(15, 1)))
    company_column_widget_list.append(sg.Text('TERM: ' + str(customer_term), size=(15, 1)))
    print(invoice_year, invoice_number)
    company_column_widget_list.append(sg.Text('INVOICE NO.: ' + invoice_year + invoice_number,
                                              size=(size_offset, 1),
                                              key=str(RELIEF_VIEW_ELEMENTS.INVOICE_NUMBER),
                                              justification="right",
                                              enable_events=True))
    if customer_address != 'None' and customer_address:
        company_column_widget_list.append(sg.Text(customer_address, size=(15, 1)))
    if customer_postal != 'None' and customer_postal:
        company_column_widget_list.append(sg.Text(customer_postal, size=(15, 1)))

    company_column_widget = widget_list_to_column(company_column_widget_list)

    invoice_layout = [[company_column_widget], [], [], []]
    date_column_list = [sg.Text('DATE', size=(15, 1))]
    do_column_list = [sg.Text('D/O', size=(15, 1))]
    quantity_row = {cp: 0 for cp in customerproduct_headings}
    unit_price_row = {cp[1]: cp[2] for cp in customerproducts}
    nett_amt_row = {cp: 0 for cp in customerproduct_headings}

    for r in routes:
        print(r)
        route_key = str(RELIEF_VIEW_ELEMENTS.INVOICE_ROUTE_ID) + str(r.get('id'))
        # Remove time from trip date
        date_column_list.append(sg.Text(r.get('trip_date')[:-5], size=(15, 1)))

        do_number = r.get('do_number')
        if do_number == '':
            do_column_list.append(sg.Text('ENTER', size=(15, 1), key=route_key, enable_events=True))
        else:
            do_column_list.append(sg.Text(do_number, size=(15, 1), key=route_key, enable_events=True))

        for cp_heading in customerproduct_headings:
            orderitem = r.get(cp_heading)
            customerproduct_list = customerproduct_widget_lists.get(cp_heading)
            if orderitem:
                print(orderitem)
                orderitem_key = str(RELIEF_VIEW_ELEMENTS.INVOICE_ORDERITEM_ID) + str(orderitem.get('id'))
                quantity = orderitem.get('quantity')
                driver_quantity = orderitem.get('driver_quantity')
                if driver_quantity != quantity:
                    customerproduct_list.append(sg.Text(str(quantity) + " \u27f6 " + str(driver_quantity),
                                                        size=(15, 1),
                                                        key=orderitem_key,
                                                        enable_events=True))
                    quantity_row[orderitem.get('customerproduct')] += driver_quantity
                else:
                    customerproduct_list.append(sg.Text(orderitem.get('quantity'),
                                                        size=(15, 1),
                                                        key=orderitem_key,
                                                        enable_events=True))
                    quantity_row[orderitem.get('customerproduct')] += quantity
            else:
                customerproduct_list.append(sg.Text('', size=(15, 1)))

    date_column_list.append(sg.Button('Add', key=str(RELIEF_BUTTON_EVENT.ADD_INVOICE_ORDER)))

    invoice_layout[1].append(widget_list_to_column(date_column_list))
    for cp_column_list in customerproduct_widget_lists.values():
        invoice_layout[1].append(widget_list_to_column(cp_column_list))
    invoice_layout[1].append(widget_list_to_column(do_column_list))

    calculation_heading_widget_list = [sg.Text('Quantity: ', size=(15, 1)),
                                       sg.Text('Unit Price: ', size=(15, 1)),
                                       sg.Text('Nett. Amt: ', size=(15, 1))]

    invoice_layout[2].append(widget_list_to_column(calculation_heading_widget_list))
    for cp in customerproduct_headings:
        quantity = quantity_row.get(cp)
        unit_price = float(unit_price_row.get(cp))
        nett_amt = quantity * unit_price
        nett_amt_row[cp] = nett_amt
        subtotal_calculation += nett_amt
        print(type(quantity), type(unit_price), type(nett_amt))
        column = list()
        column.append(sg.Text(quantity, size=(15, 1)))
        column.append(sg.Text('%.4f' % unit_price, size=(15, 1)))
        column.append(sg.Text('%.4f' % nett_amt, size=(15, 1)))
        invoice_layout[2].append(widget_list_to_column(column))

    subtotal_widget_column_list = list()

    subtotal_widget_column_list.append(sg.Text('Subtotal ($):', size=(size_offset, 1), justification="right"))
    if float(customer_gst) > 0:
        subtotal_widget_column_list.append(sg.Text('GST ($): ', size=(size_offset, 1), justification="right"))
        gst_reduction = subtotal_calculation * (customer_gst / 100)
        subtotal_calculation -= gst_reduction

    total = subtotal_calculation - float(reduction_calculation)
    subtotal_widget_column_list.append(sg.Text('Reduction ($): ', size=(size_offset, 1), justification="right"))
    subtotal_widget_column_list.append(sg.Text('Total ($): ', size=(size_offset, 1), justification="right"))
    invoice_layout[3].append(widget_list_to_column(subtotal_widget_column_list))

    subtotal_widget_column_list_values = list()
    subtotal_widget_column_list_values.append(sg.Text('%.4f' % subtotal_calculation))
    if float(customer_gst) > 0:
        subtotal_widget_column_list_values.append(sg.Text('%.4f' % gst_reduction))
    subtotal_widget_column_list_values.append(sg.Text('%.4f' % float(reduction_calculation),
                                                      key=str(RELIEF_VIEW_ELEMENTS.INVOICE_REDUCTION),
                                                      enable_events=True))
    subtotal_widget_column_list_values.append(sg.Text('%.4f' % total))
    invoice_layout[3].append(widget_list_to_column(subtotal_widget_column_list_values))

    return invoice_layout


def show_enter_invoice_number_window(invoice_year, invoice_number=''):
    invoice_number_layout = [[sg.Text('Enter invoice number')]]
    invoice_number_layout.append([sg.Text('Year: ', size=(15, 1)),
                                     sg.Input(invoice_year, key=RELIEF_INPUT_FIELDS.INPUT_INVOICE_YEAR)])
    if invoice_number == '':
        invoice_number_layout.append([sg.Text('Number: ', size=(15, 1)),
                                      sg.Input(invoice_number, key=RELIEF_INPUT_FIELDS.INPUT_INVOICE_NUMBER)])
    else:
        invoice_number = get_new_invoice_number()
        invoice_number_layout.append([sg.Text('Number: ', size=(15, 1)),
                                      sg.Input(invoice_number, key=RELIEF_INPUT_FIELDS.INPUT_INVOICE_NUMBER)])
    invoice_number_layout.append([sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_ORDER),
                                     sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)])
    invoice_order_window = sg.Window('Enter invoice number').Layout(invoice_number_layout)
    while True:
        invoice_number_event, invoice_number_val = invoice_order_window.Read()
        if invoice_number_event is None or invoice_number_event == 'Exit' or invoice_number_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            break
        if invoice_number_event == RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_ORDER:
            print(RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_ORDER)
            invoice_year = invoice_number_val.get(RELIEF_INPUT_FIELDS.INPUT_INVOICE_YEAR)
            invoice_number = invoice_number_val.get(RELIEF_INPUT_FIELDS.INPUT_INVOICE_NUMBER)
            break
    invoice_order_window.Close()
    return {'invoice_year': invoice_year, 'invoice_number': invoice_number}


def show_enter_price_reduction_window(current_reduction=0):
    price_reduction_layout = [[sg.Text('Subtract from subtotal')]]
    price_reduction_layout.append([sg.Text('Reduction: ', size=(15, 1)),
                                     sg.Input(default_text=str(current_reduction),
                                              key=RELIEF_INPUT_FIELDS.INPUT_INVOICE_REDUCTION)])

    price_reduction_layout.append([sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_REDUCTION),
                                     sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)])
    price_reduction_window = sg.Window('Subtract from subtotal').Layout(price_reduction_layout)
    while True:
        reduction_event, reduction_val = price_reduction_window.Read()
        if reduction_event is None or reduction_event == 'Exit' or reduction_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            break
        if reduction_event == RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_REDUCTION:
            print(RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_REDUCTION)
            current_reduction = reduction_val.get(RELIEF_INPUT_FIELDS.INPUT_INVOICE_REDUCTION)
            break
    price_reduction_window.Close()
    print(current_reduction)
    return current_reduction


def show_create_invoice_window(customer_id, date_range):
    print("show create invoice window")
    date_start = date_range.get('date_start')
    date_end = date_range.get('date_end')
    date_start_formatted = datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S").date()
    date_end_formatted = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S").date()
    routes = get_customer_routes_by_date(customer_id, date_start, date_end)
    customer = get_customer_detail_data(customer_id)
    customerproducts = get_customerproduct_data(customer_id)
    invoice_layout = get_edit_invoice_layout(customer, customerproducts, routes)
    invoice_window = sg.Window('Invoice').Layout(invoice_layout)
    reduction = 0
    invoice_year = datetime.now().year
    invoice_number = ''
    gst = customer.get('gst')
    while True:
        invoice_event, invoice_val = invoice_window.Read()
        if invoice_event is None or invoice_event == 'Exit' or invoice_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            invoice_window.Close()
            break
        if str(RELIEF_VIEW_ELEMENTS.INVOICE_ROUTE_ID) in invoice_event:
            route_id = invoice_event[len(str(RELIEF_VIEW_ELEMENTS.INVOICE_ROUTE_ID)):]
            print(route_id)
            do_number = show_edit_invoice_do_number_window(route_id)
            update_do_number_widget = invoice_window.FindElement(invoice_event)
            if do_number == '':
                update_do_number_widget.Update(value='ENTER')
            else:
                update_do_number_widget.Update(value=do_number)
        if str(RELIEF_VIEW_ELEMENTS.INVOICE_ORDERITEM_ID) in invoice_event:
            orderitem_id = invoice_event[len(str(RELIEF_VIEW_ELEMENTS.INVOICE_ORDERITEM_ID)):]
            print(orderitem_id)
            orderitem_driver_quantity = show_edit_invoice_orderitem_quantity_window(orderitem_id)
            update_orderitem_driver_quantity_widget = invoice_window.FindElement(invoice_event)
            update_orderitem_driver_quantity_widget.Update(value=orderitem_driver_quantity)
        if invoice_event == str(RELIEF_BUTTON_EVENT.ADD_INVOICE_ORDER):
            print(RELIEF_BUTTON_EVENT.ADD_INVOICE_ORDER)
            response = show_add_invoice_order_window(customer_id, customerproducts, date_start, date_end)
            response_json = response.json()
            route_row = convert_customer_route_json_to_dict(response_json)
            routes.append(route_row)
            updated_invoice_layout = get_edit_invoice_layout(customer, customerproducts, routes)
            invoice_window.Close()
            invoice_window = sg.Window('Invoice').Layout(updated_invoice_layout)
        if invoice_event == str(RELIEF_VIEW_ELEMENTS.INVOICE_NUMBER):
            print(RELIEF_VIEW_ELEMENTS.INVOICE_NUMBER)
            invoice_number_dict = show_enter_invoice_number_window(invoice_year, invoice_number=invoice_number)
            invoice_year = invoice_number_dict.get('invoice_year')
            invoice_number = invoice_number_dict.get('invoice_number')
            updated_invoice_layout = get_edit_invoice_layout(customer, customerproducts, routes,
                                                             reduction_calculation=reduction,
                                                             invoice_year=invoice_year,
                                                             invoice_number=invoice_number)
            print(invoice_number_dict)
            invoice_window.Close()
            invoice_window = sg.Window('Invoice').Layout(updated_invoice_layout)

        if invoice_event == str(RELIEF_VIEW_ELEMENTS.INVOICE_REDUCTION):
            print(RELIEF_VIEW_ELEMENTS.INVOICE_REDUCTION)
            reduction = show_enter_price_reduction_window()
            updated_invoice_layout = get_edit_invoice_layout(customer, customerproducts, routes,
                                                             reduction_calculation=reduction,
                                                             invoice_year=str(invoice_year),
                                                             invoice_number=invoice_number)
            invoice_window.Close()
            invoice_window = sg.Window('Invoice').Layout(updated_invoice_layout)

        if invoice_event == str(RELIEF_BUTTON_EVENT.SAVE_INVOICE):
            print(RELIEF_BUTTON_EVENT.SAVE_INVOICE)
            route_id_list = [r.get('id') for r in routes]
            response = create_invoice(gst, date_start_formatted, date_end_formatted, invoice_year, invoice_number, route_id_list)
            if response.status_code != requests.codes.created:
                sg.PopupError('Error', response.text)
            else:
                invoice_window.Close()


def show_add_invoice_order_window(customer_id, customerproducts, trip_start_date, trip_end_date):
    print(customerproducts)
    print(trip_start_date)
    print(trip_end_date)
    trips_filter = get_trip_data(trip_start_date, trip_end_date)
    trips_id = [trip[0] for trip in trips_filter]
    trips_date = [trip[1] for trip in trips_filter]

    add_invoice_order_layout = [[sg.Text('Add invoice order')]]
    add_invoice_order_layout.append([sg.Text('Date: ', size=(15, 1)),
                                     sg.InputCombo(trips_date, key=RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_TRIP_DATE)])

    add_invoice_order_layout.append([sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_ORDER),
                                     sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)])
    print(trips_filter)
    invoice_order_window = sg.Window('Add invoice order').Layout(add_invoice_order_layout)
    response = None
    while True:
        order_event, order_val = invoice_order_window.Read()
        if order_event is None or order_event == 'Exit' or order_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            break
        if order_event == RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_ORDER:
            print(RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_ORDER)
            trip_select = order_val.get(RELIEF_BUTTON_EVENT.SUBMIT_INVOICE_TRIP_DATE)
            trip_index = trips_date.index(trip_select)
            response = post_route(trips_id[trip_index], customer_id=customer_id)
            if response.status_code != requests.codes.created:
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
            else:
                break
    invoice_order_window.Close()
    return response


def show_edit_invoice_do_number_window(route_id):
    route = get_detail_route(route_id)
    print(route)
    do_number_layout = [[sg.Text('Edit D/O Number')],
              [sg.Text('D/O: ', size=(15, 1)),
               sg.InputText(default_text=route.get('do_number'), key=RELIEF_INPUT_FIELDS.INPUT_INVOICE_EDIT_DO)],
              [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_EDIT_DO), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]]
    edit_do_number_window = sg.Window('Edit D/O Number').Layout(do_number_layout)
    do_number = route.get('do_number')
    while True:
        do_event, do_val = edit_do_number_window.Read()
        if do_event is None or do_event == 'Exit' or do_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            break
        if do_event == RELIEF_BUTTON_EVENT.SUBMIT_EDIT_DO:
            print(RELIEF_BUTTON_EVENT.SUBMIT_EDIT_DO)
            input_do_number = do_val.get(RELIEF_INPUT_FIELDS.INPUT_INVOICE_EDIT_DO)
            response = update_route(route_id, do_number=input_do_number)
            if response.status_code == requests.codes.ok:
                do_number = input_do_number
                break
            else:
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
    edit_do_number_window.Close()
    return do_number


def show_edit_invoice_orderitem_quantity_window(orderitem_id):
    orderitem = get_detail_orderitem(orderitem_id)
    print(orderitem)
    quantity = orderitem.get('quantity')
    driver_quantity = orderitem.get('driver_quantity')
    orderitem_quantity_layout = [[sg.Text('Edit Orderitem Quantity')],
                                 [sg.Text('Quantity: ' + str(quantity), size=(15, 1))],
                                 [sg.Text('Driver Quantity: ', size=(15, 1)),
                                  sg.InputText(default_text=str(driver_quantity),
                                               key=RELIEF_INPUT_FIELDS.INPUT_INVOICE_ORDERITEM)],
                                 [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_EDIT_ORDERITEM),
                                  sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]]
    edit_orderitem_window = sg.Window('Edit Orderitem Quantity').Layout(orderitem_quantity_layout)

    while True:
        oi_event, oi_val = edit_orderitem_window.Read()
        if oi_event is None or oi_event == 'Exit' or oi_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            break
        if oi_event == RELIEF_BUTTON_EVENT.SUBMIT_EDIT_ORDERITEM:
            print(RELIEF_BUTTON_EVENT.SUBMIT_EDIT_ORDERITEM)
            input_driver_quantity = int(oi_val.get(RELIEF_INPUT_FIELDS.INPUT_INVOICE_ORDERITEM))
            response = update_orderitem(orderitem_id, driver_quantity=input_driver_quantity)
            if response.status_code == requests.codes.ok:
                driver_quantity = input_driver_quantity
                break
            else:
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
    edit_orderitem_window.Close()

    if driver_quantity != quantity:
        return str(quantity) + " \u27f6 " + str(driver_quantity)
    else:
        return str(driver_quantity)


def show_add_customer_product(customer_id):
    products_details = get_product_data()
    products = [p[1] for p in products_details]
    add_customerproduct_layout = [
        [sg.Text('Add a quote')],
        [sg.Text('Product', size=(15, 1)), sg.InputCombo(products,
                                                         size=(20, 3),
                                                         key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_PRODUCT)],
        [sg.Text('Quote', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_QUOTE,
                                                      do_not_clear=True)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMERPRODUCT), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    add_customerproduct_window = sg.Window('Add a quote').Layout(add_customerproduct_layout)

    while True:
        add_customerproduct_event, add_customerproduct_val = add_customerproduct_window.Read()
        if add_customerproduct_event is None or \
                add_customerproduct_event == 'Exit' or \
                add_customerproduct_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            add_customerproduct_window.Close()
            break
        if add_customerproduct_event == RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMERPRODUCT:
            print(RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMERPRODUCT)
            product_text = add_customerproduct_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_PRODUCT)
            quote = add_customerproduct_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_QUOTE)
            product_id = products_details[products.index(product_text)][0]
            response = post_customerproduct_data(quote, customer_id, product_id)
            if response.status_code == requests.codes.created:
                add_customerproduct_window.Close()
                break
            else:
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)

        if add_customerproduct_event == RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_PRODUCT:
            print(add_customerproduct_val)


def show_edit_customer_product(customerproduct_id):
    customerproduct = get_detail_customerproduct(customerproduct_id)
    edit_customerproduct_layout = [
        [sg.Text('Edit ' + customerproduct.get('product'))],
        [sg.Text('Quote', size=(15, 1)), sg.InputText(default_text=customerproduct.get('quote_price'),
                                                      key=RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_QUOTE,
                                                      do_not_clear=True)],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SAVE_CUSTOMERPRODUCT), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    edit_customerproduct_window = sg.Window('Edit a quote').Layout(edit_customerproduct_layout)

    while True:
        edit_customerproduct_event, edit_customerproduct_val = edit_customerproduct_window.Read()
        if edit_customerproduct_event is None or \
                edit_customerproduct_event == 'Exit' or \
                edit_customerproduct_event == RELIEF_BUTTON_EVENT.CANCEL:
            print(RELIEF_BUTTON_EVENT.CANCEL)
            edit_customerproduct_window.Close()
            break
        if edit_customerproduct_event == RELIEF_BUTTON_EVENT.SAVE_CUSTOMERPRODUCT:
            print(RELIEF_BUTTON_EVENT.SUBMIT_CUSTOMERPRODUCT)
            quote = edit_customerproduct_val.get(RELIEF_INPUT_FIELDS.INPUT_CUSTOMERPRODUCT_QUOTE)
            response = update_customerproduct_data(customerproduct_id, quote)
            if response.status_code == requests.codes.ok:
                edit_customerproduct_window.Close()
                break
            else:
                sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)


def show_delete_invoices_window(invoice_select):
    print(invoice_select)
    retVal = sg.PopupOKCancel("Delete this invoice?")
    if retVal == "OK":
        response = delete_customer_invoice(invoice_select)
        if response.status_code != requests.codes.no_content:
            sg.PopupError('Error', response.text)


def show_create_route_window(trip_id):
    customers = get_customer_data()
    customer_names = [c[1] for c in customers]
    customer_names.insert(0, '')
    create_route_layout = [
        [sg.Text('Customer: ', size=(10, 1)), sg.InputCombo(customer_names,
                                                            readonly=True,
                                                            key=RELIEF_INPUT_FIELDS.INPUT_ROUTE_CUSTOMER)],
        [sg.Text('Note: ', size=(10, 1)), sg.Multiline(key=RELIEF_INPUT_FIELDS.INPUT_ROUTE_NOTE,
                                                       do_not_clear=True,
                                                       size=(35, 3))],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SUBMIT_ROUTE), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]

    route_window = sg.Window('Create Route').Layout(create_route_layout)

    while True:
        route_event, route_val = route_window.Read()

        if route_event == 'Exit' or route_event is None or route_event == RELIEF_BUTTON_EVENT.CANCEL:
            route_window.Close()
            break
        if route_event == RELIEF_BUTTON_EVENT.SUBMIT_ROUTE:
            note = route_val.get(RELIEF_INPUT_FIELDS.INPUT_ROUTE_NOTE)
            customer = route_val.get(RELIEF_INPUT_FIELDS.INPUT_ROUTE_CUSTOMER)
            if customer == '' and note == '\n':
                sg.PopupOk('Enter either a customer or note')
            if customer == '' and note != '\n':
                response = post_route(trip_id, note=note)
                if response.status_code != requests.codes.created:
                    sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
                else:
                    route_window.Close()
                    break
            if customer != '' and note == '\n':
                # index minus one because blank string is inserted into customer name list
                name_index = customer_names.index(customer) - 1
                customer_id = customers[name_index][0]
                response = post_route(trip_id, customer_id=customer_id)
                if response.status_code != requests.codes.created:
                    sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
                else:
                    route_window.Close()
                    break
            if customer != '' and note != '\n':
                name_index = customer_names.index(customer) - 1
                customer_id = customers[name_index][0]
                response = post_route(trip_id, customer_id=customer_id, note=note)
                if response.status_code != requests.codes.created:
                    sg.Popup('Error', response.text, button_type=sg.POPUP_BUTTONS_OK)
                else:
                    route_window.Close()
                    break


def show_delete_routes_window(route_select):
    print(route_select)
    retVal = sg.PopupOKCancel("Delete this route?")
    if retVal == "OK":
        response = delete_route(route_select)
        if response.status_code != requests.codes.no_content:
            sg.PopupError('Error', response.text)


def get_packing_method_headings_layout(trip_packaging_methods):
    heading_layout = [sg.Text(heading,
                              font=("Helvetica", 8),
                              size=(12, 1),
                              justification='left',
                              key=heading)
                      for heading in trip_packaging_methods if heading != 'None']
    return heading_layout


def get_orderitem_quantity_row_layout(orderitem):
    layout = [sg.Text(orderitem.get('quantity'),
                      size=(8, 1),
                      key=str(RELIEF_VIEW_ELEMENTS.ORDERITEM_QTY_TEXT) + str(orderitem.get('id'))),
              sg.Text(orderitem.get('customerproduct'),
                      key=str(RELIEF_INPUT_FIELDS.INPUT_ORDERITEM_QTY) + str(orderitem.get('id')),
                      click_submits=True)]
    return layout


def get_route_note_row_layout(route):
    layout = [sg.Text(route.get('note'),
                      size=(45, 3),
                      key=str(RELIEF_INPUT_FIELDS.INPUT_ROUTE_NOTE) + str(route.get('id')))]
    return layout


def get_orderitem_packaging_column_text(orderitems, packing):
    packing_column = list()
    packing_column.append([sg.Text(packing, auto_size_text=True, font=("Helvetica", 8))])
    for oi in orderitems:
        oi_packing = oi.get('packing')
        key = str(oi.get('id')) + packing
        if oi_packing:
            quantity = oi_packing.get(packing)
            if quantity:
                packing_column.append([sg.Text(quantity, key=key, size=(8, 1))])
            else:
                packing_column.append([sg.Text('', key=key, size=(8, 1))])
        else:
            packing_column.append([sg.Text('', key=key, size=(8, 1))])
    packing = sg.Column(packing_column)
    return packing


def get_orderitem_packaging_column_input(orderitems, packing):
    packing_column = list()
    packing_column.append([sg.Text(packing, auto_size_text=True, font=("Helvetica", 8))])
    for oi in orderitems:
        oi_packing = oi.get('packing')
        key = str(oi.get('id')) + packing
        if oi_packing:
            quantity = oi_packing.get(packing)
            if quantity:
                packing_column.append([sg.Input(do_not_clear=True, default_text=quantity, key=key, size=(8, 1))])
            else:
                packing_column.append([sg.Input(do_not_clear=True, default_text='', key=key, size=(8, 1))])
        else:
            packing_column.append([sg.Input(do_not_clear=True, default_text='', key=key, size=(8, 1))])
    packing = sg.Column(packing_column)
    return packing


def get_orderitem_packing_quantity(orderitem, packing):
    packing_dict = orderitem.get('packing')
    if packing_dict is not None and packing in packing_dict:
        # return zero if key exists but value is none
        return packing_dict.get(packing, 0)
    return 0


def get_refresh_trip_detail_layout(trip_id, trip_detail):
    print(trip_id)
    trip_date = trip_detail.get('date')
    trip_notes = str(trip_detail.get('note'))
    trip_packaging_methods = str(trip_detail.get('packaging_methods')).split(',')
    trip_routes = sorted(trip_detail.get('route_set'), key=lambda route: route.get('index'))
    trip_orderitems_list = []

    # Column layout
    frame_list = []
    packing_methods_headings = get_packing_method_headings_layout(trip_packaging_methods)
    for tr in trip_routes:
        index = tr.get('index')
        do_number = str(tr.get('do_number'))
        customer_name = ''
        orderitems = tr.get('orderitem_set')

        if len(orderitems) > 0:
            customer_name = orderitems[0].get('customer')

        route_column = list()
        route_column.append([sg.Text('Inv. No: ' + ' | ' + 'D/O No.: ' + do_number)])
        for oi in orderitems:
            route_column.append(get_orderitem_quantity_row_layout(oi))
            trip_orderitems_list.append(oi)

        route_column.append([sg.Text('Notes: ',
                                     key=str(RELIEF_BUTTON_EVENT.EDIT_ROUTE) + str(tr.get('id')),
                                     click_submits=True)])
        route_column.append(get_route_note_row_layout(tr))
        route_column.append([sg.Button('Delete', key=str(RELIEF_BUTTON_EVENT.DELETE_ROUTE) + str(tr.get('id')))])

        if len(packing_methods_headings) > 0:
            f_layout = [[sg.Column(route_column), sg.VerticalSeparator(pad=None)]]
            for packing in trip_packaging_methods:
                packing_column = get_orderitem_packaging_column_text(orderitems, packing)
                f_layout[0].append(packing_column)
        else:
            f_layout = [[sg.Column(route_column)]]

        frame = sg.Frame('{0}. {1}'.format(index, customer_name), f_layout)
        frame_list.append(frame)

    margin_left_column = [[sg.Text('')]]
    total_layout = [[sg.Column(margin_left_column, size=(45, 1))]]
    packing_column_sum = get_packing_sum(trip_id)

    for packing in trip_packaging_methods:
        packing_column_total = sg.Column([[sg.Text(packing, auto_size_text=True, font=("Helvetica", 8))],
                                          [sg.Text(str(packing_column_sum.get(packing)), key=packing)]])
        total_layout[0].append(packing_column_total)

    last_frame = sg.Frame('', total_layout)
    frame_list.append(last_frame)

    layout = [[sg.Button('Edit', key=RELIEF_BUTTON_EVENT.EDIT_TRIP),
               sg.Button('PDF', key=RELIEF_BUTTON_EVENT.SAVE_PDF),
               sg.Button('Add Route', key=RELIEF_BUTTON_EVENT.ADD_ROUTE),
               sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_TRIP_ROUTE)],
              [sg.Text('Trip Date: ' + trip_date)],
              [sg.Text('Trip Notes: ' + trip_notes)],
              [sg.Column([[frame] for frame in frame_list], scrollable=True, vertical_scroll_only=False,
                         size=(800, 500))]]

    return layout


def show_trip_detail_window(trip_id):
    # Display the Window and get values
    trip_detail = get_trip_detail_list(trip_id)
    trip_date = trip_detail.get('date')
    trip_packaging_methods = str(trip_detail.get('packaging_methods')).split(',')
    layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
    trip_window = sg.Window(trip_date).Layout(layout)
    packing_sum = get_packing_sum(trip_id)
    print(packing_sum)
    while True:
        trip_event, trip_val = trip_window.Read()

        if trip_event == 'Exit' or trip_event is None:
            trip_window.Close()
            break
        if trip_event == RELIEF_BUTTON_EVENT.EDIT_TRIP:
            show_edit_trip_window(trip_id)
            # Full refresh
            trip_detail = get_trip_detail_list(trip_id)
            refresh_layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
            trip_window.Close()
            trip_window = sg.Window(trip_date).Layout(refresh_layout)
        if trip_event == RELIEF_BUTTON_EVENT.ADD_ROUTE:
            show_create_route_window(trip_id)
            # Full refresh
            trip_detail = get_trip_detail_list(trip_id)
            refresh_layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
            trip_window.Close()
            trip_window = sg.Window(trip_date).Layout(refresh_layout)
        if trip_event == RELIEF_BUTTON_EVENT.REFRESH_TRIP_ROUTE:
            # Full refresh
            trip_detail = get_trip_detail_list(trip_id)
            refresh_layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
            trip_window.Close()
            trip_window = sg.Window(trip_date).Layout(refresh_layout)
        if str(RELIEF_BUTTON_EVENT.DELETE_ROUTE) in str(trip_event):
            print('Delete Route')
            route_id = trip_event[len(str(RELIEF_BUTTON_EVENT.DELETE_ROUTE)):]
            show_delete_routes_window(route_id)
            # Full refresh
            trip_detail = get_trip_detail_list(trip_id)
            refresh_layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
            trip_window.Close()
            trip_window = sg.Window(trip_date).Layout(refresh_layout)
        if str(RELIEF_INPUT_FIELDS.INPUT_ORDERITEM_QTY) in str(trip_event):
            orderitem_id = str(trip_event)[len(str(RELIEF_INPUT_FIELDS.INPUT_ORDERITEM_QTY)):]
            orderitem_layout = get_route_orderitem_update_layout(int(orderitem_id), trip_packaging_methods)
            orderitem_window = sg.Window('Update orderitem').Layout(orderitem_layout)
            while True:
                oi_event, oi_val = orderitem_window.Read()
                if oi_event is None or oi_event == 'Exit' or oi_event == RELIEF_BUTTON_EVENT.CANCEL:
                    break
                if oi_event == RELIEF_BUTTON_EVENT.SAVE_ORDERITEM:
                    print(oi_event, oi_val)
                    response = save_route_orderitem(orderitem_id, oi_val, trip_packaging_methods)
                    if response.status_code == requests.codes.ok:
                        # update quantity text
                        orderitem_qty_text_key = str(RELIEF_VIEW_ELEMENTS.ORDERITEM_QTY_TEXT) + orderitem_id
                        orderitem_qty_dict_key = str(RELIEF_INPUT_FIELDS.INPUT_ORDERITEM_QTY) + orderitem_id
                        quantity_field = oi_val.get(orderitem_qty_dict_key)
                        orderitem_qty_text = trip_window.FindElement(orderitem_qty_text_key)
                        orderitem_qty_text.Update(value=quantity_field)
                        # update packing text
                        refresh_packing_sum = get_packing_sum(trip_id)
                        for packing in trip_packaging_methods:
                            orderitem_packing_key = orderitem_id + packing
                            orderitem_packing_qty = oi_val.get(orderitem_packing_key)
                            orderitem_packing_text = trip_window.FindElement(orderitem_packing_key)
                            orderitem_packing_text.Update(value=orderitem_packing_qty)
                            # update packing text
                            packing_sum_qty = refresh_packing_sum.get(packing)
                            packing_sum_text = trip_window.FindElement(packing)
                            packing_sum_text.Update(value=packing_sum_qty)
                        break
                    else:
                        sg.PopupError('Error', response.text)
            orderitem_window.Close()

        if str(RELIEF_BUTTON_EVENT.EDIT_ROUTE) in str(trip_event):
            route_id = str(trip_event)[len(str(RELIEF_BUTTON_EVENT.EDIT_ROUTE)):]
            route_layout = get_route_update_layout(route_id)
            route_window = sg.Window('Update route').Layout(route_layout)
            while True:
                route_event, route_val = route_window.Read()
                if route_event is None or route_event == 'Exit' or route_event == RELIEF_BUTTON_EVENT.CANCEL:
                    break
                if route_event == RELIEF_BUTTON_EVENT.SAVE_TRIP_ROUTE:
                    route_note = route_val.get(str(RELIEF_BUTTON_EVENT.EDIT_ROUTE) + str(route_id))
                    response = update_route(route_id, route_note)
                    if response.status_code == requests.codes.ok:
                        # update notes text value
                        note_text_key = str(RELIEF_INPUT_FIELDS.INPUT_ROUTE_NOTE) + route_id
                        note_text = trip_window.FindElement(note_text_key)
                        note_text.Update(route_note)
                        break
                    else:
                        sg.PopupError('Error', response.text)
            route_window.Close()

        if trip_event == RELIEF_BUTTON_EVENT.SAVE_PDF:
            print(RELIEF_BUTTON_EVENT.SAVE_PDF)
            export_order_to_pdf(trip_id)


def export_order_to_pdf(trip_id):
    trip_detail = get_trip_detail_list(trip_id)
    trip_date = trip_detail.get('date')
    trip_notes = "Note: " + str(trip_detail.get('note'))
    trip_packaging_methods = str(trip_detail.get('packaging_methods')).split(',')
    trip_routes = sorted(trip_detail.get('route_set'), key=lambda route: route.get('index'))

    pdfReportPages = "test_order_generate.pdf"
    doc = SimpleDocTemplate(pdfReportPages, pagesize=A4, rightMargin=0.5 * cm, leftMargin=0.5 * cm, topMargin=1 * cm,
                            bottomMargin=2 * cm)
    stylesheet = getSampleStyleSheet()
    styleNote = stylesheet["Normal"]
    packStyleSheet = getSampleStyleSheet()
    packNote = packStyleSheet["Normal"]
    packNote.fontSize = 7
    packNote.alignment = TA_CENTER
    packNote.leading = 10

    # container for the "Flowable" objects
    elements = []
    packaging = [Paragraph(heading, packNote) for heading in trip_packaging_methods]

    # Make heading for each column and start data list

    note_paragraph = Paragraph(trip_notes, styleNote)

    top_table_style = TableStyle([('SPAN', (0, -1), (-1, -1))])
    top_table_data = [["Date:", trip_date], [note_paragraph]]
    top_table = Table(top_table_data, [3 * cm, 10 * cm])
    top_table.hAlign = 'LEFT'
    top_table.setStyle(top_table_style)
    elements.append(top_table)
    elements.append(Spacer(1,12))

    customer_table_style = TableStyle([('SPAN', (1, 0), (3, 0)),
                                       ('SPAN', (0, -1), (-1, -1)),
                                       ('GRID', (0 - len(packaging), 0), (-1, -2), 0.5, colors.black),
                                       ('LEFTPADDING', (0, 0), (-1, -1), 1),
                                       ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                                       ('TOPPADDING', (0, 0), (-1, -1), 1),
                                       ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                                       ('ALIGN', (0 - len(packaging), 0), (-1, -1), 'CENTER')])


    total_table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')])

    packing_column_sum = get_packing_sum(trip_id)
    total_table_data = [packaging, [str(packing_column_sum.get(p)) for p in trip_packaging_methods]]
    total_table = Table(total_table_data, [(10.5 / (len(packaging))) * cm for p in packaging])
    total_table.hAlign = 'RIGHT'
    total_table.setStyle(total_table_style)

    noteStyleSheet = getSampleStyleSheet()
    noteStyle = noteStyleSheet["Normal"]
    noteStyle.fontSize = 14

    for tr in trip_routes:
        index = str(tr.get('index'))
        customer_name = ''
        trip_note = tr.get('note')
        orderitems = tr.get('orderitem_set')

        if len(orderitems) > 0:
            customer_name = orderitems[0].get('customer')

            # First Row
            route_table_data = [[index + ".", customer_name, "", ""] + packaging]

            for oi in orderitems:
                print(oi.get('customerproduct'))
                # orderitem_note = ""
                row = ["", oi.get('quantity'), Paragraph(oi.get('customerproduct'), styleNote), ""]
            # Second Row
                oi_packing = oi.get('packing')
                if oi_packing:
                    for packing in trip_packaging_methods:
                        quantity = oi_packing.get(packing)
                        if quantity:
                            row.append(quantity)
                        else:
                            row.append('')
                print(row)
                route_table_data.append(row)
            # Last Row
            route_table_data.append([trip_note])
            customer_table = Table(route_table_data,
                                   [0.5 * cm, 1 * cm, 4 * cm, 4 * cm] + [(10.5 / (len(packaging))) * cm for p in packaging])
            customer_table.hAlign = 'CENTER'
            customer_table.setStyle(customer_table_style)
            elements.append(customer_table)
            elements.append(Spacer(1,12))
        else:
            note = Paragraph(index + ". " + trip_note, noteStyle)
            elements.append(note)
            elements.append(Spacer(1,12))

    elements.append(total_table)
    elements.append(Spacer(1,12))

    doc.build(elements)


def get_route_orderitem_update_layout(orderitem_id, packing_methods):
    orderitem_key = str(RELIEF_INPUT_FIELDS.INPUT_ORDERITEM_QTY) + str(orderitem_id)
    orderitem = get_detail_orderitem(orderitem_id)
    orderitem_quantity = orderitem.get('quantity')
    orderitem_update_layout = [
        [sg.Text('Quantity'), sg.InputText(default_text=orderitem_quantity,
                                           key=orderitem_key,
                                           do_not_clear=True,
                                           size=(10, 1))],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SAVE_ORDERITEM), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]
    orderitems = [orderitem]
    for packing in packing_methods:
        column = get_orderitem_packaging_column_input(orderitems, packing)
        orderitem_update_layout[0].append(column)
    return orderitem_update_layout


def get_route_update_layout(route_id):
    route = get_detail_route(route_id)
    route_note = route.get('note')
    route_update_layout = [
        [sg.Text('Note'), sg.Multiline(default_text=route_note,
                                       do_not_clear=True,
                                       size=(30, 4),
                                       key=str(RELIEF_BUTTON_EVENT.EDIT_ROUTE) + str(route_id))],
        [sg.Submit(key=RELIEF_BUTTON_EVENT.SAVE_TRIP_ROUTE), sg.Cancel(key=RELIEF_BUTTON_EVENT.CANCEL)]
    ]

    return route_update_layout


def save_route_orderitem(orderitem_id, trip_values, packing_name_list):
    quantity_field = trip_values.get(str(RELIEF_INPUT_FIELDS.INPUT_ORDERITEM_QTY) + str(orderitem_id))
    print(trip_values)
    packaging_qty = {name: int(trip_values.get(str(orderitem_id) + name))
                     for name in packing_name_list
                     if trip_values.get(str(orderitem_id) + name)}
    print(packaging_qty)
    quantity = quantity_field
    response = update_orderitem(orderitem_id, quantity=quantity, driver_quantity=quantity, packing=packaging_qty)
    return response


def widget_list_to_column(widget_list):
    column_layout = []
    for widget in widget_list:
        column_layout.append([widget])
    column_widget = sg.Column(column_layout)
    return column_widget


if __name__ == "__main__":
    main()
