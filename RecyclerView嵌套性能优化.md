---
title: RecyclerView嵌套性能优化
tags: Android,模板,小书匠
grammar_code: true
---

## RecyclerView 嵌套RecyclerView 性能优化
> RecyclerView 是Android退出的以替代RecyclerView、GridView等容器的控件。
>通常RecyclerView可以用来实现 列表、横像列表、宫格、瀑布流等样式。
>但是也有形如Google Play主界面那种垂直列表中嵌套横向列表的情况。我们应用中心的视效和Google Play类似，我们的实现方式就是嵌套横向滑动的RecyclerView
>![enter description here][1]

### 问题
使用横向滑动的RecyclerView之后，发现在横向滑动的时候没有问题，但是垂直滑动的时候，有明显的卡顿。
### 解决
通过以下几个方式，可以优化滑动卡顿的问题
1.notifyDataSetChanged
	一般来说如果recyclerView的数据有变化，我们会调用notifyDataSetChanged以刷新界面。
但是每一次调用notifyDataSetChanged都会RecyclerView的重新布局和重新绘制，性能会有所损耗。
对于RecyclerView提供了增量更新的方式，通过比较新数据和旧数据的Diff，只做微量的刷新。@DiffUtil
2.RecycledViewPool
我们都知道RecyclerView的缓存机制，可以避免创建过多的View。
但是对于跨RecyclerView之间，如果不做特殊处理，是无法做到View的共享。
通过API提供的setRecycledViewPool，可以自定义RecyclerView的缓存池。
做到跨RecyclerView共享缓存，这样就可以减少View的创建
3.RecycledViewPool.setMaxRecycledViews(ViewType ,count)
默认RecycledViewPool的缓存池最大数量是5，但是如果我们跨recyclerview共享缓存池的话，最大数如果过少，其实会影响滑动的效果。根据实际情况跳转。我们这边设置为20

3.setRecyclerChildrenOnDetach
这个方法表示在Child View 执行onViewDetached的时候需不需要执行recycler
如果设置了RecycledViewPool，需要手动将这个参数设为true，可以优化滑动效果
4.setInitialPrefetchItemCount
这个设置在RecyclerView空闲时预加载View的个数，这样可以在闲时做事，就可以避免忙时的卡顿

  [1]: ./images/1522375270399.jpg