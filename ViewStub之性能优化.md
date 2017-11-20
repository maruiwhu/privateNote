---
title: ViewStub之性能优化 
tags: Android，性能优化
grammar_code: true
---

## 性能优化之ViewStub的使用
> 我们的首页面第一次进入时会有一个蒙版型的新手引导页面。
> 这是通过自定义一个View加载首界面的布局中，当用户点击完新手引导下次再进入时就不会有新手引导显示

### 问题 
非首次进入时，也需要初始化新手引导View，造成无谓的耗时
systrace分析，非首次进入的新手引导view初始化也要耗时30ms左右
![enter description here][1]

### 解决办法
对于不需要显示的View我们可以使用ViewStub实现。

##### ViewStub是什么

ViewStub是View的子类
1. 它不可见,大小为0
2. 用来延迟加载布局资源
> 注,关于Stub的解释
A stub is a small program routine that substitutes for a longer program, possibly to be loaded later or that is located remotely

#### ViewStub 怎么用

1. 在布局文件中使用ViewStub标签

![enter description here][2]

2. 在代码中inflate布局

![enter description here][3]

这样修改之后在非首次进入时就不需要inflate ViewStub也就减少了加载时间


  [1]: ./images/1511163824387.jpg
  [2]: ./images/1511165455971.jpg
  [3]: ./images/1511166126500.jpg