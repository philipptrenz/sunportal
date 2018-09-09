<?php


	$co2mult = 0.7;

	// Connection to database
	$db = new SQLite3("./SBFspot.db");

	$today = date('Y-m-d'); // TEST
	$todayStart = strtotime( $today );
	$todayEnd = strtotime( $today.' +1 day' );
	
	// get requested day from POST variable
	if(isset($_POST["date"])) $day = $_POST["date"];
	else $day = $today;
	
	$requestedDayStart = strtotime( $day );
	$requestedDayEnd = strtotime( $day.' +1 day' );

	$requestedMonthStart = strtotime( substr($day, 0, 7) . '-01');
	$requestedMonthEnd = strtotime(date("Y-m-t", $requestedMonthStart));

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
	
	// combined data of all inverters
	


	// Total yield (of all inverters) of requested day
	$dayTable = array();
	$hasDayPrevious = false;
	$hasDayNext = false;
	$dayTotal = 0;
	{
		$query = "
			SELECT TimeStamp, SUM(Power) AS Power 
			FROM DayData 
			WHERE TimeStamp BETWEEN $requestedDayStart AND $requestedDayEnd 
			GROUP BY TimeStamp
			HAVING Count(*)=" . sizeof($inverters) . ";
		";

		$rs = $db->query($query);
		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
			array_push($dayTable, array(
				"time" => $res['TimeStamp'],
				"power" => $res['Power']
			));
		} 

		$query = "
			SELECT SUM(EToday) as EToday
			FROM SpotData 
			WHERE TimeStamp == (SELECT MAX(TimeStamp) FROM SpotData WHERE TimeStamp BETWEEN $requestedDayStart AND $requestedDayEnd );

		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);	
		$dayTotal = $row['EToday'];


		// check if there is data available for previous and next day
		$query = "
			SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max 
			FROM (
				SELECT TimeStamp
				FROM DayData
				GROUP BY TimeStamp
				HAVING Count(*)=" . sizeof($inverters) . "
			);
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$hasDayPrevious = $row['Min'] < $requestedDayStart ? true : false;
		$hasDayNext = $row['Max'] > $requestedDayEnd ? true : false;
	}

	$monthTable = array();
	$hasMonthPrevious = false;
	$hasMonthNext = false;
	$monthTotal = 0;

	{
		$query = "
			SELECT TimeStamp, SUM(DayYield) AS Power 
			FROM MonthData 
			WHERE TimeStamp BETWEEN $requestedMonthStart AND $requestedMonthEnd
			GROUP BY TimeStamp
			HAVING Count(*)=" . sizeof($inverters) . ";
		";

		$rs = $db->query($query);
		$monthTotal = 0;
		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
			array_push($monthTable, array(
				"time" => $res['TimeStamp'],
				"power" => $res['Power']
			));
			$monthTotal += $res['Power'];
		} 


		// check if there is data available for previous and next day
		$query = "
			SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max 
			FROM (
				SELECT TimeStamp
				FROM MonthData
				GROUP BY TimeStamp
				HAVING Count(*)=" . sizeof($inverters) . "
			);
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$hasMonthPrevious = $row['Min'] < $requestedMonthStart ? true : false;
		$hasMonthNext = $row['Max'] > $requestedMonthEnd ? true : false;
		
	}
	
	$invDat = array(
		"serial" => "0000", 
		"name" => "all",
		"date" => $day, 
		"day" => array(
			"data" => $dayTable, 
			"hasPrevious" => $hasDayPrevious,
			"hasNext" => $hasDayNext,
			"interval" => array(
				"from" => $requestedDayStart,
				"to" => $requestedDayEnd
			),
			"total" => $dayTotal
		),
		"month" => array(
			"data" => $monthTable, 
			"hasPrevious" => $hasMonthPrevious,
			"hasNext" => $hasMonthNext,
			"interval" => array(
				"from" => $requestedMonthStart,
				"to" => $requestedMonthEnd
			),
			"total" => $monthTotal
		)

		);
	array_push($inverter_data, $invDat);


	// Add data
	$data['requested'] = array( "date" => $day, "inverters" => $inverter_data);

	

	/*
	// combined data of all inverters at requested month
	{

		
		// Total yield (of all inverters) of last 24h 
		$table = array();

		$query = "
			SELECT TimeStamp, SUM(DayYield) AS Power 
			FROM MonthData 
			WHERE TimeStamp BETWEEN $requestedMonthStart AND $requestedMonthEnd
			GROUP BY TimeStamp
			HAVING Count(*)=" . sizeof($inverters) . ";
		";

		$rs = $db->query($query);
		$monthTotal = 0;
		while($res = $rs->fetchArray(SQLITE3_ASSOC)){ 
			array_push($table, array(
				"time" => $res['TimeStamp'],
				"power" => $res['Power']
			));
			$monthTotal += $res['Power'];
		} 


		// check if there is data available for previous and next day
		$query = "
			SELECT MIN(TimeStamp) as Min, MAX(TimeStamp) as Max 
			FROM (
				SELECT TimeStamp
				FROM MonthData
				GROUP BY TimeStamp
				HAVING Count(*)=" . sizeof($inverters) . "
			);
		";
		$rs = $db->query($query);
		$row = $rs->fetchArray(SQLITE3_ASSOC);
		$hasPrevious = $row['Min'] < $requestedMonthStart ? true : false;
		$hasNext = $row['Max'] > $requestedMonthEnd ? true : false;
		
		$invDat = array(
			"serial" => "0000", 
			"name" => "all",
			"month" => $month, 
			"data" => $table, 
			"total" => $monthTotal,
			"hasPrevious" => $hasPrevious,
			"hasNext" => $hasNext
 		);
		array_push($inverter_data, $invDat);


		// Add month data to array
		$data['requested'] = array( "type" => "month", "month" => $month, "inverters" => $inverter_data);
	}*/

	// Reset database connection
	$db = NULL;

	echo json_encode($data);
	
?>