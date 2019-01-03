// WWJ
// zepto.js
// 2015.4.23
// verson 1.1(联动)

// zepto - swipe event - swipeUp:

// page1.on('swipeUp',function(){
// 	nextpage.call(this,fnStart,fnEnd)
// })

var pageMoving=false;
function nextpage(fnEnd, fnStart){
	if(pageMoving){return};
	pageMoving=true;
	fnStart && fnStart.call(this);
    $(this).anim({
        translateY:"-100%"
    },0.5,"ease",function(){
        $(this).removeClass('show')
        $(this).next().addClass('show')
        pageMoving=false;
        $.isFunction(fnEnd) && fnEnd.call(this);
    })
}

function prevpage(fnEnd, fnStart){
    var _this=this
	if(pageMoving){return};
	pageMoving=true;
	fnStart && fnStart.call(this);
    $(this).prev().anim({
        translateY:"0"
    },0.5,"ease",function(){
        $(_this).removeClass('show')
        $(_this).prev().addClass('show')
        pageMoving=false;
        $.isFunction(fnEnd) && fnEnd.call(this);
    })
}


// 二级联动
// arr={
// 	"1":["11","12","13","14"],
// 	"2":["21","22","23","24"]
// }
// 三级联动
// arr={
// 	"1":{
// 		"11":["111","112","113"],
// 		"12":["121","122","123"]
// 	},
// 	"2":{
// 		"21":["211","212","213"],
// 		"22":["221","222","223"],
// 	},
// 	"3":{
// 		"31":["311","312","313"],
// 		"32":["321","322","323"]
// 	}
// }
function linkage(sel1,sel2,sel3,arr){
	var placeholder1="省份";
	var placeholder2="城市";
	var placeholder3="经销商";
	if(arguments.length==3){
		arr=sel3;
	}else if(arguments.length==4){
		sel3.html("");
		sel3.append('<option value="">'+ placeholder3 +'</option>');
	}

	var sel1v=$.map(arr,function(val,key){return key})
	// 将sel1的option放入
	sel1.html("");
	sel1.append('<option value="">'+ placeholder1 +'</option>')
	$.each(arr,function(i){
		sel1.append("<option value="+ i +">"+ i +"</option>")
	})

	// 将sel1第一项对应sel2的option放入
	sel2.html("");
	sel2.append('<option value="">'+ placeholder2 +'</option>');


	// sel1 change事件开始联动 2级联动
	if(arguments.length==3){
		sel1.on('change',function(){
			var index=sel1.get(0).selectedIndex-1;
			if(index<0){index=0};
			$.each(sel1v,function(i){
				sel2.html("");
				sel2.append('<option value="">'+ placeholder2 +'</option>')
				$.each(arr[sel1v[index]],function(j){
					sel2.append("<option value="+ arr[sel1v[index]][j] +">"+ arr[sel1v[index]][j] +"</option>")
				})
			})
			if(index==0){sel2.append('<option value="">'+ placeholder2 +'</option>')}
		})
	}
	// sel1 change事件开始联动 3级联动
	if(arguments.length==4){
		sel1.on('change',function(){
			var index=sel1.get(0).selectedIndex-1;
			if(index<0){index=0};
			var sel2v=$.map(arr[sel1v[index]],function(val,key){return key})
			sel2.html("");
			sel2.append('<option value="">'+ placeholder2 +'</option>')
			sel3.html("");
			sel3.append('<option value="">'+ placeholder3 +'</option>')
			$.each(sel2v,function(i){
				sel2.append("<option value="+ sel2v[i] +">"+ sel2v[i] +"</option>")
			})
			if(index==0){sel2.append('<option value="">'+ placeholder2 +'</option>')}
		})
		sel2.on('change',function(){
			var index2=sel2.get(0).selectedIndex-1;
			var index=sel1.get(0).selectedIndex-1;
			if(index<0){index=0};
			if(index2<0){index2=0};
			var sel2v=$.map(arr[sel1v[index]],function(val,key){return key})
			var sel3v=arr[sel1v[index]][sel2v[index2]];
			sel3.html("");
			sel3.append('<option value="">'+ placeholder3 +'</option>')
			$.each(sel3v,function(i){
				var value3=sel3v[i];
				var option3=sel3v[i].split(":")[0]
				sel3.append("<option value="+ value3 +">"+ option3 +"</option>")
			})
			if(index2==0){sel3.append('<option value="">'+ placeholder3 +'</option>')}
		})
	}
}

// copy zepto.zsy.js http://mobi.mconnect.cn/auditeaser/
// 加载
// $.loader()
$.loader = function(selector, attr, fnOne, fnEnd) {
	var i = 0;
	var srcs = [];
	var imgs = typeof selector == "string" ? $(selector + " [" + attr + "]") : $(selector).find("[" + attr + "]");
	var count = imgs.length;
	if(count == 0) {
		fnEnd && fnEnd(0);
		return;
	}

	(function () { // 同步加载
		var load = arguments.callee;
		if(i == count) {
			console.log(attr + " 图片加载完成,count:", count);
			fnEnd && fnEnd(count);
			imgs = srcs = null;
			return;
		}
		var img = imgs[i];
		var src = img.getAttribute(attr);
		if(srcs.indexOf(src) == -1) {
			srcs.push(src);
			img.onload = function() {
				i++;
				fnOne && fnOne(i, count);
				img = img.onload = null;
				load();
			};
		} else {
			i++;
			fnOne && fnOne(i, count);
			load();
		}
		img.src = src;
		img.removeAttribute(attr);
	})();
};
// fadeIn()

$.fn.fadeIn = function(time, fnEnd) {
	if (!arguments.length) {
		time = 0.3;
	};
	if ($.isFunction(time)) {
		fnEnd = time;
		time = 0.3;
	};
	return this.show().anim({opacity: 1}, time, "linear", fnEnd);
};

// fadeOut()

$.fn.fadeOut = function(time, fnEnd) {
	if (!arguments.length) {
		time = 0.3;
	};
	if ($.isFunction(time)) {
		fnEnd = time;
		time = 0.3;
	};
	var self = this;
	return this.anim({opacity: 0}, time, "linear", function() {
		self.hide();
		fnEnd && fnEnd.call(this);
	});
};


// console.log(1)