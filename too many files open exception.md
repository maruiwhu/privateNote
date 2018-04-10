---
title:   too many files open exception
tags: Android,模板,小书匠
grammar_code: true
---

## too many files open exception

### 问题描述
 > 收到monkey 测试，反馈crash异常。
 crash堆栈如下：
 
 ```java
 04-08 22:43:58.539  1542  1542 E AndroidRuntime: java.lang.RuntimeException: Could not read input channel file descriptors from parcel.
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.InputChannel.nativeReadFromParcel(Native Method)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.InputChannel.readFromParcel(InputChannel.java:148)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.InputChannel$1.createFromParcel(InputChannel.java:39)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.InputChannel$1.createFromParcel(InputChannel.java:37)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at com.android.internal.view.InputBindResult.<init>(InputBindResult.java:68)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at com.android.internal.view.InputBindResult$1.createFromParcel(InputBindResult.java:112)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at com.android.internal.view.InputBindResult$1.createFromParcel(InputBindResult.java:110)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at com.android.internal.view.IInputMethodManager$Stub$Proxy.startInputOrWindowGainedFocus(IInputMethodManager.java:723)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.inputmethod.InputMethodManager.startInputInner(InputMethodManager.java:1295)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.inputmethod.InputMethodManager.checkFocus(InputMethodManager.java:1449)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.view.ViewRootImpl$ViewRootHandler.handleMessage(ViewRootImpl.java:4242)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.os.Handler.dispatchMessage(Handler.java:106)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.os.Looper.loop(Looper.java:187)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at android.app.ActivityThread.main(ActivityThread.java:6991)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at java.lang.reflect.Method.invoke(Native Method)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:438)
04-08 22:43:58.539  1542  1542 E AndroidRuntime: 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:814)
 ```
 main log 中 crash附件有如下异常
 ```java
 04-08 22:43:58.363  1542  1597 E Parcel  : fcntl(F_DUPFD_CLOEXEC) failed in Parcel::read, i is 0, fds[i] is -1, fd_count is 2, error: Too many open files
 ```
 关键信息：Too many open files
 
表示：由应用中心进程打开的文件句柄过多，导致再打开文件句柄时无法打开，进而抛出异常

在linux中一切皆文件，文件、目录、软链、网络等都是通过文件句柄的形式。

### 解决思路


 由于无法知道到底是哪些fd打开过多，我们通过再次跑monkey，并同时抓取我们应用进程打开的fb，以便分析问题。
 ```java
 adb shell lsof -p <neo_store_pid>
 ```
 为方便测试通过python脚本，定期抓取日志
 
=[get fb ][1]
 
### 问题分析

通过测试同学几次跑monkey，最终复现了改问题，并且成功抓到fb打开的文件
1. 初步分析：
	问题复现时共有393736个fb打开
	
	其中 50684 个/dev/  -----系统相关
	
	47112 个/system/----系统相关
	
	95240 个TCP ---------处于CLOSE_WAIT状态 通过排查tcp，基本全部都是443端口的tcp未被释放
	
	189854 pipe----------和tcp未关闭有关，基本1个tcp对应2个pipe
	
	其他还有一些系统的fb
	   
	**初步判定原因是有大量的TCP连接未正常断开，导致fb超过限制。**

2. 既然知道是tcp导致的问题，那么我们通过抓包以及其他手段来看是哪个请求导致的问题。
   （1）先看两张图，了解下tcp流程
   
    ![tcp流程][2]
   
	![https流程][3]	
	
 根据上图看为什么会进入CLOSE_WAIT状态？
 当client向server发送ACK之后进入CLOSE_WAIT状态，接下来呢，实际上你真正需要考虑的事情是察看你是否还有数据发送给对方，如果没有的话，那么你也就可以close这个SOCKET，发送FIN报文给对方，也即关闭连接。所以你在CLOSE_WAIT状态下，需要完成的事情是等待你去关闭连接。

  （2）打开应用的常用页面，使用netstat命令查看当前应用的tcp连接
      netstat -nap | grep < pid >
	  
	 ![netstat][4]
	  
 可以看到明显有几个连接处于CLOSE_WAIT状态
 ip是101.37.134.8端口443
 **是https的请求**
 
 （3）再看网络包，这个ip的访问
 
 ![tcp][5]
  
 之前代码中存在漏洞是当response返回非200时，会出现response未关闭的场景，这样也会导致客户端的tcp未关闭。
 
  而这里通过抓包的看到的请求是评论的头像加载，我们头像的加载都是通过了一次302的重定向的请求，这与我们排查的请求未关闭的场景吻合。
  
 我们再用修改后的版本跑一下抓包看下结果：
 
 ![change][6]
 
 可以看到再请求结束之后，客户端发送了RST的报文，这样tcp会直接关闭。
 
 netstat抓取之后结果也看到，没有CLOSE_WAIT的连接。
 
 ![change netstat ][7]
 
 ### 后记
 
 在使用网络、文件、cursor等一定要该关闭的都关闭！！！
 遗留需要分析的问题：
 通过使用N的手机对比测试，有问题的版本在N的也会有CLOSE_WAIT的连接，但是N上基本在几分钟之后CLOSE_WAIT的连接会自动断掉，也就不会暴露出问题。但是在O上CLSOE_WAIT的不会自动关闭
  
 


  [1]: ./attachments/getfb_1.py
  [2]: ./images/1523355733889.jpg
  [3]: ./images/v2-9f717c2d57cc29e7f473a500e01f9f6e_hd.jpg "v2-9f717c2d57cc29e7f473a500e01f9f6e_hd"
  [4]: ./images/1523352297856.jpg
  [5]: ./images/1523355523956.jpg
  [6]: ./images/1523357373113.jpg
  [7]: ./images/1523358294392.jpg