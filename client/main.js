(function(exports)
 {
	 
	 function loadData(files,func,callback)
	 {
		 var data=[];
		 
		 (function load()
		  {
			  if (data.length<files.length)
				  d3.text(files[data.length],function(d)
						  {
							  data.push(func[data.length](d))
							  load()
						  })
			  else
				  callback(data)
		  })()
	 }

	 function parse(data)
	 {
		 data=data.split("\n")
		 return {
			 time:data.map(function(d){return d.split("\t")[1]}),
			 lat:data.map(function(d){return parseFloat(d.split("\t")[2])}),
			 lng:data.map(function(d){return parseFloat(d.split("\t")[3])}),
			 flag:true
		 }
	 }

	 exports.parse=parse

	 function loadCSV(file,callback)
	 {
		 d3.csv(file,function(d){
			 var data={
				 lat:d.map(function(dd){return parseFloat(dd.lat)}),
				 lng:d.map(function(dd){return parseFloat(dd.long)}),
				 flag:true
			 }
			 callback([data])
		 })
	 }

	 function loadText(file,callback)
	 {
		 d3.text(file,function(d){
			 callback([parse(d)])
		 })
	 }

	 function fire()
	 {
		 viz=vis()
		 //loadData(["data/dat.txt"],[parse],viz.init)
		 //loadCSV("data/earthquakes.csv",viz.init)
		 //viz.init([{flag:false,file:"data/earth",num:8,parse:loadCSV}])
		 viz.init([{flag:false,file:"data/new/data",num:5,parse:loadText,lat:[23,48],lng:[-126,-65]}])
		 
	 }
	 
	 exports.main=function()
	 {
		 d3.select("body").append("button").on("click",fire).html("Start!")
	 }
 }
)(this)

main()
