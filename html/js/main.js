
var maxDecimals = 2;
var reloadTime = 120 * 1000;		// reload every 2 minutes
var reloadTimer;
var lastDataSetLength = [];
var inverters = [];
var langCode = "";

var currentDay; // today in format 'YYYY-MM-DD'

$(document).ready(function () {

	// set current day
	curentDay = setCurrentDay();

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

	/*
	$('.navigation-left').click(function() {
		var id = $(this).parent().parent().parent().attr('id');
		console.log(id)

		navigateOneDay(currentDay, 'backwards');
	});

	$('.navigation-right').click(function() {
		var id = $(this).parent().parent().parent().attr('id');
		console.log(id)

		navigateOneDay(currentDay, 'forwards');
	});*/

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
	for (x in inverters) {
		var inv = inverters[x];

		if ( !$( "#chart-day-"+x ).length ) {		// if chart not initialized

			var htmlDayChart = `
				<div class='chart col-12' id='chart-day-`+inv.serial+`-col'>
					<div class="row">
						<div class="col-sm"><h5 class="chart-date"></h5></div>
						<div class="col-sm"><h5 class="inverter-name">`+ ((inv.serial != '0000') ? inv.name : ((langCode == 'de') ? 'Tag' : 'day' )) +`</h5></div>
						<div class="col-sm">
							<h5 class="inverter-yield">
								<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
								<span class="sr-only">Loading ...</span>
							</h5>
						</div>
						
					</div>
					<div class="chart-container">
						<i class="fa fa-chevron-left navigation-chevrons navigation-left" onclick="navigate(this)" style="visibility: hidden;"></i>
						<div class="chart-container-inner">
							<canvas id='`+`chart-day-`+inv.serial+`' class='chart-canvas' height='200px'/>
						</div>
						<i class="fa fa-chevron-right navigation-chevrons navigation-right" onclick="navigate(this)" style="visibility: hidden;"></i>
					</div>
				</div>
			 `;

			 var htmlMonthChart = `
				<div class='chart col-12' id='chart-month-`+inv.serial+`-col'>
					<div class="row">
						<div class="col-sm"><h5 class="chart-date"></h5></div>
						<div class="col-sm"><h5 class="inverter-name">`+ ((inv.serial != '0000') ? inv.name :  ((langCode == 'de') ? 'Monat' : 'month' )) +`</h5></div>
						<div class="col-sm">
							<h5 class="inverter-yield">
								<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
								<span class="sr-only">Loading ...</span>
							</h5>
						</div>
						
					</div>
					<div class="chart-container">
						<i class="fa fa-chevron-left navigation-chevrons navigation-left" onclick="navigate(this)" style="visibility: hidden;"></i>
						<div class="chart-container-inner">
							<canvas id='`+`chart-month-`+inv.serial+`' class='chart-canvas' height='200px'/>
						</div>
						<i class="fa fa-chevron-right navigation-chevrons navigation-right" onclick="navigate(this)" style="visibility: hidden;"></i>
					</div>
				</div>
			 `;


			$( "#charts" ).append( htmlDayChart );
			$( "#charts" ).append( htmlMonthChart );

			initializeCharts(inv.serial);
			lastDataSetLength[inv.serial] = 0;
		}
	}
}


function initializeCharts(serial) {

	var ctx_day = document.getElementById( "chart-day-"+serial ).getContext('2d');
	var new_day_chart = new Chart(ctx_day, {
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

	var ctx_month = document.getElementById( "chart-month-"+serial ).getContext('2d');
	var new_month_chart = new Chart(ctx_month, {
	    type: 'bar',
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
                        unit: 'day'
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
	});;

	inverters[String(serial)].charts = { day: new_day_chart, month: new_month_chart };
}

var requesting = false;
function loadData(day) {

	// only one request at a time
	if (requesting) return;
	else requesting = true;

	clearTimeout(reloadTimer);

	var request_data = { 
		date: currentDay 
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

		console.log(response)

		// current information
		$("#dayTotal").text( addPrefix(response.today.dayTotal) + "Wh" );
		$("#total").text( addPrefix(response.today.total) + "Wh" );
		$("#co2").text( addPrefix(response.today.co2) + "T" );

		// requested information
		setCurrentDay(response.requested.date);

		// update local stored inverters
		for (var i=0; i<response.requested.inverters.length; i++) {
			var inv = response.requested.inverters[i];
			if (!(inv.serial in inverters)) inverters[String(inv.serial)] = { serial: inv.serial, name: inv.name, charts: { day: null, month: null } };
		}

		// delete chart if inverter does no longer exist
		$('canvas').each(function() {
			var id = $(this).attr('id').replace('chart-day-', '').replace('chart-month-', '');
			if (!(id in inverters)) $(this).parent().remove();
		});

		saveInvertersToCookie();
		initializeInverterCanvas();

		// get data of requested day per inverter
		response.requested.inverters.forEach(function (inv) {

			var dayChart = inverters[inv.serial].charts.day;
			var monthChart = inverters[inv.serial].charts.month;
			var currentDayDate =  moment(currentDay).format('YYYY-MM-DD');

			{	// update day chart

				$("#chart-day-" + inv.serial + "-col .chart-date").text(getDayStringForPrint());
				$("#chart-day-" + inv.serial + "-col .inverter-yield").text( addPrefix(inv.day.total) + "Wh");

				// show or hide navigation arrows on day chart
				$("#chart-day-" + inv.serial + "-col .navigation-right").each(function() {
					$(this).css("visibility", (inv.day.hasNext ? "visible" : "hidden"));
				});
				$("#chart-day-" + inv.serial + "-col .navigation-left").each(function() {
					$(this).css("visibility", (inv.day.hasPrevious ? "visible" : "hidden"));
				});

				var datapoints = inv.day.data;
				
				// update scale
				dayChart.data.labels = [
					moment.unix(inv.day.interval.from),
					moment.unix(inv.day.interval.to)
				];

				datapoints.forEach(function(obj) {
					obj.x = moment.unix(obj.time);
					obj.y = obj.power;
					delete obj.time;
					delete obj.power;
				})

				dayChart.data.datasets.forEach((dataset) => {
					dataset.data = datapoints;
				});

				dayChart.update();

			}

			{	// update day chart

				$("#chart-month-" + inv.serial + "-col .chart-date").text(getMonthStringForPrint());
				$("#chart-month-" + inv.serial + "-col .inverter-yield").text( addPrefix(inv.month.total) + "Wh");

				// show or hide navigation arrows on day chart
				$("#chart-month-" + inv.serial + "-col .navigation-right").each(function() {
					$(this).css("visibility", (inv.month.hasNext ? "visible" : "hidden"));
				});
				$("#chart-month-" + inv.serial + "-col .navigation-left").each(function() {
					$(this).css("visibility", (inv.month.hasPrevious ? "visible" : "hidden"));
				});

				var datapoints = inv.month.data;
				
				
				// update scale
				monthChart.data.labels = [
					moment.unix(inv.month.interval.from),
					moment.unix(inv.month.interval.to)
				];

				datapoints.forEach(function(obj) {
					obj.x = moment.unix(obj.time);
					obj.y = obj.power;
					delete obj.time;
					delete obj.power;
				})

				monthChart.data.datasets.forEach((dataset) => {
					dataset.data = datapoints;
				});

				monthChart.update();

			}


		});

		requesting = false;
		reloadTimer = setTimeout(loadData, reloadTime);
	}
	});
}


function navigate(self) {
	var id = $(self).parent().parent().attr('id');

	if (id.includes('day')) {
		if ( $(self).hasClass('navigation-left') ){
			navigateOneDay(currentDay, 'backwards');
		} else if ( $(self).hasClass('navigation-right') ){
			navigateOneDay(currentDay, 'forwards');
		}
	} else if (id.includes('month')) {
		if ( $(self).hasClass('navigation-left') ){
			navigateOneMonth(currentDay, 'backwards');
		} else if ( $(self).hasClass('navigation-right') ){
			navigateOneMonth(currentDay, 'forwards');
		}
	}

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

function navigateOneMonth(dayString, direction) {
	var date = moment(dayString).format('YYYY-MM-DD');

	if (direction == 'forwards') {
		date = moment(date).add(1, 'months').format("YYYY-MM-DD");
		currentDay = date;
		loadData();
	} else if (direction == 'backwards') {
		date = moment(date).subtract(1, 'months').format("YYYY-MM-DD");
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

function getDayStringForPrint() {
	var date = moment(currentDay).format('YYYY-MM-DD');
	if (currentDay) {
		if (langCode == 'de' ) {
			return moment(date).format('DD.MM.YYYY');
		} else {
			return moment(date).format('YYYY/MM/DD');
		}		
	} else {
		return '';
	}	
}

function getMonthStringForPrint() {
	var date = moment(currentDay).format('YYYY-MM-DD');
	if (currentDay) {
		return moment(date).locale(langCode).format('MMMM YYYY').toLowerCase();		
	} else {
		return '';
	}
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