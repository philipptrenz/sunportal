
var maxDecimals = 2;
var reloadTime = 120 * 1000;		// reload every 2 minutes
var reloadTimer;
var charts = [];
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

	/* ----- show content ------ */
	initializeCanvas();
	initializeCharts();

	$('#content').fadeIn(1000, function() {

		/* ----- load data from database via ajax ------ */
		loadData();

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

function initializeCanvas() {

	// initialize charts for inverters if not already initialized
    if ( !$( "#chart-day" ).length ) {		// if chart not initialized

        var htmlDayChart = `
            <div class='chart col-12' id='chart-day-col'>
                <div class="row">
                    <div class="col-sm"><h5 class="chart-date"></h5></div>
                    <div class="col-sm"><h5 class="inverter-name">`+ ((langCode == 'de') ? 'Tag' : 'day' ) +`</h5></div>
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
                        <canvas id='`+`chart-day' class='chart-canvas' height='200px'/>
                    </div>
                    <i class="fa fa-chevron-right navigation-chevrons navigation-right" onclick="navigate(this)" style="visibility: hidden;"></i>
                </div>
            </div>
         `;
    }
     if ( !$( "#chart-month" ).length ) {

         var htmlMonthChart = `
            <div class='chart col-12' id='chart-month-col'>
                <div class="row">
                    <div class="col-sm"><h5 class="chart-date"></h5></div>
                    <div class="col-sm"><h5 class="inverter-name">`+ ((langCode == 'de') ? 'Monat' : 'month' ) +`</h5></div>
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
                        <canvas id='`+`chart-month' class='chart-canvas' height='200px'/>
                    </div>
                    <i class="fa fa-chevron-right navigation-chevrons navigation-right" onclick="navigate(this)" style="visibility: hidden;"></i>
                </div>
            </div>
         `;


        $( "#charts" ).append( htmlDayChart );
        $( "#charts" ).append( htmlMonthChart );
	}
}


function initializeCharts(serial) {

	var ctx_day = document.getElementById( "chart-day" ).getContext('2d');
	var new_day_chart = new Chart(ctx_day, {
	    type: 'line',
	    data: {
	        labels: [],
	        datasets: [{}]
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
	                },
					gridLines: {
						color: 'rgba(255,255,255,0.1)'
					},
					stacked: true
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
	                },
					gridLines: {
						color: 'rgba(255,255,255,0.1)'
					},
					stacked: false
	            }]
	        },
	        legend: {
	        	labels: {
	        		fontColor: 'rgba(255,255,255,1)'
	        	}
	        },
			tooltips: {
				callbacks: {
					title: function(t, d) {
						if (langCode == 'de')
							return moment(t[0].xLabel).format('HH:mm [Uhr]');
						else
							return moment(t[0].xLabel).format('hh:mm A');

					}
				}
			}
	    }
	});

	var ctx_month = document.getElementById( "chart-month" ).getContext('2d');
	var new_month_chart = new Chart(ctx_month, {
	    type: 'bar',
	    data: {
	        labels: [],
	        datasets: [ {} ]
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
	                },
					gridLines: {
						color: 'rgba(255,255,255,0.1)'
					},
				    stacked: true
	            }],
	            xAxes: [{
	            	display: true,
	            	type: 'time',
	            	time: {
                        unit: 'day'
                    },
	                ticks: {
	                    fontColor: 'rgba(255,255,255,1)'
	                },
					gridLines: {
						color: 'rgba(255,255,255,0.1)'
					},
					stacked: true
	            }]
	        },
	        legend: {
	        	labels: {
	        		fontColor: 'rgba(255,255,255,1)'
	        	}
	        },
			tooltips: {
				callbacks: {
					title: function(t, d) {
						if (langCode == 'de')
							return moment(t[0].xLabel).format('DD.MM.YYYY');
						else
							return moment(t[0].xLabel).format('YYYY/MM/DD');
					}
				}
			}
	    }
	});;

	charts = { day: new_day_chart, month: new_month_chart };
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
		type : "POST",
        url : "/update",
        data: JSON.stringify(request_data, null, '\t'),
        contentType: 'application/json',
		error: function(XMLHttpRequest, textStatus, errorThrown) {
  			//alert("Something went wrong ...");
     		requesting = false;
     		//loadData(); 		// try again, recursively
     		alert('Loading data failed.');
		},
		success: function(response) {

	        console.log(response)

			// current information
			$("#dayTotal").text( addPrefix(response.today.dayTotal) + "Wh" );
			$("#total").text( addPrefix(response.today.total) + "Wh" );
			$("#co2").text( addPrefix(response.today.co2) + "T" );

			// requested information
			setCurrentDay(response.requested.date);

	        var dayChart = charts.day;
	        var monthChart = charts.month;
	        var currentDayDate =  moment(currentDay).format('YYYY-MM-DD');

	        var all = response.requested.all;

	        {
	            // update day chart
	            $("#chart-day-col .chart-date").text(getDayStringForPrint());
	            $("#chart-day-col .inverter-yield").text( addPrefix(all.day.total) + "Wh");

	            // show or hide navigation arrows on day chart
	            $("#chart-day-col .navigation-right").each(function() {
	                $(this).css("visibility", (all.day.hasNext ? "visible" : "hidden"));
	            });
	            $("#chart-day-col .navigation-left").each(function() {
	                $(this).css("visibility", (all.day.hasPrevious ? "visible" : "hidden"));
	            });

	            // update scale
	            dayChart.data.labels = [
	                moment.unix(all.day.interval.from),
	                moment.unix(all.day.interval.to)
	            ];

                // update month chart
	            $("#chart-month-col .chart-date").text(getMonthStringForPrint());
	            $("#chart-month-col .inverter-yield").text( addPrefix(all.month.total) + "Wh");

	            // show or hide navigation arrows on day chart
	            $("#chart-month-col .navigation-right").each(function() {
	                $(this).css("visibility", (all.month.hasNext ? "visible" : "hidden"));
	            });
	            $("#chart-month-col .navigation-left").each(function() {
	                $(this).css("visibility", (all.month.hasPrevious ? "visible" : "hidden"));
	            });

	            // update scale
	            monthChart.data.labels = [
	                moment.unix(all.month.interval.from),
	                moment.unix(all.month.interval.to)
	            ];

	        }

	        var chart_num = 0;
	        for (var k in response.requested.inverters) {
                if (response.requested.inverters.hasOwnProperty(k)) {
                    var serial = k
                    var inv_data = response.requested.inverters[k]

                    {


                        // WORKAROUND FOR CHART.JS BUG
                        if (all.day.data[0].time < inv_data.day.data[0].time) {
                            var tmp = [], i = 0;
                            while (all.day.data[i].time < inv_data.day.data[0].time) {
                                tmp.push( { 'time': all.day.data[i].time, 'power': 0 } );
                                i++;
                            }
                            var tmp2 = tmp.concat(inv_data.day.data);
                            inv_data.day.data = tmp2;
                        }
                        if (all.day.data[all.day.data.length-1].time > inv_data.day.data[inv_data.day.data.length-1].time) {
                            var tmp, i = all.day.data.length-1;
                            while (all.day.data[i].time < inv_data.day.data[inv_data.day.data.length-1].time) {
                                tmp.unshift( { 'time': all.day.data[i].time, 'power': 0 } );
                                i--;
                            }
                            inv_data.day.data.concat(tmp);
                        }
                        // WORKAROUND FOR CHART.JS BUG END


                        // update day chart
                        inv_data.day.data.forEach(function(obj) {
                            obj.x = moment.unix(obj.time);
                            obj.y = obj.power / 1000;
                            delete obj.time;
                            delete obj.power;
                        })
                        var is_label_not_defined = (dayChart.data.datasets[chart_num] && (dayChart.data.datasets[chart_num].label != response.today.inverters[k].name))
                        if (is_label_not_defined || !dayChart.data.datasets[chart_num]) {
                            dayChart.data.datasets[chart_num] = {
                                label: response.today.inverters[k].name,
                                data: inv_data.day.data,
                                backgroundColor: 'rgba(227,6,19,0.3)',
                                borderColor: 'rgba(227,6,19,1)',
                                borderWidth: 1,
                                pointRadius: 0
                            }
                        } else {
                            dayChart.data.datasets[chart_num].data = inv_data.day.data;
                        }

                    	// update month chart
                        inv_data.month.data.forEach(function(obj) {
                            obj.x = moment.unix(obj.time).subtract(1, 'days');
                            obj.y = obj.power / 1000;
                            delete obj.time;
                            delete obj.power;
                        })

                        var is_label_not_defined = (monthChart.data.datasets[chart_num] && (monthChart.data.datasets[chart_num].label != response.today.inverters[k].name))
                        if ( is_label_not_defined || !monthChart.data.datasets[chart_num]) {
                            monthChart.data.datasets[chart_num] = {
                                label: response.today.inverters[k].name,
                                data: inv_data.month.data,
                                backgroundColor: 'rgba(227,6,19,0.3)',
                                borderColor: 'rgba(227,6,19,1)',
                                borderWidth: 1,
                                pointRadius: 0
                            }
                        } else {
                            monthChart.data.datasets[chart_num].data = inv_data.month.data;
                        }
                    }
                    chart_num++;
                }
            }

            dayChart.data.datasets.sort(sort_inverter_datasets_alphabetically);   // sort alphabetically
            dayChart.update();

            monthChart.data.datasets.sort(sort_inverter_datasets_alphabetically); // sort alphabetically
            monthChart.update();

			requesting = false;
			reloadTimer = setTimeout(loadData, reloadTime);
		}
	});
}

function sort_inverter_datasets_alphabetically(a, b) {
    var textA = a.label.toUpperCase();
    var textB = b.label.toUpperCase();
    return (textA < textB) ? -1 : (textA > textB) ? 1 : 0;
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