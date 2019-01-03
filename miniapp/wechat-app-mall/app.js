//app.js
const ald = require('./utils/ald-stat.js')
App({
  onLaunch: function () {
    var that = this;    
    // 判断是否登录
    let openid = wx.getStorageSync('openid');
    if (!openid) {
      console.log('openid:' + openid)
      that.goLoginPageTimeOut()
      return
    }
  }, 
  goLoginPageTimeOut: function () {
    setTimeout(function(){
      wx.navigateTo({
        url: "/pages/authorize/index"
      })
    }, 1000)    
  },
  globalData:{
    userInfo:null,
    subDomain: "ddianke",
    version: "4.0.0",
    shareProfile: '百款精品商品，总有一款适合您', // 首页转发的时候话术
    appid: 'wxf11978168e04aba2'
  }
})
