<?
/**
 * TO RUN THIS SCRIPT YOU WILL NEED TO SETUP YOUR DATABASE PROPERLY.
 * PLEASE TAKE A LOOK AT THE README.TXT file.
 */
require "includes/class.queryboxdb.php";
 
$q 		= !empty($_GET['q']) ? $_GET['q'] : null;
$search = new QueryBoxDB();
$search->query($q);
$search->serve();

?>