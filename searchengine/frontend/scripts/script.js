var search_input = document.getElementById('search_input');
var results_meta = document.getElementById('results_meta');
var results_section = document.getElementById('results_section');


function search(data) {
    if (!data) {
        /* we've just made a search, let's get the data */
        make_request(search_input.value, false, search);
    } else {
        /* we've recieved the data, let's load the results */
        display_results(data['results'], data['meta']);
    }
}

function prsearch(data) {
    if (!data) {
        /* we've just made a search, let's get the data */
        make_request(search_input.value, true, search);
    } else {
        /* we've recieved the data, let's load the results */
        display_results(data['results'], data['meta']);
    }
}

// asynch GET request to endpoint.py
function make_request(query, pr_flag, _callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            _callback(JSON.parse(xmlHttp.responseText));
        }
    }
    xmlHttp.open("GET", 'http://127.0.0.1:5000/search/' + query + "/" + pr_flag + "/", true); 
    xmlHttp.send(null);
}


function display_results(data, meta) {

    results_section.innerHTML = ""
    results_meta.innerHTML = "About " + meta['num_results'] + " results (" + meta['seconds_elapsed'] + " seconds)";
    results_meta.style.display = 'block';
    data.forEach(function(item, index, array) {

        if (index < 3) {
            new_div = "<div class='row result best-left card'><a class='best' href='"; 
                
        } else {
            new_div = "<div class='row result'><a href='";
        }

        new_div += item['link'] + "'>" +
                item['title'] + "</a><br>" 
                + item['link'];
                

        if (item['link'].search("~") !== -1) {
            new_div += " <span class='profpage'>Professor/User page</span>";
        }

        new_div += "<br><p>" + item['des'] + "</p></div>";

        results_section.innerHTML += new_div;
    }); 
}

function trySearch(e) {
    if (e.keyCode === 13) {
        e.preventDefault();
        search();
    }
}