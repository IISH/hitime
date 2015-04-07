/**
 * QueryBox 1.0
 * 
 * @author marcos weskamp, marcos@marumushi.com
 * @published Nov 30, 2008.
 * Copyright 2008, Marcos Weskamp marcos@marumushi.com
 * This work is licensed under a Creative Commons Attribution 3.0 Unported License. 
 * http://creativecommons.org/licenses/by/3.0/
 *  
 * QueryBox allows you to easily create a Live Search Input form lets users refine 
 * a search query and continuously show all valid results as they type.
 * This widget is built on top of the Dojo javascript framework.
 */
dojo.declare("marumushi.widget.QueryBox", null, {
	
	//what should we display by default
	defaultMessage				:'Search...',
	
	//displayed when no resuts are found				
	noResultsMessage			:'no results where found for ',
	
	//url to your results script
	queryURL					:'search?q=',
	
	//css class to use in this QueryBox	
	cssClass					:'QueryBox',
	
	// when focusing on the input field and hit enter where should we go. 
	// an empty string means go back to the same page we where at.					
	searchURL					:'',
	
	//(milis) time to wait to query backend script										
	keyDownTimeout				:200, 
	
	// (milis) how long until we give up waiting for results to come back.						
	requestTimeout				:5000, 
	
	//should we submit the query when user hasn't selected anything yet.							
	submitOnInputBlur			:true,
	
	//split results based on categories
	splitResultsOnCategories	:true,
	
	//private members you shouldn't need to change any of these.
	queryInputClass				:'QueryInput',
	resultContainerClass		:'ResultBox',
	listItemClass				:'ListItem',
	listItemSelectedClass		:'Selected',
	noResultsClass				:'NoResults',
	inputFieldID				:'lsquery_search_input',
	resultContainerID			:'lsquery_result',
	selectedContainerID 		:'lsquery_selected',
	formID						:'lsquery_form',
	lastQuery					:"",
	list						:[],
	selectedCursor				:-1,
	selectedItem				:null,	
	timer						:null,
	activeRequest				:null,
	currentQuery				:null,
	queryBoxContainerID			:null,
	
	// --------------------- PUBLIC METHODS ---------------------
	/**
	 * overrite this method in the instance if you want to customize the results box markup
	 * @param item the curren item data to render
	 * @param lastQuery the lastQuery submited to the server.
	 * */
	getItemMarkup:function(item,lastQuery){
		var title 	= this.highlightString(item.title,lastQuery);
		var descr 	= item.description!='' ? '<p>'+this.highlightString(item.description,lastQuery)+'</p>' : '';
		var line 	= '<div class="'+this.listItemClass+'"><a href="'+item.link+'"><h2>'+title+'</h2>'+descr+'</a></div>';
		return line;
	},
	/**
	 * overrite this method in the instance if you want to customize the results box markup
	 * @param data is an array of item objects returned from the server
	 */	
	getDropDownMarkup:function(data){
		var str = '';
		str+= '<div class="'+this.resultContainerClass+'">';
		str+= '<div class="Inside">';
		var categories={};
		var len = data.length;
		//split results by categories, depending on the type property
		if(this.splitResultsOnCategories){
			for (var n=0;n<len;n++){
				var item 	= data[n];
				var line	= this.getItemMarkup(item,this.lastQuery);
				if(categories[item.category]){
					categories[item.category]+=line;
				}else{
					categories[item.category]=line;
				}
				//str+=line;
			}
			//now build them nicely.
			for (var category in categories){
				str+='<div class="header"><h1>'+category+'</h1>'+categories[category]+'</div>';
			}
		}else{
			for (var n=0;n<len;n++){
				var item 	= data[n];
				var line	= this.getItemMarkup(item,this.lastQuery);
				str+=line;
			}
		}
		str+='</div>'; //Inside
		str+='</div>'; //ResultBox
		return str;
	},
	/**
	 * overrite this method in the instance if you want to customize the no results marukup
	 * @param lastQuery is the last query submited.
	 */
	getNoResultsMarkup:function(lastQuery){
		var str='';
		str+= '<div class="'+this.resultContainerClass+'">';
		str+= '<div class="Inside">';
		str+= '<div class="'+this.noResultsClass+'"><p>'+this.noResultsMessage+'<b>"'+lastQuery+'"</b></p></div>';
		str+= '<div>'; //Inside
		str+= '</div>'; //ResultBox
		return str;
	},
	
	// --------------------- PRIVATE METHODS ---------------------
	constructor:function(url,divID,displayQuery){
		if(url){
			this.queryURL = url;
		}else{
			str = 	"ERROR instantiating QueryBox.\n"+
					"When instantiating QueryBox you must provide a URL to the script that will return the search results to QueryBox.\n"+
					"The URL should be the path to the script we'll use to query for results.\n" +
				  	"ex: var qbox = new marumushi.widget.LiveSearchQueryBox('http://domain.com/search.php?q=','my_div_id');\n";
			console.error(str);
		}
		if(divID){
			this.queryBoxContainerID = divID;
		}else{
			str = 	"ERROR instantiating QueryBox.\n"+
					"When instantiating QueryBox you must provide the ID where QueryBox will be rendered.\n"+
				  	"ex: var qbox = new marumushi.widget.LiveSearchQueryBox('http://domain.com/search.php?q=','my_div_id');\n";
			console.error(str);
		}
		if(displayQuery){
			this.currentQuery = displayQuery;
		}
		//make all these guys unique based on its own uniqueID
		var id = this.queryBoxContainerID+"_";
		this.inputFieldID 			= id+this.inputFieldID;
		this.resultContainerID 		= id+this.resultContainerID;
		this.selectedContainerID 	= id+this.selectedContainerID;
		this.formID					= id+this.formID;
		var scope = this;
		//hang on to dojos onload event, then initialize.
		dojo.addOnLoad(function(){scope.init()});
	},

	init:function(){
		//console.log('init',this.queryBoxContainerID,dojo.byId(this.queryBoxContainerID));
		if(this.render()){
			var input = dojo.byId(this.inputFieldID);
			var scope = this;
			if(input){
				input.setAttribute("autocomplete","off");
				dojo.connect(input, "onkeydown", this, this.onKeyPress );
				dojo.connect(input, "focus", this, this.onTextInputFocus );
				dojo.connect(input, "blur", this, this.onTextInputBlur );
				input.value = this.currentQuery ? this.currentQuery : this.defaultMessage;
				//override submit event, use our own.
				dojo.connect( dojo.byId(this.formID), 'onsubmit',function(e){ dojo.stopEvent(e);scope.onFormSubmit(); } );				
			}else{
				console.error('search div not found');
			}
		}else{
			console.error('oh no, a fatal error happened while trying to render this box!');
		}
	},

	render:function(){
		var e = dojo.byId(this.queryBoxContainerID);
		if(e){
			e.innerHTML = this.getMarkup();
			return true;
		}else{
			console.error(this.queryBoxContainerID+' div not found! you need this div to render a QueryBox.');
			return false;
		}
	},

	getMarkup:function(){
		var value = this.currentQuery ? value='value="'+this.currentQuery+'" ': '';
		var markup = 
			'<div class="'+this.cssClass+'">'+
				'<div class="'+this.queryInputClass+'">'+
				   ' <form method="get" action="'+this.searchURL+'" id="'+this.formID+'" onsubmit="dojo.stopEvent(arguments[0]);return false;">'+
				    	'<div class="Input"><input type="text" name="q" id="'+this.inputFieldID+'" class="TextInput" '+value+'/></div>'+
				    	'<div class="Input Last"><input type="submit" value="Search" class="Button"/></div>'+
				    '</form>'+
			    '</div>'+
				'<div id="'+this.resultContainerID+'" style="display:none;"></div>'+
			'</div>';
		return markup;
	},

	setQueryValue:function(query){
		var input = dojo.byId(this.inputFieldID);
		if(input){
			input.value = query;
		}else{
			console.error('querybox has not been initialized yet');
		}
	},

	onFormSubmit:function(){
		var selected = dojo.byId(this.selectedContainerID);
		if(selected){
			//if you changed the item markup, you will need to change the way you get to the href here too.
			var url = selected.firstChild.getAttribute("href");
			window.location = url;
			return false;
		}else{
			//alert(this.searchURL);
			if(this.submitOnInputBlur){
				dojo.byId(this.formID).submit();
			}else{
				return false;
			}
		}
	},

	onKeyPress:function(event){
		//console.log(event.keyCode);
		switch(event.keyCode){
			//key down
			case 40 : this.selectPrevious(event); break;
			//key up
			case 38 : this.selectNext(event); break;
			//escape
			case 27 : this.hide(); break;
			//anything else
			default : this.start(); break;
		}
	},

	selectNext:function(event){
		if (!this.selectedItem) {
			this.selectedCursor = this.list.length-1;
		} else {
			this.selectedCursor--;
		}
		this.selectIndex(this.selectedCursor);
		if (!dojo.isIE) { event.preventDefault(); }
	},
	
	selectPrevious:function(event){
		if (!this.selectedItem) {
			this.selectedCursor = 0;
		} else {
			this.selectedCursor++;
		}
		this.selectIndex(this.selectedCursor);
		if (!dojo.isIE) { event.preventDefault(); }
	},
	
	selectIndex:function(index){
		if (this.selectedItem) { 
			this.selectedItem.removeAttribute("id");
			this.selectedItem.className = this.listItemClass;
		}
		this.selectedItem = this.list[index];
		if (this.selectedItem) { 
			this.selectedItem.setAttribute("id",this.selectedContainerID); 
			this.selectedItem.className = this.listItemClass+' '+this.listItemSelectedClass;
		}
	},
	
	sendRequest:function(){
		var scope=this;
		var query = dojo.byId(this.inputFieldID).value;
		this.lastQuery = query;
		if(this.activeRequest){
			this.activeRequest.cancel();
		}
		//nothing entered. hide the form
		if ( query == "" ) {
			this.hide();
			return false;
		}
		this.displayLoader(true);
		//send a new request
		//queryURL should be the path to the script we'll use to query for results.
		//ex: "http://domain.com/search.php?q="
		this.activeRequest = dojo.xhrGet( { 
	    	url: this.queryURL +query, 
	    	handleAs: "json",
	    	timeout: this.requestTimeout, // millis
	    	load: function(response, ioArgs) { 
		      	scope.onRequestData(response.results);
		      	return response;
	    	},
			error: function(response, ioArgs) {
				console.error("HTTP status code: ", ioArgs.xhr.status); 
				return response;
			}
	    });
	},
	/**
	 * TODO:
	 * probably want to switch visibility to on/off. loading is not good.
	 */
	displayLoader:function(value){
		var path = '../images/querybox/';
		var imageURL = value ? 'ajax-loader.gif' : 'search-icon-light.gif';
		dojo.byId(this.inputFieldID).style.backgroundImage='url('+path+imageURL+')';
	},

	highlightString:function(str,query){
		/*
			Grrr I hate regex!
			this should be way more efficient with something like this:
			var regex = new RegExp("(.+?)"+query+"(.+?)","g");  
			str.replace(regex,'$1<b>$2</b>$3'); 
			return str;
			but I just can't get it going properlly. any ideas?
	     */
	    var n = str.indexOf(query);
		if(n>=0){
			before = str.substr(0,n);
			word   = str.substr(n,query.length);
			after  = str.substr(n+query.length);
			str    = before+'<b>'+word+'</b>'+after;
			//console.log(str);
		}
		return str;
	     
	},
	
	onRequestData:function(data){
		this.displayLoader(false);
		var len 	= data.length;
		//console.log(len);
		var markup 	= len == 0 ? this.getNoResultsMarkup(this.lastQuery) : this.getDropDownMarkup(data);
		var container = dojo.byId(this.resultContainerID);
		if(container){
			container.innerHTML = markup;
			//make the container visible
			container.style.display = "block";
			//create a list of all item divs so we can loop over them on keypress
			var queryClass = '#'+this.resultContainerID+" ."+this.listItemClass;
			this.list = dojo.query(queryClass);
			this.selectedCursor = 0;
		}else{
			console.error('container:'+this.resultContainerID+'was not found.')
		}
	},
	
	hide:function() {
		this.selectIndex(-1);
		dojo.byId(this.resultContainerID).style.display = "none";
	},
	
	onTextInputBlur:function(){
		var input = dojo.byId(this.inputFieldID);
		if(input.value == '' ){input.value=this.defaultMessage};
		var scope = this;
		window.setTimeout(function(){scope.hide();},400);
	},
	
	onTextInputFocus:function(){
		var input = dojo.byId(this.inputFieldID);
		if(input.value == this.defaultMessage ){
			input.value='';
		}else{
			input.select();
		}
	},
	
	start:function() {
		var scope = this;
		if (scope.timer) {
			window.clearTimeout(scope.timer);
		}
		scope.timer = window.setTimeout(function(){scope.sendRequest();},scope.keyDownTimeout);
	}
});



