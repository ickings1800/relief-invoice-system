//var el;
const draggable = window['vuedraggable'];

var Calendar = Vue.component('calendar', {
  data: function () {
      return {
          days_of_week: ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
          months_of_year: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          prev_month: [],
          days_of_month: [],
          next_month: [],
          hours: [],
          minutes: [],
          todayDate: null,
          selectedDate: null,
          selectedDate_year: null,
          selectedDate_month: null,
          selectedDate_hours: null,
          selectedDate_mins: null,
      }
  },

  template:`
      <div class="calendar">
      <!-- calendar navbar -->
      <div class="calendar-nav navbar">
        <button class="btn btn-action btn-link btn-lg" @click="prevMonth">
          <i class="icon icon-arrow-left"></i>
        </button>
        <div class="navbar-primary">{{ months_of_year[selectedDate_month] }} {{ selectedDate_year }}</div>
        <button class="btn btn-action btn-link btn-lg" @click="nextMonth">
          <i class="icon icon-arrow-right"></i>
        </button>
      </div>

      <div class="calendar-container">
        <div class="calendar-header">
          <div v-for="days in days_of_week" class="calendar-date">{{ days }}</div>
        </div>

        <div class="calendar-body">
          <!-- calendar previous month -->
          <div v-for="date in prev_month" class="calendar-date prev-month">
            <button class="date-item" @click="clickPrevMonth(date)">{{ date.getDate() }}</button>
          </div>

          <!-- calendar current month -->
          <div v-for="date in days_of_month"
          class="calendar-date"
          v-bind:class="{ 'range-start': selectDate(date), 'calendar-range': selectDate(date) , 'range-end': selectDate(date) }">
            <button class="date-item"
            @click="selectedDate = date"
            v-bind:class="{ 'date-today': date.getTime() === todayDate.getTime() }">
            {{ date.getDate() }}
            </button>
          </div>

          <!-- calendar next month -->
          <div v-for="date in next_month" class="calendar-date next-month">
            <button class="date-item" @click="clickNextMonth(date)">{{ date.getDate() }}</button>
          </div>
        </div>
       <div class="divider"></div>
       <div class="columns col-gapless">
            <a class="btn btn-link column col-4 text-center" v-on:click.prevent="closeCalendar">Cancel</a>
            <select class="form-select column col-2 text-center" v-model="selectedDate_hours">
                <option v-for="hour in hours">{{ hour }}</option>
            </select>
            <select class="form-select column col-2 text-center" v-model="selectedDate_mins">
                <option v-for="min in minutes">{{ min }}</option>
            </select>
            <button class="btn btn-primary column col-4 text-center" @click="saveDate">Save</button>
       </div>
      </div>
    </div>
   `,
   props: ['trip', 'trip_id', 'active'],
   components: {  },
   created: function(){
       this.resetCalendar();
       this.refreshDates(this.selectedDate_month, this.selectedDate_year);
       this.hours = this.getHours();
       this.minutes = this.getMinutes();
       this.todayDate = new Date(new Date().setHours(0,0,0,0));
   },
   watch: {
        selectedDate_month: function() {
           console.log("month watcher")
           this.refreshDates(this.selectedDate_month, this.selectedDate_year);
        },
        active: function() {
            console.log("calendar active watcher");
            this.resetCalendar();
        },
   },
  computed: {
   },
   methods: {
       getDaysInMonth: function(month, year) {
           let date = new Date(year, month, 1);
           let days = [];
           while(date.getMonth() === month) {
               days.push(new Date(date));
               date.setDate(date.getDate() + 1);
           }
           return days;
       },
       getPrevMonthDateRange: function(month, year){
           let days = [];
           let date = new Date(year, month, 0); // get last date of previous month
//           console.log(date)
           let prev_month_remaining = date.getDay(); // how many days since sunday, starting from zero
           for (let i = prev_month_remaining; i >= 0; i--){
               let newDate = new Date(year, month - 1, date.getDate() - i);
               days.push(newDate);
           }
           return days;
       },
       getNextMonthDateRange: function(month, year){
           let days = [];
           let date = new Date(year, month + 1, 1); // get first date of the next month
           let next_month_remaining = 6 - date.getDay(); // how many left to sunday, sunday index being 6
           for (let i = 0; i <= next_month_remaining; i++){
               let newDate = new Date(year, month + 1, date.getDate() + i);
               days.push(newDate);
           }
           return days;
       },
       getHours: function(){
           let hours = [];
           for (let i = 0; i < 24; i++) {
               hours.push(i.toString().padStart(2, '0'));
           }
           return hours;
       },
       getMinutes: function(){
           let minutes = [];
           for (let i = 0; i < 60; i+=5){
               minutes.push(i.toString().padStart(2, '0'));
           }
           return minutes;
       },
       nextMonth: function(event){
           if (this.selectedDate_month === 11){
               this.selectedDate_year += 1;
               this.selectedDate_month = 0;
           } else {
               this.selectedDate_month += 1;
           }
       },
       prevMonth: function(event){
            if (this.selectedDate_month === 0){
               this.selectedDate_year -= 1;
               this.selectedDate_month = 11;
           } else {
               this.selectedDate_month -= 1;
           }
       },
       refreshDates: function(month, year){
           console.log('refresh dates');
            this.days_of_month = this.getDaysInMonth(this.selectedDate_month, this.selectedDate_year);
            this.prev_month = this.getPrevMonthDateRange(this.selectedDate_month, this.selectedDate_year);
            this.next_month = this.getNextMonthDateRange(this.selectedDate_month, this.selectedDate_year);
       },
       resetCalendar: function(event){
            this.selectedDate = new Date(this.trip.date);
            this.selectedDate_month = this.selectedDate.getMonth();
            this.selectedDate_year = this.selectedDate.getFullYear();
            this.selectedDate_hours = this.selectedDate.getHours().toString().padStart(2, '0');
            this.selectedDate_mins = this.selectedDate.getMinutes().toString().padStart(2, '0');
       },
       selectDate: function(date){
           return date.getTime() === new Date(this.selectedDate.setHours(0,0,0,0)).getTime();
       },
       closeCalendar: function(event){
           console.log("close calendar");
           this.$emit('update:active', !this.active);
           this.resetCalendar();
       },
       clickNextMonth: function(date){
           this.selectedDate = date;
           this.nextMonth();
       },
       clickPrevMonth: function(date){
           this.selectedDate = date;
           this.prevMonth();
       },
       saveDate: function(event){
           console.log("calendar save date");
           let d = this.selectedDate.getDate();
           // javascript getMonth starts from zero index, backend requires start by one index
           let m = this.selectedDate_month + 1;
           let Y = this.selectedDate_year
           let H = this.selectedDate_hours;
           let M = this.selectedDate_mins;
           let data = {'date': `${d}-${m}-${Y} ${H}:${M}`};
           console.log(data);
           putTrip(this.trip_id, data)
           .then(res => res.json())
           .then(() => this.closeCalendar())
           .then(() => this.$emit("refreshtripdate"));
       }
   }
})

var TripHeader = Vue.component('trip-header', {
  data: function () {
      return {
          packaging_methods: null,
          hovered_methods: null,
          dropdown_active: false,
          display_year: null,
          display_month: null,
          display_date: null,
          display_hours: null,
          display_mins: null,
      }
  },

  template:`
  <div>
    <!-- basic dropdown button -->
    <div class="dropdown" v-bind:class="{ active: dropdown_active }">
        <h2 class="clickable c-hand" v-if="trip" @click="dropdown_active = !dropdown_active">
        {{ display_date }}-{{ display_month }}-{{ display_year }} {{ display_hours }}:{{ display_mins }}
        </h2>
        <!-- menu component -->
        <div class="menu" v-bind:style="{'overflow-y': 'unset'}" v-bind:class="{ 'd-none': !dropdown_active }">
            <calendar v-if="trip"
             v-bind:trip="trip"
             v-bind:trip_id="trip_id"
             v-bind:active="dropdown_active"
             v-on:update:active="dropdown_active=$event"
             @refreshtripdate="refreshtripdate">
             </calendar>
        </div>
    </div>
    <draggable v-bind="dragOptions" @end="packingrearrange">
        <span v-for="pm in packaging_methods"
            @mouseover="hovered_methods[pm] = true"
            @mouseleave="hovered_methods[pm] = false"
            :key="pm"
            class="chip c-hand packing-item"
            v-bind:data-attribute-packing="pm">
            {{ pm }}
            <a href="#" v-show="hovered_methods[pm]" key="pm" class="btn btn-clear" aria-label="Close" role="button" @click="deletepacking(pm, $event)"></a>
        </span>
        <span class="chip"><a href="#"><i class="icon icon-plus m-1" @click="addpacking"></i></a></span>
    </draggable>
    <a class="btn btn-link c-hand h5" v-if="trip && trip.notes !== null" @click="showedittripnotemodal">{{ trip.notes }}</a>
    <a class="btn btn-link c-hand h5" v-else @click="showedittripnotemodal">Add a note</a>
    <div>
        <a class="btn btn-sm" v-on:click="rearrange" href="#">Expand/Collapse</a>
        <a class="btn btn-primary btn-sm float-right" v-bind:href="pdf_url">Print</a>
    </div>

    </div>
   `,
   props: ['trip', 'trip_id', 'pdf_url'],
   components: { draggable,
   'calendar': Calendar,
 },
   created: function(){
       this.refreshPackingChips();
       this.setDisplayDate(this.trip.date);
   },
   watch: {
       trip: function() {
           console.log("trip watcher")
           this.refreshPackingChips();
           console.log(this.trip.date);
           this.setDisplayDate(this.trip.date);
       }
   },
  computed: {
    dragOptions() {
          return {
            animation: 200,
            group: "description",
            disabled: false,
            ghostClass: "ghost",
            draggable: ".packing-item",
            dataIdAttr: 'data-attribute-packing',
          };
        }
    },
   methods: {
       rearrange: function(event) {
           console.log("arrange inside trip")
           this.$emit('rearrangeroutes');
       },
       showedittripnotemodal: function(event){
           console.log("show edit trip note modal");
           this.$emit('showedittripnotemodal');
       },
       addpacking: function(event){
           console.log("add packing");
           this.$emit('showaddpackingmodal');
       },
       deletepacking: function(pm, event){
           console.log("delete packing");
           this.packaging_methods = this.packaging_methods.filter(e => e !== pm);
           let data = { packaging_methods: this.packaging_methods.join() };
           console.log(data);
           putTrip(this.trip_id, data).then(() => this.$emit('deletepacking'));
       },
       packingrearrange: function(event){
           console.log("packing rearrange");
           this.packaging_methods = Array.from(event.target.children)
                                       .filter(e => e.classList.contains("packing-item"))
                                       .map(e => e.getAttribute('data-attribute-packing'));
           let data = { "packaging_methods": this.packaging_methods.join() };
           console.log(data);
           putTrip(this.trip_id, data).then(() => this.$emit('rearrangepacking'));
       },
       refreshPackingChips: function(){
           this.packaging_methods = this.trip.packaging_methods.split(",").map(pm => pm.trim());
           this.hovered_methods = { };
           this.trip.packaging_methods.split(",").map(pm => { this.$set(this.hovered_methods, pm.trim(), false )});
       },
       setDisplayDate: function(dateString){
           let display_date = new Date(dateString);
           this.display_year = display_date.getFullYear();
           // javascript getMonth starts from zero index, backend requires start by one index
           this.display_month = (display_date.getMonth() + 1).toString().padStart(2, '0');
           this.display_date = display_date.getDate().toString().padStart(2, '0');
           this.display_hours = display_date.getHours().toString().padStart(2, '0');
           this.display_mins = display_date.getMinutes().toString().padStart(2, '0');
       },
       refreshtripdate: function(event){
           console.log("trip header refresh trip date");
           this.$emit("refreshtripdate");
       }
   }
})

var RouteComponent = Vue.component('route-component', {
  data: function () {
      return {
          hovered: false,
      }
  },
  computed: {
      styles: function() {
          let packing_length = this.route.packing.length;
          return {
              'grid-template-columns': '1fr 3fr 2fr repeat(' + packing_length.toString() + ', minmax(0, 1fr))'
          }
      }
  },
  template:`
  <div @mouseover="hovered=true" @mouseleave="hovered=false" class="my-2 columns col-12 route">
    <transition name="expand">
        <div class="add column col-12" v-show="hovered">
        <!-- route indexes starts from 1 in database but start at 0 here. -->
            <a href="#" class="btn btn-link" v-show="hovered" v-on:click.prevent="showaddroutemodal" v-bind:data-insertIndex="route.index - 1">
            <i class="icon icon-plus mx-2"></i>ADD DESTINATION
            </a>
        </div>
    </transition>
        <input type="checkbox" v-bind:id="'accordion-'+ route.id" name="accordion-checkbox" :checked="minimize" hidden>
        <div class="columns column col-12 p-1">
            <label class="accordion-header column col-10 h5" v-bind:for="'accordion-' + route.id" v-if="route.orderitem_set.length > 0">
                {{ routesorder.indexOf(route.id) + 1 }}. {{ route.orderitem_set[0].customer }}
            </label>
            <label class="accordion-header column col-10 h5" v-bind:for="'accordion-' + route.id" v-else>
                {{ routesorder.indexOf(route.id) + 1 }}.
            </label>
            <a href="#" class="btn btn-link text-right column col-2 do-number h5"
            v-if="route.do_number"
            v-bind:data-route-id="route.id"
            @click="showeditdonumbermodal">{{ route.do_number }}</a>
            <a href="#" class="btn btn-link text-right column col-2 do-number light-caps"
            v-else-if="route.orderitem_set.length > 0"
            v-bind:data-route-id="route.id"
            @click="showeditdonumbermodal">ENTER D/O</a>
        </div>

        <div class="accordion-body columns column col-12">
            <ul v-if="route.orderitem_set.length > 0" class="packing-container column col-12" v-bind:style="styles">
                <li class="packing-empty-space"></li>
                <li v-for="method in route.packing" :key="method" class="border">{{ method }}</li>
                <template v-for="oi in route.orderitem_set">
                    <li class="clickable c-hand" @click="showeditorderitemquantitymodal" v-bind:data-orderitem-id="oi.id">{{ oi.quantity }}</li>
                    <li>{{ oi.customerproduct }}</li>
                    <li class="clickable c-hand" @click="showeditorderitemnotemodal" v-bind:data-orderitem-id="oi.id">{{ oi.note }}</li>
                    <li v-for="method in route.packing"
                    v-if="oi.packing"
                    v-bind:data-orderitem-id="oi.id"
                    class="border clickable c-hand"
                    @click="showeditorderitempackingmodal"
                    v-bind:data-packing-name="method">{{oi.packing[method]}}</li>
                    <li v-else class="border clickable c-hand"
                    v-bind:data-orderitem-id="oi.id"
                    v-bind:data-packing-name="method"
                    @click="showeditorderitempackingmodal"></li>
                </template>
            </ul>

            <div v-show="route.orderitem_set.length > 0" class="divider column col-12"></div>
            <div class="column col-11 note my-1 c-hand h5"
                @click="showeditroutenotemodal"
                v-bind:data-route-id="route.id"
                    v-if="route.note">
                {{ route.note }}
            </div>
            <div class="column col-11 note light-caps my-2 c-hand"
                @click="showeditroutenotemodal"
                v-bind:data-route-id="route.id"
                v-else>
                <i class="icon icon-plus mx-2"></i>ADD A NOTE
            </div>
            <button class="delete btn btn-link column col-1" @click="showdeleteroutemodal">
                <i class="icon icon-delete float-right" v-bind:data-route-id="route.id"></i>
            </button>
        </div>
        <transition name="expand">
            <div class="add column col-12" v-show="hovered" v-if="index + 1 === routesorder.length">
            <!-- route indexes starts from 1 in database but start at 0 here. -->
                <a href="#" class="btn btn-link" v-show="hovered" v-on:click.prevent="showaddroutemodal" v-bind:data-insertIndex="route.index">
                    <i class="icon icon-plus mx-2"></i>ADD DESTINATION
                </a>
            </div>
        </transition>
    </div>
   `,
   props: ['route', 'minimize', 'index', 'routesorder', 'index'],
   components: {
   },
   created: function() {
//       console.log('route-component route prop', this.route.id)
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
       showeditorderitempackingmodal: function(event){
           console.log("show edit orderitem packing modal");
           this.$emit('showeditorderitempackingmodal', event);
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
       }
   }
})

var PackingSum = Vue.component('packing-sum', {
  data: function () {
      return {
          packing_sum: {}
      }
  },
  computed: {
      styles: function() {
          let packing_length = Object.keys(this.packing_sum).length;
          return {
              'grid-template-columns': '1fr 3fr 2fr repeat(' + packing_length.toString() + ', minmax(0, 1fr))'
          }
      }
  },
  template:`
    <div class="packing-sum columns column 12">
        <ul class="packing-container column col-12" v-bind:style="styles">
            <li class="packing-sum-empty-space"></li>
            <li class="border" v-for="(value, name) in packing_sum">{{ name }}</li>
            <li class="packing-sum-empty-space"></li>
            <li class="border" v-for="(value, name) in packing_sum">{{ value }}</li>
        </ul>
    </div>
   `,
   props: ['trip', 'routes'],
   created: function() {
       this.refreshPackingSum();
   },
   watch: {
       routes: function() {
           console.log("routes watcher")
           this.refreshPackingSum();
       },
       trip: function(){
           console.log("trip watcher");
           this.refreshPackingSum();
       }
   },
   methods: {
       refreshPackingSum: function(){
           let packaging_methods = this.trip.packaging_methods.split(',').map(pm => pm.trim())
           this.packing_sum = {};
           console.log(packaging_methods);
           packaging_methods.forEach(pm => { this.$set(this.packing_sum, pm, 0); });
           this.routes.forEach(r => {
               r.orderitem_set.forEach(oi => {
                   if (oi.packing !== null){
                       Object.keys(oi.packing).forEach(k => {
                           this.$set(this.packing_sum, k, this.packing_sum[k] += parseInt(oi.packing[k], 10));
                       });
                   }
               })
           });
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
  <div class="accordion">
      <draggable v-bind="dragOptions" @end="indexchange">
          <route-component v-for="(route, index) in routes"
          :key="route.id"
          :route="route"
          :routesorder="routes_id_ordering"
          :data-attribute-id="route.id"
          :index="index"
          v-bind:minimize="arrangeroutes"
          @showeditorderitemquantitymodal="showeditorderitemquantitymodal"
          @showeditorderitemnotemodal="showeditorderitemnotemodal"
          @showeditorderitempackingmodal="showeditorderitempackingmodal"
          @showdeleteroutemodal="showdeleteroutemodal"
          @showeditdonumbermodal="showeditdonumbermodal"
          @showeditroutenotemodal="showeditroutenotemodal"
          @showaddroutemodal="showaddroutemodal"></route-component>
      </draggable>
  </div>
   `,
   props: ['arrangeroutes', 'trip_id', 'routes'],
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
       showeditorderitempackingmodal: function(event){
           console.log("routes list show orderitem packing modal");
           this.$emit('showeditorderitempackingmodal', event);
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
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
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
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveTripNote">Save</button>
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
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
                <div class="modal-title h5">Edit Quantity</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="orderitem-quantity">Quantity</label>
                  <input class="form-input" type="number" id="orderitem-quantity" placeholder="Enter Quantity" v-model="quantity">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveOrderItemQuantity">Save</button>
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
           console.log("show edit trip note modal");
           this.quantity = null;
           this.$emit('showeditorderitemquantitymodal');
       },
       getOrderItem: async function(){
            var vm = this;
            getOrderItemDetails(this.selected_orderitem_id)
            .then(res => res.json())
            .then(res => this.quantity = res.quantity)
            .catch(e => console.log(e))
            console.log('orderitem quantity set');
       },
       saveOrderItemQuantity: function(event){
           console.log("save orderitem quantity");
           let data = {"quantity": this.quantity};
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
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
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
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveOrderItemNote">Save</button>
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

var OrderItemPackingModal = Vue.component('OrderItemPackingModal', {
  data: function () {
      return {
          packing: null,
          packing_input: null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
                <div class="modal-title h5">Edit {{ selected_orderitem_packing_name }}</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="orderitem-packing">Quantity</label>
                  <input class="form-input" type="number" id="orderitem-packing" placeholder="Enter packing quantity" v-model="packing_input">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveOrderItemPacking">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_orderitem_id', 'selected_orderitem_packing_name'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
               console.log("orderitem id is", this.selected_orderitem_id);
               this.getOrderItem();
               console.log(this.selected_orderitem_packing_name)
           }
       }
   },
   methods: {
       close: function(event) {
           this.$emit('showeditorderitempackingmodal');
       },
       getOrderItem: async function(){
            var vm = this;
            getOrderItemDetails(this.selected_orderitem_id)
            .then(res => res.json())
            .then(res => this.packing = res.packing)
            .then(() => this.packing_input = this.packing[this.selected_orderitem_packing_name])
            .catch(e => console.log(e))
            console.log('orderitem quantity set');
       },
       saveOrderItemPacking: function(event){
           console.log("save orderitem packing");
           this.packing[this.selected_orderitem_packing_name] = this.packing_input;
           let data = {"packing": this.packing};
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
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
                <div class="modal-title h5">Delete Route</div>
            </div>
            <div class="modal-body form-group">Delete this route?</div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="deleteRoute">Confirm</button>
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
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
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
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveDoNumber">Save</button>
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
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
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
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveNote">Save</button>
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


var AddPackingModal = Vue.component('AddPackingModal', {
  data: function () {
      return {
          method:null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" @click="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" @click="close"></a>
                <div class="modal-title h5">Add Packing</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="method">Method</label>
                  <input class="form-input" type="text" id="method" placeholder="Enter Method" v-model="method" maxlength="16">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" @click="close">Cancel</a>
                <button class="btn btn-primary float-right" @click="saveMethod">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'trip_id'],
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       }
   },
   methods: {
       close: function(event) {
           this.$emit('showaddpackingmodal');
       },
       saveMethod: async function(event){
           console.log("save method");
           let packaging_methods = null;
           let trip = await getTripDetails(this.trip_id)
                           .then(res => res.json())
                           .then(res => packaging_methods = res.packaging_methods.split(","))
                           .then(() => packaging_methods = packaging_methods.map(e => e.trim()))

           packaging_methods.push(this.method.trim());

           let data = { packaging_methods: packaging_methods.join() };
           console.log(data)
           putTrip(this.trip_id, data)
           .then(res => res.json())
           .then(() => this.close())
           .catch(e => console.log(e));
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
            @click="hide_autocomplete = !hide_autocomplete">
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
           if (this.route_tab_active){
               let data = {"customer": this.customer_select_id};
               console.log(data);
               postRoute(this.trip_id, data)
               .then(res => res.json())
               .then(res => {
                   if (this.create_route_at_index < this.routes.length) {
                       let rearrange_ids = this.routes.map(r => r.id);
                       // route indexes starts from 1 in database but start at 0 here.
                       rearrange_ids.splice(this.create_route_at_index, 0, res.id);
                       postIndexOrderingData(rearrange_ids, this.trip_id).then(res => res.json());
                   }
               })
               .then(() => this.close());
           }
           if (this.note_tab_active){
               console.log(data);
               let data = {"note": this.route_note};
               postRoute(this.trip_id, data)
               .then(res => res.json())
               .then(res => {
                   if (this.create_route_at_index < this.routes.length) {
                       let rearrange_ids = this.routes.map(r => r.id);
                       // route indexes starts from 1 in database but start at 0 here.
                       rearrange_ids.splice(this.create_route_at_index, 0, res.id);
                       postIndexOrderingData(rearrange_ids, this.trip_id).then(res => res.json());
                   }
               })
               .then(() => this.close());
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
          selected_orderitem_packing_name: null,
          create_route_at_index: null,
          show_edit_trip_note_modal: false,
          show_orderitem_quantity_modal: false,
          show_orderitem_note_modal: false,
          show_orderitem_packing_modal: false,
          show_route_delete_modal: false,
          show_edit_do_number_modal:false,
          show_edit_route_note_modal: false,
          show_add_packing_modal: false,
          show_add_route_modal: false,
      }
  },
  created: function() {
      console.log("created function");
  },
  mounted: async function(){
      this.trip_id = this.$el.getAttribute('data-trip-id');
      this.pdfUrl = this.$el.getAttribute('data-pdf-url');
      this.getTrip();
      this.refreshRoutes(this.trip_id);
  },
  components: {
      'trip-header': TripHeader,
      'routes-list': RouteList,
      'packing-sum': PackingSum,
      'add-route': AddRoute,
      'edit-note-modal': EditNoteModal,
      'edit-orderitem-quantity-modal':OrderItemQuantityModal,
      'edit-orderitem-note-modal': OrderItemNoteModal,
      'edit-orderitem-packing-modal': OrderItemPackingModal,
      'delete-route-modal': RouteDeleteModal,
      'do-number-modal': DoNumberModal,
      'edit-route-note-modal': RouteNoteModal,
      'add-packing-modal': AddPackingModal,
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
       showeditorderitempackingmodal: function(event){
          this.show_orderitem_packing_modal = !this.show_orderitem_packing_modal
          if (this.show_orderitem_packing_modal){
              this.selected_orderitem_packing_name = event.target.getAttribute('data-packing-name')
              this.selected_orderitem_id = event.target.getAttribute('data-orderitem-id')
          }
          if (!this.show_orderitem_packing_modal){
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
      showaddpackingmodal: function(event){
          this.show_add_packing_modal = !this.show_add_packing_modal
              if (this.show_add_packing_modal){
              }
              if (!this.show_add_packing_modal){
                  this.getTrip();
                  this.refreshRoutes(this.trip_id);
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
      deletepacking: function(event){
          this.getTrip();
          this.refreshRoutes(this.trip_id);
      },
      getTrip: async function(){
          getTripDetails(this.trip_id).then(res => res.json()).then(res => this.trip = res)
      },
      getAllRoutes: function(trip_id){
           return getRoutesDetails(this.trip_id);
       },
       rearrangepacking: function(event){
           this.getTrip();
           this.refreshRoutes(this.trip_id);
       },
       refreshRoutes: function(trip_id){
          this.getAllRoutes(this.trip_id)
          .then(res => res.json())
          .then(res => this.routes = res);
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
    let url = 'http://localhost:8000/pos/api/routes/' + route_id + '/update/';
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


async function showArrangeRouteModal(event){
    console.log("Show Arrange Modal");
    let arrangeModal = document.getElementById('arrange-modal');
    let closeModal = document.getElementById('arrange-close');
    let cancelButton = document.getElementById('arrange-cancel-button');
    let arrangeList = document.getElementById('arrange-menu');
    let saveButton = document.getElementById('arrange-save');
    let trip_id = arrangeModal.getAttribute('data-trip-id');
    let url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/detail/routes/';
    var response = await fetch(url, {
      method: 'GET', // or 'PUT'
    });
    var resp_json = await response.json();
    resp_json.forEach(function(route){
        let route_id = route.id;
        let route_index = route.index;
        let listItem = document.createElement('li');
        listItem.classList.add('menu-item')
        listItem.setAttribute('data-route-id', route_id)
        let listAnchor = document.createElement('a');
        if (route.orderitem_set.length > 0){
            listAnchor.innerHTML = route.orderitem_set[0].customer;
        } else  {
            listAnchor.innerHTML = route.note;
        }
        let listIcon = document.createElement('i');
        listIcon.classList.add('icon-menu');
        listAnchor.appendChild(listIcon);
        listItem.appendChild(listAnchor);
        arrangeList.appendChild(listItem);
    });
    console.log(resp_json);
    arrangeModal.classList.add("active");
    closeModal.addEventListener("click", function(e){
        closeArrangeRouteModal();
    }, false);
    cancelButton.addEventListener("click", function(e){
        closeArrangeRouteModal();
    }, false);
    saveButton.addEventListener("click", function(e){
        arrangeRoutes(trip_id);
    })
}

function postIndexOrderingData(index_ordering_array, trip_id){
    console.log("index ordering array", index_ordering_array);
    let url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/routes/arrange/';
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
    let url ='http://localhost:8000/pos/api/routes/' + route_id + '/';
    let response = fetch(url, {
      method: 'GET', // or 'PUT'
    }).catch(e => console.log(e));
    return response;
}

function generateEditRouteForm(routeJson){
    console.log("Generate Route Form");
    console.log(routeJson);

    let packing_methods = routeJson.packing
    let orderitems = routeJson.orderitem_set;

    let route_form = document.getElementById('edit-modal-body');



    for (var i = 0 ; i < orderitems.length; i++){
        let orderitem = orderitems[i];
        let oi_packing = orderitem.packing;
        console.log(oi_packing);

        var container = document.createElement('form');
        container.classList.add('orderitem-form');
        container.setAttribute('data-orderitem-id', orderitem.id);

        let main_container = document.createElement('div');
        main_container.classList.add('column', 'col-12', 'my-1');
        main_container.style.display = "flex";

        let quantity_div = document.createElement('input');
        quantity_div.value = orderitem.quantity;
        quantity_div.classList.add('form-input');
        quantity_div.style.flex = "1";
        quantity_div.name = 'quantity';

        let customerproduct_div = document.createElement('label');
        customerproduct_div.classList.add('form-label');
        customerproduct_div.classList.add('px-2');
        customerproduct_div.innerHTML = orderitem.customerproduct;
        customerproduct_div.style.flex = "5";

        let orderitem_note_div = document.createElement('input');
        orderitem_note_div.classList.add('form-input');
        orderitem_note_div.style.flex = "5";
        orderitem_note_div.value = orderitem.note;
        orderitem_note_div.name = 'note';
        orderitem_note_div.placeholder = "Note";

        main_container.appendChild(quantity_div);
        main_container.appendChild(customerproduct_div);
        main_container.appendChild(orderitem_note_div);
        container.appendChild(main_container);
        route_form.appendChild(container);

        let packing_container = document.createElement('form');
        packing_container.classList.add('column', 'col-12', 'my-1', 'orderitem-packing-form');
        packing_container.setAttribute("data-orderitem-id", orderitem.id);
        packing_container.style.display = "flex";
        packing_container.style.justifyContent = "space-between";
        packing_container.style.flexBasis = "0";
        packing_container.style.flexGrow = "1";

        for (var j = 0; j < packing_methods.length; j++){
            let method = packing_methods[j];
            let packing = document.createElement('input');
            packing.classList.add('form-input', 'input-sm');
            if (j !== 0){
                packing.style.marginLeft = ".2rem";
            }
            packing.name = packing_methods[j];
            packing.placeholder = packing_methods[j];
            if (oi_packing && oi_packing[packing.name]){
                packing.value = oi_packing[packing.name];
            }
            packing_container.appendChild(packing);

            route_form.appendChild(packing_container);
        }

    }

    let note_form = document.createElement('form');
    note_form.classList.add('route-form', 'column', 'col-12');
    note_form.setAttribute('data-route-id', routeJson.id);

    let note_label = document.createElement('label');
    note_label.classList.add('form-label');
    note_label.innerHTML = "Note"
    note_form.appendChild(note_label);

    let note_input = document.createElement('input');
    note_input.classList.add('form-input');
    note_input.value = routeJson.note;
    note_input.name = 'route-note';
    note_form.appendChild(note_input);
    route_form.appendChild(note_form);
}


function updateOrderitemData(orderitemJson, orderitem_packing){
    var orderitem_id = orderitemJson.id;
    var orderitem_node = document.querySelector(".orderitem-container[data-orderitem-id='" + orderitem_id + "']");
    var packing_node = document.querySelector(".packing-container[data-orderitem-id='" + orderitem_id + "']");
    orderitem_node.innerHTML = "";
    packing_node.innerHTML = "";

    var quantity = document.createElement('li');
    quantity.innerHTML = orderitemJson.quantity;
    quantity.style.flex = "1";

    var customerproduct = document.createElement('li');
    customerproduct.innerHTML = orderitemJson.customerproduct;
    customerproduct.style.flex = "8";

    if (orderitemJson.note !== "" && orderitemJson.note !== "None" && orderitemJson.note !== null){
        customerproduct.innerHTML += ' \uD83E\uDC52 ' + orderitemJson.note;
    }

    orderitem_node.appendChild(quantity);
    orderitem_node.appendChild(customerproduct);

    var packing = orderitemJson.packing;
    for (var i = 0 ; i < orderitem_packing.length; i++){
        var packing_name = orderitem_packing[i];
        var packing_label = document.createElement('li');
        packing_label.style.flex = "1";
        packing_label.style.textAlign = "center";
        if (packing[packing_name]){
            packing_label.innerHTML = packing[packing_name];
        } else {
            packing_label.innerHTML = "";
        }
        packing_node.appendChild(packing_label);
    }

}


function closeModalWindow(){
    var modal = document.getElementById('edit-modal');
    modal.classList.remove('active');
    clearEditForm();
}

function clearEditForm(){
    let route_form = document.getElementById('edit-modal-body');
    route_form.innerHTML = '';
}

async function getTripPackingSum(){
    var total_packing_sum = document.getElementById('total-packing-sum');
    var trip_id = total_packing_sum.getAttribute('data-trip-id');
    total_packing_sum.innerHTML = "";
    fetch('http://localhost:8000/pos/api/trip/' + trip_id + '/packingsum/')
        .then(res => res.json())
        .then(function(response){
            console.log(total_packing_sum);
            console.log(response);
            let empty_space = document.createElement('li');
            empty_space.classList.add('packing-sum-empty-space');
            total_packing_sum.appendChild(empty_space);
            for (var packing in response){
                let label_name = document.createElement('li');
                label_name.classList.add('border');
                label_name.innerHTML = packing;
                total_packing_sum.appendChild(label_name);
                console.log(label_name);
            }

            for (var packing in response){
                let label_qty = document.createElement('li');
                label_qty.innerHTML = response[packing];
                label_qty.classList.add('border');
                total_packing_sum.appendChild(label_qty);
            }
        });
}

async function addRouteToTrip(event){
    event.preventDefault();
    var customerInput = document.getElementById('customer');
    var noteInput = document.getElementById('note');
    var customerId;
    var data;

    if (customerInput.value === '' && noteInput.value === ''){
        console.log("Both empty");
    } else if (customerInput.value != '' && noteInput.value == ''){
        customerId = getCustomerId(customerInput.value);
        data = { 'customer': customerId, 'note': '' };
        var route = await postRoute(data);
        console.log(route);
        addRouteCardDOM(route);
    } else if (customerInput.value === '' && noteInput.value != ''){
        data = { 'note': noteInput.value };
        var route = await postRoute(data);
        console.log(route);
        addRouteCardDOM(route);
    } else if (customerInput.value != '' && noteInput.value != '') {
        customerId = getCustomerId(customerInput.value);
        data = { 'customer': customerId, 'note': noteInput.value };
        var route = await postRoute(data);
        console.log(route);
        addRouteCardDOM(route);
    }
    customerInput.value = "";
    noteInput.value = "";
    console.log(customerInput);
    console.log(customerId);
}


function addRouteCardDOM(route) {
//    console.log(route);
    var route_id = route.id;
    var route_index = route.index;
    var orderitem_set = route.orderitem_set;
    var packing_label = Array.from(document.getElementsByClassName('packing-label')).map(e => e.innerHTML);
    var route_note = route.note;
    var do_number = route.do_number;

    if (orderitem_set.length > 0){
        var customer_name = orderitem_set[0].customer;
        var route_fragment = document.createDocumentFragment();

        var route_div = document.createElement('div');
        route_div.classList.add('columns', 'col-12', 'route');
        route_div.setAttribute('data-route-id', route_id);

        var customer_heading = document.createElement('div');
        customer_heading.innerHTML = `${route_index}. ${customer_name}`;
        customer_heading.classList.add('h4', 'column', 'col-ml-auto');
        customer_heading.style.display = 'inline';

        var do_number_div = document.createElement('a');
        do_number_div.innerHTML = do_number;
        do_number_div.classList.add('btn', 'btn-link', 'text-right', 'column', 'col-2', 'do-number');
        do_number_div.style.display = 'inline';
        do_number_div.setAttribute('data-route-id', route_id);

        var card_header = document.createElement('div');
        card_header.classList.add('column', 'col-12');
        card_header.appendChild(customer_heading);
        if (do_number !== '' && do_number !== null){
            card_header.appendChild(do_number_div);
        }

        route_div.appendChild(card_header);

        var route_ul = document.createElement('ul');
        route_ul.classList.add('packing-container','column', 'col-12');
        route_ul.style.setProperty('grid-template-columns', '1fr 3fr 2fr repeat(' + packing_label.length + ', minmax(0, 1fr))');
        console.log(packing_label);
        packing_label.forEach(function(label){
            var orderitem_li = document.createElement('li');
            orderitem_li.innerHTML = label;
            route_ul.appendChild(orderitem_li);
        });
//        route_div.appendChild(route_ul);

        orderitem_set.forEach(function(item){
//            console.log(item);
            var orderitem_id = item.id;
            var orderitem_qty = item.quantity;
            var orderitem_name = item.customerproduct;
            var orderitem_note = item.note;
            var orderitem_packing = item.packing;

            var orderitem_qty_li = document.createElement('li')
            orderitem_qty_li.innerHTML = orderitem_qty;
            route_ul.appendChild(orderitem_qty_li);

            var orderitem_name_li = document.createElement('li')
            orderitem_name_li.innerHTML = orderitem_name;
            route_ul.appendChild(orderitem_name_li);

            var orderitem_note_li = document.createElement('li')
            if (orderitem_note !== "" && orderitem_note !== "None" && orderitem_note !== null){
                orderitem_note_li.innerHTML = orderitem_note;
            } else {
                orderitem_note_li.innerHTML = "";
            }
            route_ul.appendChild(orderitem_note_li);

            for (var i = 0 ; i < packing_label.length; i++){
                var packing_name = packing_label[i];
                var label = document.createElement('li');
                label.classList.add('border');

                if (orderitem_packing){
                    if (orderitem_packing[packing_name]){
                        label.innerHTML = orderitem_packing[packing_name];
                    } else {
                        label.innerHTML = "";
                    }
                }
                route_ul.appendChild(label);
            }
            route_div.appendChild(route_ul);
        });

        var note_spacing = document.createElement('div');
        note_spacing.classList.add('column', 'col-12', 'divider');
        var note_heading = document.createElement('h5');
        note_heading.classList.add('column', 'col-11', 'note');
        note_heading.innerHTML = route_note;
        note_heading.setAttribute('data-route-id', route_id);
        var route_delete = document.createElement('a');
        route_delete.classList.add('btn', 'btn-link', 'column', 'col-1');
        route_delete.addEventListener("click", deleteRoute , false);
        var delete_icon = document.createElement('i');
        delete_icon.classList.add('icon', 'icon-delete', 'float-right');
        route_delete.appendChild(delete_icon);

        route_div.appendChild(note_spacing);
        route_div.appendChild(note_heading);
        route_div.appendChild(route_delete);
        route_fragment.appendChild(route_div);
        route_div.addEventListener("click", showEditRouteModal , false);
        var routes = document.getElementById('routes');
        routes.appendChild(route_fragment);
    } else {

        var note_div = document.createElement('div');
        note_div.classList.add('columns', 'col-12', 'route');
        note_div.setAttribute('data-route-id', route_id);

        var customer_index = document.createElement('div');
        customer_index.classList.add('h4', 'column', 'col-ml-auto');
        customer_index.style.display = 'inline';
        customer_index.innerHTML = route_index.toString() + ".";

        var divider = document.createElement('div');
        divider.classList.add('column', 'col-12', 'divider');

        var note_h5 = document.createElement('h5');
        note_h5.classList.add('column', 'col-11', 'note');
        note_h5.innerHTML = route_note;
        note_h5.setAttribute('data-route-id', route_id);

        var del_anchor = document.createElement('a');
        del_anchor.addEventListener("click", deleteRoute , false);
        del_anchor.classList.add('btn', 'btn-link', 'column', 'col-1');


        var del_icon = document.createElement('i');
        del_icon.classList.add('icon', 'icon-delete', 'float-right');

        note_div.appendChild(customer_index);
        note_div.appendChild(divider);
        del_anchor.appendChild(del_icon);
        note_div.appendChild(note_h5);
        note_div.appendChild(del_anchor);
        note_div.addEventListener("click", showEditRouteModal , false);
        var routes = document.getElementById('routes');
        routes.appendChild(note_div);
    }
}


function postOrderItemData(orderitem_id, data){
    console.log("post order item data");
    var url = 'http://localhost:8000/pos/api/orderitem/' + orderitem_id + '/update/';
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
    var url = 'http://localhost:8000/pos/api/routes/' + route_id + '/update/';
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
    var url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/detail/routes/add/';
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
    let url = 'http://localhost:8000/pos/api/trip/update/' + trip_id.toString() + '/';
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
    let url = 'http://localhost:8000/pos/api/routes/' + route_id + '/delete/';
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
    let url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/';
    var response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    return response;
}

function getRoutesDetails(trip_id){
    console.log("Get Routes Details");
    let url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/detail/routes/';
    var response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    return response;
}

function getOrderItemDetails(orderitem_id){
    console.log("Get OrderItem Details");
    let url = 'http://localhost:8000/pos/api/orderitem/' + orderitem_id + '/';
    var response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    return response;
}

async function getCustomers(){
    console.log("Get Customer Details");
    let url = 'http://localhost:8000/pos/api/customers/';
    var response = await fetch(url, {
      method: 'GET', // or 'PUT'
    });
    var resp_json = await response.json();
//    console.log(resp_json);
    return resp_json;
}