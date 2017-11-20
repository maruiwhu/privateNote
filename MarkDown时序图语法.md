---
title: MarkDown时序图语法
tags: markdown
grammar_cjkRuby: true
grammar_sequence: true
---


## MarkDown时序图语法
和流程图类似，时序图也是用` ``` `包裹实现，例如：

    ···sequence
    Andrew->Bob:Say Hello,How old are you
    Note right of Bob:Bob thinns\about it
    Bob->Andrew:8,and you
    Note left of Andrew:Andrew thinks
    Andrew->Bob:8,too
    Note on Bob:HaHa
    ```
效果如下：
```sequence
Andrew->Bob: Say Hello,How old are you
Note right of Bob: Bob thinks n\about it
Bob-->Andrew: 8,and you
Note left of Andrew: Andrew thinks
Andrew->>Bob: 8,too
Note over Bob: HaHa
participant C
Note over Bob,C:over Bob and C
```
### 说明
时序图元素直接以`->`连接
其中`->`是普通实心箭头
`-->`是虚线箭头
`->>`是大箭头
可以在元素之间标记用`Note`表示
如：
`Note left(right) of`   
 `Note over`
 `Note over`可以跨列


 
 
