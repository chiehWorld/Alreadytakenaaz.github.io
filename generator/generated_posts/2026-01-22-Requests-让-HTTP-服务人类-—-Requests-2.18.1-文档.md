---
layout:     post
title:      "Requests: 让 HTTP 服务人类 — Requests 2.18.1 文档"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: 
catalog: true
tags:
    - 技术
---

# Requests: 让 HTTP 服务人类¶

发行版本 v2.18.1. (安装说明)

Requests 唯一的一个非转基因的 Python HTTP 库，人类可以安全享用。

警告：非专业使用其他 HTTP 库会导致危险的副作用，包括：安全缺陷症、冗余代码症、重新发明轮子症、啃文档症、抑郁、头疼、甚至死亡。

看吧，这就是 Requests 的威力：

```
>>> 
r
 =
 requests
.
get
(
'https://api.github.com/user'
,
 auth
=
(
'user'
,
 'pass'
))
>>> 
r
.
status_code
200
>>> 
r
.
headers
[
'content-type'
]
'application/json; charset=utf8'>>> 
r
.
encoding
'utf-8'>>> 
r
.
text
u'{"type":"User"...'>>> 
r
.
json
()
{u'private_gists': 419, u'total_private_repos': 77, ...}
```


参见 未使用 Requests 的相似代码.

Requests 允许你发送纯天然，植物饲养的 HTTP/1.1 请求，无需手工劳动。你不需要手动为
URL 添加查询字串，也不需要对 POST 数据进行表单编码。Keep-alive 和 HTTP 连接池的功能是
100% 自动化的，一切动力都来自于根植在 Requests 内部的 urllib3。

## 用户见证¶

Twitter、Spotify、Microsoft、Amazon、Lyft、BuzzFeed、Reddit、NSA、女王殿下的政府、Amazon、Google、Twilio、Mozilla、Heroku、PayPal、NPR、Obama for America、Transifex、Native Instruments、Washington Post、Twitter、SoundCloud、Kippt、Readability、以及若干不愿公开身份的联邦政府机构都在内部使用。

Armin Ronacher
:   Requests 是一个完美的例子，它证明了通过恰到好处的抽象，API 可以写得多么优美。

Matt DeBoard
:   我要想个办法，把 @kennethreitz 写的 Python requests 模块做成纹身。一字不漏。

Daniel Greenfeld
:   感谢 @kennethreitz 的 Requests 库，刚刚用 10 行代码炸掉了 1200 行意大利面代码。今天真是爽呆了！

Kenny Meyers
:   Python HTTP: 疑惑与否，都去用 Requests 吧。简单优美，而且符合 Python 风格。

---
> 参考链接：[http://cn.python-requests.org/zh_CN/latest/](http://cn.python-requests.org/zh_CN/latest/)
