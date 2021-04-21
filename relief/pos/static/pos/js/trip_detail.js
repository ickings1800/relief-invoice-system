//var el;
const draggable = window['vuedraggable'];
const origin = location.origin;

var TripHeader = Vue.component('trip-header', {
  data: function () {
      return {
      }
  },

  template:`
  <div>
    <!-- basic dropdown button -->
    <div>
        <button class="c-hand clickable btn btn-link" v-if="trip && trip.notes !== null" v-on:click.prevent="showedittripnotemodal" id="trip-notes">{{ trip.notes }}</button>
        <button class="btn btn-link c-hand h5 display-no-print" v-else v-on:click.prevent="showedittripnotemodal">Add a note</button>
        <button class="btn btn-sm d-block display-no-print" v-on:click="rearrange" href="#">Expand/Collapse</button>
    </div>

    </div>
   `,
   props: ['trip', 'trip_id', 'pdf_url'],
   components: { draggable },
   created: function(){
   },
   watch: {
       trip: function() {
           console.log("trip watcher")
       }
   },
  computed: {
  },
  methods: {
       rearrange: function(event) {
           console.log("arrange inside trip")
           this.$emit('rearrangeroutes');
       },
       showedittripnotemodal: function(event){
           console.log("show edit trip note modal");
           this.$emit('showedittripnotemodal');
       }
   }
})

var RouteComponent = Vue.component('route-component', {
  data: function () {
      return {
      }
  },
   computed: {
   },
  template:`
  <div class="my-2 columns col-12 route">
        <input type="checkbox" v-bind:id="'accordion-'+ route.id" name="accordion-checkbox" :checked="minimize" hidden>
        <div class="columns column col-12 p-1">
            <label class="accordion-header column col-9 h5" v-bind:for="'accordion-' + route.id" v-if="route.orderitem_set.length > 0">
                {{ routesorder.indexOf(route.id) + 1 }}. {{ route.orderitem_set[0].customer_name }}
            </label>
            <label class="accordion-header column col-9 h5" v-bind:for="'accordion-' + route.id" v-else>
                {{ routesorder.indexOf(route.id) + 1 }}.
            </label>
            <a href="#" class="btn btn-link text-right column col-3 do-number h5"
              v-if="route.do_number"
              v-bind:data-route-id="route.id"
              v-on:click.prevent="showeditdonumbermodal">{{ route.do_number }} | {{ route.datetime }}
            </a>
        </div>

        <div class="accordion-body columns column col-12">
            <ul v-if="route.orderitem_set.length > 0" class="packing-container column col-12">
                <li v-for="method in route.packing" :key="method" class="border">{{ method }}</li>
                <template v-for="oi in route.orderitem_set">
                     <li class="clickable c-hand quantity-input"
                        v-on:click.stop="showeditorderitemquantitymodal"
                         v-bind:data-orderitem-id="oi.id">
                         <!-- span element may be clicked instead of li, bind orderitem id for edit quantity modal -->
                         <span v-bind:data-orderitem-id="oi.id">
                            {{ showQuantity(oi.quantity, oi.driver_quantity) }} {{ oi.product_name }}
                        </span>
                     </li>
                </template>
            </ul>

            <div class="divider column col-12"></div>
            <div class="column col-11 note my-1 c-hand h5"
                v-on:click.prevent="showeditroutenotemodal"
                v-bind:data-route-id="route.id"
                    v-if="route.note">
                {{ route.note }}
            </div>
            <div class="column col-11 note light-caps my-2 c-hand display-no-print"
                v-on:click.prevent="showeditroutenotemodal"
                v-bind:data-route-id="route.id"
                v-else>
                <i class="icon icon-plus mx-2"></i>ADD A NOTE
            </div>
            <button class="delete btn btn-link column col-1 display-no-print" v-on:click.prevent="showdeleteroutemodal">
                <i class="icon icon-delete float-right" v-bind:data-route-id="route.id"></i>
            </button>
        </div>
    </div>
   `,
   props: ['route', 'minimize', 'index', 'routesorder', 'index'],
   components: {
   },
   mounted: function (){
   },
   created: function() {
   },
   methods: {
       showeditorderitemquantitymodal: function(event){
           console.log("show edit orderitem quantity modal");
           this.$emit('showeditorderitemquantitymodal', event);
       },
       showeditorderitemnotemodal: function(event){
           console.log("show edit orderitem note modal");
           this.$emit('showeditorderitemnotemodal', event);
       },
       showdeleteroutemodal: function(event){
           console.log("show delete route modal");
           this.$emit('showdeleteroutemodal', event);
       },
       showeditdonumbermodal: function(event){
           console.log("show edit do number modal");
           this.$emit('showeditdonumbermodal', event);
       },
       showeditroutenotemodal: function(event){
           console.log("show edit route note modal");
           this.$emit('showeditroutenotemodal', event);
       },
       showaddroutemodal: function(event){
           console.log("show add route modal");
           let insertIndex = event.target.getAttribute('data-insertIndex');
           this.$emit('showaddroutemodal', event, insertIndex);
       },
       showQuantity: function(quantity, driver_quantity) {
          if (!quantity && !driver_quantity) {
              if (quantity === 0 && driver_quantity === 0)
                  return 'XX';
          }
          return quantity.toString() + " " + String.fromCodePoint(8594) +  " " + driver_quantity.toString();
      }
   }
})



var RouteList = Vue.component('routes-list', {
  data: function () {
      return {
          routes_id_ordering: [],
      }
  },

  template:`
  <div class="accordion" v-if="routes.length > 0">
      <draggable v-bind="dragOptions" @end="indexchange">
          <route-component
          v-for="(route, index) in routes"
          :key="route.id"
          :route="route"
          :routesorder="routes_id_ordering"
          :data-attribute-id="route.id"
          :index="index"
          v-bind:minimize="arrangeroutes"
          @showeditorderitemquantitymodal="showeditorderitemquantitymodal"
          @showeditorderitemnotemodal="showeditorderitemnotemodal"
          @showdeleteroutemodal="showdeleteroutemodal"
          @showeditdonumbermodal="showeditdonumbermodal"
          @showeditroutenotemodal="showeditroutenotemodal"
          @showaddroutemodal="showaddroutemodal"></route-component>
      </draggable>
  </div>
    <div class="empty" v-else>
        <p class="empty-title h5">Trip has no routes</p>
        <p class="empty-subtitle">Click the button to create one.</p>
        <button class="btn btn-primary " v-on:click.prevent="showaddroutemodal">Create</button>
</div>
   `,
   props: ['arrangeroutes', 'trip_id', 'routes', 'packing_methods'],
   watch: {
       routes:function (val){
           if (val) {
               this.routes_id_ordering = this.routes.map(r => r.id);
           }
       }
   },
   created: function() {
       console.log(this.routes)
        this.routes_id_ordering = this.routes.map(r => r.id);
   },
   components: {
       'route-component': RouteComponent,
       'draggable': draggable,
   },
   mounted: function(){

   },
   methods: {
       indexchange: function(event){
           console.log("index changed");
           let rearrange_ids = Array.from(event.target.children).map(e => e.getAttribute('data-attribute-id'));
           postIndexOrderingData(rearrange_ids, this.trip_id)
           .then(res => res.json())
           .then(res => this.routes_id_ordering = res.id_arrangement);
       },
       showeditorderitemquantitymodal: function(event){
           console.log("routes list show orderitem quantity modal");
           this.$emit('showeditorderitemquantitymodal', event);
       },
       showeditorderitemnotemodal: function(event){
           console.log("routes list show orderitem note modal");
           this.$emit('showeditorderitemnotemodal', event);
       },
       showdeleteroutemodal: function(event){
           console.log("routes list show delete route modal");
           this.$emit("showdeleteroutemodal", event);
       },
       showeditdonumbermodal: function(event){
           console.log("routes list show edit do number modal");
           this.$emit("showeditdonumbermodal", event);
       },
       showeditroutenotemodal: function(event){
           console.log("routes list show route edit note modal");
           this.$emit("showeditroutenotemodal", event);
       },
       showaddroutemodal: function(event, insertIndex){
           console.log("routes list show route edit note modal");
           this.$emit("showaddroutemodal", event, insertIndex);
       },
   },
   computed: {
    dragOptions() {
          return {
            animation: 200,
            group: "description",
            disabled: false,
            ghostClass: "ghost"
          };
        }
    }
})



var EditNoteModal = Vue.component('EditNoteModal', {
  data: function () {
      return {
          trip_notes: ''
      }
  },

  template:`
    <div class="modal modal-sm " v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Add a note</div>
            </div>
            <div class="modal-body form-group">
                <label class="form-label" for="edit-note">Note</label>
                <textarea
                class="form-input"
                id="edit-note"
                placeholder="Add a note"
                rows="3"
                maxlength="255"
                v-model="trip_notes"></textarea>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveTripNote">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'trip_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getTripNote();
           }
       }
   },
   methods: {
       close: function(event) {
           console.log("show edit trip note modal");
           this.trip_notes = '';
           this.$emit('showedittripnotemodal');
       },
       getTripNote: async function(){
            var vm = this;
            getTripDetails(vm.trip_id).then(res => res.json()).then(res => this.trip_notes = res.notes)
            vm.trip_notes = this.trip.notes;
            console.log('trip notes set');
       },
       saveTripNote: function(event){
           console.log("save trip notes");
           console.log("trip note: ", this.trip_notes);
           let data = {"notes": this.trip_notes};
           putTrip(this.trip_id, data)
               .then(res => res.json())
               .catch(e => console.log(e))
           this.close();
       }
   }
})


var OrderItemQuantityModal = Vue.component('OrderItemQuantityModal', {
  data: function () {
      return {
          quantity: null,
          driver_quantity: null,
          customer_name: null,
          customer_product_name: null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit {{ customer_name }} {{ customer_product_name }}</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-inline">Quantity</label>
                  <input class="form-input" type="number" id="quantity" placeholder="Enter Quantity" v-model.number="quantity">
                  <label class="form-inline">Driver Quantity</label>
                  <input class="form-input" type="number" id="driver-quantity" placeholder="Enter Driver Quantity" v-model.number="driver_quantity">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveOrderItemQuantity">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_orderitem_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               console.log("orderitem id is", this.selected_orderitem_id);
               this.getOrderItem();
           }
       },
       quantity: function(val){
           if (val) {
               this.driver_quantity = val;
           }
       },
   },
   methods: {
       close: function(event) {
           console.log("show edit trip note modal");
           this.quantity = null;
           this.$emit('showeditorderitemquantitymodal');
       },
       getOrderItem: async function(){
            var vm = this;
            getOrderItemDetails(this.selected_orderitem_id)
            .then(res => res.json())
            .then(res => {
                console.log(res);
                this.quantity = res.quantity;
                this.driver_quantity = res.driver_quantity;
                this.customer_name = res.customer;
                this.customer_product_name = res.customerproduct;
            }).catch(e => console.log(e))
            console.log('orderitem quantity set');
       },
       saveOrderItemQuantity: function(event){
           console.log("save orderitem quantity");
           let data = {
               "quantity": this.quantity,
               "driver_quantity": this.driver_quantity,
            };
           postOrderItemData(this.selected_orderitem_id, data)
               .then(res => res.json())
               .then(() => this.close())
               .catch(e => console.log(e))
       }
   }
})

var OrderItemNoteModal = Vue.component('OrderItemNoteModal', {
  data: function () {
      return {
          note: null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit Note</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="orderitem-note">Note</label>
                  <textarea class="form-input" id="orderitem-note" placeholder="Enter Note" v-model="note"></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveOrderItemNote">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_orderitem_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               console.log("orderitem id is", this.selected_orderitem_id);
               this.getOrderItem();
           }
       }
   },
   methods: {
       close: function(event) {
           this.$emit('showeditorderitemnotemodal');
       },
       getOrderItem: async function(){
            var vm = this;
            getOrderItemDetails(this.selected_orderitem_id)
            .then(res => res.json())
            .then(res => this.note = res.note)
            .catch(e => console.log(e))
            console.log('orderitem quantity set');
       },
       saveOrderItemNote: function(event){
           console.log("save orderitem note");
           let data = {"note": this.note};
           postOrderItemData(this.selected_orderitem_id, data)
               .then(res => res.json())
               .then(() => this.close())
               .catch(e => console.log(e))
       }
   }
})


var RouteDeleteModal = Vue.component('RouteDeleteModal', {
  data: function () {
      return {
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Delete Route</div>
            </div>
            <div class="modal-body form-group">Delete this route?</div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="deleteRoute">Confirm</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened','selected_route_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       }
   },
   methods: {
       close: function(event) {
           this.$emit('showdeleteroutemodal');
       },
       getOrderItem: async function(){
            var vm = this;
            console.log('orderitem quantity set');
       },
       deleteRoute: function(event){
           console.log("delete route");
           deleteRoute(this.selected_route_id).then(() => this.close()).catch(e => console.log(e))
       }
   }
})


var DoNumberModal = Vue.component('DoNumberModal', {
  data: function () {
      return {
          do_number: null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit D/O Number</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="do-number">D/O Number</label>
                  <input class="form-input" type="number" id="do-number" placeholder="Enter D/O Number" v-model="do_number">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveDoNumber">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_route_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getDoNumber();
           }
       }
   },
   methods: {
       close: function(event) {
           this.do_number = null;
           this.$emit('showeditdonumbermodal');
       },
       getDoNumber: function(){
            var vm = this;
            getRouteDetail(this.selected_route_id)
            .then(res => res.json())
            .then(res => this.do_number = res.do_number)
            .catch(e => console.log(e))
            console.log('do number set');
       },
       saveDoNumber: function(event){
           console.log("save do number");
           let data = {
                'id': this.selected_route_id,
                'do_number': this.do_number,
            };
           putDoNumber(this.selected_route_id, data)
               .then(res => res.json())
               .then(() => this.close())
               .catch(e => console.log(e))
       }
   }
})


var RouteNoteModal = Vue.component('RouteNoteModal', {
  data: function () {
      return {
          note: null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit Route Note</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="route-note">Note</label>
                  <input class="form-input" type="text" id="route-note" placeholder="Enter Note" v-model="note">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveNote">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_route_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               this.getRouteNote();
           }
       }
   },
   methods: {
       close: function(event) {
           this.note = null;
           this.$emit('showeditroutenotemodal');
       },
       getRouteNote: function(){
            var vm = this;
            getRouteDetail(this.selected_route_id)
            .then(res => res.json())
            .then(res => this.note = res.note)
            .catch(e => console.log(e))
            console.log('route note set');
       },
       saveNote: function(event){
           console.log("save note");
           let data = {"id": this.selected_route_id, "note": this.note};
           putRouteData(this.selected_route_id, data)
           .then(res => res.json())
           .then(() => this.close())
           .catch(e => console.log(e))
       }
   }
})


var AddRoute = Vue.component('add-route', {
  data: function () {
      return {
          customer_list: [],
          customer_input_string: '',
          customer_match: [],
          customer_select: null,
          hide_autocomplete: true,
      }
  },

  template:`
  <div class="columns">
        <div class="form-autocomplete column col-12">
          <!-- autocomplete input container -->
            <label class="form-label" for="customer-input">Customer</label>
          <div class="form-autocomplete-input form-input">
            <!-- autocomplete chips -->
            <div class="chip" v-if="customer_select !== null" data-customer-id="customer_select.id">
                {{ customer_select.name}}
                <a href="#" class="btn btn-clear" aria-label="Close" role="button" v-on:click.prevent="clearCustomer"></a>
            </div>
            <!-- autocomplete real input box -->
            <input class="form-input"
            id="customer-input"
            type="text"
            placeholder="Enter Customer"
            maxlength=255
            v-model="customer_input_string"
            v-on:keyup="autocomplete"
            v-if="customer_select === null"
            v-on:click.prevent="hide_autocomplete = !hide_autocomplete">
          </div>

          <!-- autocomplete suggestion list -->
          <ul class="menu column col-12" id="add-customer-menu"  v-bind:class="{ 'd-hide': hide_autocomplete }">
            <!-- menu list items -->
            <li class="menu-item" v-for="c in customer_match" :key="c.id" v-on:click.prevent="addCustomerChip">
                <a href="#">
                    <div class="tile tile-centered">
                        <div class="tile-content" v-bind:data-customer-id="c.id">{{ c.name }}</div>
                    </div>
                </a>
            </li>
          </ul>
        </div>
    </div>
   `,
   watch: {
   },
   props: [],
   created: async function() {
       this.customer_list = await getCustomers();
       this.autocomplete();
   },
   methods: {
       addDestination: function(event){
           console.log("hello world");
       },
       autocomplete: function(event){
           console.log('fired');
           this.customer_match = this.customer_list.filter(e => e.name.toLowerCase()
                                                               .includes(this.customer_input_string.toLowerCase()));
//           console.log(this.customer_match);
       },
       addCustomerChip: function(event){
           console.log("Add Customer Chip");
           console.log(event);
           let selected_customer_id= event.target.getAttribute('data-customer-id');
           this.customer_select = this.customer_match.filter(e => e.id === parseInt(selected_customer_id, 10))[0];
           this.hide_autocomplete = true;
           this.$emit('customerselected', event, this.customer_select.id);
       },
       clearCustomer: function(event){
           console.log("clear customer");
           this.customer_select = null;
       }
   }
})


var AddRouteModal = Vue.component('AddRouteModal', {
  data: function () {
      return {
          route_tab_active: true,
          note_tab_active: false,
          route_note: null,
          customer_select_id: null,
      }
  },

  template:`
    <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Add destination</div>
                <ul class="tab tab-block">
                    <li class="tab-item" v-bind:class="{ active: route_tab_active }">
                        <a href="#" v-on:click.prevent="switchTab">Route</a>
                    </li>
                    <li class="tab-item" v-bind:class="{ active: note_tab_active }">
                        <a href="#" v-on:click.prevent="switchTab">Note</a>
                    </li>
                </ul>
            </div>
            <div class="modal-body form-group" id="add-route-modal-body">
            <!-- form input control -->
                <div class="form-group" v-bind:class="{ 'd-none': !route_tab_active }">
                    <add-route @customerselected="customerselected"></add-route>
                </div>
                <div class="form-group" v-bind:class="{ 'd-none': !note_tab_active }">
                    <label class="form-label" for="note-input">Note</label>
                    <textarea
                        class="form-input"
                        type="text"
                        id="note-input"
                        placeholder="Enter Note"
                        maxlength="255"
                        rows="4"
                        v-model="route_note">
                    </textarea>
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveRoute">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'trip_id', 'routes', 'create_route_at_index'],
   components: {'add-route': AddRoute,},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       }
   },
   methods: {
       switchTab: function(event){
            this.route_tab_active = !this.route_tab_active;
            this.note_tab_active = !this.note_tab_active;
       },
       close: function(event) {
           this.route_tab_active = true;
           this.note_tab_active = false;
           this.route_note = null;
           this.$emit('showaddroutemodal');
       },
       saveRoute: function(event){
           console.log("save route");
           let data;
           if (this.route_tab_active)
               data = {"customer": this.customer_select_id};
           if (this.note_tab_active)
               data = {"note": this.route_note};

           if (this.create_route_at_index < this.routes.length) {
               postRoute(this.trip_id, data)
               .then(res => res.json())
               .then(res => {
                   let rearrange_ids = this.routes.map(r => r.id);
                   // route indexes starts from 1 in database but start at 0 here.
                   rearrange_ids.splice(this.create_route_at_index, 0, res.id);
                   postIndexOrderingData(rearrange_ids, this.trip_id)
                   .then(res => res.json())
                   .then(() => this.close());;
               })
           } else {
               postRoute(this.trip_id, data).then(res => res.json()).then(() => this.close());
           }
       },
       customerselected: function(event, customer_select){
           this.customer_select_id = customer_select;
       }
   }
})

var app = new Vue({
  el: '#app',
  data: function () {
      return {
          trip_id: null,
          trip: null,
          pdfUrl : null,
          routes: null,
          show_routes:true,
          selected_route_id: null,
          selected_orderitem_id: null,
          create_route_at_index: null,
          show_edit_trip_note_modal: false,
          show_orderitem_quantity_modal: false,
          show_orderitem_note_modal: false,
          show_route_delete_modal: false,
          show_edit_do_number_modal:false,
          show_edit_route_note_modal: false,
          show_add_route_modal: false,
      }
  },
   watch: {
       trip: function(val){
           if (val) {
           }
       }
   },
  created: function() {
      console.log("created function");
  },
  mounted: async function(){
      this.trip_id = this.$el.getAttribute('data-trip-id');
      this.pdfUrl = this.$el.getAttribute('data-pdf-url');
      this.getTrip()
      .then((res) => res.json())
      .then(res => this.trip = res)
      .then(() => this.refreshRoutes())
      .then(res => this.routes = res);
  },
  components: {
      'trip-header': TripHeader,
      'routes-list': RouteList,
      'add-route': AddRoute,
      'edit-note-modal': EditNoteModal,
      'edit-orderitem-quantity-modal':OrderItemQuantityModal,
      'edit-orderitem-note-modal': OrderItemNoteModal,
      'delete-route-modal': RouteDeleteModal,
      'do-number-modal': DoNumberModal,
      'edit-route-note-modal': RouteNoteModal,
      'add-route-modal': AddRouteModal,
  },
  methods: {
      minimize: function(event){
          console.log("minimize function");
          this.show_routes = !this.show_routes
      },
      showedittripnotemodal: function(event){
          this.show_edit_trip_note_modal = !this.show_edit_trip_note_modal
          this.getTrip();
      },
      showeditorderitemquantitymodal: function(event){
          this.show_orderitem_quantity_modal = !this.show_orderitem_quantity_modal
          if (this.show_orderitem_quantity_modal){
              console.log(event);
              this.selected_orderitem_id = event.target.getAttribute('data-orderitem-id')
          }
          if (!this.show_orderitem_quantity_modal){
              this.refreshRoutes();
//              TODO: update refresh method so that only one route may be updated?
          }
      },
      showeditorderitemnotemodal: function(event){
          this.show_orderitem_note_modal = !this.show_orderitem_note_modal
          if (this.show_orderitem_note_modal){
              this.selected_orderitem_id = event.target.getAttribute('data-orderitem-id')
          }
          if (!this.show_orderitem_note_modal){
              this.refreshRoutes();
          }
      },
      showdeleteroutemodal: function(event){
          this.show_route_delete_modal = !this.show_route_delete_modal
          if (this.show_route_delete_modal){
              this.selected_route_id = event.target.getAttribute('data-route-id')
              console.log(event);
              console.log(this.selected_route_id)
          }
          if (!this.show_route_delete_modal){
              this.refreshRoutes();
          }
      },
      showeditdonumbermodal: function(event){
          this.show_edit_do_number_modal = !this.show_edit_do_number_modal
          if (this.show_edit_do_number_modal){
              this.selected_route_id = event.target.getAttribute('data-route-id')
              console.log(this.selected_route_id)
          }
          if (!this.show_edit_do_number_modal){
              this.refreshRoutes();
          }
      },
      showeditroutenotemodal: function(event){
          this.show_edit_route_note_modal = !this.show_edit_route_note_modal
              if (this.show_edit_route_note_modal){
                  this.selected_route_id = event.target.getAttribute('data-route-id')
                  console.log(this.selected_route_id)
              }
              if (!this.show_edit_route_note_modal){
                  this.refreshRoutes();
              }
      },
      showaddroutemodal: function(event, insertIndex){
              this.show_add_route_modal = !this.show_add_route_modal
              if (this.show_add_route_modal && insertIndex){
                  this.create_route_at_index = insertIndex;
              }
              if (!this.show_add_route_modal){
                  this.refreshRoutes(this.trip_id);
                  this.create_route_at_index = null;
              }
      },
      getTrip: function(){
          return getTripDetails(this.trip_id)
      },
      refreshRoutes: function(){
         return this.trip.route_set;
      },
      refreshtripdate: function(event){
          console.log("main app refresh trip date");
          this.getTrip();
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

function putDoNumber(route_id, data){
    let url = origin + '/pos/api/routes/' + route_id + '/update/';
    return fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error:', error));
}


function postIndexOrderingData(index_ordering_array, trip_id){
    console.log("index ordering array", index_ordering_array);
    let url = origin + '/pos/api/trips/' + trip_id + '/routes/arrange/';
    let parsed_ordered_array = index_ordering_array.map(e => parseInt(e));
    let data = {'id_arrangement': parsed_ordered_array};
    var response = fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error:', error));
    return response;
}


function getRouteDetail(route_id){
    let url =origin + '/pos/api/routes/' + route_id + '/';
    let response = fetch(url, {
      method: 'GET', // or 'PUT'
    }).catch(e => console.log(e));
    return response;
}


function postOrderItemData(orderitem_id, data){
    console.log("post order item data");
    console.log("POST ORDERITEM:", data);
    var url = origin + '/pos/api/orderitem/' + orderitem_id + '/update/';
    var response = fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });
    return response;
}


function putRouteData(route_id, data) {
    var url = origin + '/pos/api/routes/' + route_id + '/update/';
    return fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error:', error));
}

function postRoute(trip_id, data){
    var url = origin + '/pos/api/trips/' + trip_id + '/detail/routes/add/';
    var response = fetch(url, {
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

function putTrip(trip_id, data){
    let url = origin + '/pos/api/trip/update/' + trip_id.toString() + '/';
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

function deleteRoute(route_id){
    let url = origin + '/pos/api/routes/' + route_id + '/delete/';
    return fetch(url, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error:', error));
}


function getCustomerId(customerName){
    try {
        var customerId = document.querySelector("#customers option[value='"+customerName+"']").dataset.value;
    } catch (err) {
        console.log(err);
    }
    return customerId;
}


function getTripDetails(trip_id){
    console.log("Get Trip Details");
    let url = origin + '/pos/api/trips/' + trip_id + '/';
    var response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    console.log(url)
    console.log(response);
    return response;
}


function getOrderItemDetails(orderitem_id){
    console.log("Get OrderItem Details");
    let url = origin + '/pos/api/orderitem/' + orderitem_id + '/';
    var response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    return response;
}

async function getCustomers(){
    console.log("Get Customer Details");
    let url = origin + '/pos/api/customers/';
    var response = await fetch(url, {
      method: 'GET', // or 'PUT'
    });
    var resp_json = await response.json();
//    console.log(resp_json);
    return resp_json;
}