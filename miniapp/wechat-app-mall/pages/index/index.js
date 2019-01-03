//index.js
//获取应用实例
var app = getApp()
Page({
  data: {
    indicatorDots: true,
    autoplay: true,
    interval: 3000,
    duration: 1000,
    loadingHidden: false , // loading
    userInfo: {},
    swiperCurrent: 0,  
    selectCurrent:0,
    categories: [],
    activeCategoryId: 0,
    goods:[],
    scrollTop:0,
    loadingMoreHidden:true,

    hasNoCoupons:true,
    coupons: [],
    searchInput: '',

    curPage:1,
    pageSize:20
  },

  tabClick: function (e) {
    wx.navigateTo({
      url: "/pages/category-goods/index?category_id=" + e.currentTarget.dataset.id
    })
  },
  //事件处理函数
  swiperchange: function(e) {
      //console.log(e.detail.current)
       this.setData({  
        swiperCurrent: e.detail.current  
    })  
  },
  toDetailsTap:function(e){
    console.log("detail", e.currentTarget.dataset.id)
    wx.navigateTo({
      url:"/pages/goods-details/index?id="+e.currentTarget.dataset.id
    })
  },
  tapBanner: function(e) {
    console.log(e)
    var prod_id = e.currentTarget.dataset.linkid;
    if (prod_id > 0){
      wx.navigateTo({
        url: "/pages/goods-details/index?id=" + prod_id
      })
    }
  },
  bindTypeTap: function(e) {
     this.setData({  
        selectCurrent: e.index  
    })  
  },
  onLoad: function () {
    var that = this
    //let openid = wx.getStorageSync('openid')
    //if (!openid) {
    //  wx.navigateTo({
    //    url: "/pages/authorize/index"
    //  })
    //} 
    wx.setNavigationBarTitle({
      title: wx.getStorageSync('mallName')
    })
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getbannerlist/',
      data: {
        key: 'mallName'
      },
      success: function(res) {
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
    wx.request({
      url: 'https://class.ddianke.com/MiniAppAPI/getcategories/',
      success: function(res) {
        var categories = [];
        if (res.data.code == 0) {
          for (var i = 0; i < res.data.data.length; i++) {
            categories.push(res.data.data[i]);
          }
        }
        that.setData({
          categories:categories,
          activeCategoryId:0,
          curPage: 1
        });
        that.getHeatGoodsList();
        that.getGoodsList(0);
      }
    })
    //that.getTeachers();
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
      success: function(res) {
        //console.log(res);
        if (res.data.code == 404 || res.data.code == 700){
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
        for(var i=0;i<res.data.data.length;i++){
          goods.push(res.data.data[i]);
        }
        that.setData({
          loadingMoreHidden: true,
          category_list: res.data.data,
          goods:goods,
        });
      }
    })
  },
  onShareAppMessage: function () {
    return {
      title: wx.getStorageSync('mallName') + '——' + app.globalData.shareProfile,
      path: '/pages/index/index',
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
  toClear: function(){
    this.setData({
      searchInput: '',  
      search_input: ''
    });
    this.toSearch();
  },
  toSearch : function (){
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
  onPullDownRefresh: function(){
    this.setData({
      curPage: 1
    });
    this.getGoodsList(this.data.activeCategoryId)
  },
  getTeachers: function(){
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
