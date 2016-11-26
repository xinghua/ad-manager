$(function(){
    $("#mainForm").validate({
    	rules:{
    		channel_name:"required",
    	},
    	messages:{
    		channel_name:"渠道名称不能为空"
    	}		        	
    });
});

function save(obj,index){
	
	if(index==1){
		$("#channel_name").val("");
		$("#titl").text("添加渠道");
		$("#mainForm").attr("action","/games/addGames")
		
	}else if(index==2){
		var channel_id=$(obj).parent("td").parent("tr").find("input[name=channel_id]").val();
		var channel_name=$(obj).parent("td").parent("tr").find("input[name=channel_name]").val();
		var media_type =$(obj).parent("td").parent("tr").find("input[name=media_type]").val();
		var pay_type =$(obj).parent("td").parent("tr").find("input[name=pay_type]").val();
		$("#titl").text("修改渠道");
		//清除ID红色提示
		$("#errorId").remove();
		$("#channel_id").val(channel_id);
		$("#channel_id").attr('readonly',true);
		$("#channel_name").val(channel_name);
		$('#media_type').selectpicker('val', media_type);
		$('#pay_type').selectpicker('val', pay_type);
		$("#mainForm").attr("action","/games/updateGames")
		}
	}
		
