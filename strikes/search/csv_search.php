<?
/**
 * DISCLAIMER:
 * 
 * I've included this script for the sake of the demo, to let
 * you run this immediately and try it out
 * without any Database Hassle.
 * Of course this setup is REALLY, REALLY BAD for a production 
 * environment. Everytime a user types something in querybox
 * this script will run, will read the 6.5 Megabyte csv file in Memory,
 * do some really slow string match and output the results.
 * 
 * Ideally you want to do this by having all the data 
 * stored in a database and querying properlly there.
 * 
 * FOR PROPER A DATABASE QUERY DEMO, TAKE A LOOK AT /tests/includes/class.querybox.php
 * 
 */
 
 require "includes/class.queryboxcsv.php";
 
$q 		= !empty($_GET['q']) ? $_GET['q'] : null;
//$q = "kansas";
$search = new QueryBoxCSV();
echo $search->query($q);

?>
