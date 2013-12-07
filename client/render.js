(function(exports)
 {
	 var W=800,H=600
	 
	 exports.vis=function()
	 {
		 var startTime=new Date().getTime()
		 var events=[]
		 //var svg=d3.select("body").append("svg")
		 var canvas=d3.select("body").append("div").append("canvas").attr("height",H).attr("width",W).node()
		 //benchmark.start(svg.node())
		 
		 function record(d)
		 {
			 events.push({name:d,time:new Date().getTime()})
		 }

		 function draw_svg(data)
		 {
			 var id=d3.range(data.lat.length).filter(function(d){
				 return data.lng[d]>-126&&data.lng[d]<-65&&data.lat[d]>23&&data.lat[d]<48
			 })
			 var x=d3.scale.linear().domain(d3.extent(id.map(function(d){return data.lng[d]}))).range([0,W])
			 var y=d3.scale.linear().domain(d3.extent(id.map(function(d){return data.lat[d]}))).range([H,0])
			 svg.selectAll("circle").data(id).enter().append("circle")
				 .attr("cx",function(d){return x(data.lng[d])})
				 .attr("cy",function(d){return y(data.lat[d])})
				 .attr("r",1).attr("fill","red").attr("opacity",0.4)
			 alert(events[0].name+" :"+(events[0].time-startTime))
			 //record("Finishing rendering")
			 alert(events[1].name+" :"+(events[1].time-startTime))
		 }

		 function draw_canvas(data)
		 {
			 var ctx=canvas.getContext("2d")
			 var image=ctx.createImageData(W,H)
			 var c = d3.rgb(d3.scale.category20()(2));
			 var id=d3.range(data.lat.length)
			 var x=d3.scale.linear().domain(d3.extent(id.map(function(d){return data.lng[d]}))).range([0,W-1])
			 var y=d3.scale.linear().domain(d3.extent(id.map(function(d){return data.lat[d]}))).range([H-1,0])
			 var i=0
			 //			 for(var i=0;i<id.length;i++)
			 var tid=setInterval(function(){
				 var end=d3.min([i+100000,id.length])
				 //console.log(data.lat[0])
				 for(;i<end;i++)
				 {
					 var px=Math.round(x(data.lng[id[i]])),py=Math.round(y(data.lat[id[i]]))
					 image.data[(py*W+px)*4]=c.r
					 image.data[(py*W+px)*4+1]=c.g
					 image.data[(py*W+px)*4+2]=c.b
					 image.data[(py*W+px)*4+3]=d3.min([image.data[(py*W+px)*4+3]+70,255])
				 }
				 ctx.putImageData(image, 0, 0);
				 ctx.fillStyle="red"
				 //ctx.fillRect(0,0,100,100)
				 if (i==id.length)
				 {
					 record("Finishing rendering")
					 d3.select("body").append("div").html(events[0].name+" :"+(events[0].time-startTime)+"\n"+events[1].name+" :"+(events[1].time-startTime))
					 clearInterval(tid)
				 }
			 },10)
		 }

		 var ctx=canvas.getContext("2d")
		 var image=ctx.createImageData(W,H)

		 function incre_draw(dat)
		 {
			 if (!dat.lat)dat.lat=[-90,90]
			 if (!dat.lng)dat.lng=[-180,180]
			 var x=d3.scale.linear().domain(dat.lng).range([0,W-1])
			 var y=d3.scale.linear().domain(dat.lat).range([H-1,0])
			 var tt=0
			 var tid=setInterval(function(){
				 dat.parse(dat.file+tt+".txt",function(data)
						   {
							   data=data[0]
							   console.log(data)
							   var c = d3.rgb(d3.scale.category20()(2));
							   var id=d3.range(data.lat.length).filter(function(d){
								   return data.lng[d]>dat.lng[0]&&data.lng[d]<dat.lng[1]&&
									   data.lat[d]>dat.lat[0]&&data.lat[d]<dat.lat[1]
							   })
							   //id=d3.range(data.lat.length)
							   for(var i=0;i<id.length;i++)
							   {
								   var px=Math.round(x(data.lng[id[i]])),py=Math.round(y(data.lat[id[i]]))
								   image.data[(py*W+px)*4]=c.r
								   image.data[(py*W+px)*4+1]=c.g
								   image.data[(py*W+px)*4+2]=c.b
								   image.data[(py*W+px)*4+3]=d3.min([image.data[(py*W+px)*4+3]+70,255])
							   }
							   ctx.putImageData(image, 0, 0);
						   })
				 tt+=1
				 if (tt==dat.num)
					 clearInterval(tid)
			 },20)
		 }

		 return {
			 init:function(d)
			 {
				 var data=d[0]
				 record("Finishing loading data")
				 //				 draw_canvas(data)
				 if (data.flag)
					 draw_canvas(data)
				 else
					 incre_draw(data)
			 }
		 }
	 }
 })(this)
