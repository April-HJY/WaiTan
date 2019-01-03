const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    show_positive: true,
    show_txt:true,
  },
  onLoad: function () {
    let openid = wx.getStorageSync('openid');
    let that = this;
    let count = 0;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getusercashbackdetails/',
      data: {
        openid:openid,
      },
      success: function(res) {
        console.log(res);
        let positive_list = []
        let negative_list = []
        let count1=0;
        let count2=0;
        for (let i = 0; i < res.data.data.detail_list.length; i++) {
          let detail = res.data.data.detail_list[i]
          if (detail.State > 0) {
            negative_list.push(detail)
            count2+=detail.Amount;
          }
          else {
            positive_list.push(detail)
            count1+=detail.Amount;
          }
        }
        that.setData({
          detail_list: positive_list,
          signal: '+',
          positive_list: positive_list,
          negative_list: negative_list,
          count1:count1,
          count2:count2,
          count:count1,
        }) 
      }
    })
  },
  show_positive_list: function (e) {
    console.log(1)
    let that = this;
    let count1 = that.data.count1;
    this.setData({
      show_positive: true,
      signal: '+',
      detail_list: that.data.positive_list,
      show_txt:true,
      count: count1,
    })
  },
  show_negative_list: function (e) {
    console.log(2)
    let that = this;
    let count2 = that.data.count2;
    this.setData({
      show_positive: false,
      signal: '',
      detail_list: that.data.negative_list,
      show_txt: false,
      count:count2
    })
  },
  toTakeRules:function(){
    wx.navigateTo({
      url: '../../pages/take-rules/index',
    })
  },
  toMy:function(){
    wx.switchTab({
      url: '/pages/my/index',
    })
  }
})