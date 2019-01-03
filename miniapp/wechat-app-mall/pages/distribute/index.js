// pages/distribute/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    hideShopPopup: true,
  },
  handler: function(e) {
    if (e.detail.authSetting["scope.writePhotosAlbum"]) { //如果打开了地理位置，就会为true
      this.setData({
        showSetting: false
      })
    }
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    //this.canvas();
    //console.log(options)
    this.getposter(options['product_id']);
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
  getposter: function(product_id) {
    var openid = wx.getStorageSync('openid')
    product_id = parseInt(product_id)
    //product_id = 12
    if (!product_id || product_id == 0) {
      wx.switchTab({
        url: '/pages/index/index',
      })
      return;
    }
    wx.showLoading({
      title: '加载中...',
    })
    let that = this
    /*wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getposter/',
      data: {
        mini_openid:openid,
        mini_product_id: product_id
      },
      success: function (res) {
        wx.hideLoading();
        //console.log(res)
        that.setData({poster_img:res.data});
      }
    })*/
    var url = 'https://class.ddianke.com/MiniAppAPI/getposter/?mini_openid=' + openid + "&mini_product_id=" + product_id
    console.log(url)
    wx.downloadFile({
      url: url,
      success: function(res) {
        console.log(res)
        if (res.statusCode == 200) {
          that.setData({
            poster_img: res.tempFilePath
          });
        }
        wx.hideLoading();
      },
      fail: function(res) {
        console.log(res)
        wx.hideLoading();
      }
    })
  },
  canvas: function() {
    let _this = this;
    let realWidth, realHeight;
    //创建节点选择器
    var query = wx.createSelectorQuery();
    //选择id
    query.select('#mycanvas').boundingClientRect()
    query.exec(function(res) {
      //res就是 该元素的信息 数组
      realWidth = res[0].width;
      realHeight = res[0].height;
      console.log('realHeight', realHeight);
      console.log('realWidth', realWidth);
      const ctx = wx.createCanvasContext('mycanvas');
      ctx.drawImage("../../images/qrcode_bg.png", 0, 0, realWidth, realHeight);
      ctx.drawImage("../../images/banner03.jpg", 122, 380, 85, 85);

      ctx.draw();

      setTimeout(function() {
        wx.canvasToTempFilePath({
          canvasId: 'mycanvas',
          success: function(res) {
            var tempFilePath = res.tempFilePath;
            _this.setData({
              canvasUrl: tempFilePath
            })
            if (tempFilePath !== '') {
              _this.setData({
                isShowCav: false
              });
              wx.hideLoading();
              wx.previewImage({
                current: _this.data.canvasUrl, // 当前显示图片的http链接  
                urls: [_this.data.canvasUrl], // 需要预览的图片http链接列表  
              })
            }
          },
          fail: function(res) {
            console.log(res);
          }
        });
      }, 500);
    })
  },
  saveImg: function() {
    console.log('saveImg')
    let that = this;
    wx.showLoading({
      title: '请稍候',
    })
    wx.saveImageToPhotosAlbum({
      filePath: that.data.poster_img,
      success: function(res) {
        console.log(res)
        wx.showToast({
          title: '保存成功',
        })
      },
      fail: function(res) {
        console.log(res)
        wx.showToast({
          title: '保存失败',
        })
        if (res.errMsg === "saveImageToPhotosAlbum:fail auth deny") {
          that.setData({
            showSetting: true
          })
        }
      },
      complete: function(res) {
        wx.hideLoading();
      }
    })
  },
  closePopupTap: function() {
    this.setData({
      hideShopPopup: true
    })
  },
  showPopup: function() {
    this.setData({
      hideShopPopup: false
    })
  },
})