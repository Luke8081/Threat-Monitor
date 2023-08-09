//Needed for showing user different views
var view = 'console'
var execution_chart
var alert_chart

//Updates image every 10 seconds. Needs to be random element to stop browser reusing image in cache
const url = "https://cronitor.io/badges/uKVpG4/production/iVvSLth_Vq5UwQMd0yDkm40Ivjg.svg"
var image = document.getElementById("status")
image.src = url


setInterval(function(){
    var image = document.getElementById("status")
    image.src = url + "?rand=" + Math.random()
}, 7000)



//Alerts the user when there is a medium risk
function color_alerts(alerts){
    //Alerts the user if there is a high risk. 
    if (alerts.High_Alert > 0){
        //alert('ACTION NEEDED. Web server with high risk vulnerability found.')
        stylesheet = document.styleSheets[0]
        stylesheet.insertRule('.high_info_display {animation: blinking 1s infinite;}', 0)
    } else{
        element = document.getElementsByClassName('high_info_display')
        element[0].style.backgroundColor = 'darkgreen'
    }
    if (alerts.Medium_Alert > 10){
        stylesheet = document.styleSheets[0]
        stylesheet.insertRule('.medium_info_display {animation: blinking 1s infinite;}', 0)
    }else if (alerts.Medium_Alert > 1){
        element = document.getElementsByClassName('medium_info_display')
        element[0].style.backgroundColor = 'orange'
    }else{
        element = document.getElementsByClassName('medium_info_display')
        element[0].style.backgroundColor = 'darkgreen'
    }

    if (alerts.Low_Alert > 20){
        element = document.getElementsByClassName('low_info_display')
        element[0].style.backgroundColor = 'orange'
    } else{
        element = document.getElementsByClassName('low_info_display')
        element[0].style.backgroundColor = 'darkgreen'
    }
}
//If user changes settings send them to server
function change_settings(){
    let debug = document.getElementById('debug_mode').checked
    let verbose = document.getElementById('verbose_mode').checked
    let email = document.getElementById('send_email').checked
    let spider = document.getElementById('spider').checked
    let save_reports = document.getElementById('save_reports').checked
    let scan_type = document.getElementById('scan_type').checked  

    const xhr = new XMLHttpRequest();
    const url = '/scan-settings'
    const params = '?verbose='+verbose+'&debug='+debug+'&email='+email+'&spider='+spider+'&save_reports='+save_reports+'&scan_type='+scan_type
    xhr.open("GET", url+params, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log('Recieved')
        };
        }
        xhr.send()
}

//Load the settings
function get_checked_settings(){
    const xhr = new XMLHttpRequest();
    xhr.open("GET", '/scan-settings', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var settings = JSON.parse(xhr.responseText);
            document.getElementById('verbose_mode').checked = (settings['verbose'] === 'true')
            document.getElementById('debug_mode').checked = (settings['debug'] === 'true')
            document.getElementById('send_email').checked = (settings['email'] === 'true')
            document.getElementById('spider').checked = (settings['spider'] === 'true') 
            document.getElementById('save_reports').checked = (settings['save_reports'] === 'true')
            document.getElementById('scan_type').checked = (settings['scan_type'] === 'true')       
        };
    }
    xhr.send()
}
get_checked_settings()

function address_click(){
    view = 'addresses'

    let address = document.getElementById("address")
    address.style.backgroundColor="#91b7c9";
    address.style.fontWeight = 'bold'

    let console = document.getElementById("console")
    console.style.backgroundColor="#2e6883";
    console.style.fontWeight = 'normal'

    document.getElementById('refresh_button').innerHTML = 'Save'
    document.getElementById('output-text').readOnly = false
    document.getElementById('view_scan_button').style.visibility = 'hidden'

    get_addresses()
}

function console_click(){
    view = 'console'
    let console = document.getElementById("console")
    console.style.backgroundColor="#91b7c9";
    console.style.fontWeight = 'bold'

    let address = document.getElementById("address")
    address.style.backgroundColor="#2e6883";
    address.style.fontWeight = 'normal'

    document.getElementById('refresh_button').innerHTML = 'Clear'
    document.getElementById('output-text').readOnly = true
    document.getElementById('view_scan_button').style.visibility = 'visible'

    update_console()
}

function update_console(){
    const xhr = new XMLHttpRequest();
    let console_text = document.getElementById('output-text').value

    xhr.open("GET", '/console', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                const response = xhr.responseText

                //Update graphs when a scan is finished
                if (console_text.localeCompare(response) == true){
                    get_execution_graph_data()
                    get_alert_graph_data()
                }


                document.getElementById('output-text').value = xhr.responseText
            };
    }
    xhr.send()
}

function clear_console(){
    document.getElementById('output-text').value = ""
    const xhr = new XMLHttpRequest();
        const params = '?clear=true'
        xhr.open("GET", '/console'+params, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                update_console()
            };
        }
        xhr.send()
}

function button_click(){
    if (view == 'console'){
        clear_console()
    }else{
        send_addresses()
    }
}

function get_addresses(){
    const xhr = new XMLHttpRequest();
    xhr.open("GET", '/address_list', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById('output-text').value = xhr.responseText
        };
    }
    xhr.send()
}

function send_addresses(){
    let data = document.getElementById('output-text').value
    const xhr = new XMLHttpRequest();
    const output_msg = document.getElementById("output-msg")
    xhr.open("POST", '/edit_addresses', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = async function () {
        await sleep(200)
        if (xhr.readyState === 4 && xhr.status === 200) {
            output_msg.style.backgroundColor = 'green'
            output_msg.innerHTML = 'Saved'
            output_msg.style.visibility = 'visible'
            await sleep(6000)
            output_msg.style.visibility = 'hidden'
        }else{
            output_msg.style.backgroundColor = 'red'
            output_msg.innerHTML = 'Error'
            output_msg.style.visibility = 'visible'
            await sleep(10000)
            output_msg.style.visibility = 'hidden'
        }
    }
    xhr.send(JSON.stringify({addresses: data}))
}

function scroll_textArea_down(){
    const textarea = document.getElementById('output-text')
    textarea.scrollBy({ 
        top: textarea.scrollHeight,
        left: 0, 
        behavior: 'smooth' 
    });
}




function scan_log_click(){
    const xhr = new XMLHttpRequest();
    const textarea = document.getElementById('output-text')
    xhr.open("GET", '/scan_log', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            textarea.value += xhr.responseText
            scroll_textArea_down()
        }
    xhr.send()
}

function get_alerts(){
    const xhr = new XMLHttpRequest();
    xhr.open("GET", '/alerts', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.responseText){
                let alerts = JSON.parse(xhr.responseText)
                document.getElementById('low_alert_text').innerText = 'Low alert: '+alerts.Low_Alert
                document.getElementById('medium_alert_text').innerText = 'Medium alert: '+alerts.Medium_Alert
                document.getElementById('high_alert_text').innerText = 'High alert: '+alerts.High_Alert

                color_alerts(alerts)
            }
        }
    xhr.send()
}

//Scrolls the user down so other elements are within view
function scroll_down_page(){
    const scroll = document.documentElement.scrollHeight - window.innerHeight - 150
    window.scrollTo(0, scroll)
}

setInterval(function(){
    if (view == 'console'){
        update_console()
    }
},4000)

//Function to pause the code
function sleep(ms) {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
}

setInterval(function(){
    get_checked_settings()
},30000)


console_click()
document.getElementById("output-msg").style.visibility = 'hidden'

const scroll_img = document.getElementById("scroll_down_image")
const page_down_img = document.getElementById('page_down_img')
scroll_img.style.opacity = 0
page_down_img.style.opacity = 100

//Make scroll button appear and dissapear based on users scroll on the page
document.getElementById('output-text').addEventListener('scroll', event => {
    const {scrollHeight, scrollTop, clientHeight} = event.target;

    if (Math.abs(scrollHeight - clientHeight - scrollTop) > 1) {
        scroll_img.style.opacity = 100
    }
    if (Math.abs(scrollHeight - clientHeight - scrollTop) < 1) {
        scroll_img.style.opacity = 0
    }
});

//Make the page down button dissapear when user scrolls down and appear 
//when at the top
window.addEventListener('scroll', event => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop

    if (scrollTop < 250){
        page_down_img.style.opacity = 100
    }else{
        page_down_img.style.opacity = 0
    }
});


function get_execution_graph_data(){
    const xhr = new XMLHttpRequest();
    xhr.open("GET", '/scan_log?execution=execution', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {

                let graph_data = JSON.parse(xhr.responseText)
                let dates = []
                let data = []

                for (let i = 0; i < graph_data.length; i++ ){
                    dates.push(graph_data[i].Date)
                    data.push(graph_data[i].Time)
                }
                console.log(dates)
                dates.reverse()
                data.reverse()

                create_graph_execution_time(dates, data)
            }
        }
    xhr.send()
}

function get_alert_graph_data(){
    const xhr = new XMLHttpRequest();
    xhr.open("GET", '/scan_log?alert=alert', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {

                let graph_data = JSON.parse(xhr.responseText)
                let dates = []
                let data = []

                for (let i = 0; i < graph_data.length; i++ ){
                    dates.push(graph_data[i].Date)
                    data.push(graph_data[i].Alert)
                }
                dates.reverse()
                data.reverse()

                create_graph_alert(dates, data)
            }
        }
    xhr.send()
}
const graph_options = {
    responsive: true, 
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: "rgba(255, 255, 255, 0.25)"
            },
            ticks: {
                color: "white",
                font: {
                    size: 10, 
                    weight: "normal"
                }
            },
            title: {
                display: true,
                text: 'Seconds',
                color: "white",
                font: {
                    size: 14, 
                    weight: "bold"
                }
            }
        },
        x: {
            grid: {
                color: "rgba(255, 255, 255, 0.25)"
            },
            ticks: {
                color: "white",
                font: {
                    size: 10, 
                    weight: "normal"
                }
            },
            title: {
                display: true,
                text: 'Date & Time',
                color: "white",
                font: {
                    size: 14, 
                    weight: "bold"
                }
            }

        }
    },
    plugins: {
        legend: {
            labels: {
                font: {
                    size: 25
                }
            }
        }
    }
    
}



function create_graph_alert(dates, data){
    
    //Alert count graphs
    ctx = document.getElementById('alerts_over_time')

    if (typeof alert_chart === 'object'){
        alert_chart.destroy()
    }

    let alert_options = graph_options
    alert_options.scales.y.title.text = 'Alerts'

    alert_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
            label: 'Alerts',
            data: data,
            backgroundColor: "rgba(255,255,255)", 
            borderColor: "rgba(18, 175, 225, 0.8)", 
            color: "#36A2EB",
            borderWidth: 2
            }]
        },
        options: alert_options,
    });
}

function create_graph_execution_time(dates, data){
    console.log('creating')
    //Execution time chart
    let ctx = document.getElementById('execution_time_canvas');

    if (typeof execution_chart === 'object'){
        execution_chart.destroy()
    }

    execution_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
            label: 'Execution Time',
            data: data,
            backgroundColor: "rgba(255,255,255)", 
            borderColor: "rgba(18, 175, 225, 0.8)", 
            color: "#36A2EB",
            borderWidth: 2
            }]
        },
        options: graph_options,
    });
}


document.addEventListener("DOMContentLoaded", function() {
    get_execution_graph_data()
    get_alert_graph_data()
})


get_alerts()
