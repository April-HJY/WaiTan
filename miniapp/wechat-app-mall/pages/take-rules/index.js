var app = getApp();
Page({
  data: {
    char_gt:"<<",
    char_lt:">>",
    char_sign:"Q"
  },
  onLoad:function(){

  },
  back:function(){
    wx.navigateTo({
      url: '/pages/withdraw-self/index',
    })
  }
})