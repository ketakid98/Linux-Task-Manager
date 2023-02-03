eel.expose(set_interrupt)
function set_interrupt(data) {
    $("#interrupt_val").html(data["interval_val"]+" interrupts");
}

eel.expose(set_context_switch)
function set_context_switch(data) {
    $("#context_switch_val").html(data["interval_val"]+" context switches");
}

eel.expose(set_cpu)
function set_cpu(data) {
    let html = "";
    for (let i=0; i<data.length; i++) {
        html += "<div class='card col-sm-3'><div class='card-body'><h5 class='card-title'>";
        html += data[i]["name"] + "</h5>";
        html += "<p class='card-text'>User Utilization: " + data[i]["percent_user_util"] + "%</p>";
        html += "<p class='card-text'>System Utilization: " + data[i]["percent_sys_util"] + "%</p>";
        html += "<p class='card-text'>Overallr Utilization: " + data[i]["percent_overall_util"] + "%</p>";
        html += "</div></div>";
    }
    $("#cpu-stats-card").html(html);
}

eel.expose(set_memory)
function set_memory(data) {
    $("#total_memory").html(data["memory_total"]+"mb");
    $("#used_memory").html(data["memory_used"]+"mb");
    $("#util_memory").html(data["memory_util"]+"%");
}

eel.expose(set_disk)
function set_disk(data) {
    let html = "";
    for (let i=0; i<data.length; i++) {
        html += "<div class='card col-sm-3'><div class='card-body'><h5 class='card-title'>";
        html += data[i]["name"] + "</h5>";
        html += "<p class='card-text'>Disk Reads: " + data[i]["disk_read_speed"] + "</p>";
        html += "<p class='card-text'>Disk Writes: " + data[i]["disk_write_speed"] + "</p>";
        html += "<p class='card-text'>Block Reads: " + data[i]["block_read_speed"] + "</p>";
        html += "<p class='card-text'>Block Writes: " + data[i]["block_write_speed"] + "</p>";
        html += "</div></div>";
    }
    $("#disk-stats-card").html(html);
}

// check this
eel.expose(set_network_devices)
function set_network_devices(data) {
    let html = "";
    for (let i=0; i<data.length; i++) {
        html += "<div class='card col-sm-3'><div class='card-body'><h5 class='card-title'>";
        html += data[i]["name"] + "</h5>";
        html += "<p class='card-text'>Recieved: " + data[i]["rec"] + " bytes</p>";
        html += "<p class='card-text'>Sent: " + data[i]["sent"] + " bytes</p>";
        html += "<p class='card-text'>Network Bandwidth: " + data[i]["bandwidth"] + " mb</p>";
        html += "<p class='card-text'>Average Utilization: " + data[i]["avg_network_util"] + " bytes</p>";
        html += "</div></div>";
    }
    $("#network-devices-card").html(html);
}

eel.expose(set_process)
function set_process(data) {
    process_list = [];
    for (let i=0; i<data.length; i++) {
        p = [
            data[i]["pid"],
            data[i]["name"],
            data[i]["user_name"],
            data[i]["inode"],
            data[i]["percent_user_util"]+"%",
            data[i]["percent_sys_util"]+"%",
            data[i]["percent_overall_util"]+"%",
            data[i]["avg_virtual_memory_utilization"]+"",
            data[i]["physical_memory_utilization"]+"%"
        ];
        process_list.push(p);
    }
    process_table.clear().draw();
    process_table.rows.add(process_list).draw();
}

eel.expose(set_tcp_conn_count)
function set_tcp_conn_count(data) {
    $("#established-tcp").html("Established TCP connection count: " + data);   
}

eel.expose(set_tcp)
function set_tcp(data) {
    let tcp_list = [];
    for (let i=0; i<data.length; i++) {
        c = [
            data[i]["id"],
            data[i]["inode"],
            data[i]["uid"],
            data[i]["user_name"],
            data[i]["program"],
            data[i]["source_hostname"],
            data[i]["source_ip"],
            data[i]["source_port"],
            data[i]["destination_hostname"],
            data[i]["destination_ip"],
            data[i]["destination_port"]
        ];
        tcp_list.push(c);
    }
    tcp_table.clear().draw();
    tcp_table.rows.add(tcp_list).draw();
}

eel.expose(set_udp)
function set_udp(data) {
    let udp_list = [];
    for (let i=0; i<data.length; i++) {
        c = [
            data[i]["id"],
            data[i]["inode"],
            data[i]["uid"],
            data[i]["user_name"],
            data[i]["program"],
            data[i]["source_hostname"],
            data[i]["source_ip"],
            data[i]["source_port"],
            data[i]["destination_hostname"],
            data[i]["destination_ip"],
            data[i]["destination_port"]
        ];
        udp_list.push(c);
    }
    udp_table.clear().draw();
    udp_table.rows.add(udp_list).draw();
}

eel.expose(show_logged_data)
function show_logged_data(data) {
    $("#logger-val").html(data);
}

let loggerOn = false;
function openKeylogger() {
    $("#logger-val").html("");
    msg = loggerOn ? "Switch On Keylogger" : "Switch Off Keylogger";
    $("#logger-btn").html(msg);
    loggerOn = loggerOn ? false : true;
    eel.logging(loggerOn);
}

function showDiv(id) {
    $(".main-div").addClass("div-invisible");
    $("#"+id).removeClass("div-invisible");
    $(".nav-link").removeClass("active");
    $("#nav-"+id).addClass("active");
}

function setGlobalInterval() {
    eel.set_global_interval($("#global-interval").val());
}

let tcp_table = "";
let udp_table = "";
let process_table = "";
$(document).ready(function() {
    process_table = $("#process-table").DataTable({      
        language: { search: '', searchPlaceholder: "Search" }, paging: true, 
        "order": [[ 6, "desc" ]]});

    tcp_table = $("#tcp-table").DataTable( {
    language: { search: '', searchPlaceholder: "Search" },paging: true
    });

    udp_table = $("#udp-table").DataTable( {
    language: { search: '', searchPlaceholder: "Search" },paging: true
    });
});


