var InvoiceDetailModal = Vue.component('InvoiceDetailModal', {
  data: function () {
      return {
          customerproducts: [],
          customerroutes: [],
          invoice_columns: [],
      }
  },

  template:`
      <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container do-modal-window">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Invoice Detail: ID {{ selected_detail_invoice.id }}</div>
            </div>
            <div class="modal-body form-group">
            <!--
            <div class="btn-group btn-group-block">
                <button class="btn">HTML</button>
                <button class="btn disabled">CSV</button>
                <button class="btn disabled">JSON</button>
            </div>
            -->
            <draggable v-bind="dragOptions" @end="colrearrange" class="display-no-print">
                <span v-for="col in invoice_columns"
                    :key="col"
                    v-bind:data-column-name="col"
                    class="chip c-hand invoice-column">
                    {{ col }}
                </span>
            </draggable>
            <table class="invoice-table table my-2">
                <tr>
                    <th v-for="col in invoice_columns" :key="col" class="invoice-column">{{ col }}</th>
                </tr>
                <tr v-for="cr in customerroutes" :key="cr.id">
                    <td v-for="col in invoice_columns" v-if="cr[col]">{{ cr[col] }}</td>
                    <td v-else>&nbsp;</td>
                </tr>
            </table>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn" v-on:click.prevent="close">Close</a>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_detail_invoice'],
   created: function() {
   },
   computed: {
    dragOptions() {
          return {
            animation: 200,
            group: "description",
            disabled: false,
            ghostClass: "ghost",
            draggable: ".invoice-column",
          };
        }
    },
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       },
       selected_detail_invoice: function(){
           console.log("refresh selected detail invnoice");
           this.refreshInvoiceData();
       },
       customerproducts: function () {
           this.invoice_columns = ['trip_date', ...this.customerproducts.map(cp => cp.product), 'do_number']
       }
   },
   methods: {
       close: function(){
            this.$emit('showdetailinvoicemodal');
       },
       colrearrange: function (event) {
           console.log("invoice col rearrange");
           this.invoice_columns = Array.from(event.target.children).map(e => e.getAttribute('data-column-name'));
           console.log(this.invoice_columns);
       },
       refreshInvoiceData: function() {
           this.customerproducts = [];
           this.customerroutes = [];
           getCustomerProducts(this.selected_detail_invoice.customer)
            .then(res => res.json())
            .then(res => this.customerproducts = res)

            this.selected_detail_invoice.route_set.forEach(cr => {
               let row = {
                    "id": cr.id,
                    "checked": cr.checked,
                    "index": cr.index,
                    "do_number": cr.do_number,
                    "note": cr.note,
                    "invoice_number": cr.invoice_number,
                    "trip_date": cr.trip_date,
               };
               cr.orderitem_set.forEach(oi => row[oi.customerproduct] = oi.final_quantity);
               this.customerroutes.push(row);
            });
       }
   },
   beforeMount: function() {
       this.refreshInvoiceData();
   }
})


var RouteComponent = Vue.component('route-component', {
  data: function () {
      return {
          customerproducts: [],
          customerroutes: [],
          selected_routes: [],
          select_all: false,
          last_invoice_generated: null,
      }
  },
  computed: {
  },
  template:`
        <div class="accordion route my-2">
            <input type="checkbox" v-bind:id="'accordion-' + customergroup.id" name="accordion-radio" hidden>
            <label class="accordion-header" v-bind:for="'accordion-' + customergroup.id">
            <a class="btn btn-link" v-bind:href="customergroup.url">{{ customergroup.customer_name }}</a>
            <span class="label label-rounded label-primary float-right m-2">{{ customerroutes.length }}</span>
            </label>
            <div class="accordion-body">
                <table class="invoice-table table">
                <tr>
                    <th>
                    <label class="form-checkbox">
                        <input type="checkbox" v-model="select_all"><i class="form-icon"></i>Select All
                    </label>
                    </th>
                    <th>Date</th>
                    <th v-for="cp in customerproducts" :key="cp.id">{{ cp.product }}</th>
                    <th>D/O</th>
                </tr>
                <tr v-for="cr in customerroutes" :key="cr.id">
                    <td>
                    <label class="form-checkbox">
                        <input type="checkbox" v-bind:value="cr.id" v-model="selected_routes"><i class="form-icon"></i>
                    </label>
                    </td>
                    <td>{{ cr.trip_date }}</td>
                    <td v-for="cp in customerproducts" v-if="cr[cp.product]">{{ cr[cp.product].final_quantity }}</td>
                    <td v-else>&nbsp;</td>
                    <td v-if="cr.do_number">{{ cr.do_number }}</td>
                    <td v-else>&nbsp;</td>
                </tr>
                </table>
                <button class="btn btn-primary m-2" v-on:click="saveInvoice">Compile</button>
                <span class="h6" v-if="selected_routes.length > 0">{{ selected_routes.length }} out of {{ customerroutes.length }} selected</span>
                <span class="h6" v-else>No routes are selected</span>
                <a href="#"
                 v-on:click.prevent="$emit('showdetailinvoicemodal', last_invoice_generated)"
                 v-if="last_invoice_generated"
                 class="float-right m-2 btn btn-link">
                    Last invoice generated on: {{ last_invoice_generated.date_generated }}
                </a>
            </div>
        </div>
   `,
   props: ['customergroup'],
   components: {
   },
   watch: {
       select_all: function(val) {
           if (val){
               this.selected_routes = this.customerroutes.map(cr => cr.id);
           } else {
               this.selected_routes = [];
           }
       }
   },
   beforeMount: function() {
       this.getCustomerProducts(this.customergroup.customer_id);
       this.getCustomerRoutes(this.customergroup.customer_id);
       this.getLatestCustomerInvoice(this.customergroup.customer_id);
   },
   methods: {
       getCustomerProducts: function(customer_id) {
           getCustomerProducts(this.customergroup.customer_id)
           .then(res => res.json())
           .then(res => this.customerproducts = res)
       },
       getCustomerRoutes: function(customer_id) {
           this.customerroutes = [];
           this.selected_routes = [];
           getCheckedCustomerRoutes(this.customergroup.customer_id)
           .then(res => res.json())
           .then(res => res.forEach(cr => {
               let row = {
                    "id": cr.id,
                    "checked": cr.checked,
                    "index": cr.index,
                    "do_number": cr.do_number,
                    "note": cr.note,
                    "invoice_number": cr.invoice_number,
                    "trip_date": cr.trip_date,
               };
               cr.orderitem_set.forEach(oi => row[oi.customerproduct] = oi);
               this.customerroutes.push(row);
           }));
       },
       getLatestCustomerInvoice: function(customer_id) {
           getLatestCustomerInvoice(this.customergroup.customer_id)
           .then(res => res.json())
           .then(res => this.last_invoice_generated = res.invoice )
       },
       saveInvoice: function (){
           console.log("save invoices");
           if (this.selected_routes.length > 0) {
               postInvoice(this.customergroup.customer_id, this.selected_routes)
               .then(res => res.json())
               .then(res => this.$emit('showdetailinvoicemodal', res))
               .then(res => {
                   this.getCustomerRoutes(res.customer);
                   this.getLatestCustomerInvoice(res.customer);
               })
           } else {
               alert("No routes are selected");
           }
       }
   }
})

var InvoiceList = Vue.component('InvoiceList', {
  data: function () {
      return {
          groups: [],
          customer_groups: [],
          selected_group: null,
      }
  },
  watch: {
       selected_group: function() {
           console.log("selected group changed");
           getAllCustomers().then(res => res.json())
           .then(res => res.filter(g => g.id === this.selected_group.id)[0])
           .then(res => this.customer_groups = res.customergroup_set);
       },
   },
  created: function() {
      getAllGroups().then(res => res.json()).then(res => this.groups = res).then(() => this.selected_group = this.groups[0]);
  },
  template:`
    <div class="container">
    <!-- basic dropdown button -->
        <div class="dropdown">
            <a href="#" class="btn btn-link dropdown-toggle" tabindex="0" v-if="selected_group">{{ selected_group.name }}<i class="icon icon-caret"></i></a>
            <!-- menu component -->
            <ul class="menu">
                <li class="menu-item" v-for="g in groups" :key="g.id"><a href="#" v-on:click="selected_group = g">{{ g.name }}</a></li>
            </ul>
        </div>
        <route-component v-for="cg in customer_groups" :key="cg.id" v-bind:customergroup="cg" @showdetailinvoicemodal="showdetailinvoicemodal"></route-component>
    </div>
  `,
   props: [],
   components: {'route-component': RouteComponent},
   methods: {
       showdetailinvoicemodal: function(event){
           this.$emit('showdetailinvoicemodal', event);
       }
   },
   computed: {},
})


var app = new Vue({
  el: '#app',
  data: function () {
      return {
          show_detail_invoice_modal: false,
          selected_detail_invoice: null,
      }
  },
  created: function() {

  },
  components: {
      'invoice-list': InvoiceList,
      'invoice-detail-modal': InvoiceDetailModal,
  },
  methods: {
     showdetailinvoicemodal: function(event){
//         console.log("show detail invoice modal");
         this.show_detail_invoice_modal = !this.show_detail_invoice_modal
         if (this.show_detail_invoice_modal){
             this.selected_detail_invoice = event;
         }
         if (!this.show_detail_invoice_modal){
         }
     },
  }
})


function getAllGroups(){
    let url = 'http://localhost:8000/pos/api/groups/all/';
    let response = fetch(url, {
        method: 'GET', // or 'PUT'
    });
    return response;
}

function getAllCustomers() {
      let url = 'http://localhost:8000/pos/api/groups/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getCustomerProducts(customer_id){
      let url = 'http://localhost:8000/pos/api/customers/' + customer_id + '/products/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getCheckedCustomerRoutes(customer_id){
    let url = 'http://localhost:8000/pos/api/customers/' + customer_id + '/routes/?checked=true';
    let response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    return response;
}

function getLatestCustomerInvoice(customer_id){
      let url = 'http://localhost:8000/pos/api/customers/' + customer_id + '/invoices/latest/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}


function postInvoice(customer_id, route_list) {
    let url = 'http://localhost:8000/pos/api/invoice/create/';
    let data = {'customer': customer_id, 'route_id_list': route_list};
    return fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error: ', error));
}


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