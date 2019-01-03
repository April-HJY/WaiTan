var wxpay = require('../../utils/pay.js')
var app = getApp()
Page({
  data: {
    statusType: ["待付款", "退款中", "已完成"],
    //statusType: ["待付款", "待发货", "待收货", "待评价", "已完成"],
    currentType: 0,
    tabClass: ["0", "2", "1"]
    //tabClass: ["", "", "", "", ""]
  },
  statusTap: function(e) {
    var curType = e.currentTarget.dataset.index;
    this.data.currentType = curType
    this.setData({
      currentType: curType
    });
    this.onShow();
  },
  orderDetail: function(e) {
    var orderId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: "/pages/order-details/index?id=" + orderId
    })
  },
  cancelOrderTap: function(e) {
    var that = this;
    var orderId = e.currentTarget.dataset.id;
    var openid = wx.getStorageSync('openid');
    wx.showModal({
      title: '确定要取消该订单吗？',
      content: '',
      success: function(res) {
        if (res.confirm) {
          wx.showLoading();
          wx.request({
            url: 'https://class.ddianke.com/MiniAppAPI/cancelorder/',
            data: {
              openid: openid,
              appid: app.globalData.appid,
              order_id: orderId
            },
            success: (res) => {
              console.log(res);
              wx.hideLoading();
              that.onShow();
            }
          })
        }
      }
    })
  },
  toPayTap: function(e) {
    var that = this;
    var orderId = e.currentTarget.dataset.id;
    var orders = that.data.orderList;
    var order = undefined;
    orders.forEach(function(item, i) {
      if (item.id == orderId) {
        order = item;
      }
    })
    var paidPoints = order.PaidPoints;
    if (!order.prepay_id){
      wx.showLoading({
        title: '请稍候',
      })
      wx.request({
        url: 'https://class.ddianke.com/MiniAppAPI/payorder/',
        data: {
          order_id: orderId,
          use_points: paidPoints,
          curr_amount: order.amount,
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
                  url: "/pages/order-list/index?currentType=2"
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
    else{
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
              url: "/pages/order-list/index?currentType=2"
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
    
  },
  onLoad: function(options) {
    if (options['currentType']) {
      this.setData({
        currentType: options['currentType']
      })
    }
    // 生命周期函数--监听页面加载
  },
  onReady: function() {
    // 生命周期函数--监听页面初次渲染完成

  },
  onShow: function() {
    // 获取订单列表
    wx.showLoading();
    var that = this;
    let openid = wx.getStorageSync('openid')
    var postData = {
      appid: app.globalData.appid,
      openid: openid,
    };
    postData.status = that.data.currentType;
    wx.request({
      //url: 'https://api.it120.cc/' + app.globalData.subDomain + '/order/list',
      url: 'https://class.ddianke.com/MiniAppAPI/getorderlist/',
      data: postData,
      success: (res) => {
        wx.hideLoading();
        if (res.data.code == 0) {
          that.setData({
            orderList: res.data.data,
        
          });
        } else {
          this.setData({
            orderList: null,
            logisticsMap: {},
            goodsMap: {}
          });
        }
      }
    })

  },
  onHide: function() {
    // 生命周期函数--监听页面隐藏

  },
  onUnload: function() {
    // 生命周期函数--监听页面卸载

  },
  onPullDownRefresh: function() {
    // 页面相关事件处理函数--监听用户下拉动作

  },
  onReachBottom: function() {
    // 页面上拉触底事件的处理函数

  }
})