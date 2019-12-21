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
};


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
