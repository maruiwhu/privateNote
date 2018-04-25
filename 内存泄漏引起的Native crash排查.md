---
title: 内存泄漏引起的Native crash排查
tags: Android,模板,小书匠
grammar_code: true
---
### JNI ERROR (app bug): weak global reference table overflow (max=51200)'

> 最近收到一个anr问题，通过排查log发现是由于native crash引起的。那就转而分析为什么会有crash

crash堆栈如下 
```java
4-14 03:01:37.670 20949 20949 F DEBUG   : Abort message: 'art/runtime/indirect_reference_table.cc:132] JNI ERROR (app bug): weak global reference table overflow (max=51200)'
04-14 03:01:37.670 20949 20949 F DEBUG   :     r0 00000000  r1 0000338a  r2 00000006  r3 00000008
04-14 03:01:37.670 20949 20949 F DEBUG   :     r4 ee05858c  r5 00000006  r6 ee058534  r7 0000010c
04-14 03:01:37.670 20949 20949 F DEBUG   :     r8 00000000  r9 0000000a  sl 00000cd2  fp eb405400
04-14 03:01:37.670 20949 20949 F DEBUG   :     ip 0000000b  sp fffa0590  lr eb55bb87  pc eb55e408  cpsr 200d0010
04-14 03:01:38.180 20949 20949 F DEBUG   : 
04-14 03:01:38.180 20949 20949 F DEBUG   : backtrace:
04-14 03:01:38.188 20949 20949 F DEBUG   :     #00 pc 0004a408  /system/lib/libc.so (tgkill+12)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #01 pc 00047b83  /system/lib/libc.so (pthread_kill+34)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #02 pc 0001d9c5  /system/lib/libc.so (raise+10)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #03 pc 000192f1  /system/lib/libc.so (__libc_android_abort+34)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #04 pc 00017358  /system/lib/libc.so (abort+4)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #05 pc 0031ba8d  /system/lib/libart.so (_ZN3art7Runtime5AbortEPKc+328)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #06 pc 000b5319  /system/lib/libart.so (_ZN3art10LogMessageD2Ev+1132)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #07 pc 001bc7ab  /system/lib/libart.so (_ZN3art22IndirectReferenceTable3AddEjPNS_6mirror6ObjectE+194)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #08 pc 0023a7cf  /system/lib/libart.so (_ZN3art9JavaVMExt16AddWeakGlobalRefEPNS_6ThreadEPNS_6mirror6ObjectE+46)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #09 pc 0027f89f  /system/lib/libart.so (_ZN3art3JNI16NewWeakGlobalRefEP7_JNIEnvP8_jobject+418)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #10 pc 0008b403  /system/lib/libandroid_runtime.so
04-14 03:01:38.188 20949 20949 F DEBUG   :     #11 pc 01fb0e65  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.RenderNode.nCreate+96)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #12 pc 01fb0bbb  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.RenderNode.<init>+70)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #13 pc 01fb0d29  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.RenderNode.create+68)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #14 pc 01f3a499  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.View.<init>+540)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #15 pc 01f3a6b7  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.View.<init>+66)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #16 pc 01f3a63d  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.View.<init>+64)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #17 pc 01f3a5c5  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.View.<init>+56)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #18 pc 000a9a41  /system/lib/libart.so (art_quick_invoke_stub_internal+64)
04-14 03:01:38.188 20949 20949 F DEBUG   :     #19 pc 004061ad  /system/lib/libart.so (art_quick_invoke_stub+232)
04-14 03:01:38.189 20949 20949 F DEBUG   :     #20 pc 000b0ce5  /system/lib/libart.so (_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc+136)
04-14 03:01:38.189 20949 20949 F DEBUG   :     #21 pc 003169f9  /system/lib/libart.so (_ZN3artL18InvokeWithArgArrayERKNS_33ScopedObjectAccessAlreadyRunnableEPNS_9ArtMethodEPNS_8ArgArrayEPNS_6JValueEPKc+56)
04-14 03:01:38.189 20949 20949 F DEBUG   :     #22 pc 00317d2f  /system/lib/libart.so (_ZN3art12InvokeMethodERKNS_33ScopedObjectAccessAlreadyRunnableEP8_jobjectS4_S4_j+674)
04-14 03:01:38.189 20949 20949 F DEBUG   :     #23 pc 002b5bf9  /system/lib/libart.so (_ZN3artL24Constructor_newInstance0EP7_JNIEnvP8_jobjectP13_jobjectArray+868)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #24 pc 005abf7d  /system/framework/arm/boot.oat (offset 0x51c000) (java.lang.reflect.Constructor.newInstance0+96)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #25 pc 005ac9c1  /system/framework/arm/boot.oat (offset 0x51c000) (java.lang.reflect.Constructor.newInstance+52)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #26 pc 01fa1003  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.createView+1174)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #27 pc 02226a81  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (com.android.internal.policy.PhoneLayoutInflater.onCreateView+84)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #28 pc 01fa2739  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.onCreateView+44)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #29 pc 01fa19b7  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.createViewFromTag+706)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #30 pc 01f9fefd  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.createViewFromTag+64)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #31 pc 01fa29ef  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.rInflate+538)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #32 pc 01fa2cc7  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.rInflateChildren+82)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #33 pc 01fa22bd  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.inflate+760)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #34 pc 01fa1ee7  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.inflate+114)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #35 pc 01fa1e41  /system/framework/arm/boot-framework.oat (offset 0x16c4000) (android.view.LayoutInflater.inflate+52)
04-14 03:01:38.190 20949 20949 F DEBUG   :     #36 pc 0001f127  /dev/ashmem/dalvik-jit-code-cache (deleted)
```

这个堆栈并没有我们的代码，单子看关键信息
```java
JNI ERROR (app bug): weak global reference table overflow 
```
猜测可能是什么未释放导致的，那到底是什么未释放呢，
继续查main log
```java
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132] JNI ERROR (app bug): weak global reference table overflow (max=51200)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132] weak global reference table dump:
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]   Last 10 entries (of 51200):
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51199: 0x38184fa0 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51198: 0x3814fb20 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51197: 0x3814c760 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51196: 0x3814cfa0 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51195: 0x3813f0b8 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51194: 0x3813f5c8 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51193: 0x3813f9d0 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51192: 0x3813fd30 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51191: 0x3813fd90 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     51190: 0x3813ff40 android.view.RenderNode
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]   Summary:
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]     50694 of android.view.RenderNode (50694 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]       159 of byte[] (14112 elements) (159 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]       159 of byte[] (28224 elements) (159 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]        30 of java.lang.DexCache (30 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]        27 of byte[] (26244 elements) (27 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]        16 of byte[] (36864 elements) (16 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]        15 of byte[] (20736 elements) (15 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         8 of dalvik.system.PathClassLoader (4 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         8 of byte[] (9216 elements) (8 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         5 of byte[] (270400 elements) (5 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         4 of byte[] (10080 elements) (4 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         4 of byte[] (46656 elements) (4 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         4 of byte[] (57600 elements) (4 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         4 of byte[] (108000 elements) (4 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         3 of byte[] (1440 elements) (3 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         3 of byte[] (5016 elements) (3 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         3 of byte[] (79488 elements) (3 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         3 of byte[] (82944 elements) (3 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         3 of byte[] (541696 elements) (3 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         3 of byte[] (950400 elements) (3 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (736 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (1936 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (18432 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (29584 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (34848 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (35344 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (36288 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (47808 elements) (2 unique instances)
04-14 02:59:56.769 13194 13194 F art     : art/runtime/indirect_reference_table.cc:132]         2 of byte[] (725904 elements) (2 unique instances)
```
可以看到居然有50694个android.view.RenderNode对象

那就是view未被释放了，初步猜测可能是内存泄漏导致页面未被释放，进而导致了太多的view未被释放掉。

下面就要排查内存泄漏的根源了。


