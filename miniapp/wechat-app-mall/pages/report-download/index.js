const app = getApp()

Page({
  data: {
  },
  onLoad:function(){
    var openid = wx.getStorageSync('openid');
    var that = this;
    wx.showLoading({
      title: '加载中...',
    });
    wx.downloadFile({
      url: 'https://class.ddianke.com/MiniAppAPI/getcashbackposter/?openid='+openid,
      data: {
        openid:openid,
      },
      success: function (res) {
        console.log(res);
        if (res.statusCode == 200) {
          that.setData({
            poster_img: res.tempFilePath
          });
        }
        wx.hideLoading();
      }, 
      fail: function (res) {
        console.log(res)
        wx.hideLoading();
      }
    })
  },
  saveImg: function () {
    console.log('saveImg')
    let that = this;
    wx.showLoading({
      title: '请稍候',
    })
    wx.saveImageToPhotosAlbum({
      filePath: that.data.poster_img,
      success: function (res) {
        console.log(res)
        wx.showToast({
          title: '保存成功',
        })
      },
      fail: function (res) {
        console.log(res)
        wx.showToast({
          title: '保存失败',
        })
        if (res.errMsg === "saveImageToPhotosAlbum:fail auth deny"){
          that.setData({
            showSetting: true
          })
        }
      },
      complete: function (res) {
        wx.hideLoading();
      }
    })
  }
})