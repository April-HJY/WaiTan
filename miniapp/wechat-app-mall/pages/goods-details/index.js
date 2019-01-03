//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
import qqVideo from "../../utils/qqVideo.js"
Page({
  data: {
    autoplay: true,
    interval: 3000,
    duration: 1000,
    goodsDetail: undefined,
    swiperCurrent: 0,
    hasMoreSelect: false,
    selectSize: "选择：",
    selectSizePrice: 0,
    totalScoreToPay: 0,
    shopNum: 0,
    hideShopPopup: true,
    buyNumber: 0,
    buyNumMin: 1,
    buyNumMax: 0,

    propertyChildIds: "",
    propertyChildNames: "",
    canSubmit: false, //  选中规格尺寸时候是否允许加入购物车
    shopCarInfo: {},
    shopType: "addShopCar", //购物类型，加入购物车或立即购买，默认为加入购物车
  },

  //事件处理函数
  swiperchange: function(e) {
    //console.log(e.detail.current)
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  onShow: function() {
    let that = this;
    if ((that.data.usermessages == undefined || that.data.usermessages.length == 0) && that.data.goodsDetail != undefined) {
      console.log('show')
      this.getBuyerMessages();
    }
  },
  onReady: function() {

  },
  onLoad: function(e) {
    console.log(e);
    let product_id = e.id;
    let is_show = e.is_show;
    if (is_show) {
      this.setData({
        hideShopPopup: false
      })
    }
    let distributor_id = 0
    if (e.scene) {
      let scene = e.scene.split('_')
      distributor_id = scene[1]
      product_id = scene[3]
    } else if (e.distributor_id) {
      distributor_id = distributor_id
    }
    let is_cashback=0;
    if (e.is_cashback) {
      is_cashback = is_cashback;
    }
    if (!product_id || product_id == 0) {
      wx.switchTab({
        url: '/pages/index/index',
      })
      return;
    }

    this.setData({
      distributor_id: distributor_id,
      is_cashback: is_cashback
    })

    var that = this;
    that.data.kjId = e.kjId;
    let openid = wx.getStorageSync('openid')
    if (!openid) {
      wx.navigateTo({
        url: "/pages/authorize/index"
      })
    }
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getminiappproductdetail/',
      data: {
        id: product_id
      },
      success: function(res) {
        console.log(res)
        var selectSizeTemp = "";
        if (res.data.data.properties) {
          for (var i = 0; i < res.data.data.properties.length; i++) {
            selectSizeTemp = selectSizeTemp + " " + res.data.data.properties[i].name;
          }
          that.setData({
            hasMoreSelect: true,
            selectSize: that.data.selectSize + selectSizeTemp,
            selectSizePrice: res.data.data.basicInfo.Price,
            totalScoreToPay: res.data.data.basicInfo.minScore
          });
        }

        that.data.goodsDetail = res.data.data;
        if (res.data.data.basicInfo.videoId) {
          that.getVideoSrc(res.data.data.basicInfo.videoId);
        }
        that.setData({
          goodsDetail: res.data.data,
          selectSizePrice: res.data.data.basicInfo.Price,
          totalScoreToPay: 0, //res.data.data.basicInfo.Score,
          buyNumMax: res.data.data.basicInfo.Inventory,
          buyNumber: (res.data.data.basicInfo.Inventory > 0) ? 1 : 0
        });
        WxParse.wxParse('article', 'html', res.data.data.content, that, 5);
        //qqVideo.getVideoes('j0665fxmmdx').then(function (response) {
        //  console.log(response)
        //})
        that.getBuyerMessages();
      }
    })
  },
  getBuyerMessages: function() {
    let that = this;
    let openid = wx.getStorageSync('openid')
    let goodsdetail = that.data.goodsDetail;
    if (!goodsdetail || (that.data.usermessages != undefined && that.data.usermessages.length > 0)) {
      console.log('return')
      return;
    }
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getuserbuymessages/',
      data: {
        openid: openid,
      },
      success: function(res) {
        console.log(res)
        if (res.data.code == 0) {
          let usermessages = res.data.data.msgs;
          that.setData({
            usermessages: usermessages
          })

          //let prod_messages = that.data.goodsDetail.basicInfo.Messages;
          for (let i = 0; i < usermessages.length; i++) {
            let usermessage = usermessages[i]
            console.log(usermessage)
            if (usermessage.IsDefault == 1) {
              for (let j = 0; j < goodsdetail.basicInfo.Messages.length; j++) {
                let prod_message = goodsdetail.basicInfo.Messages[j];
                if (prod_message.message_name == '手机号码') {
                  prod_message.message_value = usermessage.Mobile;
                } else if (prod_message.message_name == '学生姓名') {
                  prod_message.message_value = usermessage.Name;
                } else if (prod_message.message_name == '学生年龄') {
                  prod_message.message_value = usermessage.Age;
                } else if (prod_message.message_name == '学生年级') {
                  prod_message.message_value = usermessage.Grade;
                } else if (prod_message.message_name == '微信号码') {
                  prod_message.message_value = usermessage.wxCode;
                }
              }
              that.setData({
                goodsDetail: goodsdetail
              })
            }
          }
        } else {
          wx.showToast({
            title: res.data,
          })
        }
      },
      fail: function(res) {
        wx.showToast({
          title: res,
        })
      }
    })
  },
  goShopCar: function() {
    wx.reLaunch({
      url: "/pages/shop-cart/index"
    });
  },
  toAddShopCar: function() {
    this.setData({
      shopType: "addShopCar"
    })
    this.bindGuiGeTap();
  },
  tobuy: function() {
    let max_points = this.data.goodsDetail.basicInfo.PointLimit > this.data.userpoints ? this.data.userpoints : this.data.goodsDetail.basicInfo.PointLimit
    this.setData({
      shopType: "tobuy",
      selectSizePrice: this.data.goodsDetail.basicInfo.Price,
      max_points: max_points,
      paidpoints: max_points
    });
    this.bindGuiGeTap();
  },
  toPingtuan: function() {
    this.setData({
      shopType: "toPingtuan",
      selectSizePrice: this.data.goodsDetail.basicInfo.pingtuanPrice
    });
    this.bindGuiGeTap();
  },
  /**
   * 规格选择弹出框
   */
  bindGuiGeTap: function() {
    this.setData({
      hideShopPopup: false
    })
  },
  /**
   * 规格选择弹出框隐藏
   */
  closePopupTap: function() {
    this.setData({
      hideShopPopup: true
    })
  },
  numJianTap: function() {
    if (this.data.buyNumber > this.data.buyNumMin) {
      var currentNum = this.data.buyNumber;
      currentNum--;
      this.setData({
        buyNumber: currentNum
      })
    }
  },
  numJiaTap: function() {
    console.log(this.data.buyNumMax)
    if (this.data.buyNumber < this.data.buyNumMax) {
      var currentNum = this.data.buyNumber;
      currentNum++;
      this.setData({
        buyNumber: currentNum
      })
    }
  },
  /**
   * 选择商品规格
   * @param {Object} e
   */
  labelItemTap: function(e) {
    let that = this;

    for (var i = 0; i < that.data.goodsDetail.basicInfo.SKUs.length; i++) {
      let temp_sku = that.data.goodsDetail.basicInfo.SKUs[i];
      if (temp_sku.sku_name == e.currentTarget.dataset.propertyname) {
        for (var j = 0; j < temp_sku.sku_values.length; j++) {
          if (e.currentTarget.dataset.propertyvalue == temp_sku.sku_values[j].sku_value) {
            temp_sku.sku_values[j].active = true;
          } else {
            temp_sku.sku_values[j].active = false;
          }
        }
      }
    }

    this.setData({
      goodsDetail: that.data.goodsDetail,
      canSubmit: true
    })
  },
  /**
   * 立即购买
   */
  getmsgvalue: function(e) {
    var val = e.detail.value;
    let that = this
    for (var i = 0; i < that.data.goodsDetail.basicInfo.Messages.length; i++) {
      if (e.currentTarget.dataset.id == that.data.goodsDetail.basicInfo.Messages[i].message_id) {
        that.data.goodsDetail.basicInfo.Messages[i].message_value = val;
      }
    }
  },
  buyNow: function(e) {
    let that = this
    let shoptype = e.currentTarget.dataset.shoptype
    let skus = []
    for (var i = 0; i < that.data.goodsDetail.basicInfo.SKUs.length; i++) {
      let temp_sku = that.data.goodsDetail.basicInfo.SKUs[i];
      let is_selected = false;
      let sku_value = '';
      for (var j = 0; j < temp_sku.sku_values.length; j++) {
        if (temp_sku.sku_values[j].active) {
          is_selected = true;
          sku_value = temp_sku.sku_values[j].sku_value
        }
      }
      if (!is_selected) {
        wx.showModal({
          title: '提示',
          content: '请选择' + temp_sku.sku_name,
          showCancel: false
        })
        return;
      }
      skus.push(temp_sku.sku_name + ":" + sku_value);
    }
    if (this.data.buyNumber < 1) {
      wx.showModal({
        title: '提示',
        content: '购买数量不能为0！',
        showCancel: false
      })
      return;
    }
    let messages = []
    for (var i = 0; i < that.data.goodsDetail.basicInfo.Messages.length; i++) {
      let temp_message = that.data.goodsDetail.basicInfo.Messages[i];
      console.log(temp_message.message_value)
      if (!temp_message.message_value) {
        wx.showModal({
          title: '提示',
          content: '请输入' + temp_message.message_name,
          showCancel: false
        })
        return;
      } else {
        messages.push(temp_message.message_name + ":" + temp_message.message_value)
      }
    }
    let paidpoints = that.data.paidpoints;
    if (paidpoints > that.data.goodsDetail.basicInfo.PointLimit) {
      wx.showModal({
        title: '提示',
        content: '本商品最多使用' + that.data.goodsDetail.basicInfo.PointLimit + "奖学金",
        showCancel: false
      })
      return;
    }
    if (paidpoints > that.data.userpoints) {
      wx.showModal({
        title: '提示',
        content: "您的奖学金只有" + that.data.userpoints,
        showCancel: false
      })
      return;
    }
    this.closePopupTap();
    this.save_msg();

    wx.showLoading();
    var distributor_id = that.data.distributor_id
    var openid = wx.getStorageSync('openid')
    that.createOrder(openid, skus, messages, distributor_id, paidpoints);
  },
  createOrder: function(openid, skus, messages, distributor_id, paidpoints) {
    let that = this;
    let goodsJson = [{
      number: that.data.buyNumber,
      goodsId: that.data.goodsDetail.basicInfo.ID,
      skus: skus,
      messages: messages,

    }]
    let is_cashback = that.data.is_cashback
    let prepay_data = {
      "openid": openid,
      "appid": app.globalData.appid,
      distributor_id: distributor_id,
      is_cashback: is_cashback,
      paidpoints: paidpoints,
      goodsJsonStr: JSON.stringify(goodsJson),
    }
    wx.request({
      //url: 'https://class.ddianke.com/MiniAppAPI/wechatprepaywithproductid/',
      url: 'https://class.ddianke.com/MiniAppAPI/createorder/',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      data: prepay_data, //postData, // 设置请求的 参数
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
        wx.setStorageSync("isbound", res.data.data.isbound);
        let order_id = res.data.data.order_id;
        // 下单成功，跳转到订单管理界面
        wx.redirectTo({
          url: "/pages/order-details/index?order_id=" + order_id
        });
      }
    })
  },
  onShareAppMessage: function() {
    return {
      title: this.data.goodsDetail.basicInfo.Name,
      path: '/pages/goods-details/index?id=' + this.data.goodsDetail.basicInfo.ID,
      success: function(res) {
        // 转发成功
      },
      fail: function(res) {
        // 转发失败
      }
    }
  },
  getpoints: function() {
    let that = this;
    //let openid = wx.getStorageInfoSync('openid');
    let product_id = that.data.goodsDetail.basicInfo.ID;
    if (!product_id || product_id == 0) {
      wx.showToast({
        title: '需要课程ID',
        duration: 2000
      });
      return;
    }
    wx.navigateTo({
      url: '/pages/distribute/index?product_id=' + product_id,
    });
  },
  pointinput: function(e) {
    var val = e.detail.value;
    this.setData({
      paidpoints: val
    });
  },
  select_msg: function() {
    let product_id = this.data.goodsDetail.basicInfo.ID;
    wx.navigateTo({
      url: '/pages/buy-message-select/index?product_id=' + product_id,
    })
  },
  save_msg: function() {
    let that = this;
    let usermsgs = this.data.usermessages;
    let usermessage = {};
    if (usermsgs) {
      for (let i = 0; i < usermsgs.length; i++) {
        usermessage = usermsgs[i];
        if (usermessage.IsDefault == 1) {
          break;
        }
      }
    }
    for (let j = 0; j < that.data.goodsDetail.basicInfo.Messages.length; j++) {
      let prod_message = that.data.goodsDetail.basicInfo.Messages[j];
      if (prod_message.message_name == '手机号码') {
        usermessage.Mobile = prod_message.message_value;
      } else if (prod_message.message_name == '学生姓名') {
        usermessage.Name = prod_message.message_value;
      } else if (prod_message.message_name == '学生年龄') {
        usermessage.Age = prod_message.message_value;
      } else if (prod_message.message_name == '学生年级') {
        usermessage.Grade = prod_message.message_value;
      } else if (prod_message.message_name == '微信号码') {
        usermessage.wxCode = prod_message.message_value;
      }
    }
    let openid = wx.getStorageSync('openid')
    let msg_id = usermessage.ID ? usermessage.ID : 0;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/saveuserbuymessages/',
      method: "POST",
      data: {
        openid: openid,
        msg_id: msg_id,
        mobile: usermessage.Mobile,
        name: usermessage.Name,
        age: usermessage.Age,
        grade: usermessage.Grade,
        wxcode: usermessage.wxCode,
      },
      success: function(res) {
        console.log(res)
        if (res.data == "ok") {
          wx.showToast({
            title: '保存成功',
          })
          wx.navigateBack({
            delta: 1
          })
        } else {
          wx.showToast({
            title: res.data,
          })
        }
      },
      fail: function(res) {
        wx.showToast({
          title: res,
        })
      }
    })
  }
})