$(function(){
    $("#loginForm").validate({
    	rules:{
    		username:"required",
    		password:"required",
    	},
    	messages:{
    		username:"用户名不能为空",
    		password:"密码不能为空",
    	}		        	
    });
});
//指定iframe高度
$("#mainFrame").load(function(){
       //$(this).height(10000); 
       //$("#menu").height($("#mainFrame").height()-23);
	//var height=$("#mainFrame").contents().height();
	//alert(height);
	var iframeTemp = document.getElementById("mainFrame");
    var iframeHeight = Math.min(iframeTemp.contentWindow.window.document.documentElement.scrollHeight, iframeTemp.contentWindow.window.document.body.scrollHeight);
	if(iframeHeight<700) iframeHeight=700;
	$("#mainFrame").attr("height",iframeHeight);
   }); 
   
$("#account").click(function(){
	$("#breadcrumb").hide("normal");
});
   
//加粗当前点击的菜单，更新面包屑导航
$("[id^=menuSub]").click(function(){
	$("#breadcrumb").show("normal");
	$("[id^=menuSub]").css({"font-weight":"normal"});
	$(this).css({"font-weight":"bold"});
	
	$("#breadcrumbSub").html($(this).html().substr(69));			    	
	$("#breadcrumbMain").html($(this).parent().parent().parent().parent().find(".accordion-toggle").html());
});  

//展开所有菜单
$("[id^=menuMain]").collapse("show");
$("[id=menuSub1]").click();			    



