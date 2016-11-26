$(function(){
   
 $("#mainForm").validate({
	rules:{		        		
		mediaName:"required"
	},
	messages:{		        		
		mediaName:"媒体类型不能为空"
	}		        	
 	});
    
});
