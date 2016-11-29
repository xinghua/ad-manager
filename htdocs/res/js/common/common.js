$(function(){
	$("#mainTable").dataTable( {
		"bPaginate": false,
		"bLengthChange": false,	//显示每页条数
		"bFilter": false,
		"bSort": false,
		"bInfo": false,
		"bAutoWidth": false
	} );
	
	$("#beginDate").datetimepicker({
        format:"yyyy-mm-dd",
        language:  'zh-CN',
        weekStart: 1,
        autoclose: 1,
        minView: 2
	});
	
	
	//处理开始时间格式错误问题
	$("#beginDate").blur(function(){
		var inputDate = $("#beginDate").val();
		var y = ($.trim(inputDate)).substring(0,4);
		if(y<2000){
			var now = new Date(new Date().getTime()-24*60*60*1000);
			$("#beginDate").val((now).format("yyyy-MM-dd"));
		}
	});
	
	
	$("#endDate").datetimepicker({
        format:"yyyy-mm-dd",
        language:  'zh-CN',
        weekStart: 1,
        autoclose: 1,
        minView: 2
	});
	
	//处理结束时间格式错误问题
	$("#endDate").blur(function(){
		var inputDate = $("#endDate").val();
		var y = ($.trim(inputDate)).substring(0,4);
		if(y<2000){
			var now = new Date(new Date().getTime()-24*60*60*1000);
			$("#endDate").val((now).format("yyyy-MM-dd"));
		}
	});
	
	
	 $("#checkAll").click(function(){
		$("[name=items]:checkbox").prop("checked",this.checked);

		});
	 $("[name=items]:checkbox").click(function(){
			//定义一个临时变量，避免重复使用同一个选择器选择页面中的元素，提升程序效率。
			var $tmp=$("[name=items]:checkbox");
			//用filter方法筛选出选中的复选框。并直接给CheckedAll赋值。
			$("#checkAll").prop('checked',$tmp.length==$tmp.filter(':checked').length);
		});
		$(".selectpicker").selectpicker();
		$('select.selectpicker').each(function(i, e){
		   var $self = $(e);
		   $self.val($self.attr('data-value'));
		});
		$(".selectpicker").selectpicker("render");
		$(".selectpicker").selectpicker("refresh");				
});


function setCookie(name, value) {
        var exp = new Date();
        exp.setTime(exp.getTime() + 24 * 60 * 60 * 1000);
        document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString();
    }
function getCookie(name)
{
    var regExp = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
    var arr = document.cookie.match(regExp);
    if (arr == null) {
        return null;
    }
    return unescape(arr[2]);
}


Date.prototype.format = function (fmt) { 
    var o = {
        "M+": this.getMonth() + 1, //月份 
        "d+": this.getDate(), //日 
        "h+": this.getHours(), //小时 
        "m+": this.getMinutes(), //分 
        "s+": this.getSeconds(), //秒 
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
        "S": this.getMilliseconds() //毫秒 
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}
