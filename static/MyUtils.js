//
var kd100Key={"1":"shentong","12":"yunda","18":"youshuwuliu","6":"shunfeng","10":"tiantian",
		"2":"tiandihuayu","3":"zhongtong","4":"huitongkuaidi","7":"suer","8":"debangwuliu","9":"xinbangwuliu",
		"ac6b5f8e67b34f04be4bd6e6b411f01c":"annengwuliu","e530c46fac52451ebaacedc567ebf1c3":"jiayunmeiwuliu",
		"11":"yuantong","jdex":"jd"};

function showTrace(shipId,expressId,expressNo){
	var com=kd100Key[expressId];
	if(com!=null){
		window.open("https://www.kuaidi100.com/chaxun?com="+com+"&nu="+expressNo);
	}else{
		top.$.jBox.tip("不支持查询物流轨迹。");
	}
}


function showDetail(shipId){
	var url="iframe:"+ctx+"/express/ship/trace?id="+shipId;
		top.$.jBox.open(url,"物流信息跟踪",750,600,
				{buttons:{"关闭":true}}
			);
}


function isMobile(mobile){
	mobile=$.trim(mobile);
	 var mobileReg= /^1[3|4|5|6|7|8|9][0-9]{9}$/; //验证规则
	 if(mobile==""){
		 return false;
	 }
	if(mobileReg.test(mobile)){
		return true;
	}
	 return false;
}


function isPhone(phone){
	phone=$.trim(phone);
	 var phoneReg=/^(\d{2,4}-?)?\d{7,8}$/;
	 if(phone==""){
		 return false;
	 }
	if(phoneReg.test(phone) || isMobile(phone)){
		return true;
	}
	 return false;
}



function doOpenDondong(el){
	var userId=$(el).data("userid");
	var shopId=$(el).data("shopid");
	var client=$(el).data("client");
	var pin=JdUserMap[userId+"-"+shopId];
	pin=window.encodeURIComponent(pin);
	client=window.encodeURIComponent(client);
	var param="JDWorkStation://jm/?command=openDD&pin="+pin+"&client="+client;
	param=window.btoa(param);
	var v=parseInt(Math.random()*(9999-1000+1)+1000,10);
	var url="https://localhost.jdjingmai.com:27353/?type=startClient&param="+param+"&callback=jsonp1551857617835&v="+v;
	$.get(url);
}

// 导出表格到 excel
var tableExport = (function () {
	var uri = 'data:application/vnd.ms-excel;base64,',
		template =
			'<html xmlns:o="urn:schemas-microsoft-com:office:office" ' +
			'xmlns:x="urn:schemas-microsoft-com:office:excel" ' +
			'xmlns="http://www.w3.org/TR/REC-html40"><head>' +
			'<!--[if gte mso 9]><xml><x:ExcelWorkbook>' +
			'<x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}' +
			'</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions>' +
			'</x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml>' +
			'<![endif]--></head><body><table border="1">{table}</table></body></html>',
		base64 = function (s) {
			return window.btoa(unescape(encodeURIComponent(s)));
		},
		format = function (s, c) {
			return s.replace(/{(\w+)}/g, function (m, p) { return c[p]; });
		}
	return function (table, fileName, sheetName) {
		if (!table.nodeType)
			table = document.getElementById(table);
		var ctx = { worksheet: sheetName || 'Worksheet', table: table.innerHTML }
		var a = document.createElement('a');
		a.href = uri + base64(format(template, ctx));
		a.download = fileName;
		a.click();
	}
})();
