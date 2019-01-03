// pages/buy-message-select/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    let product_id = options['product_id']
    if (product_id){
      this.setData({ product_id: product_id})
    }
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    let that = this;
    let openid = wx.getStorageSync('openid')
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getuserbuymessages/',
      data: {
        openid: openid,
      },
      success: function (res) {
        console.log(res)
        
        if (res.data.code == 0) {
          let msgs = res.data.data.msgs;
          for (let i = 0; i < msgs.length; i++) {
            if (msgs[i].IsDefault == 1) {
              msgs[i].checked = true;
            }
          }
          that.setData({
            usermessages: msgs
          })
        } else {
          wx.showToast({
            title: res.data,
          })
        }
      },
      fail: function (res) {
        wx.showToast({
          title: res,
        })
      }
    })
  },
  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },
  selectMsg: function(e){
    console.log(e)
    let that = this;
    let msgs = that.data.usermessages;
    let id = e.currentTarget.dataset.id;
    for (let i = 0; i < msgs.length; i++) {
      if (msgs[i].ID == id) {
        msgs[i].checked = true;
        msgs[i].IsDefault = 1;
      }
      else{
        msgs[i].IsDefault = 0;
        msgs[i].checked = false;
      }
    }
    that.setData({ usermessages:msgs, default_id:id})
  },
  saveDefaultMsg: function(){
    let that = this;
    let openid = wx.getStorageSync('openid')
    let product_id = that.data.product_id;
    let default_id = that.data.default_id;
    if (default_id){
      wx.request({
        url: 'https://class.ddianke.com/MiniAppAPI/setuserdefaultmessage/',
        data: {
          openid: openid,
          default_id: default_id,
        },
        success: function (res) {
          console.log(res)
          if (product_id){
            wx.redirectTo({
              url: '/pages/goods-details/index?is_show=true&id=' + product_id,
            })
          }
          else{
            wx.switchTab({
              url: '/pages/index/index',
            })
          }
        },
        fail: function (res) {
          wx.showToast({
            title: res,
          })
        }
      })
    }
    else{
      console.log(1)
      if (product_id) {
        wx.redirectTo({
          url: '/pages/goods-details/index?is_show=true&id=' + product_id,
        })
      }
      else {
        wx.switchTab({
          url: '/pages/index/index',
        })
      }
    }
  }
})