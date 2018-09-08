
var maxDecimals = 2;
var reloadTime = 120 * 1000;		// reload every 2 minutes
var reloadTimer;
var lastDataSetLength = [];
var inverters = [];
var charts = [];
var langCode = "";

var currentDay = setCurrentDay(); // today in format 'YYYY-MM-DD'

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

	});

	$('.navigation-left').click(function() {
		var canvas = $(this).parent().find( "canvas" )[0];
		var inv = $(canvas).attr('id').replace('chart-', '');
		navigateOneDay(currentDay, 'backwards');
	});

	$('.navigation-right').click(function() {
		var canvas = $(this).parent().find( "canvas" )[0];
		var inv = $(canvas).attr('id').replace('chart-', '');
		navigateOneDay(currentDay, 'forwards');
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
				<div class='chart col-12' id='chart-`+inv.serial+`-col'>
					<div class="row">
						<div class="col-sm"><h5 class="chart-date"></h5></div>
						<div class="col-sm"><h5 class="inverter-name">`+ ((inv.serial != '0000') ? inv.name : '') +`</h5></div>
						<div class="col-sm">
							<h5 class="inverter-yield">
								<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
								<span class="sr-only">Loading ...</span>
							</h5>
						</div>
						
					</div>
					<div class="chart-container">
						<i class="fa fa-chevron-left navigation-chevrons navigation-left" style="visibility: hidden;"></i>
						<div class="chart-container-inner">
							<canvas id='`+`chart-`+inv.serial+`' class='chart-canvas' height='200px'/>
						</div>
						<i class="fa fa-chevron-right navigation-chevrons navigation-right" style="visibility: hidden;"></i>
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
	    	responsive: true,
	    	animation: {
	    		duration: 1000,
	    		easing: 'easeInOutSine'
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
							hour: ((langCode == 'de') ? 'H [Uhr]' : 'h A')
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
	charts[serial] = new_chart;
}

var requesting = false;
function loadData(day) {

	// only one request at a time
	if (requesting) return;
	else requesting = true;

	clearTimeout(reloadTimer);

	var request_data = { 
		day : currentDay 
	};

//	$('.chart-date').each(function() {
//		$(this).text('');
//	});
	$('.inverter-yield').each(function() {
		if (! $(this).has('i.fa-circle-o-notch').length) 
			$(this).html('<i class="fa fa-circle-o-notch fa-spin fa-fw"></i><span class="sr-only">Loading ...</span>');
	});

	//console.log("Requesting data for "+currentDay+" ...");
	$.ajax({ 
		type: 'post', 
		url: './update.php', 
		data : request_data, 
		error: function(XMLHttpRequest, textStatus, errorThrown) {
  			//alert("Something went wrong ...");
     		requesting = false;
     		loadData(); 		// try again, recursively
		},
		success: function(resp) {

		var response = JSON.parse(resp); 

		//console.log(response.requested.inverters[0])

		// current information
		$("#dayTotal").text( addPrefix(response.today.dayTotal) + "Wh" );
		$("#total").text( addPrefix(response.today.total) + "Wh" );
		$("#co2").text( addPrefix(response.today.co2) + "T" );

		// requested information
		setCurrentDay(response.requested.day);

		// update local stored inverters
		inverters = [];
		for (var i=0; i<response.requested.inverters.length; i++) {
			inv_data = response.requested.inverters[i];
			inverters.push({ 'serial': inv_data.serial, 'name': inv_data.name});
		}

		// delete chart if inverter does no longer exist
		$('canvas').each(function() {
			var id = $(this).attr('id').replace('chart-', '');
			if (!id in inverters) $(this).parent().remove();
		});

		saveInvertersToCookie();
		initializeInverterCanvas();

		// get data of requested day per inverter
		response.requested.inverters.forEach(function (inv) {

			$("#chart-" + inv.serial + "-col .chart-date").text(getDateStringForPrint());
			$("#chart-" + inv.serial + "-col .inverter-yield").text( addPrefix(inv.dayTotal) + "Wh");

			// show or hide navigation arrows
			$("#chart-" + inv.serial + "-col .navigation-right").each(function() {
				$(this).css("visibility", (inv.hasNext ? "visible" : "hidden"));
			});
			$("#chart-" + inv.serial + "-col .navigation-left").each(function() {
				$(this).css("visibility", (inv.hasPrevious ? "visible" : "hidden"));
			});

			var chart = charts[inv.serial];
			var datapoints = inv.data;
			
			// update scale
			var currentDayDate =  moment(currentDay).format('YYYY-MM-DD');
			
			chart.data.labels = [
				moment(currentDayDate),											// from day start
				moment(currentDayDate).add(1, 'days').subtract(1, 'minutes')	// to day end
			];

			datapoints.forEach(function(obj) {
				obj.x = moment.unix(obj.time);
				obj.y = obj.power;
				delete obj.time;
				delete obj.power;
			})

			chart.data.datasets.forEach((dataset) => {
				dataset.data = datapoints;
			});

			chart.update();

		});

		requesting = false;
		reloadTimer = setTimeout(loadData, reloadTime);
	}
	});
}

function navigateOneDay(dayString, direction) {
	var date = moment(dayString).format('YYYY-MM-DD');
	if (direction == 'forwards') {
		date = moment(date).add(1, 'days').format("YYYY-MM-DD");
		currentDay = date;
		loadData();
	} else if (direction == 'backwards') {
		date = moment(date).subtract(1, 'days').format("YYYY-MM-DD");
		currentDay = date;
		loadData();
	}
}

function setCurrentDay(newDay) {
	if (newDay) currentDay = newDay;
	else currentDay = new Date().toISOString().slice(0,10);

	var date = moment(currentDay).format('YYYY-MM-DD');

    return currentDay;

}

function getDateStringForPrint() {
	if (currentDay) {
		if (langCode == 'de' ) {
			return currentDay.replace( /(\d{4})-(\d{2})-(\d{2})/, "$3.$2.$1");
		} else {
			return currentDay.replace('-', '/').replace('-', '/');
		}		
	} else {
		return '';
	}

	
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