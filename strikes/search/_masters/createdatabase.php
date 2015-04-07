<?
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

$c = new CreateDatabase();
$c->create();

class CreateDatabase {
	
	// to run this demo, go grab the this csv file over here:
	// http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv
	// then drop it inside the ../data/ folder.
	private $filePath 	 = "../data/SUB-EST2005-all.csv";
	
	private $host 	= '127.0.0.1';
	private $user 	= '--username--';
	private $pass 	= '--password--';
	private $table 	= '--tablename--';
	
	public function create(){
	
		$handle = fopen($this->filePath, "r");
		
		if(!$handle){
			echo '<h1>OH NO!</h1>' .
				 '<strong>The required file SUB-EST2005-all.csv was not found insinde the tests/data/ directory</strong>.<br />' .
				 'go grab a copy of this file at <a href="http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv">http://www.census.gov/popest/cities/files/SUB-EST2005-all.csv</a> (7MB download)<br />' .
				 'drop it inside the <strong>/tests/data</strong> directory and try running this script again.';
			die;
		}
		
		$db = mysqli_connect( $this->host, $this->user, $this->pass, $this->table);
		$row 	= 1;
		$found 	= 0;
		
		$sql = "CREATE TABLE `uscities` (" .
				"`id` int(11) NOT NULL auto_increment," .
				"`city_name` varchar(255) default NULL," .
				"`state_name` varchar(255) default NULL," .
				"`population` int(100) default NULL," .
				"PRIMARY KEY  (`id`)" .
			");";
		
		$result = mysqli_query($db,$sql);
		
		while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
			$city 	= $data[5];
			$state 	= $data[6];
			$pop	= $data[7];
			if($row!=1){
				$sql 	= "INSERT INTO uscities (city_name, state_name, population) VALUES ('$city','$state',$pop);";
				$result = mysqli_query($db,$sql);
			}
		    $row++;
		}
		fclose($handle);

	}
}


?>