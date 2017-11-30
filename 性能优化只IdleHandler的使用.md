---
title: 性能优化只IdleHandler的使用
tags: Android
grammar_code: true
---


## 性能优化只IdleHandler的使用
> Handler是我们常使用的类，用来做异步线程和主线程交互，或者发送message。
> Handler 和Looper、 MessageQueue 三者相互合作，实现android的Message消息机制。其中Handler负责发送消息和接收消息。MessageQueue负责存放消息、Looper负责提取消息


![enter description here][1]


  [1]: ./images/1083096-64bc44c65fa6cd84.png "1083096-64bc44c65fa6cd84"
  
  通常我们使用Handler是sendMessage或者直接在主线程中post run如：
  ```java
  new Handler(Looper.getMainLooper()).post(new Runnable() {
@Override
   public void run() {/do something } 
});
  ```
  #### 什么是IdleHandler
  但是在MesageQuene中有个功能IdleHandler接口，有个有趣的用法，IdleHandler的定义如下
  ```java
   /**
     * Callback interface for discovering when a thread is going to block
     * waiting for more messages.
     */
    public static interface IdleHandler {
        /**
         * Called when the message queue has run out of messages and will now
         * wait for more.  Return true to keep your idle handler active, false
         * to have it removed.  This may be called if there are still messages
         * pending in the queue, but they are all scheduled to be dispatched
         * after the current time.
         */
        boolean queueIdle();
    }
```
简而言之，就是在looper里面的message暂时处理完了，这个时候会回调这个接口，返回false，那么就会移除它，返回true就会在下次message处理完了的时候继续回调。
#### IdleHandler的回调时机

> 我们都知道当我们启动一个Activity时，Activity会经过onCreate onStart onResume的生命周期。如果我们在进入页面时添加一个IdleHandler回调，那么个什么时候会调用这个方法呢，onStart ？ onResume？

我们在Activity的生命周期打日志，并且在onCreate中向Looper添加一个IdleHander，如下：
```java
protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Log.i(TAG, "onCreate: ");
        Looper.myQueue().addIdleHandler(new MessageQueue.IdleHandler() {
            @Override
            public boolean queueIdle() {
                Log.i(TAG, "queueIdle: ");
                return false;
            }
        });
    }

```

```
11-03 15:46:54.925 31033-31033/com.example.marui.myapplication I/MainActivity: onCreate: 
11-03 15:46:54.927 31033-31033/com.example.marui.myapplication I/MainActivity: onStart: 
11-03 15:46:54.929 31033-31033/com.example.marui.myapplication I/MainActivity: onResume: 
11-03 15:46:55.079 31033-31033/com.example.marui.myapplication I/MainActivity: queueIdle: 
```
可以看到queneIdle的回调会在onResume之后执行。具体为什么在这里回调，下面单独将Activity的启动流程再讲。

我们知道这个回调会在Activity执行完onResume，页面可见的时候再调用。
我们可以利用这个接口可以实现一些独特的功能，优化启动速度。
比如：
1.如果某个图片资源比较大，从res中初始化耗时较长。我们可以先ImageView设置默认图片，然后进入页面之后利用这个回调，在Activity的主线程事情处理完成之后，再在会调用重新给ImageView设置图片。
这样做就可以提高进入Activity的速度一些必须在主线程中的操作，可以稍微延迟一会再做。
2.