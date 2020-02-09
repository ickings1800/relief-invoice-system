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
    let modal_click = document.getElementById('customerproduct-create-btn');
    let modal_close = document.getElementById('modal-close');
    let modal_cancel = document.getElementById('modal-cancel');
    let modal_save = document.getElementById('modal-save');
    let edit_buttons = Array.from(document.getElementsByClassName('customerproduct-edit'));
    let create_customerproduct_row_btn = document.getElementById('create-customerproduct-row-btn');
    let update_customerproduct_cancel = document.getElementById('update-customerproduct-cancel');
    let update_customerproduct_save = document.getElementById('update-customerproduct-save');

    edit_buttons.forEach(function(e){
        e.addEventListener("click", showUpdateCustomerProductModal, false);
    });
    modal_click.addEventListener("click", showModal, false);
    modal_close.addEventListener("click", closeModal, false);
    modal_save.addEventListener("click", saveModal, false);
    modal_cancel.addEventListener("click", closeModal, false);

    update_customerproduct_save.addEventListener("click", saveUpdateQuote, false);
    update_customerproduct_cancel.addEventListener("click", closeUpdateCustomerProductModal, false)


    create_customerproduct_row_btn.addEventListener("click", addCustomerProductRow, false);
    console.log("Added click event");
};

function closeUpdateCustomerProductModal(event){
    console.log("remove");
    let modal_div = document.getElementById('update-customerproduct-modal');
    let quote_price = document.getElementById('quote-price');
    let start_date = document.getElementById('start-date');
    modal_div.classList.remove('active');
    quote_price.value = "";
    start_date.value = "";
}

function saveUpdateQuote(event){
    let save_btn = document.getElementById('update-customerproduct-save');
    let quote_price = parseFloat(document.getElementById('quote-price').value);
    let start_date = document.getElementById('start-date').value;
    let customerproduct_id = save_btn.getAttribute('data-customerproduct-id');
    postCustomerProduct(customerproduct_id, quote_price, start_date)
    .then(resp => resp.json())
    .then(resp => handleErrors(resp))
    .then(closeUpdateCustomerProductModal())
    .catch(error => alert(error))
}


function handleErrors(response){
    if (response.error){
        throw Error(response.error);
    }
}

function postCustomerProduct(customerproduct_id, quote_price, start_date){
    let url = `http://localhost:8000/pos/api/customerproduct/${customerproduct_id}/update/`;
    let data = {"id":customerproduct_id, "quote_price": quote_price, "end_date": start_date};
    return fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).catch(error => alert('Error: ', error));
}

function showUpdateCustomerProductModal(event){
    console.log("show update customerproduct modal");
    let modal_div = document.getElementById('update-customerproduct-modal');
    let save_btn = document.getElementById('update-customerproduct-save');
    modal_div.classList.add('active');
    console.log(event.target.parentNode);
    let customerproduct_id = event.target.parentNode.getAttribute('data-customerproduct-id');
    save_btn.setAttribute('data-customerproduct-id', customerproduct_id);
    console.log(customerproduct_id);
}


function showModal(event){
    console.log("add");
    modal_div = document.getElementById('create-customer-modal');
    modal_div.classList.add('active');
    let customer_id = document.getElementById('create-customerproduct-row-btn').getAttribute('data-customer-id');
    populateProductSelect(customer_id);
}

function closeModal(event){
    console.log("remove");
    modal_div = document.getElementById('create-customer-modal');
    modal_div.classList.remove('active');
    let customerproduct_rows = Array.from(document.getElementsByClassName('create-customerproduct-row'));
    let menu_list = document.getElementById('menu-list');
    let customerproduct_list = document.getElementById('create-customerproduct-list');
    //    reset customerproduct rows
    customerproduct_rows.forEach(function(element){
        menu_list.removeChild(element);
    });
    customerproduct_list.innerHTML = "";
}

function saveModal(event){
    console.log("save");
    let customer_id = document.getElementById('create-customerproduct-row-btn').getAttribute('data-customer-id');
    createCustomerProducts(customer_id);
    closeModal();
}

function populateProductSelect(customer_id) {
    let product_select = document.getElementById('create-customerproduct-list');
    getProducts(customer_id).then(response => response.forEach(function(e){
        let option = document.createElement('option');
        option.value = e.id;
        option.innerHTML = e.name;
        product_select.appendChild(option);
    }));
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

function getProducts(customer_id){
    let url = `http://localhost:8000/pos/api/products?customer_id=${customer_id}`;
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
        row_list.setAttribute('data-list-index', cp.selectedIndex);
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
    let insert_list_index = row.getAttribute('data-list-index');
    let customerproduct_select = document.getElementById('create-customerproduct-list');
    menu.removeChild(row);
//    add product back into select list
    let new_row = document.createElement('option');
    new_row.value = removed_product_id;
    new_row.innerHTML = removed_product_name;
    customerproduct_select.insertBefore(new_row, customerproduct_select.children[insert_list_index]);
}