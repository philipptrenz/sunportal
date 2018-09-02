<!DOCTYPE HTML>
<html>
<link rel="stylesheet" type="text/css" href="css/main.css">
<head>
	<title> Status </title>
	<script src="./js/jquery-3.3.1.js"></script>
	<script src="./js/chart.js"></script>
</head>

<body>
	<div class="container">
		<div class="status-container">
			<div class="status">
				<h1>Tagesertrag</h1>
				<p class="meter" id="dayTotal"></p>
				<div class="line"></div>
			</div>
		</div>
		<div class="status-container">
			<div class="status">
				<h1>Gesamtertrag</h1>
				<p class="meter" id="total"></p>
				<div class="line"></div>
			</div>
		</div>
		<div class="status-container">
			<div class="status">
				<h1>CO2</h1>
				<p class="meter" id="co2"></p>
				<div class="line"></div>
			</div>
		</div>
	</div>
	<div class="chart">
		<canvas id="chartPower" width="200px" height="200px"></canvas>
		<script>
			var ctx = document.getElementById("chartPower").getContext('2d');
			var chartBottom = new Chart(ctx, {
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
		    		duration: 0
		    	},
		    	maintainAspectRatio: false,
		        scales: {
		            yAxes: [{
		                ticks: {
		                    beginAtZero:true,
		                    fontColor: 'rgba(255,255,255,1)',
		                    fontSize: 14
		                }
		            }],
		            xAxes: [{
		            	display: false,
		            	type: 'time',
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

		function addData(chart, label, data) {
		    chart.data.labels.push(label);
		    chart.data.datasets.forEach((dataset) => {
		        dataset.data.push(data);
		    });
		    chart.update();
		}

		</script>
	</div>
	<script type="text/javascript">

		var giga = Math.pow(10, 9);
		var mega = Math.pow(10, 6);
		var kilo = Math.pow(10, 3);

		var Giga = "G";
		var Mega = "M";
		var Kilo = "k";

		var maxDecimals = 2;

		var reloadTime = 60000;

		var lastDataSetLength = 0;

		function setDataPoints(dataPoints, chart) {
			for (i = 0; i < dataPoints.length; i++) {
				addData(chart, dataPoints[i].time, dataPoints[i].power);
			}
		}

		function removeAllData(amount, chart) {
			for (i = 0; i < amount; i++) {
				removeData(chart);
			}
		}

		function removeData(chart) {
		    chart.data.labels.pop();
		    chart.data.datasets.forEach((dataset) => {
		        dataset.data.pop();
		    });
		    chart.update();
		}

		function roundToDec(toRound, amount_of_decimals) {
			return Math.round(toRound*(Math.pow(10, amount_of_decimals))) / (Math.pow(10, amount_of_decimals));
		}

		function addPrefix(number) {
			if (number > giga) {
				return (roundToDec(number/giga, maxDecimals)) + " " + Giga;
			}
			else if (number > mega) {
				return (roundToDec(number/mega, maxDecimals)) + " " + Mega;
			}
			else if (number > kilo) {
				return (roundToDec(number/kilo, maxDecimals)) + " " + Kilo;
			}
			else {
				return roundToDec(number, maxDecimals) + " ";
			}
		}

		function loadData() {
			$.ajax({type: 'post', dataType: "json", url: './update.php', success: function(response) {
				$('#dayTotal').html(addPrefix(response.dayTotal) + "Wh");
				$('#total').html(addPrefix(response.total*1000) + "Wh");
				$('#co2').html(addPrefix(response.co2) + "t");

				removeAllData(lastDataSetLength, chartBottom);
				setDataPoints(response.last24h, chartBottom);

				lastDataSetLength = response.last24h.length;
			}
			});
		}

		loadData();
		window.setInterval(loadData, reloadTime);	
	</script>

</body>

</html>
