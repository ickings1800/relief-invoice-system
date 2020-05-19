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
            <button class="btn btn-primary column col-4 text-center" @click="saveDate">Set</button>
       </div>
      </div>
    </div>
   `,
   props: ['active', 'date'],
   components: {  },
   created: function(){
       this.resetCalendar(this.date);
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
            this.resetCalendar(this.date);
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
       resetCalendar: function(date){
            this.selectedDate = new Date(date);
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
           this.$emit("update:trip_date", new Date(this.selectedDate.setHours(H,M,0,0)));
           this.closeCalendar();
       }
   }
})

var CreateTripModal = Vue.component('CreateTripModal', {
  data: function () {
      return {
          dropdown_active: false,
          display_year: null,
          display_month: null,
          display_date: null,
          display_hours: null,
          display_mins: null,
          trip_date: null,
      }
  },

  template:`
      <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Create Trip</div>
            </div>
            <div class="modal-body form-group" v-bind:style="{ 'overflow-y': 'unset' }">
            <!-- basic dropdown button -->
            <div class="dropdown" v-bind:class="{ active: dropdown_active }">
                <h2 class="clickable c-hand" @click="dropdown_active = !dropdown_active">
                {{ display_date }}-{{ display_month }}-{{ display_year }} {{ display_hours }}:{{ display_mins }}
                </h2>
                <!-- menu component -->
                <div class="menu" v-bind:style="{'overflow-y': 'unset'}" v-bind:class="{ 'd-none': !dropdown_active }">
                    <calendar v-bind:active="dropdown_active"
                     v-on:update:active="dropdown_active=$event"
                      v-bind:date="trip_date"
                       v-on:update:trip_date="trip_date=$event"></calendar>
                </div>
            </div>
            </div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="createTrip">Save</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened'],
   created: function() {
        this.trip_date = new Date();
   },
   components: {'calendar': Calendar},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       },
       trip_date: function(val){
           console.log(this.trip_date);
           let round_5_mins = Math.ceil(this.trip_date.getMinutes()/5) * 5;
           if (round_5_mins === 60){
               round_5_mins = 0;
           }
           this.trip_date.setMinutes(round_5_mins);
           this.setDisplayDate(this.trip_date);
       }
   },
   methods: {
       close: function(){
           this.$emit('showcreatetripmodal');
           this.trip_date = new Date();
       },
       createTrip: function(event){
           let d = this.display_date
           // javascript getMonth starts from zero index, backend requires start by one index
           let m = this.display_month
           let Y = this.display_year
           let H = this.display_hours;
           let M = this.display_mins;
           let data = {'date': `${d}-${m}-${Y} ${H}:${M}`};
           createTrip(data).then(res => res.json()).then(() => this.close()).then(() => this.$emit("refreshtrips"));
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
   }
})


var DeleteTripModal = Vue.component('DeleteTripModal', {
  data: function () {
      return {
      }
  },

  template:`
      <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Delete Trip</div>
            </div>
            <div class="modal-body form-group">Delete this trip?</div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="deleteTrip">Delete</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_trip_id'],
   created: function() {
   },
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       },
   },
   methods: {
       close: function(){
           this.$emit('showdeletetripmodal');
       },
       deleteTrip: function(event){
           deleteTrip(this.selected_trip_id)
           .then(() => this.$emit('refreshtrips'))
           .then(() => this.close());
       },
   }
})


var DuplicateTripModal = Vue.component('DuplicateTripModal', {
  data: function () {
      return {
      }
  },

  template:`
      <div class="modal" v-bind:class="{ active: opened }">
        <a href="#close" class="modal-overlay" aria-label="Close" v-on:click.prevent="close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#" class="btn btn-clear float-right" aria-label="Close" v-on:click.prevent="close"></a>
                <div class="modal-title h5">Copy Trip</div>
            </div>
            <div class="modal-body form-group">Copy this trip?</div>
            <div class="modal-footer">
                <a href="#" class="btn btn-link" v-on:click.prevent="close">Cancel</a>
                <button class="btn btn-primary float-right" v-on:click.prevent="duplicateTrip">Confirm</button>
            </div>
        </div>
    </div>
   `,
   props: ['opened', 'selected_trip_id'],
   created: function() {
   },
   components: {},
   watch: {
       opened: function(val){
           if (val) {
               console.log("opened is true");
           }
       },
   },
   methods: {
       close: function(){
           this.$emit('showduplicatetripmodal');
       },
       duplicateTrip: function(event){
           duplicateTrip(this.selected_trip_id)
           .then(() => this.$emit('refreshtrips'))
           .then(() => this.close());
       },
   }
})



var TripList = Vue.component('TripList', {
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
                <h2>Trips</h2>
            </div>
            <div class="column col-mr-auto"></div>
            <div class="column col-3">
                <a class="btn btn-primary btn-sm float-right button-action" v-on:click.prevent="$emit('showcreatetripmodal')">
                    <i class="icon icon-plus"></i>&nbsp;Create
                </a>
            </div>
        </div>
        <div class="columns">
            <div class="column col-12">
                <table class="table">
                    <tr v-for="trip in trips">
                        <td>
                            <a v-bind:href="trip.url" class="btn btn-link" v-bind:class="highlight(trip.route_set)" >{{ dateFormatted(trip.date) }}</a>
                            <a href="#" class="btn btn-link float-right mx-2" v-on:click.prevent="$emit('showdeletetripmodal', trip.pk)">
                                <i class="icon icon-delete"></i>
                            </a>
                            <a href="#" class="btn btn-link float-right mx-2" v-on:click.prevent="$emit('showduplicatetripmodal', trip.pk)">
                                <i class="icon icon-copy"></i>
                            </a>
                        </td>
                    </tr>
                </table>
                <div v-if="trips.length === 0" class="empty">
                      <p class="empty-title h5">You have no trips.</p>
                        <p class="empty-subtitle">Click the button to create one.</p>
                      <div class="empty-action">
                            <a href="#" class="btn btn-primary btn-sm button-action" v-on:click.prevent="$emit('showcreatetripmodal')">
                                <i class="icon icon-plus"></i>&nbsp;Create
                            </a>
                      </div>
                </div>
            </div>
        </div>
    </div>
  `,
   props: ['trips'],
   components: {},
   methods: {
      dateFormatted: function(dateString) {
           let dateObj = new Date(dateString);
           let d = dateObj.getDate().toString().padStart(2, '0');
           // javascript getMonth starts from zero index, backend requires start by one index
           let m = (dateObj.getMonth() + 1).toString().padStart(2, '0');
           let Y = dateObj.getFullYear();
           let H = dateObj.getHours().toString().padStart(2, '0');
           let M = dateObj.getMinutes().toString().padStart(2, '0');
           return `${d}-${m}-${Y} ${H}:${M}`
       },
      highlight: function(route_set){
          if (route_set.some(r => r.checked === false)) return 'bg-warning'
          return 'bg-success'
      }
   }
})



var app = new Vue({
  el: '#app',
  data: function () {
      return {
          trips: [],
          show_trip_create_modal: false,
          show_trip_delete_modal: false,
          show_trip_duplicate_modal: false,
          selected_trip_id: null,
      }
  },
  created: function() {
      console.log("created function");
      this.getAllTrips();
  },
  components: {
      'create-trip-modal': CreateTripModal,
      'delete-trip-modal': DeleteTripModal,
      'duplicate-trip-modal': DuplicateTripModal,
      'trip-list': TripList,
  },
  methods: {
      showcreatetripmodal: function(event){
          console.log("show create trip modal");
          this.show_trip_create_modal = !this.show_trip_create_modal
          if (this.show_trip_create_modal){
          }
          if (!this.show_trip_create_modal){
//              this.getAllProducts()
          }
      },
      showdeletetripmodal: function(event){
          console.log("show delete trip modal");
          this.show_trip_delete_modal = !this.show_trip_delete_modal
          if (this.show_trip_delete_modal){
              this.selected_trip_id = event;
          }
          if (!this.show_trip_delete_modal){
          }
      },
      showduplicatetripmodal: function(event){
          console.log("show duplicate trip modal");
          this.show_trip_duplicate_modal = !this.show_trip_duplicate_modal
          if (this.show_trip_duplicate_modal){
              this.selected_trip_id = event;
          }
          if (!this.show_trip_duplicate_modal){
          }
      },
      getAllTrips: function() {
          getAllTrips().then(res => res.json()).then(res => this.trips = res);
      },
      refreshtrips: function() {
          console.log("refresh trips");
          this.getAllTrips();
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

function getAllTrips() {
      let url = origin + '/pos/api/trips/';
      let response = fetch(url, {
          method: 'GET', // or 'PUT'
      });
      return response;
}

function createTrip(data){
    let url = origin + '/pos/api/trip/create/';
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

function deleteTrip(trip_id){
    let url = origin + '/pos/api/trip/' + trip_id + '/delete/';
    return fetch(url, {
        method: 'DELETE', // or 'PUT'
        credentials: 'same-origin',
        headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    }).catch(error => console.error('Error:', error));
}

function duplicateTrip(trip_id){
    let url = origin + '/pos/api/trip/' + trip_id + '/duplicate/';
    let response = fetch(url, {
        method: 'POST', // or 'PUT'
        credentials: 'same-origin',
        headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
    })
    return response;
}


