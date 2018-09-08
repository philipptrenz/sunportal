<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8">
	<title>sunportal</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" type="text/css" href="css/bootstrap.min.css">
	<link rel="stylesheet" type="text/css" href="css/font-awesome.min.css">
	<link rel="stylesheet" type="text/css" href="css/main.css">
	<link rel="shortcut icon" href="img/favicon.ico" type="image/x-icon">
	<link rel="icon" href="img/favicon.ico" type="image/x-icon">
</head>

<body>
	<div id="outer">
		<div class="container" id="content">
			<div class="row">
				<header class="col-12"><h4>sunportal</h4></header>
			</div>
			<div class="row">
				<div class="status-container col-sm">
					<div class="status">
						<h5 class="lang en">today's yield</h5>
						<h5 class="lang de">Heutiger Ertrag</h5>
						<p class="meter" id="dayTotal">
							<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
							<span class="sr-only">Loading ...</span>
						</p>
						<div class="line"></div>
					</div>
				</div>
				<div class="status-container col-sm">
					<div class="status">
						<h5 class="lang en">total yield</h5>
						<h5 class="lang de">Gesamtertrag</h5>
						<p class="meter" id="total">
							<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
							<span class="sr-only">Loading ...</span>
						</p>
						<div class="line"></div>
					</div>
				</div>
				<div class="status-container col-sm">
					<div class="status">
						<h5 class="lang en">CO<sub>2</sub> savings</h5>
						<h5 class="lang de">CO<sub>2</sub>-Einsparung</h5>
						<p class="meter" id="co2">
							<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
							<span class="sr-only">Loading ...</span>
						</p>
						<div class="line"></div>
					</div>
				</div>
			</div>

			<div class="row" id="charts"></div>

			<div class="row">
				<div class="footer-container col-12">
					<a href="https://github.com/philipptrenz/sunportal"><i class="fa fa-github fa-2" aria-hidden="true" style="padding-right: 10px;"></i>github.com/philipptrenz/sunportal</a></div>
			</div>
		</div>
	</div>


	<script src="./js/jquery-3.3.1.js"></script>
	<script src="./js/moment.min.js"></script>
	<script src="./js/chart.js"></script>
	<script src="./js/main.js"></script>

</body>

</html>
