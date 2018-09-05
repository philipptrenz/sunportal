<?php


	$co2mult = 0.7;


	// Connection to database
	$db = new SQLite3("./SBFspot.db");



	//$day = date('Y-m-d'); // TEST
	$day = '2018-09-04';
	

	// get requested date from POST variable
	if(isset($_POST["day"])) {

		$day = $_POST["day"];

	}

	$time1 = strtotime( $day );
	$time2 = strtotime( $day.' +1 day' );


	// Uptime
	$query = "
		SELECT * 
		FROM SpotData;
	";
	$rs = $db->query($query);
	$row = $rs->fetchArray(SQLITE3_ASSOC);
	$uptime = $row['OperatingTime'];


	// Get inverters
	$inverters = array();
	$query = "
		SELECT Serial, Name 
		FROM Inverters;
	";
	$rs = $db->query($query);
	while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
		array_push($inverters, array(
			"serial" => $res['Serial'],
			"name" => $res['Name']
		));
	}

	$inverter_data = array();
	$data = array();
	$data['dayTotal'] = 0;
	$data['total'] = 0;
	$data['co2'] = 0;


	foreach($inverters as $item) {

		$serial = $item['serial'];
		$name   = $item['name'];

		// Daily yield of yesterday
		$query = "
			SELECT TimeStamp, Power 
			FROM DayData 
			WHERE Serial == $serial AND TimeStamp BETWEEN $time1 AND $time2;
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);	
		$current = $row['Power'];

		$table = array();
		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
			array_push($table, array(
				"time" => $res['TimeStamp'],
				"power" => $res['Power']
			));
		} 

		// Yield of today
		$query = "
			SELECT EToday 
			FROM SpotData 
			WHERE Serial == $serial AND TimeStamp BETWEEN $time1 AND $time2;
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);	
		$totalday = $row['EToday'];

		// Total yield and CO2 savings
		$query = "
			SELECT ETotal 
			FROM SpotData 
			WHERE Serial == $serial AND TimeStamp BETWEEN $time1 AND $time2;
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$total = $row['ETotal'] / 1000;
		$co2 = $total * $co2mult;
		$co2 = round($co2) / 1000;
		$totalall = round($total);

		// Last update
		$query = "
			SELECT MAX(TimeStamp) 
			AS TimeStamp 
			FROM SpotData 
			WHERE Serial == $serial;
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$epoch = $row['TimeStamp'];


		$inverter_data[$name] = array("serial" => $serial, "last24h" => $table, "dayTotal" => $totalday, "total" => $totalall, "co2" => $co2, "update" => $epoch);

		$data['dayTotal'] += $totalday;
		$data['total'] += $totalall;
		$data['co2'] += $co2;

	}
	
	// combined data of all inverters
	{
		// Total yield (of all inverters) of last 24h 
		$table = array();
		//$query = "SELECT TimeStamp, SUM(Power) AS Power FROM DayData WHERE TimeStamp >= (SELECT (MAX(TimeStamp)-86400) FROM DayData) GROUP BY TimeStamp HAVING Count(*)=" . sizeof($inverters) . ";";

		// WHERE TimeStamp > " . strtotime( $day ) . " AND TimeStamp < " . strtotime( $day.' +1 day' ) . " 

		$query = "
			SELECT TimeStamp, SUM(Power) 
			AS Power FROM DayData 
			WHERE TimeStamp BETWEEN $time1 AND $time2 
			GROUP BY TimeStamp
			HAVING Count(*)=" . sizeof($inverters) . ";
		";

		$rs = $db->query($query);
		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
			array_push($table, array(
				"time" => $res['TimeStamp'],
				"power" => $res['Power']
			));
		} 

		$inverter_data["all"] = array("serial" => "0000", "last24h" => $table, "dayTotal" => $data['dayTotal'], "total" =>$data['total'], "co2" => $data['co2']);
	}

	// Deactivate single charts for now
	unset($inverter_data["SN: 2130309491"]);
	unset($inverter_data["SN: 2130340030"]);

	$data['inverters'] = $inverter_data;

	// Reset database connection
	$db = NULL;

	echo json_encode($data);
	
?>