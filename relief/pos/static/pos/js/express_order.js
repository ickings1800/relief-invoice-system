const origin = location.origin;

Vue.component('v-select', VueSelect.VueSelect);


var OrderRow = Vue.component('OrderRow', {
  data: function () {
      return {
        // rowDate: this.formatDate(new Date()),
        // rowCustomer: null,
        // rowProduct: null,
        // rowQuantity: null,
        // rowDoNumber: null,
        customers: [],
        customerproducts: [],
      }
  },
  created: function() {
    this.refreshcustomers();
  },
  watch:{
    'data.selectedCustomer': function(newVal, oldVal){
      if (newVal){
        this.refreshcustomerproducts(newVal.id)
      }
    }
  },
  computed: {
  },
  template:`
    <div class="order-row d-inline-flex">
        <!-- form input control -->
        <div class="form-group mx-1">
            <label class="form-label" v-if="index === 0">Date</label>
            <input class="form-input" type="date" :value="data.date" tabindex="-1" v-on:input="data.date = formatDate($event.target.valueAsDate)">
        </div>
        <!-- form input control -->
        <div class="form-group mx-1">
            <label class="form-label" v-if="index === 0">Customer</label>
            <v-select v-model="data.selectedCustomer" :options="customers" :reduce="customer => customer" label="name"/>
        </div>
        <!-- form input control -->
        <div class="form-group mx-1">
            <label class="form-label" v-if="index === 0">Product</label>
            <v-select v-model="data.selectedProduct" :options="customerproducts" :reduce="product => product" label="product_name"/>
        </div>
        <!-- form input control -->
        <div class="form-group mx-1">
            <label class="form-label" v-if="index === 0">Quantity</label>
            <input class="form-input" type="number" placeholder="Quantity" v-model="data.quantity">
        </div>
        <!-- form input control -->
        <div class="form-group mx-1">
            <label class="form-label" v-if="index === 0">D/O</label>
            <input class="form-input" type="text" placeholder="D/O" v-model="data.do_number">
        </div>
        <div class="form-group mx-1">
            <label class="form-label" v-if="index === 0">P/O</label>
            <input class="form-input" type="text" placeholder="P/O" v-on:keydown.tab="tabHandler" v-model="data.po_number">
        </div>
        <button class="btn btn-error m-2 del-row-btn" v-on:click.prevent="deleteRow(index)">Delete</button>
    </div>
  `,
   props: ['index', 'data'],
   components: {},
   methods: {
    refreshcustomerproducts: function(customer_id){
      console.log("refresh customerproducts");
      getCustomerProducts(customer_id).then(res => res.json()).then(res => this.customerproducts = res);
    },
    refreshcustomers: function(event){
      console.log('refresh customers');
      getAllCustomers().then(res => res.json()).then(res => this.customers = res);
    },
    submitCustomer(result){
      console.log('tab was pressed')
      console.log(result)
      this.data.selectedCustomer = result;
    },
    submitProduct(result){
      console.log('submit product')
      this.data.selectedProduct = result;
    },
    tabHandler: function() {
      console.log("tab key on d/o input");
      this.$emit('create-row', this.data.date)
    },
    formatDate: function(dateObj) {
        let month = '' + (dateObj.getMonth() + 1);
        let day = '' + dateObj.getDate();
        let year = '' + dateObj.getFullYear();

        if (month.length < 2)
            month = '0' + month;
        if (day.length < 2) 
            day = '0' + day;

        return [year, month, day].join('-');
    },
    deleteRow: function(rowIndex) {
      this.$emit('delete-row', rowIndex)
    }
   },
   computed: {
   }
})

var OrderForm = Vue.component('OrderForm', {
  data: function () {
      return {
        dataArray: [{
          'selectedCustomer': null, 
          'selectedProduct': null, 
          'date': new Date(), 
          'quantity': null, 
          'do_number': null, 
          'po_number': null,
          'error': []
        }]
      }
  },
  created: function() {
  },
  template:`
    <div class="container">
        <h1>Express Order</h1>
        <order-row 
          v-for="(row, index) in dataArray" 
          :key="'order-form-' + index"
          v-bind:index="index"
          v-bind:data="row"
          v-on:create-row="createRow"
          v-on:delete-row="deleteRow">
        </order-row>
        <button class="btn btn-primary btn-lg d-block mx-1" @click="importData">Bulk Import</button>
    </div>
  `,
   props: [],
   components: { 'order-row': OrderRow, },
   methods: {
    createRow: function(prevRowDate) {
      console.log(prevRowDate)
      this.dataArray.push({
        'selectedCustomer': null,
        'selectedProduct': null,
        'date': prevRowDate,
        'quantity': null,
        'do_number': null,
        'po_number': null,
        'error': []
      })
    },
    deleteRow: function(rowIndex) {
      console.log('delete row', rowIndex);
      if (this.dataArray.length > 1){
        this.dataArray.splice(rowIndex, 1);
      } else {
        Vue.set(this.dataArray, 0, {
          'selectedCustomer': null, 
          'selectedProduct': null, 
          'date': null, 
          'quantity': null, 
          'do_number': null, 
          'po_number': null,
          'error': []
        });
      }
    },
    importData: function() {
      console.log('bulk import')
      if (!this.validateData(this.dataArray)) {
        bulkImport(this.dataArray)
        .then(res => res.json())
        .then(() => this.clearDataArray())
        .catch(error => { console.log(error) })
      }
    },
    validateData: function(data){
      let error = false;
      data.forEach(d => {
        if (!d.selectedCustomer) {
          d.error.push("Customer is required")
        }

        if (!d.selectedProduct) {
          d.error.push("Product is required")
        }
        if (!d.date) {
          d.error.push("Date is required")
        }

        if (!d.quantity) {
          d.error.push("Quantity is required")
        }

        if (d.selectedCustomer && d.selectedProduct.customer_id !== d.selectedCustomer.id){
          d.error.push("Product does not match with customer")
        }

        if (d.error.length > 0) {
          error = true;
        }
      })
      return error;
    },
    clearDataArray: function(){
      this.dataArray = [{
        'selectedCustomer': null, 
        'selectedProduct': null, 
        'date': new Date(), 
        'quantity': null, 
        'do_number': null, 
        'po_number': null,
        'error': []
      }]
    }
   },
   computed: {}
})




var app = new Vue({
  el: '#app',
  data: function () {
      return {
	  customers: [],
	  customerproducts: [],
	  routes: null,
      }
  },
  created: function() {
  },
  watch: {},
  mounted: function(){
      console.log("mounted function");
  },
  components: {
      'order-form': OrderForm,
  },
  methods: {
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

function getCustomerGroup(customer_id){
      let url = origin + '/pos/api/customers/'+ customer_id + '/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getAllCustomerProducts(customer_id){
    let url = origin + '/pos/api/quotes/';
    let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
    return response;
}

function getCustomerProducts(customer_id){
      let url = origin + '/pos/api/quotes/?customer_id=' + customer_id;
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getCustomerRoutes(customer_id){
      let url = origin + '/pos/api/customers/' + customer_id + '/routes/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function saveCustomer(customer_id, data){
    let url = origin + '/pos/api/customer/update/' + customer_id + '/';
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

function saveCustomerProduct(customer_id, data){
    let url = origin + '/pos/api/customers/' + customer_id + '/products/create/';
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

function changeCustomerGroup(customergroup_id, data){
    let url = origin + '/pos/api/customergroup/' + customergroup_id + '/update/'
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

function swapCustomerProduct(customer_id, data){
    let url = origin + '/pos/api/customers/' + customer_id + '/customerproduct/arrangement/';

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

function deleteCustomerProduct(customerproduct_id, data){
    let url = origin + '/pos/api/customerproduct/' + customerproduct_id + '/delete/';
    return fetch(url, {
          method: 'DELETE', // or 'PUT'
          credentials: 'same-origin',
          body: JSON.stringify(data), // data can be `string` or {object}!
          headers:{
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }).catch(error => console.error('Error: ', error));
}


function deleteCustomer(customer_id, data){
    let url = origin + '/pos/api/customer/' + customer_id + '/delete/';
    return fetch(url, {
          method: 'DELETE', // or 'PUT'
          credentials: 'same-origin',
          body: JSON.stringify(data), // data can be `string` or {object}!
          headers:{
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }).catch(error => console.error('Error: ', error));
}


function getAllProducts() {
      let url = origin + '/pos/api/products/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getAllGroups(){
      let url = origin + '/pos/api/groups/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getFreshbooksCustomers() {
    let url = origin + '/pos/api/freshbooks/customers/';
    let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
    return response;
}

function getAllCustomers() {
      let url = origin + '/pos/api/customers/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function bulkImport(dataObjArray){
    let url = origin + '/pos/api/express/import/';
    return fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(dataObjArray), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error: ', error));
}