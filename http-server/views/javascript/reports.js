
var address_list 

//Create view report button which links to the report from scan
function create_main_table(){

    const address_list_id = document.getElementById('address_list')
    document.getElementById("back-button").style.visibility = 'hidden'
    document.getElementById('title').innerHTML = "Scanned Addresses"
    address_list_id.innerHTML = "<tr><th>Addresses</th><th>Recent scan</th><th>Scan history</th></tr>"
    for(let i =0; i < address_list.length; i++){
        var id_button = "history_button_" + i 
        console.log(id_button)
        let history_button = '<button onclick="view_history('+i+')" class="view-button" id='+ id_button +' type="button">View</button>'
        let view_button = '<tr><td>' + address_list[i] + '</td><td><a href=/address_report?address='+ address_list[i]+ '><button class="view-button" type="button">View</button></a></td><td>'+history_button+'</a></td></tr>'
        
        address_list_id.innerHTML += view_button

        //Add event listener to history button 
        /*
        var history_button_ID = document.getElementById(id_button)
        history_button_ID.addEventListener('click', function(){
            console.log(id_button + "clicked")
            view_history(address_list[i])
            console.log('adding event for '+ id_button)
        })*/
    }
}

function create_history_table(date_list, address){
    document.getElementById('title').innerHTML = address
    document.getElementById("back-button").style.visibility = 'visible'
    const address_list = document.getElementById('address_list')
    address_list.innerHTML = '<tr><th>Date</th></tr>'
    for(let i =0; i < date_list.length; i++){
        let view_button = '<tr class="history-row"><td>'+date_list[i]+'</td><td><a href=/address_report_history?address='+address +'&date='+date_list[i]+' <button class="view-history-report-button" type="button">View</button></td></tr>'
        address_list.innerHTML += view_button
    }
}

function view_history(index){
    var address = address_list[index]
    console
    const xhr = new XMLHttpRequest();
    let url = "/address_report_history?address="+address
    xhr.open("GET", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let response = JSON.parse(xhr.responseText)
            create_history_table(response, address)
        };
    }
    xhr.send()
}

function get_addresses(){
    const xhr = new XMLHttpRequest();
    let url = "/address_report?address=get_addresses"
    xhr.open("GET", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            address_list = JSON.parse(xhr.responseText)
            create_main_table()
        };
    }
    xhr.send()
}

get_addresses()