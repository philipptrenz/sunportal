
var maxDecimals = 2;
var reloadTime = 60 * 1000;		// reload once a minute
var lastDataSetLength = [];
var inverters = [];
var charts = [];
var langCode = "";

$(document).ready(function () {

	/* ----- multi language part ------ */

	var usrLang = window.navigator.userLanguage || window.navigator.language;
	
	if (usrLang.indexOf('de') !== -1) langCode = 'de';
	else langCode = 'en';
	$('body').attr( "id",'lang-'+langCode);

	/* ----- load inverters from cookie ------ */

	getInvertersFromCookie();
	initializeInverterCanvas();

	/* ----- show content ------ */

	$('#content').fadeIn(1000, function() {

		/* ----- load data from database via ajax ------ */

		loadData();
		window.setInterval(loadData, reloadTime);	

	});

});


/* ----- functions ------ */

function roundToDec(toRound, amount_of_decimals) {
	return Math.round(toRound*(Math.pow(10, amount_of_decimals))) / (Math.pow(10, amount_of_decimals));
}

function addPrefix(number) {
	if (number > Math.pow(10, 9)) return (roundToDec(number/Math.pow(10, 9), maxDecimals)) + " G";
	else if (number > Math.pow(10, 6)) return (roundToDec(number/Math.pow(10, 6), maxDecimals)) + " M";
	else if (number >  Math.pow(10, 3)) return (roundToDec(number/ Math.pow(10, 3), maxDecimals)) + " k";
	else return roundToDec(number, maxDecimals) + " ";
}

function initializeInverterCanvas() {

	// initialize charts for inverters if not already initialized
	for (var i=0; i<inverters.length; i++) {
		var inv = inverters[i];

		if ( !$( "#chart-"+inv.serial ).length ) {		// if chart not initialized

			$( "#charts" ).append( "<div class='chart col-12'><h5>"+inv.name+"</h5><canvas id='"+"chart-"+inv.serial+"' height='200px'/></div>" );
			//var ctx = $( "#"+"chart-"+serial ).getContext('2d');
			var ctx = document.getElementById( "chart-"+inv.serial ).getContext('2d');
			charts[inv.serial] = initializeChart(ctx);

			lastDataSetLength[inv.serial] = 0;

		}
	}
}

function initializeChart(ctx) {

	var hourFormat;
	if (langCode == 'de') hourFormat = 'H [Uhr]';
	else hourFormat = 'h A';

	var new_chart = new Chart(ctx, {
	    type: 'line',
	    data: {
	        labels: [],
	        datasets: [{
	            label: 'Wh',
	            data: [],
	            backgroundColor: 'rgba(227,6,19,0.3)',
	            borderColor: 'rgba(227,6,19,1)',
	            borderWidth: 1,
	            pointRadius: 0
	        }]
	    },
	    options: {
	    	animation: {
	    		duration: 1000,
	    		easing: 'easeOutQuart'
	    	},
	    	maintainAspectRatio: false,
	        scales: {
	            yAxes: [{
	                ticks: {
	                    beginAtZero: true,
	                    fontColor: 'rgba(255,255,255,1)',
	                    fontSize: 14
	                }
	            }],
	            xAxes: [{
	            	display: true,
	            	type: 'time',
	            	time: {
                        unit: 'hour',
                        displayFormats: {
							hour: hourFormat
						}
                    },
	                ticks: {
	                    fontColor: 'rgba(255,255,255,1)'
	                }
	            }]
	        },
	        legend: {
	        	labels: {
	        		fontColor: 'rgba(255,255,255,1)'
	        	}
	        }
	    }
	});
	return new_chart;
}

function loadData() {
	$.ajax({type: 'post', dataType: "json", url: './update.php', success: function(response) {

		/*
		$("#dayTotal").fadeOut(500, function() { $(this).text( addPrefix(response.dayTotal) + "Wh" ) 	}).fadeIn(500);
		$("#total").fadeOut(500, function() { 	$(this).text( addPrefix(response.total*1000) + "Wh" ) 	}).fadeIn(500);
		$("#co2").fadeOut(500, function() { 	$(this).text( addPrefix(response.co2) + "t" ) 			}).fadeIn(500);
		*/

		$("#dayTotal").text( addPrefix(response.dayTotal) + "Wh" );
		$("#total").text( addPrefix(response.total*1000) + "Wh" );
		$("#co2").text( addPrefix(response.co2) + "t" );

		// update local stored inverters
		for (var name in response.inverters) {
			var serial = response.inverters[name].serial;

			if (!containsInverter(serial)) inverters.push({ 'serial': serial, 'name': name});
		}

		saveInvertersToCookie();
		initializeInverterCanvas();

		for (var i = 0; i < inverters.length; i++) {
			var inv = inverters[i];

			var chart = charts[inv.serial];
			var datapoints = response.inverters[inv.name].last24h;
			var amount = lastDataSetLength[inv.serial];
	
			var label = datapoints.map(a => moment.unix(a.time)); // convert unix epch (seconds) to moment.js object
			var data = datapoints.map(b => b.power);

			
			chart.data.labels = label;
			chart.data.datasets.forEach((dataset) => {
				dataset.data = data;
			});
			chart.update();

		}

	}
	});
}

function containsInverter(serial) {
	for (var i=0; i<inverters.length; i++) {
		if (inverters[i].serial == serial) return true;
	}
	return false;
}

function saveInvertersToCookie() {
	var json_str = JSON.stringify(inverters);
	createCookie('inverters', json_str);
}

function getInvertersFromCookie() {
	var inv_json = readCookie('inverters');
	if (inv_json) inverters = JSON.parse(inv_json);
}

function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}