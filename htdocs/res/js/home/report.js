
$("#btnSubmit").click(function(){
	var action = "/ltv/showLtvPage/0";						
		$("#searchForm").attr("action",action);
		$("#searchForm").submit();	
	});
//$("#mediaType").trigger("change");
					
$("#btnExport").click(function(){
	$("#searchForm").attr("action","/ltv/showLtvPage/excel");			 		
	$("#searchForm").submit();
});

$("#adType").change(function(){
	var adType=$("#adType").val();
	var mediaType=$("#mediaType");
	var mediaId = $("#mediaId");
	var random=Math.random();
	$("#mediaType option").remove();
	$("#mediaId option").remove();
	var optionAll="<option value='0'>全部</option>";
	mediaType.append(optionAll);
	mediaId.append(optionAll);
	$.ajax({
		type:"GET",
		contentType:"application/json",
		url:"/customize/userMediaType",
		data:{adType:adType,random:random},
		dataType:"json",
		async:false,
		success:function(data){
			if(data&&data.success=="true"){
				$.each(data.dataMediaType,function(i,item){
					var option="<option value="+item.typeId+">"+item.typeName+"</option>";  
			          mediaType.append(option);
				});
				$.each(data.dataMedia, function(i, item) {
					var option="<option value="+item.mediaId+">"+item.mediaName+"</option>";  
			          mediaId.append(option);
			    });
			}
		}
	});
	$(".selectpicker").selectpicker("refresh");
});

$("#mediaType").change(function(){
	var mediaType = $("#mediaType").val();
	var adType = $("#adType").val();
	var mediaId = $("#mediaId");
	var random = Math.random();
	$("#mediaId option").remove();
	var optionAll="<option value='0'>全部</option>";  
	mediaId.append(optionAll);	
	$.ajax({  
		type : "GET",  
		contentType : "application/json",  
		url : "/customize/userMedia",  
		data : {mediaType:mediaType,adType:adType,random:random},
		dataType : "json",  
		async:false,
		success : function(data) {  
			if (data && data.success == "true") {							  		
				$.each(data.data, function(i, item) {
					var option="<option value="+item.mediaId+">"+item.mediaName+"</option>";  
			        mediaId.append(option);
			    });
			}
		}						  
	});						 
	$(".selectpicker").selectpicker("refresh");										 					 
});
