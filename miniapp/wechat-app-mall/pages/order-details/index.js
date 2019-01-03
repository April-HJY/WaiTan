var app = getApp();
Page({
  data: {
    orderId: 0,
    goodsList: [],
    yunPrice: "0.00"
  },
  onLoad: function(e) {
    var orderId = e.order_id;
    if (!orderId){
      wx.switchTab({
        url: '/pages/index/index',
      })
      return;
    }
    this.data.orderId = orderId;
    
    this.setData({
      orderId: orderId
    });
  },
  onShow: function() {
    var that = this;
    wx.showLoading({
      title: '请稍候',
    })
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getorderinfo/',
      data: {
        order_id: that.data.orderId
      },
      success: (res) => {
        console.log(res)
        wx.hideLoading();
        if (res.data.code != 0) {
          wx.showModal({
            title: '错误',
            content: res.data.msg,
            showCancel: false
          })
          return;
        }
        that.setData({
          orderDetail: res.data.data,
          used_points: 0,
          curr_display_amount: res.data.data.display_price
        });
      }
    })
  },
  usepoint: function(e) {
    let that = this;
    if(e.detail.value){
      let curr_display_amount = (that.data.orderDetail.display_price - that.data.orderDetail.point_limit).toFixed(2)
      that.setData({ used_points: that.data.orderDetail.point_limit, curr_display_amount: curr_display_amount})
    }
    else{
      let curr_display_amount = that.data.orderDetail.display_price
      that.setData({ used_points: 0, curr_display_amount: curr_display_amount})
    }
  },
  payBill: function(){
    wx.showLoading({
      title: '请稍候',
    })
    let that = this;
    let order_id = that.data.orderDetail.order_id;
    let use_points = that.data.used_points;
    let curr_amount = parseInt(that.data.curr_display_amount * 100);
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/payorder/',
      data: {
        order_id: order_id,
        use_points: use_points,
        curr_amount: curr_amount,
      },
      success: (res) => {
        console.log(res)
        wx.hideLoading();
        if (res.data.code != 0) {
          wx.showModal({
            title: '错误',
            content: res.data.msg,
            showCancel: false
          })
          return;
        }
        let order = res.data.data;
        wx.requestPayment({
          timeStamp: order.timeStamp,
          nonceStr: order.nonceStr,
          package: order.package,
          signType: 'MD5',
          paySign: order.sign,
          fail: function (aaa) {
            wx.showToast({
              title: '支付失败:' + aaa
            })
          },
          success: function () {
            wx.showToast({
              title: '支付成功'
            })
            if (wx.getStorageSync("isbound")) {
              wx.redirectTo({
                //url: "/pages/order-list/index?currentType=2"
                url: "/pages/hint/index"
              });
            }
            else {
              wx.redirectTo({
                url: "/pages/customer-service/index"
              });
            }
          }
        })
      }
    })
  }
})