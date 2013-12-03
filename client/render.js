(function(exports)
 {
	 var W=800,H=600
	 
	 exports.vis=function()
	 {
		 var startTime=new Date().getTime()
		 var events=[]

		 function record(d)
		 {
			 events.push({name:d,time:new Date().getTime()})
		 }

		 return {
			 init:function(d)
			 {
				 record("Finishing loading data")
				 var data=d[0]
				 var svg=d3.select("body").append("svg")
				 exports.data=data
				 var id=d3.range(data.lat.length).filter(function(d){
					 return data.lng[d]>-126&&data.lng[d]<-65&&data.lat[d]>23&&data.lat[d]<48
				 })
				 var x=d3.scale.linear().domain(d3.extent(id.map(function(d){return data.lng[d]}))).range([0,W])
				 var y=d3.scale.linear().domain(d3.extent(id.map(function(d){return data.lat[d]}))).range([H,0])
				 svg.selectAll("circle").data(id).enter().append("circle")
					 .attr("cx",function(d){return x(data.lng[d])})
					 .attr("cy",function(d){return y(data.lat[d])})
					 .attr("r",1).attr("fill","red").attr("opacity",0.4)
				 record("Finishing rendering")
				 alert(events[0].name+" :"+(events[0].time-startTime)+"\n"+events[1].name+" :"+(events[1].time-startTime))
			 }
		 }
	 }
 })(this)
