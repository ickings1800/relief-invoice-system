window.onload = function(e){
    refresh_btn = document.getElementById('refresh');
    modal_close = document.getElementById('close');
    modal_save = document.getElementById('modal-save');
    add_row_ul = document.getElementById('add-row');
    gst_select = document.getElementById('gst-select');
    invoice_create = document.getElementById('create');
    refresh_btn.addEventListener("click", getRoutes, false);
    modal_close.addEventListener("click", closeModal, false);
    modal_save.addEventListener("click", saveOrderItem , false);
    invoice_create.addEventListener("click", createInvoice, false);
    gst_select.addEventListener("click", calculateInvoice, false);
    getInvoiceNumber();
    console.log("Added click event");
};


async function getInvoiceNumber(){
    var d = new Date();
    var invoice_year_input = document.getElementById('invoice-year');
    var invoice_number_input = document.getElementById('invoice-number');
    var customer_id = document.getElementById('customer').getAttribute('data-customer-id');
    var url = 'http://localhost:8000/pos/api/invoice/getnewinvoicenumber/';
    var response = await fetch(url);
    var invoice_year = d.getFullYear();
    var invoice_number = await response.json();
    invoice_year_input.value = invoice_year;
    invoice_number_input.value = invoice_number.number;
    console.log(invoice_year);
    console.log(invoice_number);
}


async function createInvoice(event) {
    await saveRouteDoNumber();
    var customer_id = document.getElementById('customer').getAttribute('data-customer-id');
    var gst_select = document.getElementById('gst-select');
    var customer = await getCustomer(customer_id);
    console.log(customer);
    var do_nums = Array.from(document.getElementsByClassName('do-number-input'));
    var invoice_year = document.getElementById('invoice-year').value;
    var invoice_number = document.getElementById('invoice-number').value;
    var start_date = document.getElementById('start-date').value;
    var end_date = document.getElementById('end-date').value;
    var minus = document.getElementById('minus').value;
    var gst = customer.gst;
    var remark = document.getElementById('remark').value;
    var route_ids = do_nums.map(do_input => do_input.getAttribute('data-route-id'));
    var url = 'http://localhost:8000/pos/api/invoice/create/';
    console.log(route_ids);

    if (gst_select.checked == false){
        gst = 0;
    }

    var data = {
        'invoice_year':invoice_year,
        'invoice_number':invoice_number,
        'start_date':start_date,
        'end_date':end_date,
        'minus':minus,
        'gst':gst,
        'remark':remark,
        'customer':customer_id,
        'route_id_list':route_ids
    };
    console.log(data);
    fetch(url, {
      method: 'POST', // or 'PUT'
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
    .catch(error => console.error('Error: ', error));
}


async function saveRouteDoNumber(){
    var do_inputs = Array.from(document.getElementsByClassName('do-number-input'));
    if (do_inputs.length > 0){
        do_inputs.forEach(function(element){
            var route_id = element.getAttribute('data-route-id');
            var url = `http://localhost:8000/pos/api/routes/${route_id}/update/`;
            var do_number = element.value;
            var data = {
                'id': route_id,
                'do_number': do_number
            };
            fetch(url, {
              method: 'PUT', // or 'PUT'
              body: JSON.stringify(data), // data can be `string` or {object}!
              headers:{
                'Content-Type': 'application/json'
              }
            }).then(response => response.json())
            .catch(error => console.error('Error: ', error));
        });
    } else {
        console.error('Error: ', 'Cannot have zero selected routes to create invoice');
    }
}

async function getRoutes(event) {
    var route_table = document.getElementById('route-table');
    var route_rows = Array.from(document.getElementsByClassName('route-row'));
    var heading = document.getElementById('heading');
    var add_row = document.getElementById('add-row');
    var customer_id = refresh_btn.getAttribute('data-customer-id');
    var date_start = document.getElementById('start-date').value;
    var date_end = document.getElementById('end-date').value;
    var url = `http://localhost:8000/pos/api/invoice/date_range/${customer_id}/?date_start=${date_start}&date_end=${date_end}`;
    route_rows.forEach(function(element){
        route_table.deleteRow(element.rowIndex);
    })
    add_row.innerHTML = "";

    console.log(url);
    console.log(date_start);
    console.log(date_end);

    var customerproducts = await getCustomerProducts(customer_id);
    var customerproduct_heading = [];
    customerproduct_heading.push("Date");
    customerproducts.forEach(function(element){
        customerproduct_heading.push(element.product);
    });
    customerproduct_heading.push("D/O");
    customerproduct_heading.push("Delete");
    console.log(customerproduct_heading);

    var heading_row = document.createElement('tr')
    heading_row.classList.add('route-row');
    heading_row.id = "heading";
    route_table.insertAdjacentElement('afterbegin', heading_row);
    var customerproduct_tr = document.getElementById('heading');
    customerproduct_heading.forEach(function(heading){
        var customerproduct_th = document.createElement('th');
        customerproduct_th.innerHTML = heading;
        customerproduct_tr.appendChild(customerproduct_th);
    });

    var routeResponse = await fetch(url);
    var routeData = await routeResponse.json();
    addRouteTableRows(routeData, customerproducts);
    generateAddRowFields(date_start, date_end, customerproducts);
}


async function generateAddRowFields(date_start, date_end, customerproducts){
    var add_row = document.getElementById('add-row');
    var date_column = document.createElement('td');
    var date_select = document.createElement('select');
    date_select.id = 'add-row-date';
    date_select.classList.add('form-select');
    var trip_list_url = `http://localhost:8000/pos/api/trips/?date_start=${date_start}&date_end=${date_end}`;
    var response = await fetch(trip_list_url);
    var data = await response.json();
    console.log(data);
    var dates = data.map(t => ({'id': t.id, 'date': t.date}));
    console.log(dates);
    dates.forEach(function(element){
        var option = document.createElement('option');
        option.value = element.id;
        option.text = element.date;
        date_select.appendChild(option);
    });
    date_column.appendChild(date_select);
    console.log(customerproducts);
    add_row.appendChild(date_column);
    customerproducts.forEach(function(element){
        var customerproduct_td = document.createElement('td');
//        var customerproduct_input = document.createElement('input');
//        customerproduct_input.classList.add('form-input');
//        customerproduct_input.type = "number";
//        customerproduct_input.placeholder = element.product;
//        customerproduct_input.setAttribute('data-customerproduct-id', element.id);
//        customerproduct_td.appendChild(customerproduct_input);
        add_row.appendChild(customerproduct_td);
    });
    var do_td = document.createElement('td');
    var do_input = document.createElement('input');
    do_input.id = 'add-do-number'
    do_input.classList.add('form-input');
    do_input.type = 'text';
    do_input.placeholder = 'D/O'
    do_td.appendChild(do_input);
    add_row.appendChild(do_td);

    var add_td = document.createElement('td');
    var add_btn = document.createElement('button');
    add_btn.classList.add('btn', 'btn-link', 'add');
    var add_icon = document.createElement('i');
    add_icon.classList.add('icon', 'icon-plus');
    add_btn.appendChild(add_icon);
    add_td.appendChild(add_btn);
    add_row.appendChild(add_td);

    add_btn.addEventListener("click", addRouteForm, false);
}


async function addRouteForm(event){
    var trip_id = document.getElementById('add-row-date').value;
    var customer_id = refresh_btn.getAttribute('data-customer-id');
    var do_number = document.getElementById('add-do-number').value;
    var url = `http://localhost:8000/pos/api/trips/${trip_id}/detail/routes/add/`;
    var customerproducts = await getCustomerProducts(customer_id);
    console.log(url);
    var data = {
        'customer': customer_id,
        'do_number': do_number
    };
    fetch(url, {
      method: 'POST', // or 'PUT'
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
    .then(response => addRouteTableRows([response], customerproducts))
    .then(() => clearAddFormFields())
    .catch(error => console.error('Error: ', error));
}


function clearAddFormFields(){
    var add_do_number = document.getElementById('add-do-number');
    add_do_number.value = "";
}

function addRouteTableRows(routeData, customerproducts){
    var add_row = document.getElementById('add-row');
    var row_list = [];
    console.log(routeData);
    routeData.forEach(function(route){
        var row = {};
        row['id'] = route.id;
        row['date'] = route.trip_date;
        row['do_number'] = route.do_number;
        route.orderitem_set.forEach(function(oi){
            row[oi.customerproduct] = {'id': oi.id, 'quantity':oi.quantity, 'driver_quantity':oi.driver_quantity};
        });
        row_list.push(row);
    });
    console.log(row_list);

    row_list.forEach(function(row){
        var row_tr = document.createElement('tr');
        row_tr.classList.add('route-row');
        var date_td = document.createElement('td');
        date_td.innerHTML = row.date
        row_tr.appendChild(date_td)
        customerproducts.forEach(function(cp){
            var customerproduct_td = document.createElement('td');
            customerproduct_td.classList.add('orderitem');
            if (row[cp.product]){
                customerproduct_td.setAttribute('data-orderitem-id', row[cp.product].id);
                customerproduct_td.setAttribute('data-customerproduct-id', cp.id);
                var quantity = row[cp.product].quantity;
                var driver_quantity = row[cp.product].driver_quantity;
                customerproduct_td.setAttribute('data-quantity-calc', driver_quantity);
                customerproduct_td.innerHTML = getOrderItemQuantityDisplay(quantity, driver_quantity);
            }
            row_tr.appendChild(customerproduct_td);
        });
        var do_number_td = document.createElement('td');
        var do_number_input = document.createElement('input');
        do_number_input.classList.add('form-input', 'do-number-input');
        do_number_input.value = row.do_number;
        do_number_input.setAttribute('data-route-id', row.id)
        do_number_td.appendChild(do_number_input);
        row_tr.appendChild(do_number_td);
        var delete_td = document.createElement('td');
        var delete_btn = document.createElement('button');
        delete_btn.classList.add('btn', 'btn-link', 'delete');
        var delete_icon = document.createElement('i');
        delete_icon.classList.add('icon', 'icon-delete');
        delete_btn.appendChild(delete_icon);
        delete_td.appendChild(delete_btn);
        row_tr.appendChild(delete_td);
        add_row.insertAdjacentElement('beforebegin', row_tr);
    });
    setOrderItemClickEvent();
    setRouteDeleteClickEvent();
    calculateInvoice();
}



async function saveOrderItem(event){
    var orderitem_id = this.getAttribute('data-orderitem-id');
    var driver_quantity_input = document.getElementById('oi-driver-quantity').value;
    var url = `http://localhost:8000/pos/api/orderitem/${orderitem_id}/update/`;
    var data = {
        'id': orderitem_id,
        'driver_quantity': driver_quantity_input
    };
    fetch(url, {
      method: 'PUT', // or 'PUT'
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
    .then(response => updateOrderItemValue(response))
    .then(() => closeModal())
    .catch(error => console.error('Error: ', error));
}


function updateOrderItemValue(orderitem){
    var orderitem_id = orderitem.id;
    var orderitem_label = document.querySelectorAll(".orderitem[data-orderitem-id='" + orderitem_id + "']")[0];
    var orderitem_label_value = getOrderItemQuantityDisplay(orderitem.quantity, orderitem.driver_quantity);
    orderitem_label.innerHTML = orderitem_label_value;
    orderitem_label.setAttribute('data-quantity-calc', orderitem.driver_quantity);
    calculateInvoice();
}


async function showEditModal(event){
    console.log(this);
    var quantity_label = document.getElementById('oi-quantity');
    var driver_quantity_input = document.getElementById('oi-driver-quantity');
    var modal_save = document.getElementById('modal-save');
    var orderitem_id = this.getAttribute('data-orderitem-id');
    modal_save.setAttribute('data-orderitem-id', orderitem_id);
    var modal = document.getElementById('orderitem-modal');
    var url = `http://localhost:8000/pos/api/orderitem/${orderitem_id}/`;
    var response = await fetch(url);
    var data = await response.json();
    quantity_label.innerHTML = data.quantity;
    driver_quantity_input.value = data.driver_quantity;
    modal.classList.add('active');
}


async function getCustomerProducts(customer_id){
    var url = `http://localhost:8000/pos/api/customers/${customer_id}/products/`;
    var response = await fetch(url);
    var data = await response.json();
    return data;
}

async function getCustomer(customer_id){
    var url = `http://localhost:8000/pos/api/customers/${customer_id}/`;
    var response = await fetch(url);
    var data = await response.json();
    return data;
}

function setOrderItemClickEvent(){
    var orderitem_li = Array.from(document.getElementsByClassName('orderitem'));
    orderitem_li.forEach(function(element){
        element.addEventListener("click", showEditModal, false);
    })
}

function closeModal(event){
    var modal = document.getElementById('orderitem-modal');
    var modal_content = document.getElementById('modal-content');
    var oi_quantity_label = document.getElementById('oi-quantity');
    var oi_driver_quantity_input = document.getElementById('oi-driver-quantity');
    oi_quantity_label.innerHTML = "";
    oi_driver_quantity_input.value = "0";
    modal.classList.remove('active');
}


function getOrderItemQuantityDisplay(quantity, driver_quantity){
    if (quantity === driver_quantity)
        return quantity;
    else
        return quantity + " \u2192 " + driver_quantity;
}


function deleteRow(element){
    var rows = document.getElementById('route-table');
    var row = this.parentNode.parentNode;
    console.log(row.rowIndex);
    rows.deleteRow(row.rowIndex);
}


function setRouteDeleteClickEvent(event){
    var deleteButtons = Array.from(document.getElementsByClassName('delete'));
    deleteButtons.forEach(function(element){
        element.addEventListener("click", deleteRow, false);
    });
}


async function calculateInvoice(){
    var table = document.getElementById('route-table');
    var gst_percent = document.getElementById('gst-percent');

    var original_total = document.getElementById('original-total');
    var minus = document.getElementById('minus');
    var nett_total = document.getElementById('nett-total');
    var gst = document.getElementById('gst');
    var total_incl_gst = document.getElementById('total-incl-gst');
    var gst_select = document.getElementById('gst-select');

    var customer_id = document.getElementById('customer').getAttribute('data-customer-id');
    //  get customer gst data.
    var customer = await getCustomer(customer_id);
    console.log(customer);

    var gst_checked = gst_select.checked;
    gst_percent.innerHTML = `
    <input type="checkbox" id="gst-select" checked=${gst_checked}>
        <i class="form-icon"></i> GST ${customer.gst} %
    `;

    var customerproducts = await getCustomerProducts(customer_id);
    var cp_dict_list = []
    customerproducts.forEach(function(element){
        var cp_dict = {'id': element.id, 'sum': 0, 'unit_price':element.quote_price, 'nett': 0}
        var cp_orderitems = document.querySelectorAll(".orderitem[data-customerproduct-id='" + element.id + "']");
        cp_orderitems.forEach(oi => cp_dict.sum += parseInt(oi.getAttribute('data-quantity-calc')));
        cp_dict_list.push(cp_dict);
    });
    console.log(cp_dict_list);

    var do_blank_td = document.createElement('td');
    var delete_blank_td = document.createElement('td');

    var quantity_row = document.getElementById('quantity-row');
    var unit_price_row = document.getElementById('unit-price-row');
    var nett_amt_row = document.getElementById('nett-amt-row');

    quantity_row.innerHTML = "";
    unit_price_row.innerHTML = "";
    nett_amt_row.innerHTML = "";

    var quantity_text_td = document.createElement('td');
    quantity_text_td.innerHTML = 'QUANTITY';
    quantity_row.appendChild(quantity_text_td);
    cp_dict_list.forEach(function(element){
        var customerproduct_td = document.createElement('td');
        customerproduct_td.innerHTML = element.sum;
        quantity_row.appendChild(customerproduct_td);
    });
    quantity_row.appendChild(do_blank_td);
    quantity_row.appendChild(delete_blank_td);

    var unit_price_text_td = document.createElement('td');
    unit_price_text_td.innerHTML = 'UNIT PRICE';
    unit_price_row.appendChild(unit_price_text_td);
    cp_dict_list.forEach(function(element){
        var customerproduct_td = document.createElement('td');
        customerproduct_td.innerHTML = element.unit_price;
        unit_price_row.appendChild(customerproduct_td);
    });

    unit_price_row.appendChild(do_blank_td.cloneNode(true));
    unit_price_row.appendChild(delete_blank_td.cloneNode(true));

    var original_total_calc_list = [];
    var nett_amt_text_td = document.createElement('td');
    nett_amt_text_td.innerHTML = 'NETT AMT';
    nett_amt_row.appendChild(nett_amt_text_td);
    cp_dict_list.forEach(function(element){
        var customerproduct_td = document.createElement('td');
        var nett = parseFloat(element.unit_price) * element.sum;
        customerproduct_td.innerHTML = nett
        nett_amt_row.appendChild(customerproduct_td);
        original_total_calc_list.push(nett);
    });

    nett_amt_row.appendChild(do_blank_td.cloneNode(true));
    nett_amt_row.appendChild(delete_blank_td.cloneNode(true));

    // invoice calculation
    var invoice_gst = customer.gst;
    // show actual gst percent on invoice, but actual calculation is zero.
    if (gst_select.checked == false){
        invoice_gst = 0;
    }
    var reducer = (accumulator, currentValue) => accumulator + currentValue;
    var original_total_val = original_total_calc_list.reduce(reducer, 0);
    var nett_total_val = original_total_val - minus.value;
    var gst_value = nett_total_val * invoice_gst;
    var total_incl_gst_val = nett_total_val + gst_value;

    minus.value = minus.value;
    original_total.innerHTML = original_total_val;
    nett_total.innerHTML = nett_total_val;
    gst.innerHTML = gst_value;
    total_incl_gst.innerHTML = total_incl_gst_val;
}
