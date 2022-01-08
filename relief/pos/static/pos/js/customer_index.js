const draggable = window['vuedraggable'];
const origin = location.origin;


var UpdateInvoiceModal = Vue.component('UpdateInvoiceModal', {
  data: function () {
      return {
        customer_orderitems: [],
        selected_orderitems: [],
        invoice_number: null,
        po_number: null,
        discount: 0,
        discount_description: null,
        highlight_index: 0,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="update-invoice-modal" v-bind:class="{ 'active': opened }" v-if="selected_invoice">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container" id="invoice-update-modal-window">
        <div class="modal-header h6">
        <div class="modal-title h5">Update {{ selected_invoice.customer_name }} Invoice</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body create-update-invoice-modal-body columns">
          <div class="column col-6 invoice-modal-body-left">
  	        <div class="invoice-form">
  	            <!-- form input control -->
  	            <div class="form-group">
  	              <label class="form-label" for="update-date">Create Date</label>
                  <input class="form-input" id="update-date" type="date" v-model="selected_invoice.date_created" readonly>
  	            </div>
  	            <div class="form-group">
  	              <label class="form-label" for="po-number">PO Number</label>
  	              <input class="form-input" type="text" id="po-number" v-model="po_number">
  	            </div>
  	            <div class="form-group">
  	              <label class="form-label" for="invoice-number">Invoice Number</label>
  	              <input class="form-input" type="text" id="invoice-number" v-model="invoice_number">
  	            </div>
  	        </div>
            <div class="invoice-form">
              <div class="form-group">
                <label class="form-label" for="discount-desc">Discount Description</label>
                <input class="form-input" type="text" id="discount-desc" v-model="discount_description">
              </div>
              <div class="form-group">
                <label class="form-label" for="discount">Discount (Credit Note)</label>
                <input class="form-input" type="text" id="discount" v-model="discount">
              </div>
            </div>
  	        <div class="invoice-create-update-table">
  		        <table class="table">
  		          <thead>
  		            <tr>
  		              <th>Date</th>
  		              <th>Item Name</th>
  		              <th>Driver Quantity</th>
  		              <th>Unit Price</th>
  		              <th>P/O</th>
  		              <th>D/O</th>
  		            </tr>
  		          </thead>
  		          <tbody>
  		            <tr v-for="(orderitem, index) in customer_orderitems" 
                  :class="{ highlight: highlight_index === index }"
                  :key="orderitem.id"
                  v-on:keyup="nextItem">
  		              <td>
  		                <label class="form-checkbox">
  		                  <input type="checkbox" v-bind:value="orderitem.id" v-model="selected_orderitems">
  		                  <i class="form-icon"></i> {{ orderitem.date }}
  		                </label>
  		              </td>
  		              <td>{{ orderitem.product_name }}</td>
  		              <td>{{ orderitem.driver_quantity }}</td>
  		              <td>{{ orderitem.unit_price }}</td>
  		              <td>{{ orderitem.note }}</td>
  		              <td>{{ orderitem.do_number }}</td>
  		            </tr>
  		          </tbody>
  		        </table>
  		      </div>
          </div>
          <div class="column col-6 invoice-modal-body-right">
            <img class="img-responsive do-image" v-if="customer_orderitems[highlight_index]" :src="customer_orderitems[highlight_index].do_image" />
          </div>
        </div>
        <div class="modal-footer columns">
          <div class="divider"></div>
          <div class="column col-6 col-mr-auto">
            <span v-if="!different_price_for_product" class="text-error">
              Unit price for product must be consistent throughout the invoice
            </span>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a id="customer-update-submit-button"
             v-bind:class="{ disabled: !different_price_for_product }"
             href="#save"
             class="btn btn-primary" v-on:click.prevent="updateInvoice">Update</a>
          </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'selected_invoice'],
   components: {},
   computed: {
    different_price_for_product: function() {
      let price_map = {}
      for (let i = 0; i < this.customer_orderitems.length; i++){
        let orderitem = this.customer_orderitems[i];
        if (this.selected_orderitems.indexOf(orderitem.id) > -1){
          if (!price_map[orderitem.product_name]){
            price_map[orderitem.product_name] = orderitem.unit_price
          }
          if (price_map[orderitem.product_name] != orderitem.unit_price){
            return false
          }
        }
      }
      return true
    }
   },
   watch: {
     opened: function(val){
       if (val) {
         console.log("opened is true");
         getInvoice(this.selected_invoice.id)
         .then(res => res.json())
         .then(res => {
           console.log(res)
          this.selected_orderitems =  res.orderitem_set.map(oi => oi.id)
          this.customer_orderitems = res.orderitem_set
          this.invoice_number =  res.invoice_number
          this.po_number =  res.po_number  
          this.discount =  res.minus
          this.discount_description =  res.discount_description 
         })
         .then(() => {
          orderitemFilter(null, null, [this.selected_invoice.customer_pk])
            .then(res => res.json())
            .then(res => {
              res.forEach(oi => this.customer_orderitems.push(oi))
            })
         })
         document.addEventListener("keyup", this.nextItem)
       }

       if (!val) {
        document.removeEventListener("keyup", this.nextItem);
       }
       this.highlight_index = 0;
     },
   },
   methods: {
       nextItem: function() {
          if (event.keyCode === 38 && this.highlight_index > 0) {
            this.highlight_index--
          } else if (event.keyCode === 40 && this.highlight_index < this.customer_orderitems.length-1) {
            this.highlight_index++
          }
       },
       close: function(event){
           console.log("update customer modal close");
           this.resetInputs();
           this.$emit('show-update-invoice');
       },
       updateInvoice: function(event){
        console.log('creating invoice')
        const data = {
          'orderitems_id': this.selected_orderitems,
          'invoice_number': this.invoice_number,
          'po_number': this.po_number,
          'discount': this.discount,
          'discount_description': this.discount_description
        }
        updateInvoice(data, this.selected_invoice.id)
        .then(res => res.json())
        .then(() => this.resetInputs());
      },
      resetInputs: function(event) {
        console.log('reset inputs')
        this.selected_orderitems = [];
        this.customer_orderitems = [];
        this.invoice_number = null;
        this.po_number = null;
        this.discount = 0;
        this.discount_description = null;
      }
  }
})


var ProductDetailModal = Vue.component('ProductDetailModal', {
  data: function () {
      return {
        freshbooks_item_id: null,
        freshbooks_products: [],
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" v-if="product" id="detail-product-modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container product-detail-modal-window">
        <div class="modal-header h6" v-if="product">{{ product.name }}</div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Name: {{ product.name }}</label>
            <label class="form-label">Freshbooks Name</label>
            <select class="form-select" v-model="freshbooks_item_id">
              <option :value="null"></option>
              <option v-for="product in freshbooks_products" :value="product.itemid">{{ product.name }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a href="#" class="btn btn-primary" v-on:click.prevent="linkProduct">Submit</a>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'product'],
   components: {},
   watch: {
       opened: function(val){
          if (val) {
           console.log("customer details modal");
           this.freshbooks_item_id = this.product.freshbooks_item_id
           getFreshbooksProducts()
           .then(res => res.json())
           .then(res => this.freshbooks_products = res);
           console.log(this.freshbooks_products)
          }
       }
   },
   methods: {
       close: function(event){
           console.log("show product modal close");
           this.$emit('show-product-detail-modal');
           this.freshbooks_item_id = null;
       },
       linkProduct: function(event) {
        const data = {
          'product_id': this.product.id,
          'freshbooks_item_id': this.freshbooks_item_id,
        }
        linkProduct(data).then(res => res.json()).then(() => this.close())
       }
   }
})


var ImportProductModal = Vue.component('ImportProductModal', {
  data: function () {
      return {
        freshbooks_product_list: [],
        import_product_list: [],
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
      <div class="modal-container">
        <div class="modal-header">
          <div class="modal-title h5">Import Freshbooks Products</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body">
          <div class="content form-group">
            <!-- content here -->
            <label class="form-checkbox" v-for="product in freshbooks_product_list">
              <input type="checkbox" :value="product.id" v-model="import_product_list">
              <i class="form-icon"></i> {{ product.name }}
            </label>
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <div class="action-container">
              <a class="btn btn-link my-2" v-on:click.prevent="close">Cancel</a>
              <a class="btn btn-primary" v-on:click.prevent="importProduct">Import</a>
            </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
            this.loadFreshbooksProducts();
           }
       },
   },
   methods: {
    close: function(event){
      this.$emit('show-import-product-modal');
    },
    importProduct: function(event){
      console.log('import product')
      console.log(this.import_product_list)
      const data = {'freshbooks_id_list': this.import_product_list}
      importProduct(data)
      .then(res => res.json())
      .then(() => this.resetFields())
      .then(() => this.close())
    },
    loadFreshbooksProducts: function(event) {
      getFreshbooksProductsImport().then(res => res.json()).then(res => this.freshbooks_product_list = res)
    },
    resetFields: function(){
      this.freshbooks_product_list = [];
      this.import_product_list = [];
    }
   }
})

var DownloadRangeModal = Vue.component('DownloadRangeModal', {
  data: function () {
      return {
        from: null,
        to: null,
        download_promises: [],
        downloaded_pdfs: [],
      }
  },

  template:`
  <!-- Download Range Modal -->
    <div class="modal" v-bind:class="{ 'active': opened }">
      <div class="modal-container">
        <div class="modal-header">
          <div class="modal-title h5">Download Invoice Range</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body">
          <div class="content form-group">
            <!-- content here -->
            <!-- form input control -->
            <div class="form-group">
              <label class="form-label" for="from-range">From</label>
              <input class="form-input" type="number" id="from-range" v-model="from">
            </div>
            <!-- form input control -->
            <div class="form-group">
              <label class="form-label" for="to-range">To</label>
              <input class="form-input" type="number" id="to-range" v-model="to">
            </div>
            <div class="form-group" v-for="download in downloaded_pdfs">
              <label class="form-label"><i class="icon icon-check mx-2"></i>{{ download }}</label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <div class="action-container">
              <a class="btn btn-link my-2" v-on:click.prevent="close">Cancel</a>
              <a class="btn btn-primary" v-on:click.prevent="download">Download</a>
            </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
           }
       },
   },
   methods: {
      close: function(event){
        this.$emit('show-download-range-modal');
        this.resetFields();
       },
       download: function(event){
        console.log('download invoice range')
        for (let i = this.from; i <= this.to ; i++){
          let pdf_promise = downloadInvoicePDF(i)
          this.download_promises.push(pdf_promise)
        }

        // set a delay before executing each download to prevent being rate limited.
        // Promise.all / Promise.allSettled will execute all promises at once
        // and cause rate limiting for a large range of pdfs
        let timeout_ms = 0;
        this.download_promises.forEach((promise) => {
          timeout_ms += 2000;
          setTimeout(function() {
            promise.then(async res => {
              const filename = res.headers.get("content-disposition").split('"')[1];
              const blob = await res.blob()
              return { blob, filename }
            }).then(res => {
                // to add to zip file next time
                var a = document.createElement("a");
                a.style = "display: none";
                a.download = res.filename;
                var url = window.URL.createObjectURL(res.blob);
                a.href = url;
                document.body.appendChild(a);
                a.click();
                return res.filename;
            }).then(filename => {
              this.downloaded_pdfs.push(filename);
            })
          }.bind(this), timeout_ms)
        })
       },
       resetFields: function(event) {
        this.from = null;
        this.to = null;
        this.download_promises = [];
        this.downloaded_pdfs = [];
       }
   }
})


var ImportClientModal = Vue.component('ImportClientModal', {
  data: function () {
      return {
        import_client_list: [],
        freshbooks_client_list: [],
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
      <div class="modal-container">
        <div class="modal-header">
          <div class="modal-title h5">Import Freshbooks Clients</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body">
          <div class="content form-group">
            <!-- content here -->
            <label class="form-checkbox" v-for="client in freshbooks_client_list">
              <input type="checkbox" :value="client.id" v-model="import_client_list">
              <i class="form-icon"></i> {{ client.organization }}
            </label>
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <div class="action-container">
              <a class="btn btn-link my-2" v-on:click.prevent="close">Cancel</a>
              <a class="btn btn-primary" v-on:click.prevent="importClient">Import</a>
            </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
            this.loadFreshbooksClients()
           }
       },
   },
   methods: {
      close: function(event){
        this.$emit('show-import-client-modal');
        this.resetFields();
       },
       importClient: function(event){
        console.log('import client')
        const data = {'freshbooks_id_list': this.import_client_list}
        importClient(data)
        .then(res => res.json())
        .then(() => this.resetFields())
        .then(() => this.close())
       },
       loadFreshbooksClients: function(event) {
        getFreshbooksClientsImport().then(res => res.json()).then(res => this.freshbooks_client_list = res)
       },
       resetFields: function(){
        this.freshbooks_client_list = [];
        this.import_client_list = [];
       }
   }
})

// hard delete / unlink modal
var InvoiceDeleteModal = Vue.component('InvoiceDeleteModal', {
  data: function () {
      return {
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div v-if="invoice" class="modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header">
          <div class="modal-title h5">Delete {{ invoice.customer_name }} Invoice</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body">
          <div class="content">
            <!-- content here -->
            Delete {{ invoice.invoice_number }}?
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <div class="delete-container">
              <a class="btn btn-link my-2 float-left bg-error" v-on:click.prevent="deleteInvoice(invoice.id)">Hard Delete</a>
            </div>
            <div class="action-container">
              <a class="btn btn-link my-2" v-on:click.prevent="close">Cancel</a>
              <a class="btn btn-primary" v-on:click.prevent="unlinkInvoice(invoice.id)">Unlink</a>
            </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'invoice'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
           }
       },
   },
   methods: {
      close: function(event){
        this.$emit('show-invoice-delete-modal');
       },
      unlinkInvoice: function(invoiceId){
        console.log('unlink customer invoice');
        const data = {'invoice_id': invoiceId}
        unlinkInvoice(data).then(res => res.json()).then(() => this.close())
      },
      deleteInvoice: function(invoiceId) {
        console.log('hard delete invoice');
        deleteInvoice(invoiceId).then(res => res.json()).then(() => this.close())
      }
   }
})

var EditQuoteModal = Vue.component('EditQuoteModal', {
  data: function () {
      return {
          edit_quote_price: null,
          edit_freshbooks_text_1: null,
          edit_archived: null,
          tax_list: [],
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div v-if="quote" class="modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header">
          <div class="modal-title h5">Create Quote</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Customer Name: {{ quote.customer_name }}</label>
            </div>
            <div class="form-group">
              <label class="form-label">Item Name: {{ quote.product_name }}</label>
            </div>
            <div class="form-group">
              <label class="form-label">Quote Price</label>
              <input class="form-input" v-model="edit_quote_price">
            </div>
            <div class="form-group">
              <label class="form-label">Freshbooks Tax 1</label>
              <select class="form-select column col-12 my-1" v-model="edit_freshbooks_text_1">
                  <option :value="null"></option>
                  <option v-for="t in tax_list" :value="t.id">{{ t.name }} - Tax Amount: {{ t.amount }}%</option>
              </select>
            </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <div class="delete-container">
              <a class="btn btn-link btn-sm my-2 float-left" 
              v-if="edit_archived"
              v-on:click.prevent="toggleArchive">Restore</a>
              <a class="btn btn-error float-left"
              v-if="!edit_archived"
              v-on:click.prevent="toggleArchive">Archive</a>
            </div>
            <div class="action-container">
              <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
              <a class="btn btn-primary" v-on:click="saveCustomerQuote">Save</a>
            </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'quote'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               this.getAllTaxes();
               this.edit_quote_price = this.quote.quote_price;
               this.edit_freshbooks_text_1 = this.quote.freshbooks_tax_1;
               this.edit_archived = this.quote.archived;
           }
       },
   },
   methods: {
       close: function(event){
           console.log("create customer modal close");
           this.edit_quote_price = null;
           this.edit_freshbooks_text_1 = null;
           this.$emit('show-quote-edit-modal');
       },
       toggleArchive: function () {
        console.log('toggle archive');
        this.edit_archived = !this.edit_archived;
        this.saveCustomerQuote();
       },
       saveCustomerQuote: function(){
           console.log('save customer quote');
           const data = {
            'id': this.quote.id,
            'quote_price': this.edit_quote_price,
            'freshbooks_tax_1': this.edit_freshbooks_text_1,
            'archived': this.edit_archived
          }
           updateQuote(data)
           .then(res => res.json())
           .then(() => this.close())
           .catch(e => console.log(e));

       },
       getAllTaxes: function(){
        getAllTaxes().then(res => res.json()).then(res => this.tax_list = res);
       }
   }
})


var OrderItemEditModal = Vue.component('OrderItemEditModal', {
  data: function () {
      return {
        edit_quantity: null,
        edit_driver_quantity: null,
        note: null,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="edit-orderitem-modal" v-if="orderitem" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container orderitem-edit-modal-window">
        <div class="modal-header h6">Edit {{ orderitem.customer_name }}'s OrderItem</div>
        <div class="modal-body">
          <div class="form-group">
            <!-- form input control -->
            <div class="form-group">
              <label class="form-label">Customer: {{ orderitem.customer_name }}</label>
              <label class="form-label">Date: {{ orderitem.date }}</label>
              <label class="form-label">D/O: {{ orderitem.do_number }}</label>
            </div>
            <div class="form-group">
              <label class="form-label" for="quantity">Quantity</label>
              <input class="form-input" type="number" id="quantity" v-model="edit_quantity">
            </div>
            <div class="form-group">
              <label class="form-label" for="driver-quantity">Driver Quantity</label>
              <input class="form-input" type="number" id="driver-quantity" v-model="edit_driver_quantity">
            </div>
            <div class="form-group">
              <label class="form-label" for="note">P/O</label>
              <input class="form-input" type="text" id="note" v-model="note">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <div class="delete-container">
              <button class="btn btn-error float-left" v-on:click.prevent="deleteOrderItem(orderitem.id)">Delete</button>
          </div>
          <div class="action-container">
              <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
              <a href="#" class="btn btn-primary" v-on:click.prevent="saveOrderItem">Submit</a>
          </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'orderitem'],
   components: {},
   watch: {
       opened: function(val){
          if (val) {
            this.edit_quantity = this.orderitem.quantity;
            this.edit_driver_quantity = this.orderitem.driver_quantity;
            this.note = this.orderitem.note;
          }
       }
   },
   methods: {
       close: function(event){
           console.log("show orderitem edit modal close");
           this.edit_quantity = null;
           this.edit_driver_quantity = null;
           this.note = null;
           this.$emit('show-orderitem-edit-modal');
       },
       saveOrderItem: function() {
        console.log('save orderitem')
        const data = {
          'id': this.orderitem.id,
          'quantity': this.edit_quantity,
          'driver_quantity': this.edit_driver_quantity,
          'note': this.note,
        }
        updateOrderItem(data)
        .then(res => res.json())
        .then(() => this.close())
       },
       deleteOrderItem: function(orderitemId) {
        console.log('delete orderitem')
        deleteOrderItem(orderitemId).then(() => this.close())
       }
   }
})


var CustomerDetailModal = Vue.component('CustomerDetailModal', {
  data: function () {
      return {
        freshbooks_client_id: null,
        freshbooks_clients: [],
        invoice_pivot: null,
        gst: null,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" v-if="customer" id="detail-customer-modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header h6" v-if="customer">{{ customer.name }}</div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Name: {{ customer.name }}</label>
            <label class="form-label">Address: {{ customer.address }}</label>
            <label class="form-label">Postal code: {{ customer.postal_code }}</label>
            <div class="form-group">
              <label class="form-label">GST
                <input class="form-input" type="number" id="gst" placeholder="GST" v-model="gst">
              </label>
            </div>
            <div class="form-group">
              <label class="form-label form-inline">Prefix
                <input class="form-input" placeholder="Prefix" v-model="dowlnoad_prefix">
              </label>
              <label class="form-label form-inline">Suffix
                <input class="form-input" placeholder="Suffix" v-model="download_suffix">
              </label>
            </div>
            <div class="form-group">
            <label class="form-checkbox my-2 form-inline">
              <input type="checkbox" v-model="to_fax">
              <i class="form-icon"></i> Fax
            </label>
            <label class="form-checkbox my-2 form-inline">
              <input type="checkbox" v-model="to_print">
              <i class="form-icon"></i> Print
            </label>
            <label class="form-checkbox my-2 form-inline">
              <input type="checkbox" v-model="to_email">
              <i class="form-icon"></i> Email
            </label>
            <label class="form-checkbox my-2 form-inline">
              <input type="checkbox" v-model="to_whatsapp">
              <i class="form-icon"></i> Whatsapp
            </label>
            </div>
            <label class="form-label">Freshbooks Name</label>
            <select class="form-select" v-model="freshbooks_client_id">
              <option :value="null"></option>
              <option v-for="client in freshbooks_clients" :value="client.id">{{ client.organization }}</option>
            </select>
            <label class="form-checkbox my-2">
              <input type="checkbox" v-model="invoice_pivot">
              <i class="form-icon"></i> Pivot Invoice
            </label>
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a href="#" class="btn btn-primary" v-on:click.prevent="linkClient">Submit</a>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'customer'],
   components: {},
   watch: {
       opened: function(val){
          if (val) {
           console.log("customer details modal");
           this.freshbooks_client_id = this.customer.freshbooks_client_id;
           this.invoice_pivot = this.customer.pivot_invoice;
           this.gst = this.customer.gst
           this.download_prefix = this.customer.download_prefix;
           this.download_suffix = this.customer.download_suffix;
           this.to_fax = this.customer.to_fax;
           this.to_email = this.customer.to_email;
           this.to_print = this.customer.to_print;
           this.to_whatsapp = this.customer.to_whatsapp;
           getFreshbooksClients()
           .then(res => res.json())
           .then(res => this.freshbooks_clients = res);
           console.log(this.freshbooks_clients)
          }
       }
   },
   methods: {
       close: function(event){
           console.log("show customer modal close");
           this.$emit('show-customer-detail-modal');
           this.freshbooks_account_id = null;
           this.freshbooks_client_id = null;
           this.gst = null;
           this.download_prefix = null;
           this.download_suffix = null;
           this.to_fax = null;
           this.to_email = null;
           this.to_print = null;
       },
       linkClient: function(event) {
        const data = {
          'customer_id': this.customer.id,
          'freshbooks_client_id': this.freshbooks_client_id,
          'pivot_invoice': this.invoice_pivot,
          'gst': this.gst,
          'download_prefix': this.download_prefix,
          'download_suffix': this.download_suffix,
          'to_fax': this.to_fax,
          'to_email': this.to_email,
          'to_print': this.to_print,
          'to_whatsapp': this.to_whatsapp,
        }
        linkClient(data).then(res => res.json()).then(() => this.close())
       }
   }
})

var CreateInvoiceModal = Vue.component('CreateInvoiceModal', {
  data: function () {
      return {
        customer_orderitems: [],
        selected_orderitems: [],
        create_date: null,
        invoice_number: null,
        po_number: null,
        discount: 0,
        discount_description: null,
        select_all: false,
        highlight_index: 0,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="create-invoice-modal" v-bind:class="{ 'active': opened }" v-if="selected_customer">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container" id="invoice-create-modal-window">
        <div class="modal-header h6">
        <div class="modal-title h5">Create {{ selected_customer.name }} Invoice</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body create-update-invoice-modal-body columns">
          <div class="column col-6 invoice-modal-body-left">
  	        <div class="invoice-form">
  		        <!-- form input control -->
  		        <div class="form-group">
  		          <label class="form-label" for="create-date">Create Date</label>
  		          <input class="form-input" type="date" id="create-date" v-model="create_date">
  		        </div>
  		        <div class="form-group">
  		          <label class="form-label" for="po-number">PO Number</label>
  		          <input class="form-input" type="text" id="po-number" v-model="po_number">
  		        </div>
  		        <div class="form-group">
  		          <label class="form-label" for="invoice-number">Invoice Number</label>
  		          <input class="form-input" type="text" id="invoice-number" v-model="invoice_number">
  		        </div>
            </div>
            <div class="invoice-form">
              <div class="form-group">
                <label class="form-label" for="discount-desc">Discount Description</label>
                <input class="form-input" type="text" id="discount-desc" v-model="discount_description">
              </div>
              <div class="form-group">
                <label class="form-label" for="discount">Discount (Credit Note)</label>
                <input class="form-input" type="text" id="discount" v-model="discount">
              </div>
            </div>
    		    <div class="invoice-create-update-table">
    		        <table class="table">
    		          <thead>
    		            <tr>
    		              <th>
    		                <label class="form-checkbox">
    		                  <input type="checkbox" v-model="select_all"><i class="form-icon"></i> Date
    		                </label>
    		              </th>
    		              <th>Item Name</th>
    		              <th>Driver Quantity</th>
    		              <th>Unit Price</th>
    		              <th>P/O</th>
    		              <th>D/O</th>
    		            </tr>
    		          </thead>
    		          <tbody>
    		            <tr v-for="(orderitem, index) in customer_orderitems" 
                    :class="{ highlight: highlight_index === index }"
                    :key="orderitem.id"
                    v-on:keyup="nextItem">
    		              <td>
    		                <label class="form-checkbox">
    		                  <input type="checkbox" v-bind:value="orderitem" v-model="selected_orderitems">
    		                  <i class="form-icon"></i> {{ orderitem.date }}
    		                </label>
    		              </td>
    		              <td>{{ orderitem.product_name }}</td>
    		              <td>{{ orderitem.driver_quantity }}</td>
    		              <td>{{ orderitem.unit_price }}</td>
    		              <td>{{ orderitem.note }}</td>
    		              <td>{{ orderitem.do_number }}</td>
    		            </tr>
    		          </tbody>
    		        </table>
            </div>
  		    </div>
          <div class="column col-6 invoice-modal-body-right">
            <img class="img-responsive do-image" v-if="customer_orderitems[highlight_index]" :src="customer_orderitems[highlight_index].do_image" />
          </div>
        </div>
        <div class="modal-footer columns">
            <div class="divider"></div>
            <div class="column col-6 col-mr-auto">
              <span v-if="!different_price_for_product" class="text-error">
                Unit price for product must be consistent throughout the invoice
              </span>
              <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
              <a 
                id="customer-create-submit-button"
                href="#save"
                class="btn btn-primary" 
                v-bind:class="{ disabled: !different_price_for_product }"
                v-on:click.prevent="createInvoice">Submit</a>
            </div>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'selected_customer', 'orderitems'],
   components: {},
   computed: {
    different_price_for_product: function() {
      let price_map = {}
      for (let i = 0; i < this.selected_orderitems.length; i++){
        let orderitem = this.selected_orderitems[i];
        if (!price_map[orderitem.product_name]){
          price_map[orderitem.product_name] = orderitem.unit_price
        }
        if (price_map[orderitem.product_name] != orderitem.unit_price){
          return false
        }
      }
      return true
    }
   },
   watch: {
     opened: function(val){
       if (val) {
         this.filterOrderItemsByCustomer(this.selected_customer.id)
         document.addEventListener("keyup", this.nextItem);
       }

       if (!val) {
        document.removeEventListener("keyup", this.nextItem);
       }
       this.highlight_index = 0;
     },
     select_all: function(val) {
      if (val){
        console.log("select all");
        this.selected_orderitems = this.customer_orderitems.map(oi => oi)
      } else {
        this.selected_orderitems = [];
      }
     }
   },
   methods: {
      nextItem: function() {
          if (event.keyCode === 38 && this.highlight_index > 0) {
            this.highlight_index--
          } else if (event.keyCode === 40 && this.highlight_index < this.customer_orderitems.length-1) {
            this.highlight_index++
          }
       },
       close: function(event){
           console.log("create customer modal close");
           this.resetInputs();
           this.$emit('show-create-invoice');
       },
       filterOrderItemsByCustomer: function(client_id){
        return orderitemFilter(null, null, [client_id])
                .then(res => res.json())
                .then(res => this.customer_orderitems = res)
       },
       createInvoice: function(event){
        console.log('creating invoice')
        const data = {
          'customer_id': this.selected_customer.id,
          'create_date': this.create_date,
          'orderitems_id': this.selected_orderitems.map(orderitem => orderitem.id),
          'invoice_number': this.invoice_number,
          'po_number': this.po_number,
          'discount': this.discount,
          'discount_description': this.discount_description
        }
        createInvoice(data)
        .then(res => res.json())
        .then(() => this.resetInputs())
        .then(() => this.filterOrderItemsByCustomer(this.selected_customer.id));
      },
      resetInputs: function(event) {
        console.log('reset inputs')
        this.selected_orderitems = [];
        this.customer_orderitems = [];
        this.create_date = null;
        this.invoice_number = null;
        this.po_number = null;
        this.discount = 0;
        this.discount_description = null;
        this.select_all = false;
      }
  }
})


var CreateTripModal = Vue.component('CreateTripModal', {
  data: function () {
      return {
          notes: null,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="create-trip-modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header h6">Create Trip</div>
        <div class="modal-body">
            <!-- form input control -->
            <div class="form-group">
            <label class="form-label" for="note">Note</label>
            <input class="form-input" type="text" id="note" placeholder="Enter Note" v-model="notes">
            </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a id="trip-create-submit-button"
             href="#save"
             class="btn btn-primary" v-on:click.prevent="saveTrip">Create</a>
        </div>
      </div>
    </div>
   `,
   props: ['opened'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       }
   },
   methods: {
       close: function(event){
           console.log("create trip modal close");
           this.notes = null;
           this.$emit('show-create-trip-modal');
       },
       saveTrip: function(event) {
           console.log("save trip");
           let data = {"notes": this.notes}
           createTrip(data).then(res => res.json()).then(() => this.close());
       }
   }
})


var CreateGroupModal = Vue.component('CreateGroupModal', {
  data: function () {
      return {
          name: null,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="create-customer-modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header h6">Create Group</div>
        <div class="modal-body">
            <!-- form input control -->
            <div class="form-group">
            <label class="form-label" for="name">Name</label>
            <input class="form-input" type="text" id="name" placeholder="Name" v-model="name">
            </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a id="customer-create-submit-button"
             href="#save"
             class="btn btn-primary" v-on:click.prevent="saveGroup">Submit</a>
        </div>
      </div>
    </div>
   `,
   props: ['opened'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       }
   },
   methods: {
       close: function(event){
           console.log("create customer modal close");
           this.name = null;
           this.$emit('show-create-group-modal');
       },
       saveGroup: function(event) {
           console.log("save group");
           let data = {"name": this.name}
           createGroup(data).then(res => res.json()).then(() => this.close());
       }
   }
})

var EditGroupModal = Vue.component('EditGroupModal', {
  data: function () {
      return {
        filtered_client_list: [],
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="edit-group-modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close" v-on:click="close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header h6" v-if="group">Edit {{ group.name }} Group</div>
        <div class="modal-body">
          <!-- form checkbox control -->
          <div class="form-group">
            <label class="form-checkbox" v-for="client in clients" :key="client.id">
              <input type="checkbox" v-model="filtered_client_list" :value="client.id">
              <i class="form-icon"></i> {{ client.name }}
            </label>
          </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a href="#save" class="btn btn-primary" v-on:click.prevent="saveGrouping">Submit</a>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'group', 'clients'],
   components: {},
   computed: {
   },
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.filtered_client_list = this.filterCustomersByGroup(this.group.name).map(client => client.id)
           }
       },
   },
   methods: {
       close: function(event){
           console.log("create customer modal close");
           this.name = null;
           this.$emit('show-edit-group-modal')
       },
       saveGrouping: function(event) {
           console.log("save group");
           let data = {"group_id": this.group.id, "arrangement": this.filtered_client_list}
           updateGrouping(data)
             .then(res => res.json())
             .then(() => this.close());
       },
       filterCustomersByGroup: function(group_name){
        console.log('get customers in group')
        return this.clients.filter(client => client.group.indexOf(this.group.name) >= 0)
       },
   }
})


var CreateQuoteModal = Vue.component('CreateQuoteModal', {
  data: function () {
      return {
          product_list: [],
          customer_list: [],
          tax_list: [],
          selected_customer_id: null,
          selected_product_id: null,
          quote_price: null,
          selected_product: null,
          selected_tax_1: null,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header">
          <div class="modal-title h5">Create Quote</div>
          <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
        </div>
        <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="quote-customer-name">Customer Name</label>
              <select class="form-select column col-12 my-1" id="quote-customer-name" v-model="selected_customer_id">
                  <option v-for="c in customer_list" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="quote-item-name">Item Name</label>
              <select class="form-select column col-12 my-1" id="quote-item-name" v-model="selected_product_id">
                  <option v-for="p in product_list" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="quote-price">Quote Price</label>
              <input class="form-input" id="quote-price" v-model.number="quote_price">
            </div>
            <div class="form-group">
              <label class="form-label" for="tax-1-id">Tax 1</label>
              <select class="form-select column col-12 my-1" id="tax-1-id" v-model="selected_tax_1">
                  <option v-for="t in tax_list" :value="t.id">{{ t.name }} - Tax Amount: {{ t.amount }}%</option>
              </select>
            </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
            <a class="btn btn-primary" v-on:click="saveCustomerQuote" >Save</a>
        </div>
      </div>
    </div>
   `,
   props: ['opened', 'clients'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               this.getProducts();
               this.getCustomers();
               this.getAllTaxes();
           }
       },
       selected_product_id: function(newVal, oldVal){
        if (newVal){
          this.getProductDetail(newVal);
        }
       },
       selected_product: function(newVal, oldVal){
        if (newVal){
          this.quote_price = newVal.response.result.item.unit_cost.amount;
        } else {
          this.quote_price = null;
        }
       }
   },
   methods: {
       close: function(event){
           console.log("create customer modal close");
           this.selected_products = [];
           this.$emit('show-quote');
       },
       saveCustomerQuote: function(){
           console.log('save customer quote');
           let data = {
            'customer': this.selected_customer_id, 
            'product': this.selected_product_id,
            'quote_price': this.quote_price,
            'freshbooks_tax_1': this.selected_tax_1
           };
           createQuote(data)
           .then(res => res.json())
           .then(() => this.close())
           .catch(e => console.log(e));

       },
       getProducts: function(){
        getAllProducts().then(res => res.json()).then(res => this.product_list = res);
       },
       getCustomers: function() {
        getAllCustomers().then(res => res.json()).then(res => this.customer_list = res);
       },
       getProductDetail: function(product_id) {
        getProductDetail(product_id).then(res => res.json()).then(res => this.selected_product = res);
       },
       getAllTaxes: function(){
        getAllTaxes().then(res => res.json()).then(res => this.tax_list = res);
       }
   }
})

var CustomerList = Vue.component('CustomerList', {
  data: function () {
      return {
        currentTab: 'clients',
        show_clients: [],
        showArchivedQuotes: false,
        customerOrderitemCount: {},
        show_client_orderitem_data: [],
      }
  },
  created: function() {
  },
  template:`
    <div class="container">
      <ul class="tab tab-block">
        <li class="tab-item" v-bind:class="{ active: currentTab === 'clients'}">
          <a href="#" v-on:click="currentTab = 'clients'">Clients</a>
        </li>
        <li class="tab-item" v-bind:class="{ active: currentTab === 'items'}">
          <a href="#" v-on:click="currentTab = 'items'">Items</a>
        </li>
        <li class="tab-item" v-bind:class="{ active: currentTab === 'quotes'}">
          <a href="#" v-on:click="currentTab = 'quotes'">Quotes</a>
        </li>
        <li class="tab-item" v-bind:class="{ active: currentTab === 'orderitems'}">
          <a href="#" v-on:click="currentTab = 'orderitems'">Order Items</a>
        </li>
        <li class="tab-item" v-bind:class="{ active: currentTab === 'invoices'}">
          <a href="#" v-on:click="currentTab = 'invoices'">Invoices</a>
        </li>
      </ul>

      <div class="btn-group btn-group-block float-right my-2" v-if="currentTab === 'clients'">
        <button class="btn" v-on:click="$emit('sync-clients')">Sync Clients</button>
        <button class="btn btn-primary" v-on:click="$emit('show-create-group-modal')">Create Group</button>
        <button class="btn btn-primary" v-on:click="$emit('show-import-client-modal')">Import Clients</button>
      </div> 

      <div class="btn-group btn-group-block float-right my-2" v-if="currentTab === 'invoices'">
        <button class="btn" v-on:click="$emit('sync-invoices')">Sync Invoices</button>
        <button class="btn btn-primary" v-on:click="$emit('show-download-range-modal')">Range Download</button>
      </div> 

      <div class="btn-group btn-group-block float-right my-2" v-if="currentTab === 'items'">
        <button class="btn btn-primary" v-on:click="$emit('show-import-product-modal')">Import Items</button>
      </div> 

      <div class="form-group d-inline-flex my-1 action-bar" v-if="currentTab === 'quotes'">
        <div class="flex-1">
          <label class="form-checkbox">
            <input type="checkbox" v-model="showArchivedQuotes">
            <i class="form-icon"></i> Archived
          </label>
        </div>
        <div class="flex-1">
          <button class="btn btn-primary float-right flex-1" v-on:click="$emit('show-quote')">Create Quote</button>
        </div>
      </div>
      <table class="table" v-for="group in groups" v-if="currentTab === 'clients'">
        <thead>
          <tr>
            <th>{{ group.name }}</th>
            <th><button class="btn btn-sm" v-on:click.prevent="$emit('show-edit-group-modal', group)">Edit Group</button></th>
          </tr>
        </thead>
        <tbody v-for="client in filterCustomersByGroup(group.name)" :key="client.id">
          <tr>
            <td>
              <span class="label c-hand" v-on:click.prevent="show_customer_details(client)">{{ client.name }}</span>
              <span v-if="client.freshbooks_client_id" class="label label-secondary">FreshBooks</span>           
            </td>
            <td>
                <button class="btn btn-primary btn-sm badge"
                v-show="customerOrderitemCount[client.name]"
                v-bind:data-badge="customerOrderitemCount[client.name]" 
                v-on:click="showCreateInvoice(client)">Create Invoice</button>
            </td>
          </tr>
        </tbody>
      </table>
      <table class="table" id="items" v-if="currentTab === 'items'">
        <thead>
          <tr>
            <th>Item Name</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>
              <span class="label c-hand" v-on:click.prevent="show_product_details(product)">{{ product.name }}</span>
              <span v-if="product.freshbooks_item_id" class="label label-secondary">FreshBooks</span>
            </td>
          </tr>
        </tbody>
      </table>
      <table class="table table-hover" id="quotes" v-if="currentTab === 'quotes'">
        <thead>
          <tr>
            <th>Client Name</th>
            <th>Item Name</th>
            <th>Quote Price</th>
            <th>Freshbooks Tax 1</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quote in filterQuotesByArchived(showArchivedQuotes)"
           :key="quote.id" 
           class="c-hand"
           v-on:click.prevent="show_quote_edit(quote)">
            <td>{{ quote.customer_name }}</td>
            <td>{{ quote.product_name }}</td>
            <td>{{ quote.quote_price }}</td>
            <td v-if="quote.freshbooks_tax_1">{{ getTax(quote.freshbooks_tax_1).name }}</td>
            <td v-else></td>
          </tr>
        </tbody>
      </table>
      <table class="table table-hover" id="orderitems" v-if="currentTab === 'orderitems'">
        <thead>
          <tr>
            <th>Date</th>
            <th>Client Name</th>
            <th>Item Name</th>
            <th>Unit Price</th>
            <th>Quantity</th>
            <th>Driver Quantity</th>
            <th>P/O</th>
            <th>D/O</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="orderitem in orderitems" 
              v-on:click.prevent="show_orderitem_edit(orderitem)" 
              :key="orderitem.id" 
              class="c-hand">
            <td>{{ orderitem.date }}</td>
            <td>{{ orderitem.customer_name }}</td>
            <td>{{ orderitem.product_name }}</td>
            <td>{{ orderitem.unit_price }}</td>
            <td>{{ orderitem.quantity }}</td>
            <td>{{ orderitem.driver_quantity }}</td>
            <td>{{ orderitem.note }}</td>
            <td>{{ orderitem.do_number }}</td>
          </tr>
        </tbody>
      </table>
      <table class="table" id="invoices" v-if="currentTab === 'invoices'">
        <thead>
          <tr>
            <th>Invoice Number</th>
            <th>Customer Name</th>
            <th>Date Generated</th>
            <th>Total</th>
            <th>PDF</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invoice in invoices" :key="invoice.id" class="c-hand">
            <td>
              <a href="#" v-on:click.prevent="show_invoice_update(invoice)">{{ invoice.invoice_number }}</a>
            </td>
            <td>
              <a href="#" v-on:click.prevent="show_invoice_delete(invoice)">{{ invoice.customer_name }}</a>
            </td>
            <td>
              <a :href="invoice.url">{{ invoice.date_generated }}</a>
            </td>
            <td>{{ invoice.total_incl_gst }}</td>
            <td><a class="btn btn-sm" :href="invoice.download_url">Download</a></td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
   props: ['products', 'clients', 'quotes', 'taxes','groups', 'orderitems', 'invoices'],
   components: {draggable, },
   methods: {
       createQuote: function(event){
        this.$emit('createquote', event)
       },
       showCreateInvoice: function(client){
        this.$emit('show-create-invoice', client)
       },
       filterCustomersByGroup: function(group_name){
        return this.clients.filter(client => client.group.indexOf(group_name) >= 0)
       },
       filterQuotesByArchived: function(archived) {
        return this.quotes.filter(quote => quote.archived === archived)
       },
       getTax: function(tax_id){
        return this.taxes.find(tax => tax.id.toString() === tax_id)
       },
       show_customer_details: function(client) {
        console.log('show customer details');
        this.$emit('show-customer-detail-modal', client);
       },
       show_product_details: function(product) {
        console.log('show product details')
        this.$emit('show-product-detail-modal', product);
       },
       show_orderitem_edit: function(orderitem) {
        this.$emit('show-orderitem-edit-modal', orderitem);
       },
       show_quote_edit: function(quote) {
        this.$emit('show-quote-edit-modal', quote);
       },
       show_invoice_delete: function(invoice){
        this.$emit('show-invoice-delete-modal', invoice);
       },
       show_invoice_update: function(invoice){
        console.log('invoice update event')
        this.$emit('show-update-invoice', invoice);
       }
   },
   watch: {
    orderitems: function(newVal, oldVal){
      this.customerOrderitemCount = {}
      newVal.forEach(oi => {
        if (!this.customerOrderitemCount[oi.customer_name])
          this.customerOrderitemCount[oi.customer_name] = 1
        else
          this.customerOrderitemCount[oi.customer_name] += 1
      })
   }
 },
   computed: {
    dragOptions() {
          return {
            animation: 200,
            group: "description",
            disabled: false,
            ghostClass: "ghost",
            draggable: ".menu-item",
          };
        }
    }
})



var app = new Vue({
  el: '#app',
  data: function () {
      return {
          show_quote_modal: false,
          show_quote_edit_modal: false,
          show_create_group_modal: false,
          show_create_invoice_modal: false,
          show_update_invoice_modal: false,
          show_edit_group_modal: false,
          show_customer_detail_modal: false,
          show_product_detail_modal: false,
          show_orderitem_edit_modal: false,
          show_invoice_delete_modal: false,
          show_import_client_modal: false,
          show_download_range_modal: false,
          show_import_product_modal: false,
          edit_group: null,
          edit_quote: null,
          detail_customer: null,
          detail_product: null,
          edit_orderitem: null,
          delete_invoice: null,
          create_invoice_customer: null,
          update_invoice: null,
          create_invoice_orderitems: [],
          products: [],
          clients: [],
          quotes: [],
          taxes: [],
          groups: [],
          orderitems: [],
          invoices: [],
      }
  },
  created: function() {
    getAllProducts().then(res => res.json()).then(res => this.products = res)
    getAllCustomers().then(res => res.json()).then(res => this.clients = res)
    getAllQuotes().then(res => res.json()).then(res => this.quotes = res)
    getAllOrderitems().then(res => res.json()).then(res => this.orderitems = res)
    getAllTaxes().then(res => res.json()).then(res => this.taxes = res).catch((err) => window.location.href=origin)
    getAllGroups().then(res => res.json()).then(res => this.groups = res)
    getAllInvoices().then(res => res.json()).then(res => this.invoices = res)
  },
  computed: {
    modal_opened: function() {
      let open =  this.show_quote_modal ||
                  this.show_quote_edit_modal ||
                  this.show_create_group_modal ||
                  this.show_create_invoice_modal ||
                  this.show_update_invoice_modal ||
                  this.show_edit_group_modal ||
                  this.show_customer_detail_modal ||
                  this.show_product_detail_modal ||
                  this.show_orderitem_edit_modal ||
                  this.show_invoice_delete_modal ||
                  this.show_import_client_modal ||
                  this.show_download_range_modal ||
                  this.show_import_product_modal
      return open
    }
  },
  watch: {
    modal_opened: function(open) {
      if (open) {
        document.body.classList.add('modal-open');
      }
      if (!open) {
        document.body.classList.remove('modal-open');
      }
    }
  },
  components: {
      'edit-quote-modal': EditQuoteModal,
      'create-quote-modal': CreateQuoteModal,
      'create-group-modal': CreateGroupModal,
      'edit-group-modal': EditGroupModal,
      'create-invoice-modal': CreateInvoiceModal,
      'update-invoice-modal': UpdateInvoiceModal,
      'detail-customer-modal': CustomerDetailModal,
      'detail-product-modal': ProductDetailModal,
      'edit-orderitem-modal': OrderItemEditModal,
      'delete-invoice-modal': InvoiceDeleteModal,
      'import-client-modal': ImportClientModal,
      'import-product-modal': ImportProductModal,
      'download-range-modal': DownloadRangeModal,
      'customer-list': CustomerList,
  },
  methods: {
    show_import_product_modal_window: function(event){
        console.log("show import product modal");
        this.show_import_product_modal = !this.show_import_product_modal
        if (this.show_import_product_modal){
        }
        if (!this.show_import_product_modal){
          getAllProducts().then(res => res.json()).then(res => this.products = res)
        }
    },
    show_import_client_modal_window: function(event){
        console.log("show import client modal");
        this.show_import_client_modal = !this.show_import_client_modal
        if (this.show_import_client_modal){
        }
        if (!this.show_import_client_modal){
          getAllCustomers().then(res => res.json()).then(res => this.clients = res)
        }
    },
    show_quote_modal_window: function(event){
        console.log("show create quote modal");
        this.show_quote_modal = !this.show_quote_modal
        if (this.show_quote_modal){
        }
        if (!this.show_quote_modal){
          getAllQuotes().then(res => res.json()).then(res => this.quotes = res)
        }
    },
    show_quote_edit_modal_window: function(quote) {
      console.log("show quote edit modal window");
      this.show_quote_edit_modal = !this.show_quote_edit_modal;
      if (this.show_quote_edit_modal) {
        this.edit_quote = quote;
      }
      if (!this.show_quote_edit_modal) {
        this.edit_quote = null;
        getAllQuotes().then(res => res.json()).then(res => this.quotes = res)
      }
    },
    show_create_invoice_modal_window: function(selected_customer, selected_client_orderitems){
      console.log("show create invoice modal");
      console.log(selected_client_orderitems)
      this.show_create_invoice_modal = !this.show_create_invoice_modal
      if (this.show_create_invoice_modal){
        this.create_invoice_customer = selected_customer
        this.create_invoice_orderitems = selected_client_orderitems
      }
      if (!this.show_create_invoice_modal){
        this.create_invoice_customer_id = null
        this.create_invoice_orderitems = []
        getAllOrderitems().then(res => res.json()).then(res => this.orderitems = res)
      }
    },
    show_update_invoice_modal_window: function(selected_invoice, selected_client_orderitems){
      console.log("show update invoice modal");
      console.log(selected_client_orderitems)
      this.show_update_invoice_modal = !this.show_update_invoice_modal
      if (this.show_update_invoice_modal){
        this.update_invoice = selected_invoice
      }
      if (!this.show_update_invoice_modal){
        this.update_invoice = null
      }
    },
    show_create_group_modal_window: function(event){
      console.log("show create group modal");
      this.show_create_group_modal = !this.show_create_group_modal
      if (this.show_create_group_modal){
      }
      if (!this.show_create_group_modal){
        getAllGroups().then(res => res.json()).then(res => this.groups = res)
      }
    },
    show_edit_group_modal_window: function(group){
        console.log("show edit group modal");
        this.show_edit_group_modal = !this.show_edit_group_modal
        if (this.show_edit_group_modal){
          this.edit_group = group
        }
        if (!this.show_edit_group_modal){
          this.edit_group_name = null
          getAllGroups().then(res => res.json()).then(res => this.groups = res)
          getAllCustomers().then(res => res.json()).then(res => this.clients = res)
        }
    },
    show_customer_detail_modal_window: function(client) {
      console.log("show customer detail modal");
      this.show_customer_detail_modal = !this.show_customer_detail_modal;
      if (this.show_customer_detail_modal){
        this.detail_customer = client;
      }
      if (!this.show_customer_detail_modal){
        this.detail_customer = null;
        getAllCustomers().then(res => res.json()).then(res => this.clients = res)
      }      
    },
    show_product_detail_modal_window: function(product) {
      console.log("show product detail modal");
      this.show_product_detail_modal = !this.show_product_detail_modal;
      if (this.show_product_detail_modal){
        this.detail_product = product;
      }
      if (!this.show_product_detail_modal){
        this.detail_product = null;
        getAllProducts().then(res => res.json()).then(res => this.products = res)
      }      
    },
    show_orderitem_edit_modal_window: function(orderitem) {
      console.log("show orderitem edit modal")
      this.show_orderitem_edit_modal = !this.show_orderitem_edit_modal;
      if (this.show_orderitem_edit_modal){
        this.edit_orderitem = orderitem;
      }
      if (!this.show_orderitem_edit_modal){
        this.edit_orderitem = null;
        getAllOrderitems().then(res => res.json()).then(res => this.orderitems = res)
      }
    },
    show_invoice_delete_modal_window: function(invoice){
      console.log("show invoice delete modal")
      this.show_invoice_delete_modal = !this.show_invoice_delete_modal;
      if (this.show_invoice_delete_modal){
        this.delete_invoice = invoice;
      }
      if (!this.show_invoice_delete_modal){
        this.delete_invoice = null;
        getAllInvoices().then(res => res.json()).then(res => this.invoices = res)
      }
    },
    show_download_range_modal_window: function(){
      console.log("show download range modal")
      this.show_download_range_modal = !this.show_download_range_modal;
      if (this.show_download_range_modal){
      }
      if (!this.show_download_range_modal){
      }
    },
    sync_clients: function(){
      console.log('sync clients')
      syncClients().then(res => res.json()).then(res => this.clients = res)
    },
    sync_invoices: function() {
      console.log('sync invoices')
      syncInvoices().then(res => res.json()).then(res => this.invoices = res)
    }
  }
})

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getAllCustomers() {
      let url = origin + '/pos/api/customers/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getAllGroups(){
    let url = origin + '/pos/api/groups/all/';
    let response = fetch(url, {
        method: 'GET', // or 'PUT'
    });
    return response;
}

function getAllProducts(){
    let url = origin + '/pos/api/products/';
    let response = fetch(url, {
        method: 'GET', // or 'PUT'
    });
    return response;
}

function getAllQuotes(){
    let url = origin + '/pos/api/quotes/';
    let response = fetch(url, {
        method: 'GET', // or 'PUT'
    });
    return response;
}

function getAllTaxes() {
  let url = origin + '/pos/api/taxes/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getTax(tax_id) {
  let url = origin + '/pos/api/tax/' + tax_id.toString();
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getAllOrderitems() {
  let url = origin + '/pos/api/orderitems/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getFreshbooksClients() {
  let url = origin + '/pos/api/customers/freshbooks/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getFreshbooksProducts() {
  let url = origin + '/pos/api/products/freshbooks/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;  
}

function downloadInvoicePDF(invoice_number){
  let url = origin + '/pos/invoice/pdf/?invoice_number=' + invoice_number;
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
      encoding: "binary",
      headers: {
        'Content-Type': 'application/pdf'
      }
  });
  return response;
}

function importClient(data){
  let url = origin + '/pos/api/customers/freshbooks/import/create/'
  let response = fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}

function importProduct(data){
  let url = origin + '/pos/api/products/freshbooks/import/create/'
  let response = fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}


function getFreshbooksClientsImport() {
  let url = origin + '/pos/api/customers/freshbooks/import/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}


function getFreshbooksProductsImport() {
  let url = origin + '/pos/api/products/freshbooks/import/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function orderitemFilter(formatted_start_date = null, formatted_end_date = null, customer_ids = []){
  let url = origin + '/pos/api/orderitems/?';
  if (formatted_start_date && formatted_end_date)
    url += `start_date=${formatted_start_date}&end_date=${formatted_end_date}`;
  if (customer_ids.length > 0){
    url += 'customer_ids=';
    customer_ids.forEach(c => {
      url += c.toString() + ';';
    })
  }
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getProductDetail(product_id){
  let url = origin + '/pos/api/products/' + product_id + '/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getAllInvoices(){
  let url = origin + '/pos/api/invoices/'
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function getInvoice(invoice_id){
  let url = origin + '/pos/api/invoices/' + invoice_id + '/';
  let response = fetch(url, {
      method: 'GET', // or 'PUT'
  });
  return response;
}

function createInvoice(data){
  let url = origin + '/pos/api/invoice/create/'
  let response = fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}

function createCustomer(data){
    let url = origin + '/pos/api/customer/create/';
    let response = fetch(url, {
        method: 'POST', // or 'PUT'
        credentials: 'same-origin',
        body: JSON.stringify(data), // data can be `string` or {object}!
        headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    })
    return response;
}

function createQuote(data){
    let url = origin + '/pos/api/quote/';
    let response = fetch(url, {
        method: 'POST', // or 'PUT'
        credentials: 'same-origin',
        body: JSON.stringify(data), // data can be `string` or {object}!
        headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    })
    return response;
}


function createGroup(data){
    let url = origin + '/pos/api/group/create/';
    let response = fetch(url, {
        method: 'POST', // or 'PUT'
        credentials: 'same-origin',
        body: JSON.stringify(data), // data can be `string` or {object}!
        headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    })
    return response;
}

function linkClient(data){
  let url = origin + '/pos/api/customer/link/';
  let response = fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}

function linkProduct(data){
  let url = origin + '/pos/api/product/link/';
  let response = fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}

function updateGrouping(data){
    let url = `${origin}/pos/api/group/update/`;
    return fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error: ', error));
}

function deleteOrderItem(orderitemId) {
  let url = `${origin}/pos/api/orderitem/${orderitemId}/delete/`;
  return fetch(url, {
    method: 'DELETE', // or 'PUT'
    credentials: 'same-origin',
    headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }).catch(error => console.error('Error: ', error));
}

function updateOrderItem(data){
    let url = `${origin}/pos/api/orderitem/${data.id}/update/`;
    return fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error: ', error));
}

function updateQuote(data) {
  let url = `${origin}/pos/api/quote/${data.id}/update/`;
  return fetch(url, {
    method: 'PUT', // or 'PUT'
    credentials: 'same-origin',
    body: JSON.stringify(data), // data can be `string` or {object}!
    headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }).catch(error => console.error('Error: ', error));
}

function unlinkInvoice(data){
  let url = `${origin}/pos/api/invoices/unlink/${data.invoice_id}/`;
  return fetch(url, {
    method: 'PUT', // or 'PUT'
    credentials: 'same-origin',
    body: JSON.stringify(data), // data can be `string` or {object}!
    headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }).catch(error => console.error('Error: ', error));
}

function deleteInvoice(invoiceId){
  let url = `${origin}/pos/api/invoices/delete/${invoiceId}/`;
  return fetch(url, {
    method: 'DELETE', // or 'PUT'
    credentials: 'same-origin',
    headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }).catch(error => console.error('Error: ', error));
}

function syncClients(data={}){
  let url = origin + '/pos/api/customers/sync/';
  let response = fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}

function syncInvoices(data={}){
  let url = origin + '/pos/api/invoices/sync/';
  let response = fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}

function updateInvoice(data, invoice_id){
  let url = origin + '/pos/api/invoices/' + invoice_id + '/update/';
  let response = fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
      'X-CSRFToken': getCookie('csrftoken'),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
  })
  return response;
}