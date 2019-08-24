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

window.onload = function(e){
    let print_button = document.getElementById('print');
    if (print_button !== null){
        // Apply click events if on trip details page
        let routes = getRouteDomElements();
        let del_buttons = getDeleteButtonsDomElements();
        let edit_submit_btn = document.getElementById('modal-save');
        let close_btn = document.getElementById('modal-close');
        let add_route_btn = document.getElementById('add-route');
        let arrange_button = document.getElementById('arrange-button');
        let arrange_cancel = document.getElementById('arrange-cancel-button');
        arrange_cancel.addEventListener("click", cancelArrangeRoutes, false);
        arrange_button.addEventListener("click", arrangeRoutes, false);
        add_route_btn.addEventListener("click", addRouteToTrip, false);
        edit_submit_btn.addEventListener("click", postOrderItemData, false);

        applyShowEditRouteModalEvent(routes);
        applyDeleteRouteEvent(del_buttons);

        close_btn.addEventListener("click", clearEditForm, false);
    }
    // Only get trip packing sum if on print trip details page
    getTripPackingSum();
};

function getRouteDomElements(){
    return document.getElementsByClassName('route');;
}

function getDeleteButtonsDomElements(){
    return del_buttons = document.getElementsByClassName('delete');
}

function getIndexInputDomElements(){
    return index_inputs = document.getElementsByClassName('index');
}

function applyShowEditRouteModalEvent(route_div){
    for (var i = 0 ; i < route_div.length ; i++){
        route_div[i].addEventListener("click", showEditRouteModal , false);
    }
}

function applyDeleteRouteEvent(delete_buttons){
    for (var j = 0 ; j < delete_buttons.length ; j++){
        delete_buttons[j].addEventListener("click", deleteRoute , false);
    }
}

function removeShowEditRouteModalEvent(route_div){
    for (var i = 0 ; i < route_div.length ; i++){
        route_div[i].removeEventListener("click", showEditRouteModal , false);
    }
}

function removeDeleteRouteEvent(delete_buttons){
    for (var j = 0 ; j < delete_buttons.length ; j++){
        delete_buttons[j].removeEventListener("click", deleteRoute , false);
    }
}

function validateIndexInputsWithinRange(index_array, max_index){
    let all_index = [];
    for (let i = 1; i <= max_index; i++){
        all_index.push(i.toString());
    }
    return all_index.every((e) => index_array.indexOf(e) !== -1);
}

function orderIndexInputsByIndexValue(index_inputs){
    index_inputs.sort(function(a, b){
        return parseInt(a.value) - parseInt(b.value);
    });
}

function cancelArrangeRoutes(event){
    console.log("Toggled");
    let arrange_cancel = document.getElementById('arrange-cancel-button');
    let arrange_button = document.getElementById('arrange-button');
    let index_inputs = Array.from(getIndexInputDomElements());
    let route_divs = getRouteDomElements();
    let del_buttons = getDeleteButtonsDomElements();
    index_inputs.forEach((e) => {
        e.value = e.defaultValue;
        e.readOnly=true;
        e.disabled=true;
    });
    applyDeleteRouteEvent(del_buttons);
    applyShowEditRouteModalEvent(route_divs);
    arrange_cancel.classList.add('d-hide');
    arrange_button.classList.remove('btn-success');
    arrange_button.innerHTML = "Arrange";
}

async function arrangeRoutes(event){
    console.log("Toggled");
    let arrange_cancel = document.getElementById('arrange-cancel-button');
    let index_inputs = Array.from(getIndexInputDomElements());
    let route_divs = getRouteDomElements();
    let del_buttons = getDeleteButtonsDomElements();
    if (event.target.innerHTML === 'Arrange'){
        console.log("Arrange checked");
        index_inputs.forEach((e) => {
            e.readOnly=false;
            e.disabled=false;
            e.setAttribute('min', 1);
            e.setAttribute('max', index_inputs.length);
        });
        removeShowEditRouteModalEvent(route_divs);
        removeDeleteRouteEvent(del_buttons);
        event.target.classList.add('btn-success');
        event.target.innerHTML = 'Save';
        arrange_cancel.classList.remove('d-hide');
    } else {
        console.log("Arrange Unchecked");
        let index_values = index_inputs.map(e => e.value);
        let result = validateIndexInputsWithinRange(index_values, route_divs.length);
        if (result) {
            orderIndexInputsByIndexValue(index_inputs);
            index_ordering = [];
            index_inputs.forEach((e) => {
                e.readOnly=true;
                e.disabled=true;
                console.log(e.getAttribute('data-route-id'), e.value);
                index_ordering.push(parseInt(e.getAttribute('data-route-id')));
            });
            // POST index ordering request to server.
            let trip_id = document.getElementById('total-packing-sum').getAttribute('data-trip-id');
            await postIndexOrderingData(index_ordering, trip_id);
            event.target.classList.remove('btn-success');
            event.target.innerHTML = 'Arrange';
            arrange_cancel.classList.add('d-hide');
            // Refresh the DOM.
            refreshTripRoutesDOM(trip_id);
        } else {
            // duplicated indexes
            alert("Number ordering may be duplicated, change and save again.");
        }
    }
}


async function postIndexOrderingData(index_ordering_array, trip_id){
    console.log("index ordering array", index_ordering_array);
    let url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/routes/arrange/';
    let data = {'id_arrangement': index_ordering_array};
    var response = await fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => console.error('Error:', error));;
}


function showEditRouteModal(event){
    console.log("ShowModal");
    let editModal = document.getElementById('edit-modal');
    let closeModal = document.getElementById('modal-close');
    let modalForm = document.getElementById('modal-form');
    editModal.classList.add("active")
    closeModal.addEventListener("click", function(e){
        editModal.classList.remove("active");
    }, false);
    routeId = this.getAttribute('data-route-id');
    fetch('http://localhost:8000/pos/api/routes/' + routeId + '/')
        .then(function(response){
            return response.json();
        })
        .then(function(response){
            generateEditRouteForm(response)
        });
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

        main_container = document.createElement('div');
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
    var orderitem_node = document.querySelectorAll(".orderitem-container[data-orderitem-id='" + orderitem_id + "']")[0];
    var packing_node = document.querySelectorAll(".packing-container[data-orderitem-id='" + orderitem_id + "']")[0];
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
    let total_packing_sum_label = Array.from(document.getElementsByClassName('packing-label')).map(e => e.innerHTML);
    let total_packing_sum_label_trim = total_packing_sum_label.map(s => s.trim());
    console.log(total_packing_sum_label_trim);
    var trip_id = total_packing_sum.getAttribute('data-trip-id');
    total_packing_sum.innerHTML = "";
    fetch('http://localhost:8000/pos/api/trip/' + trip_id + '/packingsum/')
        .then(res => res.json())
        .then(function(response){
            console.log(total_packing_sum);
            console.log(response);
            for (var i = 0; i < total_packing_sum_label_trim.length; i++){
                var label = document.createElement('li');
                var label_name = total_packing_sum_label_trim[i];
                label.innerHTML = response[label_name];

                total_packing_sum.appendChild(label);
                console.log(label);
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


async function refreshTripRoutesDOM(trip_id){
    console.log("Refresh Trip Route DOM");
    let url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/detail/routes/';
    let route_divs = getRouteDomElements();
    let del_buttons = getDeleteButtonsDomElements();
    let routes_div = document.getElementById('routes');
    var response = await fetch(url, {
      method: 'GET', // or 'PUT'
    });
    var resp_json = await response.json();
    console.log(resp_json);
    routes_div.innerHTML = "";
    let routes = resp_json;
    console.log(routes);
    routes.forEach((r) => addRouteCardDOM(r));
    applyShowEditRouteModalEvent(route_divs);
    applyDeleteRouteEvent(del_buttons);
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

        var customer_index = document.createElement('input');
//        customer_index.innerHTML = route_index;
        customer_index.classList.add('index', 'form-input', 'input-lg');
        customer_index.setAttribute('data-route-id', route_id);
        customer_index.type = 'number';
        customer_index.value = route_index;
        customer_index.readOnly = true;
        customer_index.disabled = true;
        customer_index.style.display = 'inline';

        var customer_heading = document.createElement('div');
        customer_heading.innerHTML = `${customer_name}`;
        customer_heading.classList.add('h4', 'mx-2');
        customer_heading.style.display = 'inline';

        var do_number_div = document.createElement('div');
        do_number_div.innerHTML = do_number;
        do_number_div.classList.add('h4', 'text-error', 'float-right');
        do_number_div.style.display = 'inline';

        var card_header = document.createElement('div');
        card_header.classList.add('column', 'col-12');
        card_header.appendChild(customer_index);
        card_header.appendChild(customer_heading);
        if (do_number !== '' && do_number !== null){
            card_header.appendChild(do_number_div);
        }

        route_div.appendChild(card_header);

        var spacing_div = document.createElement('div');
        spacing_div.classList.add('column', 'col-6');
        var packing_ul = document.createElement('ul');
        packing_ul.classList.add('packing-container','column', 'col-6');
        packing_label.forEach(function(label){
            var orderitem_li = document.createElement('li');
            orderitem_li.innerHTML = label;
            orderitem_li.style.flex = "1";
            orderitem_li.style.textAlign = "center";
            packing_ul.appendChild(orderitem_li);
        });
        route_div.appendChild(spacing_div);
        route_div.appendChild(packing_ul);

        orderitem_set.forEach(function(item){
//            console.log(item);
            var orderitem_id = item.id;
            var orderitem_qty = item.quantity;
            var orderitem_name = item.customerproduct;
            var orderitem_note = item.note;
            var orderitem_packing = item.packing;

            var orderitem_ul = document.createElement('ul');
            orderitem_ul.style.display = "flex";
            orderitem_ul.classList.add('orderitem-container','column', 'col-6');
            orderitem_ul.setAttribute('data-orderitem-id', orderitem_id);

            var orderitem_qty_li = document.createElement('li')
            orderitem_qty_li.style.flex = "1";
            orderitem_qty_li.innerHTML = orderitem_qty;
            orderitem_ul.appendChild(orderitem_qty_li);

            var orderitem_name_li = document.createElement('li')
            orderitem_name_li.style.flex = "8";
            orderitem_name_li.innerHTML = orderitem_name;
            orderitem_ul.appendChild(orderitem_name_li);

            if (orderitem_note !== "" && orderitem_note !== "None" && orderitem_note !== null){
                orderitem_name_li.innerHTML += ' \uD83E\uDC52 ' + orderitem_note;
            }

            var packing_value_ul = document.createElement('ul');
            packing_value_ul.style.display = "flex";
            packing_value_ul.classList.add('packing-container', 'column', 'col-6');
            packing_value_ul.setAttribute('data-orderitem-id', orderitem_id);

            for (var i = 0 ; i < packing_label.length; i++){
                var packing_name = packing_label[i];
                var label = document.createElement('li');
                label.style.flex = "1";
                label.style.textAlign = "center";

                if (orderitem_packing){
                    if (orderitem_packing[packing_name]){
                        label.innerHTML = orderitem_packing[packing_name];
                    } else {
                        label.innerHTML = "";
                    }
                } else {
                    label.innerHTML = "";
                }
                packing_value_ul.appendChild(label);
            }
            route_div.appendChild(orderitem_ul);
//            orderitem_div.appendChild(orderitem_qty_div);
            route_div.appendChild(packing_value_ul);
        });

        var note_spacing = document.createElement('div');
        note_spacing.classList.add('column', 'col-12', 'divider');
        var note_heading = document.createElement('h5');
        note_heading.classList.add('column', 'col-10');
        note_heading.innerHTML = route_note;
        var route_delete = document.createElement('a');
        route_delete.classList.add('btn', 'btn-link', 'column', 'col-2');
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

        var note_h5 = document.createElement('h5');
        note_h5.classList.add('column', 'col-11');
        note_h5.innerHTML = route_note;

        var del_anchor = document.createElement('a');
        del_anchor.classList.add('btn', 'btn-link', 'column', 'col-1');

        var del_icon = document.createElement('i');
        del_icon.classList.add('icon', 'icon-delete', 'float-right');

        del_anchor.appendChild(del_icon);
        note_div.appendChild(note_h5);
        note_div.appendChild(del_anchor);
        note_div.addEventListener("click", showEditRouteModal , false);
        var routes = document.getElementById('routes');
        routes.appendChild(note_div);
    }
}


async function postOrderItemData(){
    console.log("Submit pressed");
    let orderitem_packing = Array.from(document.getElementsByClassName('packing-label')).map(e => e.innerHTML);
    console.log(orderitem_packing);
    var forms = document.getElementsByClassName('orderitem-form');
    for (var i = 0 ; i < forms.length; i++) {
        var orderitem_form = forms[i];
        var orderitem_id = orderitem_form.getAttribute('data-orderitem-id');
        var orderitem_packing_form = document.querySelectorAll(".orderitem-packing-form[data-orderitem-id='" + orderitem_id + "']")[0];
        console.log(orderitem_packing_form);
        var orderitem_quantity = orderitem_form.elements['quantity'].value;
        var orderitem_note = orderitem_form.elements['note'].value;
        var orderitem_packing_json = {};
        console.log(orderitem_form.elements);
        for (var j = 0 ; j < orderitem_packing_form.length; j++){
            var heading = orderitem_packing[j];
            console.log(heading);
            if (orderitem_packing_form.elements[heading].value != ""){
                orderitem_packing_json[heading] = orderitem_packing_form.elements[heading].value;
            }
        }

        var url = 'http://localhost:8000/pos/api/orderitem/' + orderitem_id + '/update/';
        var data = {
            'id': orderitem_id,
            'quantity': orderitem_quantity,
            'note': orderitem_note,
            'packing': orderitem_packing_json
        };
        var response = await fetch(url, {
          method: 'PUT', // or 'PUT'
          credentials: 'same-origin',
          body: JSON.stringify(data), // data can be `string` or {object}!
          headers:{
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })

        var data = await response.json();
        updateOrderitemData(data, orderitem_packing);
    };
    await postRouteData();
    await getTripPackingSum();
    closeModalWindow();
}


async function postRouteData() {
    var route_forms = document.getElementsByClassName('route-form');
    for (var i = 0 ; i < route_forms.length; i++){
        var route_form = route_forms[i];
        var route_id = route_form.getAttribute('data-route-id');
        var url = 'http://localhost:8000/pos/api/routes/' + route_id + '/update/';
        var note_input = route_form.elements['route-note'].value;
        console.log(url);
        var data = {
            'id': route_id,
            'note': note_input,
        };
        await fetch(url, {
          method: 'PUT', // or 'PUT'
          credentials: 'same-origin',
          body: JSON.stringify(data), // data can be `string` or {object}!
          headers:{
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }).then(res => res.json())
        .then(response => console.log('Success:', JSON.stringify(response)))
        .catch(error => console.error('Error:', error));
    }
}

async function postRoute(data){
    var trip_id = document.getElementById('add-route').getAttribute('data-trip-id');
    var url = 'http://localhost:8000/pos/api/trips/' + trip_id + '/detail/routes/add/';
    var response = await fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    var resp_json = await response.json()
    return resp_json;
}


function deleteRoute(event){
    event.stopPropagation();
    var all_routes = document.getElementById('routes');
    var parentDiv = this.parentElement;
    var route_id = parentDiv.getAttribute('data-route-id');
    var trip_id = document.getElementById('add-route').getAttribute('data-trip-id');
    var url = 'http://localhost:8000/pos/api/routes/' + route_id + '/delete/';
    fetch(url, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then(function(){
        all_routes.removeChild(parentDiv);
    }).then(() => refreshTripRoutesDOM(trip_id))
    .catch(error => console.error('Error:', error));
}


function getCustomerId(customerName){
    try {
        var customerId = document.querySelector("#customers option[value='"+customerName+"']").dataset.value;
    } catch (err) {
        console.log(err);
    }
    return customerId;
}