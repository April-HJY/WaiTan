const app = getApp()

Page({
  data: {
    char_lt:"<<",
    chat_gt:">>"
  },
  onLoad:function(option) {
    var that=this;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getcashbackpage',
      data: {
      },
      success:function(res){
        console.log(res);
        that.setData({
          banner_url : res.data.data.banner_url,
          product_list: res.data.data.product_list,
        });
      }
    })
  },
  toDetailsTap: function (e) {
    console.log("detail", e.currentTarget.dataset.id)
    wx.navigateTo({
      url: "/pages/goods-details/index?id=" + e.currentTarget.dataset.id
    })
  },
  toReportSelf:function(){
    wx.navigateTo({
      url: "/pages/report-download/index"
    })
  },
  onShow() {
  }
})