const draggable = window['vuedraggable'];
const origin = location.origin;

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
           this.$emit('showcreategroupmodal');
       },
       saveGroup: function(event) {
           console.log("save group");
           let data = {"name": this.name}
           createGroup(data).then(res => res.json())
           .then(() => this.$emit('refreshcustomers'))
           .then(() => this.close());
       }
   }
})


var CreateCustomerModal = Vue.component('CreateCustomerModal', {
  data: function () {
      return {
          name: null,
          group_id: 1, // Default group
          groups: [],
          product_list: [],
          selected_products: [],
          show_create_tab: true,
      }
  },

  template:`
    <!-- Add Customer Modal -->
    <div class="modal" id="create-customer-modal" v-bind:class="{ 'active': opened }">
      <a href="#close" class="modal-overlay" aria-label="Close"></a>
      <div class="modal-container customer-create-modal-window">
        <div class="modal-header">
            <ul class="step">
                <li id="create-customer-tab" class="step-item" v-bind:class="{ active: show_create_tab }">
                    <a href="#">Create Customer</a>
                </li>
                <li id="quote-tab" class="step-item" v-bind:class="{ active: !show_create_tab }">
                    <a href="#">Quote</a>
                </li>
            </ul>
        </div>
        <div class="modal-body" id="create-customer-menu">
            <!-- First step: creating customer -->
            <form id="create-customer-form" class="form-horizontal" v-bind:class="{'d-none': !show_create_tab}">
                <div class="form-group">
                    <div class="col-3 col-sm-12">
                        <label class="form-label" for="customer-create-name">Name:</label>
                    </div>
                    <div class="col-9 col-sm-12">
                        <input class="form-input" type="text" maxlength="255" id="customer-create-name" v-model="name">
                    </div>
                </div>
                <div class="form-group">
                    <div class="col-3 col-sm-12">
                        <label class="form-label" for="customer-create-group">Group:</label>
                    </div>
                    <div class="col-9 col-sm-12">
                        <select class="form-select" id="customer-create-group" v-model="group_id">
                            <option v-for="g in groups" v-bind:value="g.id">{{ g.name }}</option>
                        </select>
                    </div>
                </div>
            </form>

            <!-- Second step: creating customer products -->
            <div id="create-customer-product" v-bind:class="{'d-none': show_create_tab}">
                <ul id="menu-list">
                    <li v-for="p, index in selected_products" class="columns">
                        <span class="column col-11">{{ p.name }}</span>
                        <a href="#" class="btn btn-link column col-1" v-on:click="removeQuote(index)">
                            <i class="icon icon-minus"></i>
                        </a>
                    </li>
                    <li id="create-customerproduct-row" class="columns">
                      <select class="form-select column col-11" ref="quote_list">
                          <option v-for="p in product_list" value="p.id">{{ p.name }}</option>
                      </select>
                        <a href="#" class="btn btn-link column col-1 float-right"
                        id="create-customerproduct-row-btn"
                        v-on:click="addQuote">
                        <i class="icon icon-plus"></i>
                        </a>
                    </li>
                </ul>
            </div>
        </div>
        <div class="modal-footer">
            <div class="divider"></div>
            <a class="btn btn-link btn-sm my-2 float-left"
            v-bind:class="{ 'd-none': show_create_tab }"
            v-on:click="show_create_tab = !show_create_tab"
            id="customer-create-back">Back</a>
            <a class="btn btn-link btn-sm my-2" v-on:click="close">Cancel</a>
            <a id="customer-create-submit-button"
             href="#save"
             v-on:click="show_create_tab ? show_create_tab = false : saveCustomerQuote()"
             class="btn btn-primary">{{ show_create_tab ? 'Next' : 'Save'}}</a>
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
               this.getGroups();
               this.getProducts();
           }
       }
   },
   methods: {
       close: function(event){
           console.log("create customer modal close");
           this.selected_products = [];
           this.name = null;
           this.show_create_tab = false;
           this.$emit('showcreatecustomermodal');
       },
       saveCustomerQuote: function(){
           console.log('save customer quote');
           let data = {'name': this.name, 'group': this.group_id};
           createCustomer(data)
           .then(res => res.json())
           .then(res => {
               this.selected_products.forEach(
                   e => createCustomerProduct(res.id, {'customer': res.id, 'product': e.id}).then(res => res.json())
               )
           })
           .then(() => this.close())
           .catch(e => console.log(e));

       },
       addQuote: function(event){
           console.log("add quote");
           let quote_list = this.$refs.quote_list;
           let selectedObj = this.product_list[quote_list.selectedIndex];
           this.selected_products.push(selectedObj);
           this.product_list = this.product_list.filter(p => p.id !== selectedObj.id);
       },
       removeQuote: function(event){
            console.log("remove quote");
            let index = event;
            let selectedObj = this.selected_products[index];
            this.product_list.push(selectedObj)
            this.selected_products.splice(index, 1);
       },
       getGroups: function(){
           getAllGroups().then(res => res.json()).then(res => this.groups = res);
       },
       getProducts: function(){
           getAllProducts().then(res => res.json()).then(res => this.product_list = res);
       }
   }
})

var CustomerList = Vue.component('CustomerList', {
  data: function () {
      return {
      }
  },
  created: function() {
  },
  template:`
    <div class="container">
        <div class="columns">
            <div class="column col-3">
                <h2>Customers</h2>
            </div>
            <div class="column col-mr-auto"></div>
            <div class="column col-3">
                <a class="btn btn-primary btn-sm float-right button-action" id="create-customer-button" v-on:click="$emit('showcreatecustomermodal')">
                    <i class="icon icon-plus"></i>&nbsp;Create Customer
                </a>
                <a class="btn btn-primary btn-sm float-right button-action mx-2" v-on:click="$emit('showcreategroupmodal')">
                    <i class="icon icon-plus"></i>&nbsp;Create Group
                </a>
            </div>
        </div>
        <div class="columns">
            <div class="column col-12">
                <!-- standard Accordions example -->
                <div class="accordion" v-for="group in customer_groups" :key="group.id">
                  <input type="checkbox" v-bind:id="'accordion' + group.id" name="accordion-checkbox" hidden>
                  <label class="accordion-header" v-bind:for="'accordion' + group.id">
                    <i class="icon icon-arrow-right mr-1"></i>
                    {{ group.name }}
                  </label>
                  <div class="accordion-body">
                    <!-- Accordions content -->
                      <div class="menu menu-nav" id="rowParent">
                          <ul class="draggable-list" v-bind:id="'menu' + group.id" v-bind:data-group-id="group.id">
                        <draggable v-bind="dragOptions" @end="customergroup_swap">
                              <li class="menu-item"
                              v-for="cg in group.customergroup_set"
                              v-bind:data-customergroup-id="cg.id">
                              <a v-bind:href="cg.url">{{ cg.customer_name }}</a>
                              </li>
                        </draggable>
                          </ul>
                      </div>
                  </div>
                </div>
            </div>
        </div>
    </div>
  `,
   props: ['customer_groups'],
   components: {draggable, },
   methods: {
       customergroup_swap: function(event){
           let draggable_list = event.target;
           let group_id = event.target.parentNode.getAttribute('data-group-id');
           let arrangement = Array.from(draggable_list.children)
           .map(c => parseInt(c.getAttribute('data-customergroup-id'), 10))
           updateCustomerGroupIndex(group_id, arrangement).then(res => res.json())
       },
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
    },
})



var app = new Vue({
  el: '#app',
  data: function () {
      return {
          customer_groups: [],
          show_customer_create_modal: false,
          show_create_group_modal: false,
      }
  },
  created: function() {
      console.log("created function");
      this.getAllCustomers();
  },
  components: {
      'create-customer-modal': CreateCustomerModal,
      'create-group-modal': CreateGroupModal,
      'customer-list': CustomerList,
  },
  methods: {
      showcreatecustomermodal: function(event){
          console.log("show create customer modal");
          this.show_customer_create_modal = !this.show_customer_create_modal
          if (this.show_customer_create_modal){
          }
          if (!this.show_customer_create_modal){
              this.getAllCustomers()
          }
      },
    showcreategroupmodal: function(event){
          console.log("show create group modal");
          this.show_create_group_modal = !this.show_create_group_modal
          if (this.show_customer_create_modal){
          }
          if (!this.show_create_group_modal){
          }
      },
      refreshcustomers: function(event){
          console.log("refresh customers");
          this.getAllCustomers();
      },
      getAllCustomers: function() {
          getAllCustomers().then(res => res.json()).then(res => this.customer_groups = res);
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
      let url = origin + '/pos/api/groups/';
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

function createCustomerProduct(customer_id, data){
    let url = origin + '/pos/api/customers/' + customer_id + '/products/create/';
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



function updateCustomerGroupIndex(group_id, arrangement){
    let url = `${origin}/pos/api/customergroup/swap/`;
    var data = {
        "group_id": group_id,
        "arrangement": arrangement
    };

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