 console.log(data);
 //城市联动
 //step1:省份
 var text = "";
 for (i = 0; i < data.length; i++) {
     text += "<option value=" + i + " data-pId=" + data[i].pId + ">" + data[i].pName + "</option>";
 }
 console.log(text);
 $(".shengf").append(text);

 //step2:城市
 var text2 = "";
 $(".shengf").change(function () {
     text2 = "<option>请选择城市</option>";
     $(".city option").remove();
     $(".jxs option").remove();
     $(".jxs").append("<option>请选择经销商</option>");
     var cityid = $(this).val();
     var shengfs;
     if (cityid.length < 5) {
         shengfs = data[cityid].cities;
         for (j = 0; j < shengfs.length; j++) {
             text2 += "<option value=" + j + " data-cId=" + shengfs[j].cId + ">" + shengfs[j].cName + "</option>";
         }
         //step3:店铺
         var text3 = "";
         $(".city").change(function () {
             text3 = "<option>请选择经销商</option>";
             $(".jxs option").remove();
             var shengfid = $(this).val();
             if (shengfid.length < 5) {
                 var jxs = shengfs[shengfid].dealers;
                 for (z = 0; z < jxs.length; z++) {
                     text3 += "<option value=" + z + " data-dCode=" + jxs[z].dealerCode + ">" + jxs[z].dName + "</option>";
                 }
             }
             $(".jxs").append(text3);
         });
     }
     $(".city").append(text2);
 });