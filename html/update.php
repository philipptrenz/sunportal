<?php


	$co2mult = 0.7;

	// Connection to database
	$db = new SQLite3("./SBFspot.db");

	$today = date('Y-m-d'); // TEST
	$todayStart = strtotime( $today );
	$todayEnd = strtotime( $today.' +1 day' );
	
	// get requested date from POST variable
	if(isset($_POST["day"])) $day = $_POST["day"];
	else $day = $today;

	$requestedDayStart = strtotime( $day );
	$requestedDayEnd = strtotime( $day.' +1 day' );

	$data = array();

	// general current data
	{	
		$currentInverterData = array();
		$totalday = 0;
		$total = 0;
		$co2 = 0;

		$query = "
			SELECT Serial, TimeStamp, EToday, ETotal, Status, OperatingTime
			FROM SpotData 
			WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM SpotData);
		";

		$rs = $db->query($query);
		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 

			$invCo2 = round( $res["ETotal"] / 1000 * $co2mult );

			$currentInverterData[$res["Serial"]] = array( 
				"lastUpdated" => $res["TimeStamp"], 
				"dayTotal" => $res["EToday"], 
				"total" => $res["ETotal"] , 
				"co2" => $invCo2,
				"status" => $res["Status"]
			);

			$totalday += $res["EToday"];
			$total += $res["ETotal"];
			$co2 += $invCo2;

		}

		$data['today'] = array( "dayTotal" => $totalday, "total" => $total, "co2" => $co2, "inverters" => $currentInverterData);
	}

	$inverters = array();
	$inverter_data = array();

	// Get inverters
	$query = "
		SELECT Serial, Name 
		FROM Inverters;
	";
	$rs = $db->query($query);
	while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
		array_push($inverters, array(
			"serial" => strval($res['Serial']),
			"name" => $res['Name']
		));
	}
	
	// combined data of all inverters at requested day
	{
		// Total yield (of all inverters) of last 24h 
		$table = array();

		$query = "
			SELECT TimeStamp, SUM(Power) AS Power 
			FROM DayData 
			WHERE TimeStamp BETWEEN $requestedDayStart AND $requestedDayEnd 
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

		$query = "
			SELECT SUM(EToday) as EToday
			FROM SpotData 
			WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM SpotData WHERE TimeStamp BETWEEN $requestedDayStart AND $requestedDayEnd );

		";

		//WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM (SELECT TimeStamp FROMSpotData WHERE TimeStamp BETWEEN $requestedDayStart AND $requestedDayEnd ));

		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);	
		$dayTotal = $row['EToday'];


		$invDat = array(
			"serial" => "0000", 
			"name" => "all",
			"day" => $day, 
			"data" => $table, 
			"dayTotal" => $dayTotal
		);
		array_push($inverter_data, $invDat);
	}

	/*
	{
		foreach($inverters as $item) {

			$serial = $item['serial'];
			$name   = $item['name'];

			// Daily yield of requested day
			$query = "
				SELECT TimeStamp, Power, SUM(Power) AS TotalDay
				FROM DayData 
				WHERE Serial == $serial AND TimeStamp BETWEEN $requestedDayStart AND $requestedDayEnd;
			";
			$rs = $db->query($query);
			$row = $rs->fetchArray(SQLITE3_ASSOC);	
			$current = $row['Power'];

			$totalday = 0;
			$table = array();
			while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
				array_push($table, array(
					"time" => $res['TimeStamp'],
					"power" => $res['Power']
				));
				$totalday = $row['TotalDay'];
			} 

			$invDat = array(
				"serial" => $serial, 
				"name" => $name, 
				"day" => $day, 
				"data" => $table, 
				"dayTotal" => $totalday
			);
			array_push($inverter_data, $invDat);
		}
	}*/

	$data['requested'] = array( "day" => $day, "inverters" => $inverter_data);

	// Reset database connection
	$db = NULL;

	echo json_encode($data);
	
?>