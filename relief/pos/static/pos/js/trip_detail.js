window.onload = function(e){
    let route_form = document.getElementById('routeform');
    let submit_btn = document.getElementById('save');
    route_form.addEventListener('submit', function(e) {
        e.preventDefault();
    }, false);

    submit_btn.addEventListener('click', function(e) {
        addRouteTrip();
    }, false);

    getTripRouteList();
};

function addRouteTrip() {
    let url = document.getElementById('routeform').action;
    let customer = document.getElementById('customer');
    let note = document.getElementById('note');
    data = { 'customer': customer.value, 'note': note.value };
    console.log(data);
    fetch(url, {
        method:'POST',
        body: JSON.stringify(data),
        headers:{
            'Content-Type': 'application/json'
        }
    }).then(res => res.json())
    .then (function(rJson) {
        console.log('getTripRouteList');
        getTripRouteList();
        customer.value = '';
        note.value = '';
    })
    .catch(error => console.error('Error:', error));
};

function getTripRouteList() {
    let url = window.location.href + 'routes/';
    console.log(url);
    fetch(url)
    .then(response => response.json())
    .then(function(tripJson) {
        tripJson.route_set.sort(function(a,b){
            return a.index - b.index;
        });
        addRoutes(tripJson);
    });
};


function addRoutes(tripJson) {
    let routes = document.getElementById('routes');
    let headers = tripJson.packaging_methods.split(',');
    console.log('inner html set blank');
    routes.innerHTML = '';

    for (let i = 0; i < tripJson.route_set.length; i++){
        let routeJson = tripJson.route_set[i];
        let route = `
            <div class="card route">
                <div class="card-header">
                    <div class="columns">
                        <div class="column col-1">
                            <h5>${ routeJson.index }.</h5>
                        </div>
                        <div class="column col-5">
                            <h5>${ routeJson.orderitem_set[0].customerproduct.customer }</h5>
                        </div>
                        <div class="column col-5">
                            <h5 class="float-right">${ routeJson.do_number }</h5>
                        </div>
                        <div class="column col-1">
                            <a href="#"><i class="float-right icon icon-cross m-1 route-delete"></i></a>
                        </div>
                    </div>
                    <div class="divider"></div>
                </div>
                <div class="card-body">
                    <div class="columns">
                        <div class="column col-12">
                        <div class="columns">
                            <div class="column col-4"></div>
                            <div class="column col-8">
                                <div class="row row-header">
                                    ${headers.map((val, i) => `<div class="col">${ val }</div>`).join('')}
                                </div>
                            </div>
                        </div>
                            <div class="columns">
                            ${ routeJson.orderitem_set.map((oi, i) =>`
                            <div class="column col-1">${ oi.quantity }</div>
                            <div class="column col-3">${ oi.customerproduct.product }</div>
                            <div class="column col-8">
                                <div class="row">
                                    ${headers.map((val, i) => `
                                        <div class="col">${ oi.packing ? oi.packing[val] || '' : ''}</div>`
                                    ).join('')}
                                </div>
                            </div>
                            <div class="column col-12 divider"></div>
                            `).join('')}
                            </div>
                        </div>
                        <div class="column col-12"><h5>${ routeJson.note }</h5></div>
                    </div>
                </div>
            </div>
        `
        routes.innerHTML += route;
    }

    addOrderItemPacking(tripJson);
}

function addOrderItemPacking(tripJson){
    let packingSum = document.getElementById('packing-sum-header');
    let packingDiv = document.getElementById('packing-sum-value');
    let headers = tripJson.packaging_methods.split(',');
    let routes = tripJson.route_set;
    let calcSum = new Object();
    let sum = [];

    headers.forEach(function(header){
        calcSum[header] = 0;
    });

    routes.forEach(function(route){
        route.orderitem_set.forEach(function(orderitem){
            if (orderitem.packing !== null){
                for (var i in orderitem.packing){
                    if (calcSum[i] !== null){
                        calcSum[i] += orderitem.packing[i];
                    }
                }
            }
        });
    });

    headers.forEach(function(header){
        sum.push(calcSum[header]);
    });

    let packingHeader = `${headers.map((val, i) => `<div class="col">${ val }</div>`).join('')}`;
    let packingValue = `${sum.map((val, i) => `<div class="col">${ val }</div>`).join('')}`;
    packingSum.innerHTML = packingHeader;
    packingDiv.innerHTML = packingValue;
}