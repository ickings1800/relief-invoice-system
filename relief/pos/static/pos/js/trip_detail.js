//var el;
const draggable = window['vuedraggable'];
const origin = location.origin;

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
        <button class="btn btn-action btn-link btn-lg" v-on:click.prevent="prevMonth">
          <i class="icon icon-arrow-left"></i>
        </button>
        <div class="navbar-primary">{{ months_of_year[selectedDate_month] }} {{ selectedDate_year }}</div>
        <button class="btn btn-action btn-link btn-lg" v-on:click.prevent="nextMonth">
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
            <button class="date-item" v-on:click.prevent="clickPrevMonth(date)">{{ date.getDate() }}</button>
          </div>

          <!-- calendar current month -->
          <div v-for="date in days_of_month"
          class="calendar-date"
          v-bind:class="{ 'range-start': selectDate(date), 'calendar-range': selectDate(date) , 'range-end': selectDate(date) }">
            <button class="date-item"
            v-on:click.prevent="selectedDate = date"
            v-bind:class="{ 'date-today': date.getTime() === todayDate.getTime() }">
            {{ date.getDate() }}
            </button>
          </div>

          <!-- calendar next month -->
          <div v-for="date in next_month" class="calendar-date next-month">
            <button class="date-item" v-on:click.prevent="clickNextMonth(date)">{{ date.getDate() }}</button>
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
            <button class="btn btn-primary column col-4 text-center" v-on:click.prevent="saveDate">Save</button>
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
        <h2 class="clickable c-hand" v-if="trip" v-on:click.prevent="dropdown_active = !dropdown_active">
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
    <draggable v-bind="dragOptions" @end="packingrearrange" class="display-no-print">
        <span v-for="pm in packaging_methods"
            @mouseover="hovered_methods[pm] = true"
            @mouseleave="hovered_methods[pm] = false"
            :key="pm"
            class="chip c-hand packing-item"
            v-bind:data-attribute-packing="pm">
            {{ pm }}
            <a href="#" v-show="hovered_methods[pm]" key="pm" class="btn btn-clear" aria-label="Close" role="button" v-on:click.prevent="deletepacking(pm, $event)"></a>
        </span>
        <span class="chip"><a href="#"><i class="icon icon-plus m-1" v-on:click.prevent="addpacking"></i></a></span>
    </draggable>
    <div>
        <button class="c-hand clickable btn btn-link" v-if="trip && trip.notes !== null" v-on:click.prevent="showedittripnotemodal" id="trip-notes">{{ trip.notes }}</button>
        <button class="btn btn-link c-hand h5 display-no-print" v-else v-on:click.prevent="showedittripnotemodal">Add a note</button>
        <button class="btn btn-sm d-block display-no-print" v-on:click="rearrange" href="#">Expand/Collapse</button>
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
           console.log("DELETE PACKING", this.packaging_methods);
           let data = { "packaging_methods": null }
           if (this.packaging_methods.length > 0){
               data = { "packaging_methods": this.packaging_methods.join(",") };
           }
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
           if (this.trip.packaging_methods !== null && this.trip.packaging_methods !== "") {
               this.hovered_methods = { };
               if (this.trip.packaging_methods.indexOf(",") === -1) {
                   console.log("no comma");
                   this.packaging_methods = [this.trip.packaging_methods.trim()]
                   this.$set(this.hovered_methods, this.packaging_methods, false);
               } else {
                   console.log("comma")
                   this.packaging_methods = this.trip.packaging_methods.split(",").map(pm => pm.trim());
                   this.trip.packaging_methods.split(",").map(pm => { this.$set(this.hovered_methods, pm.trim(), false )});
               }
           } else {
               this.packaging_methods = [];
           }
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
          checked: false,
      }
  },
   computed: {
      packingLength: function() {
          console.log("Route Component Trip Watcher Packaging Method")
          console.log("PACKING:", this.packing_methods);
          if (this.packing_methods === null || this.packing_methods === ""){
                console.log("packing methods is empty or null");
                let packing_arr = [];
                console.log("Packing array length: ", packing_arr.length)
                return {'grid-template-columns': '2fr 4fr' };
          }
          else {
              console.log("NOT NULL", this.packing_methods);
              if (this.packing_methods.indexOf(",") === -1){
                  let packing_arr = [this.packing_methods];
                  return {'grid-template-columns':'2fr 4fr repeat(' + packing_arr.length + ', minmax(0, 1fr))'};
              } else {
                  let packing_arr = this.packing_methods.split(",");
                  return {'grid-template-columns': '2fr 4fr repeat(' + packing_arr.length + ', minmax(0, 1fr))'};
              }
          }
      }
   },
  template:`
  <div @mouseover="hovered=true" @mouseleave="hovered=false" class="my-2 columns col-12 route">
        <transition name="expand">
            <div class="add column col-12 display-no-print" v-show="hovered">
            <!-- route indexes starts from 1 in database but start at 0 here. -->
                <a href="#" class="btn btn-link" v-show="hovered" v-on:click.prevent="showaddroutemodal" v-bind:data-insertIndex="route.index - 1">
                <i class="icon icon-plus mx-2"></i>ADD DESTINATION
                </a>
            </div>
        </transition>
        <input type="checkbox" v-bind:id="'accordion-'+ route.id" name="accordion-checkbox" :checked="minimize" hidden>
        <div class="columns column col-12 p-1">
            <label class="accordion-header column col-10 h5" v-bind:for="'accordion-' + route.id" v-if="route.orderitem_set.length > 0">
                <label class="form-checkbox d-inline display-no-print"><input type="checkbox" v-on:click="checkRoute(route.id)" v-model="checked"><i class="form-icon m-1"></i></label>
                {{ routesorder.indexOf(route.id) + 1 }}. {{ route.orderitem_set[0].customer }}
            </label>
            <label class="accordion-header column col-10 h5" v-bind:for="'accordion-' + route.id" v-else>
                {{ routesorder.indexOf(route.id) + 1 }}.
            </label>
            <a href="#" class="btn btn-link text-right column col-2 do-number h5"
            v-if="route.do_number"
            v-bind:data-route-id="route.id"
            v-on:click.prevent="showeditdonumbermodal">{{ route.do_number }}</a>
            <a href="#" class="btn btn-link text-right column col-2 do-number light-caps display-no-print"
            v-else-if="route.orderitem_set.length > 0"
            v-bind:data-route-id="route.id"
            v-on:click.prevent="showeditdonumbermodal">ENTER D/O</a>
        </div>

        <div class="accordion-body columns column col-12">
            <ul v-if="route.orderitem_set.length > 0" class="packing-container column col-12" v-bind:style="packingLength">
                <li class="packing-empty-space"></li>
                <li v-for="method in route.packing" :key="method" class="border">{{ method }}</li>
                <template v-for="oi in route.orderitem_set">
                     <li class="clickable c-hand"
                        v-on:click.stop="showeditorderitemquantitymodal"
                         v-bind:data-orderitem-id="oi.id">
                         <!-- span element may be clicked instead of li, bind orderitem id for edit quantity modal -->
                         <span v-bind:data-orderitem-id="oi.id">{{ oi.quantity }}</span>
                         <span v-bind:data-orderitem-id="oi.id" class="display-no-print">
                             &nbsp;&#8594;&nbsp;{{ oi.driver_quantity }}
                         </span>
                     </li>
                    <li class="clickable c-hand"
                         v-on:click.prevent="showeditorderitemnotemodal"
                         v-bind:data-orderitem-id="oi.id"
                         v-if="oi.note">
                         {{ oi.customerproduct }}&#8594;{{ oi.note }}
                     </li>
                    <li class="clickable c-hand"
                         v-on:click.prevent="showeditorderitemnotemodal"
                         v-bind:data-orderitem-id="oi.id"
                         v-else>
                         {{ oi.customerproduct }}
                     </li>
                    <li v-for="method in route.packing"
                    v-if="oi.packing"
                    v-bind:data-orderitem-id="oi.id"
                    class="border clickable c-hand"
                    v-on:click.prevent="showeditorderitempackingmodal"
                    v-bind:data-packing-name="method">{{oi.packing[method]}}</li>
                    <li v-else class="border clickable c-hand"
                    v-bind:data-orderitem-id="oi.id"
                    v-bind:data-packing-name="method"
                    v-on:click.prevent="showeditorderitempackingmodal"></li>
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
        <transition name="expand" class="display-no-print">
            <div class="add column col-12 display-no-print" v-show="hovered" v-if="index + 1 === routesorder.length">
            <!-- route indexes starts from 1 in database but start at 0 here. -->
                <a href="#" class="btn btn-link" v-show="hovered" v-on:click.prevent="showaddroutemodal" v-bind:data-insertIndex="route.index">
                    <i class="icon icon-plus mx-2"></i>ADD DESTINATION
                </a>
            </div>
        </transition>
    </div>
   `,
   props: ['route', 'minimize', 'index', 'routesorder', 'index', 'packing_methods'],
   components: {
   },
   mounted: function (){
   },
   created: function() {
       this.checked = this.route.checked;
//       console.log('route-component route prop', this.route.id)
   },
   methods: {
       checkRoute: function(event){
           console.log("check route");
           let data = { "checked": !this.checked };
           let route_id = event;
           putRouteData(route_id, data)
           .then(res => res.json())
           .then(res => this.checked = res.checked);
       },
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
          packing_sum: {},
          packing_arr: [],
      }
  },
  computed: {
      packingLength: function() {
          console.log("Route Component Trip Watcher Packaging Method")
          console.log("PACKING:", this.packing_methods);
          if (this.packing_methods === null || this.packing_methods === ""){
                console.log("packing methods is empty or null");
                console.log("Packing array length: ", this.packing_arr.length)
                return {'grid-template-columns': '2fr 4fr'};
          }
          else {
              console.log("NOT NULL", this.packing_methods);
              if (this.packing_methods.indexOf(",") === -1){
                  this.packing_arr = [this.packing_methods.trim()];
                  return {'grid-template-columns':'2fr 4fr repeat(' + this.packing_arr.length + ', minmax(0, 1fr))'};
              } else {
                  this.packing_arr = this.packing_methods.split(",").map(pm => pm.trim());
                  return {'grid-template-columns': '2fr 4fr repeat(' + this.packing_arr.length + ', minmax(0, 1fr))'};
              }
          }
      }
  },
  template:`
    <div class="packing-sum columns column 12">
        <ul class="packing-container column col-12" v-bind:style="packingLength">
            <li class="packing-sum-empty-space"></li>
            <li class="border" v-for="name in packing_arr">{{ name }}</li>
            <li class="packing-sum-empty-space"></li>
            <li class="border" v-for="name in packing_arr">{{ packing_sum[name] }}</li>
        </ul>
    </div>
   `,
   props: ['trip', 'routes', 'packing_methods'],
   created: function() {
   },
   mounted: function() {
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
       },
   },
   methods: {
       refreshPackingSum: function(){
           this.packing_sum = {};
           this.packing_arr = [];
           if (this.packing_methods !== null){
               if (this.packing_methods.indexOf(",") === -1){
                   this.packing_arr = [this.packing_methods.trim()];
               } else {
                   this.packing_arr = this.packing_methods.split(",").map(pm => pm.trim());
               }
               this.packing_arr.forEach(pm => { this.$set(this.packing_sum, pm, 0); });
               this.routes.forEach(r => {
                   r.orderitem_set.forEach(oi => {
                       if (oi.packing !== null){
                           Object.keys(oi.packing).forEach(k => {
                               let parsedPackingQty = parseInt(oi.packing[k], 10);
                               if (isNaN(parsedPackingQty)) { parsedPackingQty = 0 }
                               this.$set(this.packing_sum, k, this.packing_sum[k] += parsedPackingQty);
                           });
                       }
                   })
               });
           }
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
          :packing_methods="packing_methods"
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
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit Quantity</div>
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
                this.quantity = res.quantity;
                this.driver_quantity = res.driver_quantity;
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

var OrderItemPackingModal = Vue.component('OrderItemPackingModal', {
  data: function () {
      return {
          packing: {},
          packing_input: null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Edit {{ selected_orderitem_packing_name }}</div>
            </div>
            <div class="modal-body form-group">
            <!-- form input control -->
                <div class="form-group">
                  <label class="form-label" for="orderitem-packing">Quantity</label>
                  <input class="form-input" type="number" id="orderitem-packing" placeholder="Enter packing quantity" v-model.number="packing_input">
                </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveOrderItemPacking">Save</button>
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
            .then(res => { this.packing = {}; if (res.packing) { this.packing = res.packing } })
            .then(() => this.packing_input = this.packing[this.selected_orderitem_packing_name])
            .catch(e => console.log(e))
            console.log('orderitem quantity set');
       },
       saveOrderItemPacking: function(event){
           console.log("save orderitem packing");
           this.packing[this.selected_orderitem_packing_name] = this.packing_input;
           let data = {'packing': this.packing};
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


var AddPackingModal = Vue.component('AddPackingModal', {
  data: function () {
      return {
          method:null,
      }
  },

  template:`
    <div class="modal modal-sm" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
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
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="saveMethod">Save</button>
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
           let packaging_methods = [];
           let trip = await getTripDetails(this.trip_id)
                           .then(res => res.json())
                           .then(res => { if (res.packaging_methods) { packaging_methods = res.packaging_methods.split(",") } })
                           .then(res => { if (packaging_methods) { packaging_methods = packaging_methods.map(e => e.trim()) }})


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
          packing_methods: null,
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
   watch: {
       trip: function(val){
           if (val) {
               this.packing_methods = this.trip.packaging_methods;
           }
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
          .then(res => this.routes = res)
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

function getRoutesDetails(trip_id){
    console.log("Get Routes Details");
    let url = origin + '/pos/api/trips/' + trip_id + '/detail/routes/';
    var response = fetch(url, {
      method: 'GET', // or 'PUT'
    });
    console.log(url);
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