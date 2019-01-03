/*数据提交*/
var patrn = /^(13[0-9]|14[0-9]|15[0-9]|18[0-9])\d{8}$$/;
var cUrl = 'http://ama.adwo.com';
//var cUrl = 'http://test.zhangkuo.net';
$(".reset").click(function () {
    $(".name").val("");
    $(".phone").val("");
    $(".type option:first").attr("selected", 'selected');
    $(".shengf option:first").attr("selected", 'selected');
    $(".city option:first").attr("selected", 'selected');
    $(".jxs option:first").attr("selected", 'selected');
});
$('.submit').click(function () {
    if (!$('.name').val()) {
        alert("请输入真实姓名!");
        return;
    }
    if ($('.phone').val() == "" || !patrn.test($('.phone').val())) {
        alert('请输入电话号码!');
        return;
    }
    if ($('.type').val().indexOf("选择") > 0) {
        alert("请选择车型!");
        return;
    }
    if ($('.shengf').val().indexOf("选择") > 0) {
        alert("请选择省份!");
        return;
    }
    if ($('.city').val().indexOf("选择") > 0) {
        alert("请选择城市!");
        return;
    }
    if ($('.jxs').val().indexOf("选择") > 0) {
        alert("请选择经销商!");
        return;
    }


    // alert($("input[name='sjsj']:checked").val());

    var url = cUrl + "/advmessage/adv/addResultJsonP.action?advid=30420" +
        "&expand1=" + $(".type option:selected").html() + //车型
        "&expand2=" + $(".type option:selected").data("mId") + //车型ID
        "&provincename=" + $(".shengf option:selected").html() + //省份
        "&provinceid=" + $(".shengf option:selected").data("pid") + //省份ID
        "&cityname=" + $(".city option:selected").html() + //城市
        "&cityid=" + $(".city option:selected").data("cid") + //城市ID
        "&expand3=" + $(".jxs option:selected").html() + //专营店
        "&expand4=" + $(".jxs option:selected").data("dcode") + //专营店code
        "&realname=" + $('.name').val() + //名字
        "&mobile=" + $('.phone').val(); //提交电话

    console.log(url);
    $.ajax({
        type: "get",
        url: url,
        dataType: 'jsonp',
        success: function (data) {
            if (data[0].success == 1) {
                console.log(data)
                alert("提交成功!");
            } else {
                alert(data[0].info);
                return;
            }

        },
        error: function (data) {
            alert("网络错误,请查看您的网络!");
        }
    });
});