//Needed for showing user different views
var view = 'console'

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
    xhr.open("GET", '/console', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
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
/*
document.addEventListener("DOMContentLoaded", function() {
    console.log('draw')
    // Sample data (replace with your own data)
    var data = {
      labels: ["January", "February", "March", "April", "May", "June", "July"],
      datasets: [{
        label: "Monthly Sales",
        data: [1200, 1500, 800, 1800, 1300, 2000, 1700],
        backgroundColor: "rgba(75, 192, 192, 0.2)", // Optional: Background color of the data points
        borderColor: "rgba(75, 192, 192, 1)", // Optional: Border color of the data points
        borderWidth: 1 // Optional: Border width of the data points
      }]
    };
  
    // Chart configuration
    var options = {
      responsive: true, // Make the chart responsive
      maintainAspectRatio: false, // Preserve aspect ratio
      scales: {
        y: {
          beginAtZero: true // Start the y-axis at zero
        }
      }
    };
  
    // Create the chart
    var ctx = document.getElementById("execution_time_canvas").getContext("2d");
    var myChart = new Chart(ctx, {
      type: "bar", // Specify the chart type (e.g., bar, line, pie, etc.)
      data: data,
      options: options
    });
  });
*/
document.addEventListener("DOMContentLoaded", function() {
    //Chart 1
    let ctx = document.getElementById('execution_time_canvas');
    console.log('drawing')
    new Chart(ctx, {
    type: 'line',
    data: {
        labels: ["January", "February", "March", "April", "May", "June", "July"],
        datasets: [{
        label: 'Sales',
        data: [1200, 1500, 800, 1800, 1300, 2000, 1700],
        backgroundColor: "rgba(255,255,255)", // Optional: Background color of the data points
        borderColor: "rgba(255,255,255)", // Optional: Border color of the data points
        borderWidth: 1
        }]
    },
    options: {
        responsive: true, // Make the chart responsive
        scales: {
        y: {
            beginAtZero: true
        }
        }
    }
    });


    //Chart 2
    ctx = document.getElementById('alerts_over_time');
    console.log('drawing')
    new Chart(ctx, {
    type: 'line',
    data: {
        labels: ["January", "February", "March", "April", "May", "June", "July"],
        datasets: [{
        label: 'Sales',
        data: [1200, 1500, 800, 1800, 1300, 2000, 1700],
        backgroundColor: "rgba(255,255,255)", // Optional: Background color of the data points
        borderColor: "rgba(255,255,255)", // Optional: Border color of the data points
        borderWidth: 1
        }]
    },
    options: {
        responsive: true, // Make the chart responsive
        scales: {
        y: {
            beginAtZero: true
        }
        }
    }
    });
})


get_alerts()
