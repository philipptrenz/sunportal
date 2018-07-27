<?php


	$co2mult = 0.7;


	//Connection to database
	$db = new SQLite3("../SBFspot.db");

	//Uptime
	$query = "SELECT * FROM SpotData;";
	$rs = $db->query($query);
	$row = $rs->fetchArray(SQLITE3_ASSOC);
	$uptime = $row['OperatingTime'];


	//Huidig kwh van de laatste dag
	$query = "SELECT TimeStamp, Power FROM DayData WHERE TimeStamp >= (SELECT (MAX(TimeStamp)-86400) FROM DayData);";
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

	//Totaal van deze dag
	$query = "SELECT EToday FROM SpotData WHERE TimeStamp = (SELECT MAX(TimeStamp) FROM SpotData);";
	$rs = $db->query($query);
	$row = $rs->fetchArray(SQLITE3_ASSOC);	
	$totalday = $row['EToday'];

	//Huidig totaal en CO2
	$query = "SELECT ETotal FROM SpotData WHERE TimeStamp = (SELECT MAX(TimeStamp) FROM SpotData);";
	$rs = $db->query($query);
	$row = $rs->fetchArray(SQLITE3_ASSOC);
	$total = $row['ETotal'] / 1000;
	$co2 = $total * $co2mult;
	$co2 = round($co2) / 1000;
	$totalall = round($total);

	//Laatste update
	$query = "SELECT MAX(TimeStamp) AS TimeStamp FROM SpotData;";
	$rs = $db->query($query);
	$row = $rs->fetchArray(SQLITE3_ASSOC);
	$epoch = $row['TimeStamp'];



	//Reset database connection
	$db = NULL;

	echo json_encode(array("last24h" => $table, "dayTotal" => $totalday, "total" => $totalall, "co2" => $co2, "update" => $epoch));
	
?>