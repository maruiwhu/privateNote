---
title: MarkDown流程图语法整理 
tags: markdown
grammar_cjkRuby: true
---

[TOC]

## MarkDown流程图语法整理

@(学习工作)[markdown]

流程图代码在MarkDown中类似如下：
```
```flow
st=>start: Start
e=>end: End
opFirst=>operation: Operation First
subFirst=>subroutine: Subroutine
cond=>condition: Yes or No
io=>inputoutput: input something 
st->opFirst->cond
cond(yes)->e
cond(no)->subFirst(left)->opFirst ```
```


输出实际结果如下：
```flow
st=>start: Start
e=>end: End
opFirst=>operation: Operation First
subFirst=>subroutine: Subroutine
cond=>condition: Yes or No
io=>inputoutput: input something 

st->opFirst->cond
cond(yes)->io->e
cond(no)->subFirst(right)->opFirst
```
在MarkDown中流程图需要写在	` ``` `	之间
### 语法
流程图的语法分为两部分
- 前面部分定义流程图的元素
- 后半部分连接流程图的元素，指定流程图的执行走向
#### 定义元素的语法
	tag=>type: content:>url
上例中的定义元素部分如下：
	
    st=>start: Start
	e=>end: End
	opFirst=>operation: Operation First
	subFirst=>subroutine: Subroutine
	cond=>condition: Yes or No
	io=>inputoutput: input something
**说明**
- tag 是流程图的标签，在第二段连接元素时会用到。名称可以任意，一般为流程的英文缩写和数字组合
- type 用来确定标签的类型，`=>` 后面表示类型
- 标签有6种类型：`start` `end` `operation` `subroutine` `condition` `inputoutput`
- content 是流程图文本框中的描述内容，`: `后面表示类容，中英文均可。但是冒号和文本框之间要有个空格
- url 是一个链接，与文本框的内容绑定，`: >` 后面就是对应的url链接，点击文本时可以跳转到对于的url页面，url以不写
#### 连接流程图的元素
示例代码的后面部分
```
st->opFirst->cond
cond(yes)->e
cond(no)->subFirst(left)->opFirst
```
**说明**
- 使用 `->`来连接元素
- 对于 condition 类型，有yes和no两个分支，使用方式如cond(yes) 和cond(no)
- 每个元素可以定义分支走向，默认向下，也可以指向右边，左边如subFirst(left)