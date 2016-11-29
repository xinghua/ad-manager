$(function(){
	var gameIdGlob=$("#gameId").val();
 	
    $("#mainForm").validate({
    	rules:{
    		gameId:{required:true,digits:true},
    		gameName:"required"
    	},
    	messages:{
    		gameId:{required:"游戏ID不能为空",digits:"游戏ID必须为整数"},
    		gameName:"游戏名称不能为空"
    	}		        	
    });
    /*
	//游戏ID校验 
    $("#gameId").blur(function(){
    //当前操作为修改时，不校验ID
    	if($("#titl").html()!="修改游戏"){
		  var gameId=$("#gameId").val();
			var $parent = $(this).parent();
			$parent.find(".formtips").remove();
			 //验证广告ID的合法性
			 if( $(this).is('#gameId') ){
				 $.ajax({
						Type:"Get",
						url:"/games/gameIdCheck",
						data:{gameId:gameId},
						contentType:"application/json",
						dataType:"json",
						success:function(msg){
							$parent.append('<span class="formtips onError" id="errorId" style="color:red">'+msg.msg+'</span>');
							if(msg.ret=="1"){
								$("#btn").attr("disabled",true);
							}else{
								$("#btn").attr("disabled",false);
							}
						 }	
						});	
			 		}
			 }
			});

    */

   // $(".selectpicker").selectpicker();
    $(".mytooltip").tooltip("");
});
/*
function deleteRow(obj,index){
	var gameId=$(obj).parent("td").parent("tr").find("input[name=gameId]").val();
	var flag=confirm("确定要删除游戏ID为"+gameId+"记录!");
	if(flag){
			$.ajax({
				Type:"GET",
				url:"/games/deleteGame",
				data:{gameId:gameId},
				dataType:"json",
				contentType:"application/json",
				success:function(msg){
					alert(msg.msg);
					//$(obj).parent("td").parent("tr").remove();	
					$("#mainTable").dataTable().fnDeleteRow($("#mainTable").dataTable().fnGetPosition($(obj).parents("tr").get(0)));
					}
				});
			}
	}
*/
function save(obj,index){
	
	if(index==1){
		$("#gameName").val("");
		$("#titl").text("添加游戏");
		$("#mainForm").attr("action","/app/system/game/add")
		
	}else if(index==2){
		var gameId=$(obj).parent("td").parent("tr").find("input[name=gameId]").val();
		var gameName=$(obj).parent("td").parent("tr").find("input[name=gameName]").val();
		$("#titl").text("修改游戏");
		//清除ID红色提示
		$("#errorId").remove();
		$("#gameId").val(gameId);
		$("#gameId").attr('readonly',true);
		$("#gameName").val(gameName);
		$("#mainForm").attr("action","/app/system/game/modify")
		}
	}
		
