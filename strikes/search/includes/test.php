<?php
/**
 
Copyright (c) 2008 Marcos Weskamp.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

**/

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
 */
class QueryBoxCSV {
	// to run this demo, go grab the this csv file over here:
	// http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv
	// then drop it inside the data folder.
	private $filePath 	 = "data/SUB-EST2009_ALL.csv";
	private $max_results = 10;
	
	public function query($q){
	
		$output = "{query:'$q',results:[";
		if($q){
			$row 	= 1;
			$found 	= 0;
			$handle = fopen($this->filePath, "r");
			if(!$handle){
				echo '<h1>OH NO!</h1>' .
					 '<strong>The required file SUB-EST2005-all.csv was not found insinde the tests/data/ directory</strong>.<br />' .
					 'go grab a copy of this file at <a href="http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv">http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv</a> (7MB download)<br />' .
					 'drop it inside the <strong>/tests/data</strong> directory and try running this script again.';
				die;
			}
			while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
				$city 	= $data[5];
				$state 	= $data[6];
				$pop	= $data[7];
				if($row!=1){
					if(preg_match("/$q/i",$city)) {
						$output.=  "{\"title\":\"$city\",\"link\":\"$city\",\"description\":\"population: $pop\",\"id\":\"$row\",\"category\":\"$state\"}";
						if($found++>$this->max_results){
							break;
						}else{
							$output.=",\n";
						}
					}
				}
			    $row++;
			}
			fclose($handle);
		}
		$output.=']}';
		
		return $output;
	}
}

?>

