
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

			var html = `	
				<div class='chart col-12'>
					<h5>`+inv.name+`</h5>
					<div class="chart-container">
						<i class="icon-chevron-left"></i>
						<canvas id='`+`chart-`+inv.serial+`' height='200px'/>
						<i class="icon-chevron-right"></i>
					</div>
				</div>
			 `;

			$( "#charts" ).append( html );

			initializeChart(inv.serial);
			lastDataSetLength[inv.serial] = 0;
		}
	}
}

function initializeChart(serial) {
	var ctx = document.getElementById( "chart-"+serial ).getContext('2d');
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
	                	beginAtZero: true,
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
	charts[serial] = new_chart;
}

function loadData(day) {

	var today = new Date().toISOString().slice(0,10);


	// request chart from day x in format 'YYYY-MM-DD'

	var get_day;
	if (day) get_day = day
	else get_day = today

	var request_data = { 
		day : get_day 
	};

	$.ajax({ type: 'post', url: './update.php', data : request_data, success: function(resp) {

		var response = JSON.parse(resp); 

		$("#dayTotal").text( addPrefix(response.dayTotal) + "Wh" );
		$("#total").text( addPrefix(response.total*1000) + "Wh" );
		$("#co2").text( addPrefix(response.co2) + "t" );

		// update local stored inverters
		inverters = [];
		for (var name in response.inverters) {
			var serial = response.inverters[name].serial;
			inverters.push({ 'serial': serial, 'name': name});
		}

		// delete chart if inverter does no longer exist
		$('canvas').each(function() {
			var id = $(this).attr('id').replace('chart-', '');
			if (!id in inverters) $(this).parent().remove();
		});

		saveInvertersToCookie();
		initializeInverterCanvas();

		for (var i = 0; i < inverters.length; i++) {

			var inv = inverters[i];

			if (!response.inverters[inv.name].last24h) continue;

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

			for (var j = 0; j < datapoints.length; j++) {
				var d = datapoints[j];
				console.log(moment.unix(d.time).format('DD.MM.YYYY, HH:mm [Uhr]'), d.power)
			}

			//console.log(inv.serial, moment.unix(label[0]).format('DD.MM.YYYY, HH:mm:ss'), moment.unix(label[label.length-1]).format('DD.MM.YYYY, HH:mm:ss'));
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