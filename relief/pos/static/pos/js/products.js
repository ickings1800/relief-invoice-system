const origin = location.origin;

var EditProductModal = Vue.component('EditProductModal', {
  data: function () {
      return {
          name: null,
      }
  },

  template:`
    <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit Product</div>
            </div>
            <div class="modal-body form-group">
                <label class="form-label" for="edit-name">Name</label>
                <input class="form-input" type="text" id="edit-name" placeholder="Enter Name" v-model="name" maxlength="128" required>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveProduct">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'product_id'],
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getProductDetail(this.product_id);
           }
       }
   },
   methods: {
      close: function(){
           this.$emit('showeditproductmodal');
       },
       getProductDetail(product_id){
           getProduct(product_id).then(res => res.json()).then(res => this.name = res.name);
       },
       saveProduct(event){
           let data = {'name': this.name};
           updateProduct(this.product_id, data).then(res => res.json()).then(() => this.close());
       }
   }
})

var CreateProductModal = Vue.component('CreateProductModal', {
  data: function () {
      return {
          name: null,
      }
  },

  template:`
      <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Add Product</div>
            </div>
            <div class="modal-body form-group">
                <label class="form-label" for="create-name">Name</label>
                <input class="form-input" type="text" id="create-name" placeholder="Enter Name" v-model="name" maxlength="128" required>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="createProduct">Save</button>
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
       close: function(){
           this.$emit('showcreateproductmodal');
       },
       createProduct: function(event){
           let data = {'name': this.name};
           createProduct(data).then(res => res.json()).then(() => this.close());
       }
   }
})

var ProductList = Vue.component('ProductList', {
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
                <h2>Products</h2>
            </div>
            <div class="column col-mr-auto"></div>
            <div class="column col-3">
                <a class="btn btn-primary btn-sm float-right button-action" v-on:click.prevent="$emit('showcreateproductmodal')">
                    <i class="icon icon-plus"></i>&nbsp;Create
                </a>
            </div>
        </div>
        <div class="columns">
            <div class="column col-12">
                <table class="table">
                    <tr v-for="product in products">
                        <td><a class="btn btn-link" v-on:click.prevent="$emit('showeditproductmodal', product.id)">{{ product.name }}</a></td>
                    </tr>
                </table>
                <div v-if="products.length === 0" class="empty">
                      <p class="empty-title h5">You have no products.</p>
                        <p class="empty-subtitle">Click the button to create one.</p>
                      <div class="empty-action">
                            <a href="#" class="btn btn-primary btn-sm button-action" v-on:click.prevent="$emit('showcreateproductmodal')">
                                <i class="icon icon-plus"></i>&nbsp;Create
                            </a>
                      </div>
                </div>
            </div>
        </div>
    </div>
  `,
   props: ['products'],
   components: {},
   methods: {
   }
})



var app = new Vue({
  el: '#app',
  data: function () {
      return {
          products: [],
          show_product_edit_modal: false,
          show_product_create_modal: false,
          selected_product_id: null,
      }
  },
  created: function() {
      console.log("created function");
      this.getAllProducts();
  },
  components: {
      'create-product-modal': CreateProductModal,
      'product-list': ProductList,
  },
  methods: {
      showcreateproductmodal: function(event){
          console.log("show create product modal");
          this.show_product_create_modal = !this.show_product_create_modal
          if (this.show_product_create_modal){
          }
          if (!this.show_product_create_modal){
              this.getAllProducts()
          }
      },
      showeditproductmodal: function(product_id){
          console.log("show edit product modal");
          this.show_product_edit_modal = !this.show_product_edit_modal
          if (this.show_product_edit_modal){
              this.selected_product_id = product_id;
          }
          if (!this.show_product_edit_modal){
              this.selected_product_id = null;
              this.getAllProducts()
          }
      },
      getAllProducts: function() {
          getAllProducts().then(res => res.json()).then(res => this.products = res);
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

function getAllProducts() {
      let url = origin + '/pos/api/products/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}


function getProduct(product_id){
    let url = origin + '/pos/api/products/' + product_id + '/';
    let response = fetch(url, {
        method: 'GET', // or 'PUT'
    });
    return response;
}


function createProduct(data){
    let url = origin + '/pos/api/product/create/';
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


function updateProduct(product_id, data){
    let url = origin + '/pos/api/product/update/' + product_id + '/';
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

