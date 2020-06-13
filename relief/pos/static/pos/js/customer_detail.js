const draggable = window['vuedraggable'];
const origin = location.origin;

var DeleteCustomerModal = Vue.component('DeleteCustomerModal', {
  data: function () {
      return {
          routes: null,
          customerproducts: null,
      }
  },

  template:`
        <div class="modal" v-bind:class="{ active: opened }">
            <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
            <div class="modal-container">
                <div class="modal-header">
                    <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                    <div v-if="customer" class="modal-title h5">Delete {{ customer.customer_name }}</div>
                </div>
                <div class="modal-body">
                    <label v-if="customer" class="form-label">Delete {{ customer.customer_name }}</label>
                </div>
                <div class="modal-footer">
                    <div class="divider"></div>
                    <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
                    <a href="#" class="btn btn-primary " v-on:click="deleteCustomer">Delete</a>
                </div>
            </div>
        </div>
   `,
   props: ['opened', 'customer'],
   components: {},
   created: function(){

   },
   watch: {
       opened: function (val){
           if (val) {
               console.log("opened is true");
               this.getCustomerProducts(this.customer.customer_id);
               this.getCustomerRoutes(this.customer.customer_id);
           }
       },
   },
   methods: {
       close: function(event){
           console.log("delete customerproduct modal close");
           this.$emit('showdeletecustomermodal');
       },
       getCustomerRoutes: function(customer_id){
           console.log("get customer routes");
           getCustomerRoutes(this.customer.customer_id)
           .then(res => res.json())
           .then(res => this.routes = res)
       },
       getCustomerProducts: function(customer_id){
           console.log("get customerproducts");
           getCustomerProducts(this.customer.customer_id)
           .then(res => res.json())
           .then(res => this.customerproducts = res)
       },
       deleteCustomer: function(event){
           console.log("delete customer");
           deleteCustomer(this.customer.customer_id, {})
           .then(() => this.close())
           .then(() => window.location.href=origin + '/pos/customers/')
       },
   }
})

var DeleteCustomerProductModal = Vue.component('DeleteCustomerProductModal', {
  data: function () {
      return {
          customerproducts: null,
          selected_customerproduct: null,
      }
  },

  template:`
        <div class="modal" v-bind:class="{ active: opened }">
            <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
            <div class="modal-container">
                <div class="modal-header">
                    <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                    <div class="modal-title h5">Delete Customer Product</div>
                </div>
                <div class="modal-body">
                    <label class="form-label" v-if="selected_customerproduct">Delete {{ customer.customer_name }} {{ selected_customerproduct.product }}</label>
                </div>
                <div class="modal-footer">
                    <div class="divider"></div>
                    <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
                    <a href="#" class="btn btn-primary " v-on:click="deleteCustomerProduct">Delete</a>
                </div>
            </div>
        </div>
   `,
   props: ['opened', 'customer', 'customerproduct_id'],
   components: {},
   created: function(){

   },
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getCustomerProducts(this.customer.customer_id);
           }
       }
   },
   methods: {
       close: function(event){
           console.log("delete customerproduct modal close");
           this.$emit('showdeletecustomerproductmodal');
       },
       getCustomerProducts: function(customer_id){
           console.log("get customerproducts");
           getCustomerProducts(this.customer.customer_id)
           .then(res => res.json())
           .then(res => this.customerproducts = res)
           .then(res => this.selected_customerproduct = res.filter(cp => cp.id == this.customerproduct_id)[0])
       },
       deleteCustomerProduct: function(event){
           deleteCustomerProduct(this.customerproduct_id, {})
           .then(() => this.$emit("refreshcustomerproducts"))
           .then(() => this.close())
       },
   }
})


var EditCustomerNameModal = Vue.component('EditCustomerNameModal', {
  data: function () {
      return {
          customergroup: null,
          name: null,
      }
  },

  template:`
        <div class="modal" v-bind:class="{ active: opened }">
            <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
            <div class="modal-container">
                <div class="modal-header">
                    <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                    <div class="modal-title h5">Update Quote</div>
                </div>
                <div class="modal-body">
                    <label class="form-label" for="name">Name</label>
                    <input class="form-input" id="name" v-model="name">
                </div>
                <div class="modal-footer">
                    <div class="divider"></div>
                    <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
                    <a href="#" class="btn btn-primary" v-on:click="saveCustomer">Save</a>
                </div>
            </div>
        </div>
   `,
   props: ['opened', 'customergroup_id'],
   components: {},
   created: function(){

   },
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getCustomer();
           }
       },
       customergroup: function(val){
           if (val){
               this.name = this.customergroup.customer_name;
           }
       }
   },
   methods: {
       close: function(event){
           console.log("edit customer modal close");
           this.name = null;
           this.$emit('showeditcustomernamemodal');
       },
       getCustomer: function(){
           getCustomerGroup(this.customergroup_id)
           .then(res => res.json())
           .then(res => this.customergroup = res);
       },
       saveCustomer: function(event){
           let data = { "id": this.customergroup.customer_id, "name": this.name };
           saveCustomer(this.customergroup.customer_id, data)
           .then(res => res.json())
           .then(() => this.$emit("refreshcustomer"))
           .then(() => this.close())
       }
   }
})

var EditCustomerGroupModal = Vue.component('EditCustomerGroupModal', {
  data: function () {
      return {
          groups: null,
          selectedGroup: null,
      }
  },

  template:`
        <div class="modal" v-bind:class="{ active: opened }">
            <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
            <div class="modal-container">
                <div class="modal-header">
                    <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                    <div class="modal-title h5">Update Group</div>
                </div>
                <div class="modal-body">
                    <label class="form-label" for="group">Group</label>
                    <select class="form-select" id="group" v-model="selectedGroup">
                        <option v-for="g in groups" v-bind:value="g.id">{{ g.name }}</option>
                    </select>
                </div>
                <div class="modal-footer">
                    <div class="divider"></div>
                    <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
                    <a href="#" class="btn btn-primary" v-on:click.prevent="saveCustomerGroup">Save</a>
                </div>
            </div>
        </div>
   `,
   props: ['opened', 'customergroup_id'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getCustomerGroup();
               this.getGroups();
           }
       }
   },
   methods: {
       close: function(event){
           console.log("edit customer modal close");
           this.$emit('showeditcustomergroupmodal');
       },
       getCustomerGroup: function() {
           console.log("get customer group");
           getCustomerGroup(this.customergroup_id).then(res => res.json()).then(res => this.selectedGroup = res.group_id);
       },
       getGroups: function(){
           console.log("get all groups");
           getAllGroups().then(res => res.json()).then(res => this.groups = res);
       },
       saveCustomerGroup: function(){
           console.log("save customer group");
           let data = {"group": this.selectedGroup};
           changeCustomerGroup(this.customergroup_id, data)
           .then(res => res.json())
           .then(() => this.$emit("refreshcustomer"))
           .then(() => this.close())
       }
   }
})

var CreateCustomerProductModal = Vue.component('CreateCustomerProductModal', {
  data: function () {
      return {
          avail_products: [],
          selectedProduct: null,
      }
  },

  template:`
        <div class="modal" v-bind:class="{ active: opened }">
            <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
            <div class="modal-container">
                <div class="modal-header">
                    <a href="#close" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                    <div class="modal-title h5">Create Quote</div>
                </div>
                <div class="modal-body">
                    <label class="form-label" for="products">Quote</label>
                    <select class="form-select" id="products" v-model="selectedProduct">
                        <option disabled value="">Select a product</option>
                        <option v-for="p in avail_products" v-bind:value="p.id">{{ p.name }}</option>
                    </select>
                </div>
                <div class="modal-footer">
                    <div class="divider"></div>
                    <a class="btn btn-link btn-sm my-2" v-on:click.prevent="close">Cancel</a>
                    <a href="#" class="btn btn-primary" v-on:click.prevent="saveProduct">Save</a>
                </div>
            </div>
        </div>
   `,
   props: ['opened', 'customerproducts', 'customer',],
   components: {},
   created: function(){
   },
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getProducts();
           }
       },
   },
   methods: {
       close: function(event){
           console.log("edit customerproduct modal close");
           this.$emit('showcreatecustomerproductmodal');
       },
       getProducts: function(event){
           let already_quoted_ids = this.customerproducts.map(cp => cp.product_id);
           getAllProducts()
           .then(res => res.json())
           .then(res => res.filter(p => already_quoted_ids.indexOf(p.id) === -1))
           .then(res => this.avail_products = res)
       },
       saveProduct: function(event){
           console.log("save products");
           let customer_id = this.customer.customer_id;
           let data = {"customer": customer_id, "product": this.selectedProduct};
           saveCustomerProduct(customer_id, data)
           .then(res => res.json())
           .then(() => this.$emit("refreshcustomerproducts"))
           .then(() => this.close())
       }
   }
})

var CustomerDetail = Vue.component('CustomerDetail', {
  data: function () {
      return {
          show_profile_tab: true,
          show_quote_tab: false,
          show_orders_tab: false,
          customerproduct_list_ids: null
      }
  },
  created: function() {
  },
  template:`
    <div class="container">
        <div class="columns">
            <div class="column col-12">
                <div class="panel">
                    <div class="panel-header text-center">
                        <div class="panel-title h3 mt-10">{{ this.customer.customer_name }}</div>
                        <button class="btn btn-primary float-right"  v-on:click.prevent="$emit('showdeletecustomermodal')">Delete Customer</button>
                    </div>
                    <div>
                    <nav class="panel-nav">
                        <ul class="tab">
                            <li class="tab-item" v-bind:class="{ active: show_profile_tab }" v-on:click.prevent="profile_tab_click"><a href="#">Profile</a></li>
                            <li class="tab-item" v-bind:class="{ active: show_quote_tab }" v-on:click.prevent="quote_tab_click"><a href="#">Quote</a></li>
                            <li class="tab-item" v-bind:class="{ active: show_orders_tab }" v-on:click.prevent="order_tab_click"><a href="#">Orders</a></li>
                        </ul>
                    </nav>
                    <div class="panel-body">
                        <!-- customer profile table -->
                        <table class="table" v-bind:class="{'d-none': !show_profile_tab}">
                            <tr>
                                <td>Name:</td>
                                <td><a href="#" v-on:click.prevent="$emit('showeditcustomernamemodal')">{{ this.customer.customer_name }}</a></td>
                            </tr>
                            <tr>
                                <td>Group:</td>
                                <td><a href="#" v-on:click.prevent="$emit('showeditcustomergroupmodal')">{{this.customer.group_name}}</a></td>
                            </tr>
                            <tr>
                                <td>UUID:</td>
                                <td><a href="#">{{this.customer.uuid}}</a></td>
                            </tr>
                        </table>

                        <!-- customerproduct table -->
                        <draggable class="menu" v-bind="dragOptions" @end="swapCustomerProduct" v-bind:class="{'d-none': !show_quote_tab}" v-if="customerproducts.length > 0">
                            <div v-for="cp in customerproducts" :key="cp.id" class="menu-item c-hand" v-bind:data-customerproduct-id="cp.id" href="#">
                                <a v-on:click.prevent="$emit('showdeletecustomerproductmodal', cp.id)">{{ cp.product }}</a>
                            </div>
                            <button class="btn btn-primary" v-on:click.prevent="$emit('showcreatecustomerproductmodal')">Create Quote</button>
                        </draggable>
                        <div class="empty" v-bind:class="{'d-none': !show_quote_tab}" v-else>
                          <p class="empty-title h5">Customer has no quote</p>
                            <p class="empty-subtitle">Click the button to create one.</p>
                          <div class="empty-action">
                                <a href="#" class="btn btn-primary btn-sm button-action" v-on:click.prevent="$emit('showcreatecustomerproductmodal')">
                                    <i class="icon icon-plus"></i>&nbsp;Create
                                </a>
                          </div>
                        </div>

                        <!-- customer routes table -->
                        <table class="table" v-bind:class="{'d-none': !show_orders_tab}" v-if="routes.length > 0">
                            <tr v-for="r in routes" :key="r.id">
                                <td>
                                    <a v-bind:href="r.trip_url">{{ r.trip_date }}</a>
                                </td>
                                <td>{{ r.do_number }}</td>
                                <td>
                                    {{ r.note }}
                                </td>
                            </tr>
                        </table>
                        <div class="empty" v-bind:class="{'d-none': !show_orders_tab}" v-else>
                          <p class="empty-title h5">Customer has no orders</p>
                            <p class="empty-subtitle">Go to trips and create one.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </div>
  `,
   props: ['customer', 'customerproducts', 'routes'],
   components: { draggable, },
   methods: {
       profile_tab_click: function(event){
           this.show_profile_tab = true
           this.show_quote_tab = false
           this.show_orders_tab = false
       },
       quote_tab_click: function(event){
           this.show_profile_tab = false
           this.show_quote_tab = true
           this.show_orders_tab = false
       },
       order_tab_click: function(event){
           this.show_profile_tab = false
           this.show_quote_tab = false
           this.show_orders_tab = true
       },
       swapCustomerProduct: function(event){
           console.log(event)
           let customer_id = this.customer.customer_id;
           let customerproduct_ids = Array.from(event.target.children)
           .filter(e => e.classList.contains('menu-item'))
           .map(e => parseInt(e.getAttribute('data-customerproduct-id')));
           console.log(customerproduct_ids);
           let data = {'arrangement': customerproduct_ids}
           swapCustomerProduct(customer_id, data)
           .then(res => res.json())
           .then(() => this.$emit('refreshcustomerproducts'))
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
          show_customerproduct_create_modal: false,
          show_customer_edit_name_modal: false,
          show_customer_edit_group_modal: false,
          show_customerproduct_create_modal: false,
          show_customerproduct_delete_modal: false,
          show_customer_delete_modal: false,
          customer: null,
          customergroup_id: null,
          customerproducts: [],
          routes: [],
          delete_customerproduct_id: null,
      }
  },
  created: function() {
        console.log("created function");
  },
  watch: {
      customergroup_id: function(val){
          if (val){
            this.refreshcustomer();
          }
      },
      customer: function(val){
          if (val){
            this.refreshcustomerproducts();
            this.refreshcustomerroutes();
          }
      }
  },
  mounted: function(){
      console.log("mounted function");
      this.customergroup_id = this.$el.getAttribute('data-customergroup-id');
  },
  components: {
      'edit-customer-name-modal': EditCustomerNameModal,
      'edit-customer-group-modal': EditCustomerGroupModal,
      'delete-customer-product-modal': DeleteCustomerProductModal,
      'delete-customer-modal': DeleteCustomerModal,
      'customer-detail': CustomerDetail,
  },
  methods: {
       showdeletecustomermodal: function(event){
          console.log("show create customerproduct modal");
          this.show_customer_delete_modal = !this.show_customer_delete_modal
          if (this.show_customer_delete_modal){
          }
          if (!this.show_customer_delete_modal){
          }
      },
      showcreatecustomerproductmodal: function(event){
          console.log("show create customerproduct modal");
          this.show_customerproduct_create_modal = !this.show_customerproduct_create_modal
          if (this.show_customerproduct_create_modal){
          }
          if (!this.show_customerproduct_create_modal){
          }
      },
    showeditcustomernamemodal: function(event){
          console.log("show edit customer modal");
          this.show_customer_edit_name_modal = !this.show_customer_edit_name_modal
          if (this.show_customer_edit_name_modal){
          }
          if (!this.show_customer_edit_name_modal){
          }
      },
     showeditcustomergroupmodal: function(event){
         console.log("show edit customer group modal");
         this.show_customer_edit_group_modal = !this.show_customer_edit_group_modal
         if (this.show_customer_edit_group_modal){
         }
         if (!this.show_customer_edit_group_modal){
         }
     },
     showdeletecustomerproductmodal: function(event){
         console.log("show edit customer product delete modal");
         this.show_customerproduct_delete_modal = !this.show_customerproduct_delete_modal
         if (this.show_customerproduct_delete_modal){
             this.delete_customerproduct_id = event;
         }
         if (!this.show_customerproduct_delete_modal){
         }
     },
     refreshcustomer: function(event){
         console.log("refresh customer object");
         getCustomerGroup(this.customergroup_id).then(res => res.json()).then(res => this.customer = res);
     },
     refreshcustomerproducts: function(event){
         console.log("refresh customerproducts");
         getCustomerProducts(this.customer.customer_id).then(res => res.json()).then(res => this.customerproducts = res);
     },
     refreshcustomerroutes: function(event){
         console.log("refresh customerroutes");
         getCustomerRoutes(this.customer.customer_id).then(res => res.json()).then(res => this.routes = res);
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

function getCustomerGroup(customer_id){
      let url = origin + '/pos/api/customers/'+ customer_id + '/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function getCustomerProducts(customer_id){
      let url = origin + '/pos/api/customers/' + customer_id + '/products/';
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