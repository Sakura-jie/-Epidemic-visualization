var ec_right1=echarts.init(document.getElementById('r1'),"dark");
var ec_right1_Option={
	title:{
		text:"非湖北地区城市确诊TOP5",
		textStyle:{
			color:'white',
		},
		left:'left',
	},
	  color:['#3398DB'],
	    tooltip:{
		    trigger:'axis',
		    axisPointer:{
			    type:'shadow',			   
			}
		},
	xAxis:{
		type:'category',
		data:['东莞','珠海','境外输入','邢台','南京']
	},
	yAxis:{
		type:'value',
	},
	series:[{
		data:[99,98,96,94,93],
		type:'bar',
		barMaxWidth:"50%"
	}]
};
ec_right1.setOption(ec_right1_Option)