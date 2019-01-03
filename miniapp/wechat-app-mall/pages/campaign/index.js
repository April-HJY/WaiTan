//index.js
//获取应用实例
var app = getApp()
Page({
  data: {
    goods: [],
    scrollTop: 0,
    loadingMoreHidden: true,
  },
  toDetailsTap: function (e) {
    console.log("detail", e.currentTarget.dataset.id)
    wx.navigateTo({
      url: "/pages/goods-details/index?id=" + e.currentTarget.dataset.id
    })
  },
  onLoad: function () {
    var that = this
    wx.setNavigationBarTitle({
      title: wx.getStorageSync('mallName')
    })
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getcampaingpage/',
      data: {
      },
      success: function (res) {
        //console.log(res)
        if (res.data.code != 0) {
          wx.showModal({
            title: '提示',
            content: res.data,
            showCancel: false
          })
        } else {
          that.setData({
            banner_url: res.data.data.banner_url,
            tag_list: res.data.data.tag_list,
          });
        }
      }
    })
  },
  onPageScroll(e) {
    let scrollTop = this.data.scrollTop
    this.setData({
      scrollTop: e.scrollTop
    })
  },
  getHeatGoodsList: function () {
    var that = this;
    wx.showLoading({
      "mask": true
    })
    var openid = wx.getStorageSync('openid')
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getheatminiappproducts/',
      data: {
        nameLike: that.data.searchInput,
        openid: openid
      },
      success: function (res) {
        //console.log(res)
        wx.hideLoading()
        if (res.data.code == 404 || res.data.code == 700) {
          that.setData(newData);
          return
        }
        that.setData({
          loadingMoreHidden: true,
          heat_products: res.data.data,
        });
      }
    })
  },
  getGoodsList: function (categoryId, append) {
    if (categoryId == 0) {
      categoryId = "";
    }
    var that = this;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getminiappproductsbycategory/',
      data: {
        categoryId: categoryId,
        nameLike: that.data.searchInput,
        page: this.data.curPage,
        pageSize: this.data.pageSize
      },
      success: function (res) {
        //console.log(res);
        if (res.data.code == 404 || res.data.code == 700) {
          let newData = { loadingMoreHidden: false }
          if (!append) {
            newData.goods = []
          }
          that.setData(newData);
          return
        }
        let goods = [];
        if (append) {
          goods = that.data.goods
        }
        for (var i = 0; i < res.data.data.length; i++) {
          goods.push(res.data.data[i]);
        }
        that.setData({
          loadingMoreHidden: true,
          category_list: res.data.data,
          goods: goods,
        });
      }
    })
  },
  onShareAppMessage: function () {
    return {
      title: wx.getStorageSync('mallName') + '——' + app.globalData.shareProfile,
      path: '/pages/campaign/index',
      success: function (res) {
        // 转发成功
      },
      fail: function (res) {
        // 转发失败
      }
    }
  },
  listenerSearchInput: function (e) {
    this.setData({
      searchInput: e.detail.value
    })

  },
  toClear: function () {
    this.setData({
      searchInput: '',
      search_input: ''
    });
    this.toSearch();
  },
  toSearch: function () {
    this.setData({
      curPage: 1
    });
    this.getHeatGoodsList();
    this.getGoodsList();
  },
  //onReachBottom: function () {
  //  this.setData({
  //    curPage: this.data.curPage+1
  //  });
  //  this.getGoodsList(this.data.activeCategoryId, true)
  //},
  onPullDownRefresh: function () {
    this.setData({
      curPage: 1
    });
    this.getGoodsList(this.data.activeCategoryId)
  },
  getTeachers: function () {
    let that = this;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getteachers/',
      data: { pageSize: 5 },
      success: function (res) {
        //console.log(res)
        if (res.data.code == 0) {
          that.setData({
            teacherList: res.data.data
          });
        }
      }
    })
  }
})
