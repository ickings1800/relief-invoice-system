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
    modal_click = document.getElementById('customer_group_name');
    modal_close = document.getElementById('modal-close');
    modal_save = document.getElementById('modal-save');
    modal_click.addEventListener("click", showModal, false);
    modal_close.addEventListener("click", closeModal, false);
    modal_save.addEventListener("click", saveModal, false);
    console.log("Added click event");
};


function showModal(event){
    console.log("add");
    modal_div = document.getElementById('change_customer_group_modal');
    modal_div.classList.add('active');
}

function closeModal(event){
    console.log("remove");
    modal_div = document.getElementById('change_customer_group_modal');
    modal_div.classList.remove('active');
}

function saveModal(event){
    console.log("save");
    modal_select = document.getElementById('modal-select');
    customer_group_id = modal_select.getAttribute('data-customer-groupid');
    let selectedValue = modal_select.options[modal_select.selectedIndex].value;
    let selectedName = modal_select.options[modal_select.selectedIndex].text;
    let url = `http://localhost:8000/pos/api/customergroup/${customer_group_id}/update/`;

    var data = {
        "id": customer_group_id,
        "group": selectedValue
    };
    fetch(url, {
      method: 'PUT', // or 'PUT'
      credentials: 'same-origin',
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers:{
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
    .then(() => updateGroupName(selectedName))
    .then(() => closeModal())
    .catch(error => console.error('Error: ', error));
}

function updateGroupName(groupName){
    modal_click = document.getElementById('customer_group_name');
    modal_click.innerHTML = groupName;
}
