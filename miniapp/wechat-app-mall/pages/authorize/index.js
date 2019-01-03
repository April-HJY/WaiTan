// pages/authorize/index.js
var app = getApp();
Page({

  /**
   * 页面的初始数据
   */
  data: {
    hidePointPopup:true
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    
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
  bindGetUserInfo: function (e) {
    if (!e.detail.userInfo){
      return;
    }
    wx.setStorageSync('userInfo', e.detail.userInfo)
    this.login();
  },
  login: function () {
    wx.showLoading({
      title: '请稍候',
    });
    let that = this;
    let user_info = wx.getStorageSync('userInfo')
    wx.login({
      success: function (res) {
        wx.request({
          url: 'https://class.ddianke.com/MiniAppAPI/getminiappuserinfo/',
          data: {
            login_code: res.code,
            user_info: user_info
          },
          success: function (res) {
            wx.hideLoading();
            /*if (res.data.code == 10000) {
              // 去注册
              that.registerUser();
              return;
            }*/
            if (res.data.code != 0) {
              // 登录错误
              wx.hideLoading();
              wx.showModal({
                title: '提示',
                content: '无法登录，请重试',
                showCancel: false
              })
              return;
            }
            else{
              wx.setStorageSync('openid', res.data.data.openid)
              if (res.data.data.isNew){
                console.log(1)
                that.setData({ hidePointPopup:false})
                return
              }
            }
            // 回到原来的地方放
            wx.navigateBack();
          }
        })
      }
    })
  },
  closePopupTap: function(){
    this.setData({hidePointPopup:true});
  },
  toHome: function(){
    wx.switchTab({
      url: '/pages/index/index',
    })
  }
})