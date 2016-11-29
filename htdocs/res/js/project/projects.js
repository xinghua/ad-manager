$(function(){
    $("#mainForm").validate({
    	rules:{
    		project_name:"required",
    		url:"required",
    	},
    	messages:{
    		project_name:"广告名称不能为空",
    		url:"跳转链接不能为空",
    	}		        	
    });
});

$("#adCode").blur(function(){
	var $parent = $(this).parent();
	$parent.find(".formtips").remove();
	//验证广告ID的合法性
	if ($(this).is('#adCode')) {
		if (isNaN($("#adCode").val()) || $("#adCode").val().length > 10) {
			var errorMsg = '请输入合法的数字广告ID!';
			$parent.append('<span class="formtips onError" style="color:red">' + errorMsg + '</span>');
		}
	}
});

$("#search").click(function(){
	var adCode = $("#adCode").val() == "" ? 0 : $("#adCode").val().trim();
	var state = $("#state").val();
	var pageSize = $("#pageSize option:selected").val();
	console.info("pageSize=" + pageSize);
	var url = "/adCodes/" + $("#gameId").val() + "/" + adCode + "/" + $("#state").val() + "/" + $("#mediaId").val()  + "/" + pageSize + "/0";
	window.location.href = url;
});
$("#uploadForm").submit(function(){
	//验证文件扩展名
		var file=$("#fileUpload").val();
		var filename=file.replace(/.*(\/|\\)/, "");
		var fileExt=(/[.]/.exec(filename)) ? /[^.]+$/.exec(filename.toLowerCase()) : '';
		
		if(fileExt!="xls"){
			$("#alertDiv").css("display","block");
			return false;
		}
		return true;
	});

//检查是否数字
function isNum(a)
{
    var reg = /^d+(.d+)?$/;
    reg.test(a);
}
	
function save(obj,index){
	
	if(index==1){
		$("#project_name").val("");
		$("#url").val("");
		$("#titl").text("添加广告");
		$("#mainForm").attr("action","/app/project/add")
		
	}else if(index==2){
		var project_id=$(obj).parent("td").parent("tr").find("input[name=project_id]").val();
		var project_name=$(obj).parent("td").parent("tr").find("input[name=project_name]").val();
		var platform_id=$(obj).parent("td").parent("tr").find("input[name=platform_id]").val();
		var channel_id=$(obj).parent("td").parent("tr").find("input[name=channel_id]").val();
		var game_id=$(obj).parent("td").parent("tr").find("input[name=game_id]").val();
		var url=$(obj).parent("td").parent("tr").find("input[name=url]").val();
		$("#titl").text("修改广告");
		//清除ID红色提示
		$("#errorId").remove();
		$("#project_id").val(project_id);
		$("#project_id").attr('readonly',true);
		$("#project_name").val(project_name);
		$('#platform_id').selectpicker('val', platform_id);
		$('#channel_id').selectpicker('val', channel_id);
		$('#game_id').selectpicker('val', game_id);
		$("#url").val(url);
		$("#mainForm").attr("action","/app/project/modify")
		}
	}

function gen_code(obj){
    var adcode=$(obj).parent("td").parent("tr").find("input[name=adcode]").val();
    $("#adcode").val(adcode);
    $("#adcode").attr('readonly',true);
}
