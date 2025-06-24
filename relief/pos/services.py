
import json
from .models import Customer

class FreshbooksService(object):
    def __init__(self, freshbooks_account_id, freshbooks_session):
        """
        Initialize the FreshbooksService.

        Args:
            freshbooks_account_id (str): The FreshBooks account ID.
            freshbooks_session (OAuth2Session): The session object for making API requests.
        """
        self.freshbooks_account_id = freshbooks_account_id
        self.freshbooks_session = freshbooks_session

    def search_freshbooks_invoices(self, invoice_number):
        search_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices?search[invoice_number]={1}'.format(
            self.freshbooks_account_id, invoice_number
        )
        freshbooks_invoice = self.freshbooks_session.get(search_url).json()

        freshbooks_invoice_search = freshbooks_invoice.get('response')\
            .get('result')\
            .get('invoices')
        return freshbooks_invoice_search

    def download_freshbooks_invoice(self, freshbooks_invoice_id):
        download_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices/{1}/pdf'.format(
            self.freshbooks_account_id, freshbooks_invoice_id
        )
        pdf = self.freshbooks_session.get(download_url, stream=True, headers={'Accept': 'application/pdf'})
        return pdf

    def create_freshbooks_invoice(self, invoice_data):
        invoice_create_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices'.format(
            self.freshbooks_account_id)
        headers = {'Api-Version': 'alpha', 'Content-Type': 'application/json'}
        response = self.freshbooks_session.post(invoice_create_url, data=json.dumps(invoice_data), headers=headers)

        if response.status_code != 200:
            raise Exception("Failed to create invoice: {}".format(response.text))
        invoice = response.json().get('response').get('result').get('invoice')
        return invoice

    def update_freshbooks_invoice(self, freshbooks_invoice_id, invoice_data):
        invoice_update_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices/{1}'.format(
            self.freshbooks_account_id, freshbooks_invoice_id
        )
        headers = {'Api-Version': 'alpha', 'Content-Type': 'application/json'}
        response = self.freshbooks_session.put(invoice_update_url, data=json.dumps(invoice_data), headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to update invoice: {}".format(response.text))
        return response.json().get('response').get('result').get('invoice')

    def get_freshbooks_tax(self, freshbooks_tax_id):
        res = self.freshbooks_session.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes/{1}"
                             .format(self.freshbooks_account_id, freshbooks_tax_id)).json()
        tax = res.get('response').get('result').get('tax')
        return tax

    def get_freshbooks_taxes(self):
        page = 1
        taxes_arr = []
        while True:
            print("get_freshbooks_taxes::", page)
            print("get_freshbooks_taes::", self.freshbooks_account_id, page)
            res = self.freshbooks_session.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes?page={1}".format(
                self.freshbooks_account_id, page
            )).json()
            max_pages = res.get('response')\
                .get('result')\
                .get('pages')

            curr_page = res.get('response')\
                .get('result')\
                .get('page')

            taxes = res.get('response')\
                .get('result')\
                .get('taxes')

            for tax in taxes:
                taxes_arr.append(tax)
            if curr_page == max_pages:
                break
            else:
                page += 1
        print("get_freshbooks_taxes::", taxes_arr)
        return taxes_arr

    def get_freshbooks_client(self, freshbooks_client_id):
        res = self.freshbooks_session.get("https://api.freshbooks.com/accounting/account/{0}/users/clients/{1}".format(
            self.freshbooks_account_id, freshbooks_client_id)).json()
        #  print(res)
        return res

    def get_freshbooks_clients(self):
        page = 1
        client_arr = []
        while True:
            res = self.freshbooks_session.get(
                "https://api.freshbooks.com/accounting/account/{0}/users/clients?page={1}".format(self.freshbooks_account_id, page)).json()
            
            max_pages = res.get('response')\
                .get('result')\
                .get('pages')

            curr_page = res.get('response')\
                .get('result')\
                .get('page')

            clients = res.get('response')\
                .get('result')\
                .get('clients')

            for client in clients:
                client_arr.append(client)
            if curr_page == max_pages:
                break
            else:
                page += 1
        return client_arr

    def update_freshbooks_clients(self):
        page = 1
        client_arr = []
        while True:
            res = self.freshbooks_session.get(
                "https://api.freshbooks.com/accounting/account/{0}/users/clients?page={1}".format(self.freshbooks_account_id, page)).json()
            max_pages = res.get('response')\
                .get('result')\
                .get('pages')

            curr_page = res.get('response')\
                .get('result')\
                .get('page')

            clients = res.get('response')\
                .get('result')\
                .get('clients')

            for client in clients:
                client_arr.append(client)
            if curr_page == max_pages:
                break
            else:
                page += 1

        for client in client_arr:
            client_id = str(client.get('id'))
            if client.get('organization', ''):
                client_name = client.get('organization', '')
            else:
                client_name = client.get('fname', '') + ' ' + client.get('lname', '')
            client_address = client.get('p_street')
            client_postal_code = client.get('p_code')
            client_country = client.get('p_country')
            client_accounting_systemid = client.get('accounting_systemid')

            client_queryset = Customer.objects.filter(
                freshbooks_client_id=client_id, freshbooks_account_id=client_accounting_systemid
            )
            if client_queryset.count() > 0:
                update_client = client_queryset.get()
                if update_client.freshbooks_client_id == client_id:
                    print(client_name, client_address, client_postal_code, client_country)
                    update_client.name = client_name
                    update_client.address = client_address
                    update_client.postal_code = client_postal_code
                    update_client.country = client_country
                    update_client.save()

    def get_freshbooks_products(self):
        page = 1
        item_arr = []
        while True:
            print(page)
            res = self.freshbooks_session.get(
                "https://api.freshbooks.com/accounting/account/{0}/items/items?page={1}".format(self.freshbooks_account_id, page)).json()
            print(res)
            max_pages = res.get('response')\
                .get('result')\
                .get('pages')

            curr_page = res.get('response')\
                .get('result')\
                .get('page')

            items = res.get('response')\
                .get('result')\
                .get('items')

            for item in items:
                item_arr.append(item)
            if curr_page == max_pages:
                break
            else:
                page += 1
        return item_arr

    def freshbooks_product_detail(self, freshbooks_item_id):
        print("frehsbooks_product_detail::", self.freshbooks_session)
        res = self.freshbooks_session.get("https://api.freshbooks.com/accounting/account/{0}/items/items/{1}".format(
            self.freshbooks_account_id, freshbooks_item_id)).json()
        print(res)
        return res

    def update_freshbooks_products(self):
        page = 1
        item_arr = []
        while True:
            res = self.freshbooks_session.get(
                "https://api.freshbooks.com/accounting/account/{0}/items/items?page={1}".format(self.freshbooks_account_id, page)).json()
            max_pages = res.get('response')\
                .get('result')\
                .get('pages')

            curr_page = res.get('response')\
                .get('result')\
                .get('page')

            items = res.get('response')\
                .get('result')\
                .get('items')

            for item in items:
                item_arr.append(item)
            if curr_page == max_pages:
                break
            else:
                page += 1
        return item_arr