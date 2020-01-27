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
    let create_customer_cancel = document.getElementById('customer-create-cancel-button');
    let create_customer_submit = document.getElementById('customer-create-submit-button');
    let create_customer_btn = document.getElementById('create-customer-button');
    let create_customerproduct_row_btn = document.getElementById('create-customerproduct-row-btn');
    var el = Array.from(document.getElementsByClassName('draggable-list'));
    console.log(el);
    el.forEach(function(element){
        Sortable.create(element, {
          group: element.id,
          animation: 100,
          onEnd: function(event){
            saveModal(event);
          }
        });
    })

    create_customer_btn.addEventListener("click", showCreateCustomerModal, false);
    create_customer_cancel.addEventListener("click", closeCreateCustomerModal, false);
    create_customer_submit.addEventListener("click", quoteCustomerTab, false);
    create_customerproduct_row_btn.addEventListener("click", addCustomerProductRow, false);
};


function addCustomerProductRow(event){
    let quote_input = document.getElementById('create-customerproduct-quote');
    let cp = document.getElementById('create-customerproduct-list');
    let menu = document.getElementById('menu-list');
    let create_customerproduct_row = document.getElementById('create-customerproduct-row');
    if (quote_input.value === ""){
        alert("Fill in quote box");
    } else if (cp.options.length === 0){
        alert("No products available");
    } else {
        let selected_value = cp.options[cp.selectedIndex].value;
        let selected_product_name = cp.options[cp.selectedIndex].text;
        let quote = quote_input.value;
        let row_list = document.createElement('li');
        row_list.classList.add('columns', 'create-customerproduct-row');
        row_list.setAttribute('data-product-id', selected_value);
        row_list.setAttribute('data-quote', quote_input.value);
        row_list.setAttribute('data-product-name', selected_product_name)
        let row_product_name = document.createElement('div');
        row_product_name.classList.add('column', 'col-7');
        row_product_name.innerHTML = selected_product_name;
        let row_separator = document.createElement('div');
        row_separator.classList.add('column', 'col-1');
        let row_quote = document.createElement('div');
        row_quote.innerHTML = quote_input.value;
        row_quote.classList.add('column', 'col-3');
        let row_remove = document.createElement('a');
        row_remove.classList.add('btn', 'btn-link', 'column', 'col-1');
        row_remove.href = "#";
        let remove_icon = document.createElement('i');
        remove_icon.classList.add('icon', 'icon-minus');
        row_remove.appendChild(remove_icon);
        row_list.appendChild(row_product_name);
        row_list.appendChild(row_separator);
        row_list.appendChild(row_quote);
        row_list.appendChild(row_remove);
        menu.insertBefore(row_list, menu.childNodes[menu.childNodes.length - 2]);
        row_remove.addEventListener("click", removeCustomerProductRow, false);
        quote_input.value = "";
        cp.remove(cp.selectedIndex);
    }
}


function removeCustomerProductRow(event){
    console.log("Remove customerproduct row");
    let row = event.target.parentNode.parentNode;
    let menu = document.getElementById('menu-list');
    let removed_product_id = row.getAttribute('data-product-id');
    let removed_product_name = row.getAttribute('data-product-name');
    let create_customerproduct_list = document.getElementById('create-customerproduct-list');
    menu.removeChild(row);
//    add product back into select list
    let new_row = document.createElement('option');
    new_row.value = removed_product_id;
    new_row.innerHTML = removed_product_name;
}


async function quoteCustomerTab(){
    let quote_tab = document.getElementById('quote-tab');
    let create_customer_tab = document.getElementById('create-customer-tab');
    let menu_list = document.getElementById('create-customer-product');
    let form = document.getElementById('create-customer-form');
    let create_customer_submit = document.getElementById('customer-create-submit-button');
    let prev_btn = document.getElementById('customer-create-back');
    let customerproduct_list = document.getElementById('create-customerproduct-list');
    let product_list = await getProducts();
    create_customer_tab.classList.remove('active');
    quote_tab.classList.add('active');
    form.style.display = "none";
    menu_list.style.display = "block";
    create_customer_submit.innerHTML = "Create";
    create_customer_submit.addEventListener("click", postCustomerAndQuote, false);
    prev_btn.style.display = "block";
    prev_btn.addEventListener("click", createCustomerTab, false);
    product_list.forEach(function(element){
        let product_row = document.createElement('option');
        product_row.value = element.id;
        product_row.innerHTML = element.name;
        customerproduct_list.appendChild(product_row);
    })
}

function getProducts(){
    let url = `http://localhost:8000/pos/api/products/`;
    return fetch(url, {
      method: 'GET', // or 'PUT'
      credentials: 'same-origin',
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then((response) => response.json())
    .catch(error => console.error('Error: ', error));
}

function createCustomer(){
    let url = `http://localhost:8000/pos/api/customer/create/`;
    let product_id = document.getElementById('create-customerproduct-list');
    let customer_name = document.getElementById('customer-create-name').value;
    let customer_address = document.getElementById('customer-create-address').value;
    let customer_postal = document.getElementById('customer-create-postal').value;
    let customer_tel = document.getElementById('customer-create-tel').value;
    let customer_fax = document.getElementById('customer-create-fax').value;
    let customer_term = parseInt(document.getElementById('customer-create-term').value);
    let customer_gst = parseInt(document.getElementById('customer-create-gst').value);
    let customer_group = parseInt(document.getElementById('customer-create-group').value);

    var data = {
        "name": customer_name,
        "address": customer_address,
        "postal_code": customer_postal,
        "tel_no": customer_tel,
        "fax_no": customer_fax,
        "term": customer_term,
        "gst": customer_gst,
        "group": customer_group
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
    }).then(response => response.json())
    .catch(error => console.error('Error: ', error));
}


function createCustomerProducts(customer_id){
    console.log('Creating Customer Products');
     let customerproduct_rows = Array.from(document.getElementsByClassName('create-customerproduct-row'));
     let customerproducts_promises = []
     customerproduct_rows.forEach(async (element) => {
        let product_id = element.getAttribute('data-product-id');
        let quote_price = element.getAttribute('data-quote');
        customerproducts_promises.push(createCustomerProduct(customer_id, product_id, quote_price));
     });
     return customerproducts_promises;
}

function createCustomerProduct(customer_id, product_id, quote_price){
    console.log('Create Customer Product');
    let url = `http://localhost:8000/pos/api/customers/${customer_id}/products/create/`;
    var data = {
        "customer": customer_id,
        "product": parseInt(product_id),
        "quote_price": parseFloat(quote_price)
    };
    console.log(data);
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


async function postCustomerAndQuote(event){
    event.preventDefault();
    console.log("Submit quote");
//    POST quote
    let created_customer = await createCustomer();
    let url = `http://localhost:8000/pos/customers/detail/${created_customer.id}/`;
    console.log(created_customer);
    customerproducts_promises = createCustomerProducts(created_customer.id);
    Promise.all(customerproducts_promises).then(function(e){
        window.location.href = url;
    });
    closeCreateCustomerModal();
}


function createCustomerTab(){
    let quote_tab = document.getElementById('quote-tab');
    let create_customer_tab = document.getElementById('create-customer-tab');
    let menu_list = document.getElementById('create-customer-product');
    let form = document.getElementById('create-customer-form');
    let create_customer_submit = document.getElementById('customer-create-submit-button');
    let prev_btn = document.getElementById('customer-create-back');
    create_customer_tab.classList.add('active');
    quote_tab.classList.remove('active');
    form.style.display = "block";
    menu_list.style.display = "none";
    create_customer_submit.innerHTML = "Next";
    create_customer_submit.addEventListener("click", quoteCustomerTab, false);
    prev_btn.style.display = "none";
}


function showCreateCustomerModal(event){
    let modal_create_customer = document.getElementById('create-customer-modal');
    let customer_tab = document.getElementById('create-customer-tab');
    let prev_btn = document.getElementById('customer-create-back');
    modal_create_customer.classList.add('active');
    customer_tab.classList.add('active');
    prev_btn.style.display = "none";
}

function closeCreateCustomerModal(event){
    let modal_create_customer = document.getElementById('create-customer-modal');
    let create_customer_tab = document.getElementById('create-customer-tab');
    let quote_tab = document.getElementById('quote-tab');
    let menu_list = document.getElementById('menu-list');
    let customerproduct_rows = Array.from(document.getElementsByClassName('create-customerproduct-row'));
    let customerproduct_list = document.getElementById('create-customerproduct-list');
    modal_create_customer.classList.remove('active');
    create_customer_tab.classList.remove('active');
    quote_tab.classList.remove('active');
    createCustomerTab();
//    reset customerproduct rows
    customerproduct_rows.forEach(function(element){
        menu_list.removeChild(element);
    });
    customerproduct_list.innerHTML = "";
}

function saveModal(event){
    console.log("save");
    let customer_list = event.target;
    console.log(event);
    group_id = event.item.getAttribute('data-group-id');
    let url = `http://localhost:8000/pos/api/customergroup/${group_id}/swap/`;
    let list_items = Array.from(customer_list.children);
    let arrangement = [];
    list_items.forEach(function(item){
        arrangement.push(parseInt(item.getAttribute('data-customergroup-id'), 10));
    });
    console.log(arrangement);
    var data = {
        "arrangement": arrangement
    };

    fetch(url, {
      method: 'POST', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
    .catch(error => console.error('Error: ', error));
}
