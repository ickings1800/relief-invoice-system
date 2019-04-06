import PySimpleGUI as sg
import requests
from enum import Enum
from datetime import datetime, date, time
from relief_controller import get_customer_data, get_product_data, get_trip_data, post_customer_data, \
    post_product_data, post_trip_data, get_product_detail_data, get_trip_detail_data, update_product_data, \
    update_trip_data, get_customer_detail_data, update_customer_data, get_customerproduct_data, \
    get_detail_customerproduct, post_customerproduct_data, update_customerproduct_data, get_customer_routes,\
    get_customer_invoices, delete_customer_invoice, get_all_invoices, get_trip_detail_list, post_route, delete_route,\
    update_route, update_orderitem, get_detail_orderitem, get_detail_route


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
    trip_layout =  [[sg.Button('Add', key=RELIEF_BUTTON_EVENT.ADD_TRIP),
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

    window = sg.Window('Relief Temp GUI', default_element_size=(12,1), resizable=True).Layout(layout)

    while True:                 # Event Loop  
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
            window.FindElement(RELIEF_VIEW_ELEMENTS.CUSTOMER_VIEW_TABLE)\
                .Update(values=customer_data if len(customer_data) > 0 else blank_customer_data)
        if event == RELIEF_BUTTON_EVENT.REFRESH_PRODUCT:
            print(RELIEF_BUTTON_EVENT.REFRESH_PRODUCT)
            product_data = get_product_data()
            window.FindElement(RELIEF_VIEW_ELEMENTS.PRODUCT_VIEW_TABLE)\
                .Update(values=product_data if len(product_data) > 0 else blank_product_data)
        if event == RELIEF_BUTTON_EVENT.REFRESH_TRIP:
            print(RELIEF_BUTTON_EVENT.REFRESH_TRIP)
            trip_data = get_trip_data()
            window.FindElement(RELIEF_VIEW_ELEMENTS.TRIP_VIEW_TABLE)\
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
        if event == RELIEF_BUTTON_EVENT.DELETE_INVOICE:
            invoice_id = invoice_select[0]
            if type(invoice_id) is int:
                show_delete_invoices_window(invoice_id)
        if event == RELIEF_BUTTON_EVENT.REFRESH_INVOICE:
            invoices = get_all_invoices()
            window.FindElement(RELIEF_VIEW_ELEMENTS.INVOICE_VIEW_TABLE)\
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
    # Populate text fields with retrieved data
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
    # TODO: Add Date/Time picker
    add_trip_layout = [      
              [sg.Text('Add a trip')],      
              [sg.Text('Date', size=(15, 1)),
               sg.Input('', size=(15, 1), key=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE), do_not_clear=True),
              sg.CalendarButton('Choose Date', key=RELIEF_BUTTON_EVENT.CALENDAR_TRIP, target=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE)),
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
    # TODO: Retrieve trip object from db
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
               sg.Input(size=(15, 1), key=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE), default_text=trip_date_str, do_not_clear=True),
              sg.CalendarButton('Choose Date', key=RELIEF_BUTTON_EVENT.CALENDAR_TRIP, target=str(RELIEF_INPUT_FIELDS.INPUT_TRIP_DATE)),
               sg.InputCombo(["%02d" % hour for hour in range(0, 24)], key=RELIEF_INPUT_FIELDS.INPUT_TRIP_HOURS, default_value=trip_hour),
               sg.InputCombo(["%02d" % minute for minute in range(0, 60, 15)], key=RELIEF_INPUT_FIELDS.INPUT_TRIP_MINUTE, default_value=trip_minute)],
              [sg.Text('Notes', size=(15, 1)), sg.InputText(key=RELIEF_INPUT_FIELDS.INPUT_TRIP_NOTES, default_text=trip.get('notes'), do_not_clear=True)],
              [sg.Text('Packing', size=(15, 1)), sg.Multiline(size=(35, 3), key=RELIEF_INPUT_FIELDS.INPUT_TRIP_PACKAGING_METHODS, default_text=trip.get('packaging_methods'), do_not_clear=True)],
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
        [sg.Text('Address: ' + str(customer.get('address')),  size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_ADDRESS_TEXT)],
        [sg.Text('Postal: ' + str(customer.get('postal_code')),  size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_POSTAL_TEXT)],
        [sg.Text('Tel: ' + str(customer.get('tel_no')),  size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_TEL_TEXT)],
        [sg.Text('Fax: ' + str(customer.get('fax_no')),  size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_FAX_TEXT)],
        [sg.Text('Term: ' + str(customer.get('term')),  size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_TERM_TEXT)],
        [sg.Text('GST: ' + str(customer.get('gst')),  size=(45, 1), key=RELIEF_VIEW_ELEMENTS.CUSTOMER_GST_TEXT)]
    ]

    customerproduct_headings = ['ID', 'Product', 'Quote']
    customerproducts = get_customerproduct_data(customer_id)
    blank_customerproducts = [['' for i in range(len(customerproduct_headings))]]
    customerproduct_layout = [[sg.Button('Add', key=RELIEF_BUTTON_EVENT.ADD_CUSTOMERPRODUCT),
                                sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_CUSTOMERPRODUCT)],
                              [sg.Table(values=customerproducts if len(customerproducts) > 0 else blank_customerproducts,
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
    invoice_layout = [[sg.Button('Delete', key=RELIEF_BUTTON_EVENT.DELETE_INVOICE)],
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

    customer_window = sg.Window('Customer Detail', default_element_size=(12,1), resizable=True).Layout(layout)
    
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
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_ADDRESS_TEXT).Update('Address: ' + customer.get('address'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_POSTAL_TEXT).Update('Postal: ' + customer.get('postal_code'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_TEL_TEXT).Update('Tel: ' + customer.get('tel_no'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_FAX_TEXT).Update('Fax: ' + customer.get('fax_no'))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_TERM_TEXT).Update('Term: ' + str(customer.get('term')))
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMER_GST_TEXT).Update('GST: ' + str(customer.get('gst')))
        if event == RELIEF_BUTTON_EVENT.REFRESH_CUSTOMERPRODUCT:
            print(RELIEF_BUTTON_EVENT.REFRESH_CUSTOMERPRODUCT)
            if type(customerproduct_id) is int:
                customerproducts = get_customerproduct_data(customer_id)
                customer_window.Element(RELIEF_VIEW_ELEMENTS.CUSTOMERPRODUCT_VIEW_TABLE)\
                    .Update(values=customerproducts if len(customerproducts) > 0 else blank_customerproducts)
        if event == RELIEF_BUTTON_EVENT.DELETE_INVOICE:
            print(RELIEF_BUTTON_EVENT.DELETE_INVOICE)
            invoice_id = invoice_select[0]
            if type(invoice_id) is int:
                show_delete_invoices_window(invoice_id)

    customer_window.Close()


def show_add_customer_product(customer_id):
    products_details = get_product_data()
    products = [p[1] for p in products_details]
    add_customerproduct_layout = [      
              [sg.Text('Add a quote')],      
              [sg.Text('Product', size=(15, 1)), sg.InputCombo(products,
                                                               size=(20,3),
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
              size=(8, 1)),
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
        key = packing
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


def get_orderitem_packing_sum(orderitem_set, trip_packaging_methods):
    packing_column_sum = {k: 0 for k in trip_packaging_methods}
    for oi in orderitem_set:
        for packing in oi.get('packing').keys():
            quantity = int(get_orderitem_packing_quantity(oi, packing))
            packing_column_sum[packing] += quantity
    return packing_column_sum


def get_refresh_trip_detail_layout(trip_id, trip_detail):
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
    packing_column_sum = get_orderitem_packing_sum(trip_orderitems_list, trip_packaging_methods)

    for packing in trip_packaging_methods:
        packing_column_total = sg.Column([[sg.Text(packing, auto_size_text=True, font=("Helvetica", 8))],
                                          [sg.Text(str(packing_column_sum.get(packing)), key=packing)]])
        total_layout[0].append(packing_column_total)

    last_frame = sg.Frame('', total_layout)
    frame_list.append(last_frame)

    layout = [[sg.Button('Edit', key=RELIEF_BUTTON_EVENT.EDIT_TRIP),
               sg.Button('PDF'),
               sg.Button('Add Route', key=RELIEF_BUTTON_EVENT.ADD_ROUTE),
               sg.Button('Refresh', key=RELIEF_BUTTON_EVENT.REFRESH_TRIP_ROUTE)],
              [sg.Text('Trip Date: ' + trip_date)],
              [sg.Text('Trip Notes: ' + trip_notes)],
              [sg.Column([[frame] for frame in frame_list], scrollable=True, vertical_scroll_only=False, size=(800, 500))]]

    return layout


def show_trip_detail_window(trip_id):
    # Display the Window and get values
    trip_detail = get_trip_detail_list(trip_id)
    trip_date = trip_detail.get('date')
    trip_packaging_methods = str(trip_detail.get('packaging_methods')).split(',')
    layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
    trip_window = sg.Window(trip_date).Layout(layout)

    while True:
        trip_event, trip_val = trip_window.Read()

        if trip_event == 'Exit' or trip_event is None:
            trip_window.Close()
            break
        if trip_event == RELIEF_BUTTON_EVENT.EDIT_TRIP:
            show_edit_trip_window(trip_id)
        if trip_event == RELIEF_BUTTON_EVENT.ADD_ROUTE:
            show_create_route_window(trip_id)
        if trip_event == RELIEF_BUTTON_EVENT.REFRESH_TRIP_ROUTE:
            # Full refresh
            trip_detail = get_trip_detail_list(trip_id)
            refresh_layout = get_refresh_trip_detail_layout(trip_id, trip_detail)
            trip_window.Close()
            trip_window = sg.Window(trip_date).Layout(refresh_layout)
        if 'DELETE_ROUTE_' in str(trip_event):
            route_id = trip_event[len(str(RELIEF_BUTTON_EVENT.DELETE_ROUTE))]
            show_delete_routes_window(route_id)
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
                        break
                    else:
                        sg.PopupError('Error', response.text)
            orderitem_window.Close()

        if str(RELIEF_BUTTON_EVENT.EDIT_ROUTE) in str(trip_event):
            route_id = str(trip_event)[len(str(RELIEF_BUTTON_EVENT.EDIT_ROUTE)):]
            print(route_id)
            route_layout = get_route_update_layout(route_id)
            route_window = sg.Window('Update route').Layout(route_layout)
            while True:
                route_event, route_val = route_window.Read()
                if route_event is None or route_event == 'Exit' or route_event == RELIEF_BUTTON_EVENT.CANCEL:
                    break
                if route_event == RELIEF_BUTTON_EVENT.SAVE_TRIP_ROUTE:
                    route_note = route_val.get(str(RELIEF_BUTTON_EVENT.EDIT_ROUTE) + str(route_id))
                    print(route_note)
                    response = update_route(route_id, route_note)
                    if response.status_code == requests.codes.ok:
                        break
                    else:
                        sg.PopupError('Error', response.text)
            route_window.Close()


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
    packaging_qty = {name: int(trip_values.get(name))
                     for name in packing_name_list
                     if trip_values.get(name)}
    quantity = quantity_field
    response = update_orderitem(orderitem_id, quantity=quantity, packing=packaging_qty)
    return response


if __name__ == "__main__":
    main()
