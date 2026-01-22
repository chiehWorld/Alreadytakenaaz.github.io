---
layout:     post
title:      "flask在同一个页面提交多个form请求"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/flask在同一个页面提交多个form请求_header.jpg
catalog: true
tags:
    - Python
    - pythonweb
    - python
    - 技术
---

1.首先，在写网站的后台管理页面的时候，发现，我要在同一个页面上提交两个表单，或者是可以单一的的提交其中一个，其中一个表单可以没有数据也可以有数据，即两者之间的提交是没有什么鸟关系的。

随手写的表单

```
<p>活动</p>
    <form method="post" action="/admin_event/" name="event">
        标题
        <input name="event_title" value="" type="text">
        内容
        <input name="event_content" value="" type="text">
        开始时间
        <input name="start_time" value="" type="datetime">
        结束时间
        <input name="end_time" value="" type="datetime">
        <button type="submit" value="">提交</button>
    </form>
<p>资源</p>
    <form method="post" action="/admin_resource/" name="resource">
        资源标题
        <input name="resource_title" value="" type="text">
        资源描述
        <input name="description" value="" type="text">
        下载链接
        <input name="download_url" value="" type="text">
        <button type="submit">提交</button>
    </form>
```


这里的重点是form标签里一定要填写action属性和name属性。

```
@app.route('/admin_event/',methods=['GET','POST'])
def admin_event():
    if request.method=='GET':
        return render_template('admin.html')
    else:
        event_title = request.form.get('event_title')
        event_content = request.form.get('event_content')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        print(event_title)
        event = Event(title=event_title, content=event_content, start_time=start_time, end_time=end_time)
        db.session.add(event)
        db.session.commit()
        return render_template('admin.html')
@app.route('/admin_resource/',methods=['GET','POST'])
def admin_resource():
   if request.method=='GET':
       return render_template('admin.html')
   else:
       resource_title = request.form.get('resource_title')
       description = request.form.get('description')
       download_url = request.form.get('download_url')
       resources = Resource(title=resource_title, content=description, download_url=download_url)
       db.session.add(resources)
       db.session.commit()
       return render_template('admin.html')
```


通过所提交 的地址不同，去向不同的视图函数

学习笔记

---
> 参考链接：[https://www.cnblogs.com/s42-/p/9954854.html](https://www.cnblogs.com/s42-/p/9954854.html)
