# SubTimeLine

最终效果演示：http://pan.iqiyi.com/ext/paopao/?token=eJxjYGBgmBQtsZUBBA4uqQQAFiIDmQ.mp4

GUI效果演示：http://pan.iqiyi.com/ext/paopao/?token=eJxjYGBgmBQtsZUBBA4lzQEAFcQDew.mp4

GUI效果演示v2：https://alime-customer-upload-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/customer-upload/1587832342011_i66d3drp9iai.mp4

GUI效果演示v3（对比可见参数很重要）：https://alime-customer-upload-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/customer-upload/1587832960475_7kazj2qji6m7.mp4

![界面预览](http://puui.qpic.cn/vshpic/0/Hn6XV06k80NSOYAiRM4qIOk7aM6SVyo8gK1Y7p-L7imGCQOz_0/0)
![结果预览](http://puui.qpic.cn/vshpic/0/UG7pzw5ZCmPbM3Ga8ptbxMTox5weObjuaJa2bp1NZaDSAUDB_0/0)

# 说明

从硬字幕视频中提取字幕时间轴，并尝试OCR。

discord交流群：https://discord.gg/Cr68MgG

# 使用

调整参数：
- hmax通常在180左右
- smax根据情况不宜太小，也不能太大
- vmax根据字幕颜色而定，字幕纯白则跳255最佳，不是纯白需要减小以获得更好的效果
- vmin在170-240这个范围
- hmin和smin一般是0

# 其他

目前除OCR部分外基本是可使用状态，但字幕文本判别效果有待完善，优化中。

# 更新

## 2020/05/12

- 速度优化
- MSER box过滤改进
- 逻辑拆分