<?PHP
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
	 * 
	 * QueryBox
	 * @author Marcos Weskamp, marcos@marumushi.com
	 * @published Nov 30, 2008.
	 * Copyright 2008, Marcos Weskamp marcos@marumushi.com
	 * This work is licensed under a Creative Commons Attribution 3.0 Unported License. 
	 * http://creativecommons.org/licenses/by/3.0/
	 * 
	 * PHP Serverside counterpart for QueryBox.
	 * Queries Database and send back results to the dojo Widget using Json
	 * 
	 * @example:
	 * <?
	 * 		require '../includes/class.querybox.php';
	 * 
	 *		$search_query = !empty($_GET['q']) ? $_GET['q'] : null;
	 * 		$search = new QueryBoxDB();
	 * 
	 * 		if($search_query){
	 * 	 		//create the query to your DB, and serve the Json Results:
	 *			$search->query($search_query);
	 *			$search->serve();
	 *		} else {
	 *	 		//render the Dojo SearchBox:
	 *			?>
	 *		    <html>
	 *			<head>
	 *			<link rel="stylesheet" type="text/css" href="css/querybox.css" />
	 *			<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/dojo/1.2.0/dojo/dojo.xd.js"></script>
	 *			<script type="text/javascript" src="js/marumushi.widget.querybox.js"></script>
	 *			<script type="text/javascript">
	 *				var queryBox  = new marumushi.widget.QueryBox("tests/search.php?q=","qbox"); //<-- thats it!
	 *			</script>
	 *			<head>
	 *			<body>
	 *			<div class="qbox"><!--- querybox will be rendered here ---></div>
	 *			</body>
	 *			</html>
	 *			<?
	 *		}
	 *	?>
	 */
	class QueryBoxDB {
		
		/**
		 * You will need to set these up to get this demo running.
		 */	 	
		public $host	 = "--host--";		/* The host to connect to */
		public $dbname	 = "--dbname--"; 	/* The name of the database to query */ 
		public $username = "--username--"; 	/* The user to connect as */
		public $password = "--password--"; 	/* The password to use */
		
		
		public $limit = 10;
		public $items = array();
		/**
		 * renders QueryBox
		 */
		public function render($id='qbox',$queryURL=null){
			if(!$queryURL){$queryURL=$_SERVER['PHP_SELF'].'?q=';};
			echo $this->getMarkUp($id,$queryURL);
		}
		/**
		 * gets the HTML Markup for QueryBox.
		 */
		public function getMarkUp($id,$queryURL){
			$output = 
			'<script type="text/javascript">' .
			'var '.$id.' 	= new marumushi.widget.QueryBox("'.$queryURL.'","'.$id.'");' .
			'</script>'.
			'<div id="'.$id.'"></div>';
			return $output;
		}
		/**
		 * Serves the result of a query in JSON format.
		 * Used to send back the results to the Dojo LiveSearchQueryBox
		 * */
		public function serve() {
			$output = $this->getOutput();
			//header("Content-type: application/json");
			echo $output;
		}
		/**
		 * call this method to add items in the JSON result
		 */
		public function addItem($item) {
			$this->items[] = $item;
		}
		/**
		 * gets the JSON result output
		 */
		private function getOutput() {
			//write header
			$out  = '{results:[';
			$c=0;
			//write content
			foreach($this->items as $item) {
				if($c++>0){
					$out.=',';
				}
				$out .= $item->getOutput();
			}
			//write footer
			$out .= ']}';

			return $out;
		}
		public function getResultsMarkup(){
			$out ="<div class='QueryBox'><div class='ResultsPage'>";
			foreach($this->items as $item) {
				$out .= $item->getMarkup();
			}
			$out .="</div></div>";
			return $out;
		}
		public function renderResultsMarkup(){
			echo $this->getResultsMarkup();
		}
		/**
		 * For the sake of the demo, I've included all data querying in here.
		 * You probably want to abstract all this by using any of the super
		 * fancy PHP framworks out there.
		 * 
		 * The important thing is:
		 * 1. query the database
		 * 2. loop over the results
		 * 3. create one result object for each row you found in the DB
		 * 4. add that result object to this QueryBoxDB instance using $this->addItem($result);
		 * 5. when done call the serve() method to serve the results.
		 * 6. boila.
		 */
		function query($q){
			$this->items = array();
			$db 	= mysqli_connect( $this->host,$this->username,$this->password,$this->dbname );
	        $q 		= mysqli_real_escape_string($db, $q);
			$sql 	= 'SELECT * FROM uscities WHERE `city_name` LIKE "%'.$q.'%" ORDER BY population DESC LIMIT '.$this->limit.';';
			if ($rows = mysqli_query($db,$sql)){
				while( $row = mysqli_fetch_assoc($rows) ){ 
					$result = new Result();
					$result->id				= $row['id'];
					$result->title 			= $row['city_name'];
					$result->description 	= 'population: '.$row['population'];
					$result->link 			= 'http://www.google.com/search?q='.$result->title;
					$result->category 		= $row['state_name'];
					$this->addItem($result);
				}
				mysqli_free_result($rows); 
			}
			mysqli_close($db); 
		}
	
	}

	/**
	 * Each result object that will be rendered as a JSON item.
	 */
	class Result {
		
		public $title;
		public $link;
		public $description;
		public $id;	
		public $category;	
		/**
		 * gets the JSON encoded string representation for this object.
		 */
		function getOutput() {
			$this->title 		= strip_tags($this->title);
			$this->description 	= strip_tags($this->description);
			$this->title 		= $this->smart_trim($this->title,30);
			$this->description 	= $this->smart_trim($this->description,35);
			//JSON encode self
			return json_encode($this);
		}
		/**
		 * gets the HTML Markup for this object.
		 */
		function getMarkup(){
			$str = "<div class='Result'>".
			$str.= "<h3><a href=''>".$this->smart_trim(strip_tags($this->title),60)."</a></h3>";
			$str.= "<p>".$this->smart_trim(strip_tags($this->description),100)."</p>";
			$str.= "</div>";
			return $str;
		}
		/**
		 * you probably don't need this here.
		 * Added for the sake of the Demo.
		 */
		function smart_trim($text, $max_len, $trim_chars = '...') {
			$text = trim($text);
			if (strlen($text) < $max_len) {
				return $text;
			}else{
				$trimmed_text = substr($text, 0, $max_len);
				$trimmed_text = trim($trimmed_text);
				return $trimmed_text.$trim_chars;
			}
		} 
	}