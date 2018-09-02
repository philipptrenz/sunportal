<?php


	$co2mult = 0.7;


	// Connection to database
	$db = new SQLite3("./SBFspot.db");

	// Uptime
	$query = "SELECT * FROM SpotData;";
	$rs = $db->query($query);
	$row = $rs->fetchArray(SQLITE3_ASSOC);
	$uptime = $row['OperatingTime'];


	// Get inverters
	$query = "SELECT Serial, Name FROM Inverters;";
	$rs = $db->query($query);

	$inverters = array();
	$i = 0;

	while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
		$inverters[$i]['serial'] = $res['Serial']; 
		$inverters[$i]['name'] = $res['Name']; 
		# echo 'Found inverter ' . $inverters[$i]['name'] . ' with serial number ' . $inverters[$i]['serial'] . '<br />';
		$i++; 
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
		$query = "SELECT TimeStamp, Power FROM DayData WHERE Serial == $serial AND TimeStamp >= (SELECT (MAX(TimeStamp)-86400) FROM DayData);";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);	
		$current = $row['Power'];

		$table = array();
		$i = 0; 

		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
			$table[$i]['time'] = $res['TimeStamp']; 
			$table[$i]['power'] = $res['Power']; 
			$i++; 
		} 

		// Total yield of today
		$query = "SELECT EToday FROM SpotData WHERE Serial == $serial AND TimeStamp = (SELECT MAX(TimeStamp) FROM SpotData);";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);	
		$totalday = $row['EToday'];

		// Latest yield and CO2 savings
		$query = "SELECT ETotal FROM SpotData WHERE Serial == $serial AND TimeStamp = (SELECT MAX(TimeStamp) FROM SpotData);";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$total = $row['ETotal'] / 1000;
		$co2 = $total * $co2mult;
		$co2 = round($co2) / 1000;
		$totalall = round($total);

		// Last update
		$query = "SELECT MAX(TimeStamp) AS TimeStamp FROM SpotData WHERE Serial == $serial;";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$epoch = $row['TimeStamp'];


		$inverter_data[$name] = array("serial" => $serial, "last24h" => $table, "dayTotal" => $totalday, "total" => $totalall, "co2" => $co2, "update" => $epoch);

		$data['dayTotal'] += $totalday;
		$data['total'] += $totalall;
		$data['co2'] += $co2;

	}

	$data['inverters'] = $inverter_data;

	// Reset database connection
	$db = NULL;

	echo json_encode($data);
	
?>