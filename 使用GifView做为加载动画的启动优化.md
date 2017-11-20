---
title: 使用GifView做为加载动画的启动优化
tags: Android,性能优化
grammar_cjkRuby: true
---


### 使用GifView做为加载动画的启动优化
> Android中加载gif图片，我们一般是使用类似Movie的方式实现，如
> [GifView](https://github.com/Cutta/GifView)

我们是使用GifView来实现了一个页面loading的动画，所有的加载页面都是使用的这个GifView，通过systemTrace分析发现，每次进入一个页面GifView的inflate方法执行时间都在20ms左右，再加上其他控件的初始化，进入页面的初始化操作肯定会丢帧
![enter description here][1]

而通过分析发现，GifView的耗时操作主要是在加载gif图片
![enter description here][2]

参考Android对于res资源的处理，同样的资源只加载一次，下次使用直接使用缓存的方式，这样就可以避免每次进入页面的Gif图片加载的耗时。
优化方法：
![enter description here][3]
![enter description here][4]
优化后的systrace

![enter description here][5]

可以看到优化后GifView的非初次inflate时间有明显优化

  [1]: ./images/1511159174662.jpg
  [2]: ./images/1511159230590.jpg
  [3]: ./images/1511159779716.jpg
  [4]: ./images/1511159796453.jpg
  [5]: ./images/1511159691154.jpg