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
			 lng:data.map(function(d){return parseFloat(d.split("\t")[3])})
		 }
	 }

	 function fire()
	 {
		 viz=vis()
		 loadData(["data/d.txt"],[parse],viz.init)
	 }
	 
	 exports.main=function()
	 {
		 d3.select("body").append("button").on("click",fire).html("Start!")
	 }
 }
)(this)

main()
