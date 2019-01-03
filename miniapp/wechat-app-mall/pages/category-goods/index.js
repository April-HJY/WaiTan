// pages/category-goods/index.js
var app = getApp()
Page({
  data: {
    indicatorDots: true,
    autoplay: true,
    interval: 3000,
    duration: 1000,
    loadingHidden: false, // loading
    userInfo: {},
    swiperCurrent: 0,
    selectCurrent: 0,
    categories: [],
    activeCategoryId: 0,
    goods: [],
    scrollTop: 0,
    loadingMoreHidden: true,

    hasNoCoupons: true,
    coupons: [],
    searchInput: '',

    curPage: 1,
    pageSize: 20
  },

  tabClick: function (e) {
    let that = this;
    let tag_list = that.data.tag_list;
    let id = e.currentTarget.dataset.id;
    for(var i=0;i<tag_list.length;i++){
      if (tag_list[i].ID == id)
      {
        tag_list[i].Active = true;
      }
      else{
        tag_list[i].Active = false;
      }
    }
    that.setData({tag_list:tag_list});
  },
  //事件处理函数
  swiperchange: function (e) {
    //console.log(e.detail.current)
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  toDetailsTap: function (e) {
    wx.navigateTo({
      url: "/pages/goods-details/index?id=" + e.currentTarget.dataset.id
    })
  },
  tapBanner: function (e) {
    console.log(e)
    var prod_id = e.currentTarget.dataset.linkid;
    if (prod_id > 0) {
      wx.navigateTo({
        url: "/pages/goods-details/index?id=" + prod_id
      })
    }
  },
  bindTypeTap: function (e) {
    this.setData({
      selectCurrent: e.index
    })
  },
  onLoad: function (option) {
    let category_id = option.category_id
    this.setData({ category_id: category_id})
    var that = this
    wx.setNavigationBarTitle({
      title: wx.getStorageSync('mallName')
    })
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getbannerlist/',
      data: {
        category_id: category_id
      },
      success: function (res) {
        //console.log(res)
        if (res.data.code == 404) {
          wx.showModal({
            title: '提示',
            content: '请在后台添加 banner 轮播图片',
            showCancel: false
          })
        } else {
          that.setData({
            banners: res.data.data
          });
        }
      }
    }),
    that.getGoodsList(category_id);
    //that.getTeachers();
  },
  onPageScroll(e) {
    let scrollTop = this.data.scrollTop
    this.setData({
      scrollTop: e.scrollTop
    })
  },
  getGoodsList: function (categoryId, append) {
    var that = this;
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getminiappproductsbycategory/',
      data: {
        category_id: categoryId,
        nameLike: that.data.searchInput,
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
        let tags = []
        let show_tag = false;
        let cate = res.data.data[0];
        if (cate.ShowTag){
          show_tag = true;
          for (var i = 0; i < cate.Tags.length; i++) {
            if (i==0)
              cate.Tags[i].Active = true;
            else
              cate.Tags[i].Active = false;
          }
        }
        else{

        }
        that.setData({
          loadingMoreHidden: true,
          tag_list: res.data.data[0].Tags || [],
          prod_list: res.data.data[0].Products || [],
          goods: goods,
          show_tag: show_tag,
        });
      }
    })
  },
  onShareAppMessage: function () {
    let that = this;
    return {
      title: wx.getStorageSync('mallName') + '——' + app.globalData.shareProfile,
      path: '/pages/category-goods/index?category_id=' + that.data.category_id,
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
