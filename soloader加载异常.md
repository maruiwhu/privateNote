---
title: soloader加载异常
tags: Android,模板,小书匠
grammar_code: true
---
## platform应用使用soloader开源库时 加载so异常
问题堆栈：

```java

04-08 09:25:12.168 6509-6509/? W/ybrid:Launcher0: type=1400 audit(0.0:2155): avc: denied { execute } for path="/data/data/cn.nubia.hybrid/lib-main/libfb.so" dev="sda11" ino=32083 scontext=u:r:platform_app:s0:c512,c768 tcontext=u:object_r:app_data_file:s0:c512,c768 tclass=file permissive=0
04-08 09:25:12.187 6579-6579/? I/cr_ChildProcessService: Creating new ChildProcessService pid=6579
04-08 09:25:12.178 6509-6509/? W/ybrid:Launcher0: type=1400 audit(0.0:2156): avc: denied { execute } for path="/data/data/cn.nubia.hybrid/lib-main/libyoga.so" dev="sda11" ino=32097 scontext=u:r:platform_app:s0:c512,c768 tcontext=u:object_r:app_data_file:s0:c512,c768 tclass=file permissive=0
04-08 09:25:12.191 6509-6509/? E/zygote: No implementation found for long com.facebook.yoga.YogaNode.jni_YGNodeNew() (tried Java_com_facebook_yoga_YogaNode_jni_1YGNodeNew and Java_com_facebook_yoga_YogaNode_jni_1YGNodeNew__)
04-08 09:25:12.191 6509-6509/? D/AndroidRuntime: Shutting down VM
                                                 
                                                 
                                                 --------- beginning of crash
04-08 09:25:12.192 6509-6509/? E/AndroidRuntime: FATAL EXCEPTION: main
                                                 Process: cn.nubia.hybrid:Launcher0, PID: 6509
                                                 java.lang.UnsatisfiedLinkError: No implementation found for long com.facebook.yoga.YogaNode.jni_YGNodeNew() (tried Java_com_facebook_yoga_YogaNode_jni_1YGNodeNew and Java_com_facebook_yoga_YogaNode_jni_1YGNodeNew__)
                                                     at com.facebook.yoga.YogaNode.jni_YGNodeNew(Native Method)
                                                     at com.facebook.yoga.YogaNode.<init>(YogaNode.java:88)
                                                     at org.hapjs.component.view.YogaLayout.<init>(SourceFile:46)
                                                     at org.hapjs.component.view.YogaLayout.<init>(SourceFile:36)
                                                     at org.hapjs.component.view.flexbox.PercentFlexboxLayout.<init>(SourceFile:23)
                                                     at org.hapjs.widgets.Div.createViewImpl(SourceFile:29)
                                                     at org.hapjs.widgets.Div.createViewImpl(SourceFile:15)
                                                     at org.hapjs.component.Component.createView(SourceFile:132)
                                                     at org.hapjs.render.vdom.VDomActionApplier.generateComponent(SourceFile:143)
                                                     at org.hapjs.render.vdom.VDomActionApplier.a(SourceFile:117)
                                                     at org.hapjs.render.vdom.VDomActionApplier.applyChangeAction(SourceFile:43)
                                                     at org.hapjs.render.RootView.a(SourceFile:517)
                                                     at org.hapjs.render.RootView$b.handleMessage(SourceFile:203)
                                                     at android.os.Handler.dispatchMessage(Handler.java:106)
                                                     at android.os.Looper.loop(Looper.java:187)
                                                     at android.app.ActivityThread.main(ActivityThread.java:6913)
                                                     at java.lang.reflect.Method.invoke(Native Method)
                                                     at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:438)
                                                     at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:814)
​
```
从堆栈可以看出，是yoga加载一个so库无法加载到，导致的问题。

问题分析

 快应用引擎依赖了一个facebook的开源库 yoga https://github.com/facebook/yoga

而 yoga 又引用了SoLoader 的一个so动态加载库
https://github.com/facebook/SoLoader

而SoLoader所做的事情，大致是解压apk中的so，放到data/data/packagename/lib-main的文件夹中。
加载的时候再从lib-main的文件夹中加载so库



快应用属于platform appliction ，由于SeLinux的权限限制，无法访问lib-main下的so，进而导致so无法加载，导致快应用运行异常

```java
04-08 09:25:12.168 6509-6509/? W/ybrid:Launcher0: type=1400 audit(0.0:2155): avc: denied { execute } for path="/data/data/cn.nubia.hybrid/lib-main/libfb.so" dev="sda11" ino=32083 scontext=u:r:platform_app:s0:c512,c768 tcontext=u:object_r:app_data_file:s0:c512,c768 tclass=file permissive=0
04-08 09:25:12.187 6579-6579/? I/cr_ChildProcessService: Creating new ChildProcessService pid=6579
04-08 09:25:12.178 6509-6509/? W/ybrid:Launcher0: type=1400 audit(0.0:2156): avc: denied { execute } for path="/data/data/cn.nubia.hybrid/lib-main/libyoga.so" dev="sda11" ino=32097 scontext=u:r:platform_app:s0:c512,c768 
```
### 解决
1. 最先想到的就是去除selinux的权限控制，但是风险较大，也不一定能通过。所以这条暂不考虑
2. 阅读soloader的源码，soloader可以自定义so的加载策略。那么可以修改soloder的默认加载策略（从data/data/lib-mani），改为使用平台的默认加载机制。
最新选用方案2来进行修改
