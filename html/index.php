<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8">
	<title>sunportal</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" type="text/css" href="css/bootstrap.min.css">
	<link rel="stylesheet" type="text/css" href="css/main.css">
</head>

<body>
	<div id="outer">
		<div class="container">
			<div class="row">
				<div class="status-container col-sm">
					<div class="status">
						<h5>Tagesertrag</h5>
						<p class="meter" id="dayTotal"></p>
						<div class="line"></div>
					</div>
				</div>
				<div class="status-container col-sm">
					<div class="status">
						<h5>Gesamtertrag</h5>
						<p class="meter" id="total"></p>
						<div class="line"></div>
					</div>
				</div>
				<div class="status-container col-sm">
					<div class="status">
						<h5>CO<sub>2</sub>-Einsparung</h5>
						<p class="meter" id="co2"></p>
						<div class="line"></div>
					</div>
				</div>
			</div>

			<div class="row" id="charts"></div>

		</div>
	</div>


	<script src="./js/jquery-3.3.1.js"></script>
	<script src="./js/chart.js"></script>
	<script src="./js/main.js"></script>

</body>

</html>
