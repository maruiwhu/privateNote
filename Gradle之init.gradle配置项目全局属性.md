---
title: Gradle之init.gradle配置项目全局属性
tags: Android,gradle
grammar_code: true
---

## Gradle之init.gradle配置项目全局属性
> 在项目代码迁移的时候，如果项目中包含有很多的子项目，而在子项目中对应的仓库都是单独配置的
> 如果公司切换到内部的私有仓库，这就需要遍历所有的子项目脚本，修改对应的仓库地址，那么是否有简单的方式处理呢？

### Initialization Scripts
通过阅读官方文档，发现gradle存在一个初始化的脚本的方式，可以针对整个项目进行设置
#### init.gradle的作用
先来简单介绍一下init.gradle这个文件的作用。

1. 它可以用来建立公司内部的配置,如定义公司内部的仓库地址。
2. 它可以用来配置一些全局属性,比如配置持续集成服务器的地址等配置。
3. 它可以用来提供构建所需要的用户的个人信息,如仓库或数据库的用户名和密码。
4. 它可以用来定义开发者机器的环境,比如定义jdk安装在什么位置，android sdk安装在什么位置等等。
5. 最重要的功能之一，它可以用来注册一些监听器。比如监听Gradle事件的发生，做一些额外的操作，例如需要对某个项目构建前和构建后做一些操作，又例如对项目的依赖做检测，检测是否含有snapshot包，在release构建中一般来说是禁止依赖snapshot包的，所以这时候就可以扔出一个异常。
6. 重定向日志。我们可以将gradle默认的日志进行重定向，甚至我们可以不输出默认日志，自定义如何输出gradle产生的日志信息。
#### init.gradle的加载顺序
    
再来说说init.gradle文件的加载顺序（不一定命名为init.gradle）。Gradle会依次对一些目录进行检测，按照优先级加载这些目录下的文件，如果一个目录下有多个文件被找到，则按照英文字母的顺序依次加载。加载优先级如下：

1.通过 -I 或者 –init-script 参数在构建开始时指定路径，如 
```java
gradle --init-script init.gradle clean
gradle --I init.gradle assembleDebug
```
2. 加载USER_HOME/.gradle/init.gradle文件
3. 加载USER_HOME/.gradle/init.d/目录下的以.gradle结尾的文件
4. 加载GRADLE_HOME/init.d/目录下的以.gradle结尾的文件
5. 
#### 脚本的编写
我们这里使用到的是统一定义仓库的功能，所以这里就介绍下定义仓库的脚本
![脚本][1]

如上图所示，将所有项目的仓库地址修改，就不需要每个gradle的脚本中去修改了，减少工作量


  


  [1]: ./images/_20180228141552.jpg "_20180228141552"