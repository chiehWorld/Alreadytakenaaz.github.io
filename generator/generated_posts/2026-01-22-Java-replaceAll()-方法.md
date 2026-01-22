---
layout:     post
title:      "Java replaceAll() 方法"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/Java-replaceAll()-方法_header.jpg
catalog: true
tags:
    - HTML 拾色器
    - HTML ASCII 字符集
    - Java
    - Java replaceAll() 方法
    - 技术
---

# Java replaceAll() 方法

Java String类

replaceAll() 方法使用给定的参数 replacement 替换字符串所有匹配给定的正则表达式的子字符串。

### 语法

```
public String replaceAll(String regex, String replacement)
```


### 参数

* regex -- 匹配此字符串的正则表达式。\n
* replacement -- 用来替换每个匹配项的字符串。

### 返回值

成功则返回替换的字符串，失败则返回原始字符串。

### 实例

## 实例

```

```


public

class

Test

{

\n

public

static

void

main

(

String

args

[

]

)

{

\n

String

Str

=

new

String

(

"www.google.com"

)

;

\n

System

.

out

.

print

(

"匹配成功返回值 :"

)

;

\n

System

.

out

.

println

(

Str.

replaceAll

(

"(.\*)google(.\*)"

,

"runoob"

)

)

;

\n

System

.

out

.

print

(

"匹配失败返回值 :"

)

;

\n

System

.

out

.

println

(

Str.

replaceAll

(

"(.\*)taobao(.\*)"

,

"runoob"

)

)

;

\n

}

\n

}

\n

以上程序执行结果为：

```
匹配成功返回值 :runoob
匹配失败返回值 :www.google.com
```


Java String类

---
> 参考链接：[https://www.runoob.com/java/java-string-replaceall.html](https://www.runoob.com/java/java-string-replaceall.html)
