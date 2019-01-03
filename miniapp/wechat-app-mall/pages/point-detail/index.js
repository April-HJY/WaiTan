// pages/point-detail/index.js
var app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    show_positive: true,
    hideShopPopup: true,
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    this.getUserPoints();
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
  getUserPoints: function() {
    let openid = wx.getStorageSync('openid')
    let that = this;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getuserpointdetail/',
      data: {
        openid: openid,
        appid: app.globalData.appid,
      },
      success: (res) => {
        console.log(res)
        if (res.data.code == 0) {
          let positive_list = []
          let negative_list = []
          for (let i = 0; i < res.data.data.detail_list.length;i++){
            let detail = res.data.data.detail_list[i]
            if (detail.points>0){
              positive_list.push(detail)
            }
            else{
              negative_list.push(detail)
            }
          }
          that.setData({
            user_points: res.data.data.points,
            show_positive: true,
            signal:'+',
            detail_list: positive_list,
            positive_list: positive_list,
            negative_list: negative_list
          })
        } else {
          wx.showToast({
            title: res.data,
          })
        }
      }
    })
  },
  show_positive_list: function(e){
    console.log(1)
    let that = this;
    this.setData({ show_positive:true,
      signal: '+',
      detail_list: that.data.positive_list,})
  },
  show_negative_list: function (e) {
    console.log(2)
    let that = this;
    this.setData({
      show_positive: false,
      signal: '',
      detail_list: that.data.negative_list, })
  },
  showPopup: function () {
    this.setData({
      hideShopPopup: false
    })
  },
  closePopupTap: function () {
    this.setData({
      hideShopPopup: true
    })
  },
  toRules: function(){
    wx.navigateTo({
      url: "/pages/point-rules/index"
    })
  }
})