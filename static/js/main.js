
$(function () {
    $('.page_box').css('opacity', '1')
    // 取消默认事件
    document.addEventListener("touchmove", function (ev) { ev.preventDefault(); }, false);

    // page1
    var page1 = $(".page1");
    page1.on('swipeUp', function () {
        $('.point1').tap(function () {
            $(this).next().show()
        })
        page1.anim({
            translateY: "-100%"
        }, 0.8, 'ease', function () {
            page1.removeClass('show first');
            $(".page2").addClass('show');
        })
    });
    var now = 0;
    var imgs = $("[_src]");
    var span = $(".loader span");
    var count = 0;
    var length = imgs.length;
    var last = 100 - now;
    var next = function () {
        $('.p1_load').hide();
        $('.arrowup').show();
        $('.p1_block').hide();
        $(".page2,.page3,.page4,.page5,.page6,.page7,.page8,.page9,.page10").css('opacity', '1');
    };
    $.each(imgs, function (i, img) {
        img.onload = function () {
            if (++count == length) {
                setTimeout(next, 1000);
                page1.addClass('show');
            }
            span.html(Math.round(count / length * last) + now);
        };
        img.src = img.getAttribute("_src");
        img.removeAttribute("_src");
    });
    //试驾
    $('.p1_right').on('touchend', function () {
        setTimeout(function () {
            $('.page10').css('z-index', '140');
            $('.arrowup').hide();
            $('.p4_back1').show()
        }, 500)
    })
    $('.p4_back1').tap(function () {
        $('.page10').css('z-index', '10');
        $('.arrowup').show()
        $('.p4_back1').hide()
    })
    $('.p4_back').tap(function () {
         $('.page9').anim({
            translateY: "0"
        }, 0.8, "ease", function () {
            $('.page10').removeClass('show')
            $('.page9').addClass('show')
            $('.arrowup').show()
        })
    })
     document.getElementById('p11_again').onclick=function(){
        location.reload()
    }
    // page2
    // ----------------------------------------------------------------------------------------------------

    var page2 = $('.page2').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page3 = $('.page3').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page4 = $('.page4').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page4 = $('.page4').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page5 = $('.page5').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page6 = $('.page6').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page7 = $('.page7').on('swipeUp', nextpage).on('swipeDown', prevpage);
    var page8 = $('.page8').on('swipeUp', nextpage).on('swipeDown', prevpage);
    //var page9 = $('.page9').on('swipeUp', nextpage).on('swipeDown', prevpage);
    $('.page9').on('swipeUp', function () {
        if ($(this).hasClass('show')) {
           // $('.arrowup').hide()
            $(this).anim({
                translateY: "-100%"
            }, 0.8, "ease", function () {
                $(this).removeClass('show')
               $('.page10').addClass('show')
            })
        }
    }).on('swipeDown', prevpage)

    $('.page10').on('swipeUp', function () {
        if ($(this).hasClass('show')) {
            $('.arrowup').hide()
            $(this).anim({
                translateY: "-100%"
            }, 0.8, "ease", function () {
               $(this).removeClass('show')
               $(this).next().addClass('show')
            })
        }
    }).on('swipeDown', function () {
        var _this = this;
         $('.page9').anim({
            translateY: "0"
        }, 0.8, "ease", function () {
            $(_this).removeClass('show')
            $('.page9').addClass('show')
            $('.arrowup').show()
        })
    })

     $('.page11').on('swipeDown', function () {
        var _this = this;
         $('.page10').anim({
            translateY: "0"
        }, 0.8, "ease", function () {
            $(_this).removeClass('show')
            $('.page10').addClass('show')
            $('.arrowup').show()
        })
    })

    var video = document.getElementById('video');


    window.onload = function () {
        setTimeout(function () {
            // $('#slider1,#slider2,#slider3,#slider4').hide();
            $('.page_box').css('opacity', '1')
            // $("html").css("fontSize",window.innerWidth / 20);
        }, 3500)
    }
    // page7
    // -------------------------------------------------------------------------------------------------------------



    // page8
    // --------------------------------------------------------------------------------------------------------

    $(".p8_btn").tap(function () {
        $('.p5_share').show()
    })
    $('.p5_share').tap(function () {
        $(this).hide()
    })
    document.getElementById('p8_again').onclick = function () {
        location.reload()
    }


    function nextpage() {
        $(this).anim({
            translateY: "-100%"
        }, 0.8, "ease", function () {
            $(this).removeClass('show')
            $(this).next().addClass('show')
        })
    }
    function prevpage() {
        var _this = this
        $(this).prev().anim({
            translateY: "0"
        }, 0.8, "ease", function () {
            $(_this).removeClass('show')
            $(_this).prev().addClass('show')
        })
    }
})

$('.p9_pic1').tap(function () {
    myScroll.scrollTo(0, 0);
    p9move(0, 100, 100,1);
    myScroll.refresh();
    $('.arrowup').hide()
})
$('.p9_pic2').tap(function(){
    myScroll2.scrollTo(0,0);
    p9move(0, 100, 100,2);
    myScroll2.refresh();
    $('.arrowup').hide()
})
$('.p9_pic3').tap(function(){
    myScroll3.scrollTo(0,0);
    p9move(0, 100, 100,3);
    myScroll3.refresh();
    $('.arrowup').hide()
})
$('.p9_p12').tap(function(){
    p9move(-100,0,100,1);   
    $('.arrowup').show()
})
$('.p9_p13').tap(function(){
      p9move(-100,0,100,2);   
     $('.arrowup').show()
})
$('.p9_p14').tap(function(){
      p9move(-100,0,100,3);   
     $('.arrowup').show()
})
 function p9move(m1,m2,m3,m4){
        $('.p9_page'+m4).anim({
            translateX:m1+"%",
        },0.8,'ease',false)       
    }

    window.myScroll = new IScroll('#wrapper', {
        mouseWheel: true,
        click: true,
        freeScroll:true,
        bounce:false
    });
    window.myScroll2 = new IScroll('#wrapper2', {
        mouseWheel: true,
        click: true,
        freeScroll:true,
        bounce:false
    });
    window.myScroll3 = new IScroll('#wrapper3', {
        mouseWheel: true,
        click: true,
        freeScroll:true,
        bounce:false
    });

// console.log