// pages/buy-message-detail/index.js
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
    console.log(options)
    let msg_id = options['msg_id'];
    console.log(msg_id)
    if (msg_id) {
      let mobile = options['mobile'];
      let name = options['name'];
      let age = options['age'];
      let grade = options['grade'];
      let wxcode = options['wxcode'];
      this.setData({
        msg_id: msg_id,
        name: name,
        mobile: mobile,
        age: age,
        grade: grade,
        wxcode: wxcode
      })
    }
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
  getmsgvalue: function(e) {
    var val = e.detail.value;
    let that = this
    if (e.currentTarget.dataset.key == "mobile") {
      that.setData({
        mobile: val
      })
    } else if (e.currentTarget.dataset.key == "name") {
      that.setData({
        name: val
      })
    } else if (e.currentTarget.dataset.key == "age") {
      that.setData({
        age: val
      })
    } else if (e.currentTarget.dataset.key == "grade") {
      that.setData({
        grade: val
      })
    } else if (e.currentTarget.dataset.key == "wxcode") {
      that.setData({
        wxcode: val
      })
    }
  },
  saveMsg: function() {
    let that = this;
    if (that.data.mobile == undefined || that.data.mobile == "") {
      wx.showToast({
        title: '请输入手机号码',
      })
      return;
    }
    if (that.data.name == undefined || that.data.name == "") {
      wx.showToast({
        title: '请输入学生姓名',
      })
      return;
    }
    if (that.data.age == undefined || that.data.age == "") {
      wx.showToast({
        title: '请输入学生年龄',
      })
      return;
    }
    if (that.data.grade == undefined || that.data.grade == "") {
      wx.showToast({
        title: '请输入学生年级',
      })
      return;
    }
    if (that.data.wxcode == undefined || that.data.wxcode == "") {
      wx.showToast({
        title: '请输入微信号码',
      })
      return;
    }
    let openid = wx.getStorageSync('openid')
    let msg_id = that.data.msg_id ? that.data.msg_id : 0;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/saveuserbuymessages/',
      method: "POST",
      data: {
        openid: openid,
        msg_id: msg_id,
        mobile: that.data.mobile,
        name: that.data.name,
        age: that.data.age,
        grade: that.data.grade,
        wxcode: that.data.wxcode,
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