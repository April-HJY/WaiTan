// pages/buy-messages/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function() {
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
          that.setData({
            usermessages: res.data.data.msgs
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
  onHide: function() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function() {

  },
  newMsg: function() {
    wx.navigateTo({
      url: '/pages/buy-message-detail/index',
    })
  },
  editMsg: function(e) {
    let id = e.currentTarget.dataset.id;
    console.log(id)
    let msg_list = this.data.usermessages;
    let item = undefined;
    for (var i = 0; i < msg_list.length; i++) {
      let msg = msg_list[i];
      if (id == msg.ID) {
        item = msg;
      }
    }
    if (item) {
      let params = "msg_id=" + id + "&name=" + item.Name + "&mobile=" + item.Mobile + "&age=" + item.Age + "&grade=" + item.Grade + "&wxcode=" + item.wxCode
      wx.navigateTo({
        url: '/pages/buy-message-detail/index?' + params,
      })
    } else {
      wx.navigateTo({
        url: '/pages/buy-message-detail/index',
      })
    }
  }
})