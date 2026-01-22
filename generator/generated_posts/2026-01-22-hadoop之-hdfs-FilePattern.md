---
layout:     post
title:      "hadoop之 hdfs FilePattern"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/hadoop之-hdfs-FilePattern_header.png
catalog: true
tags:
    - hadoop
    - 技术
---

举一个例子:使用mapreduce统计一个月或者两个的日志文件，这里可能有大量的日志文件。如何快速的提取文件路径？  
在HDFS中，可以使用通配符来解决这个问题。与linux shell的通配符相同。

例如：

| Tables | Are |
| --- | --- |
| 2016/\* | 2016/05 2016/04 |
| 2016/0[45] | 2016/05 2016/04 |
| 2016/0[4-5] | 2016/05 2016/04 |

代码：

```
public static void globFiles(String pattern){
    try {
        FileSystem fileSystem = FileSystem.get(configuration);
        FileStatus[] statuses = fileSystem.globStatus(new Path(pattern));
        Path[] listPaths = FileUtil.stat2Paths(statuses);
        for (Path path : listPaths){
            System.out.println(path);
        }
    } catch (IOException e) {
        e.printStackTrace();
    }
}
```


hdfs 还提供了一个PathFilter 对我们获取的文件路径进行过滤，与java.io.FileFilter类似

```
/**
 * Return an array of FileStatus objects whose path names match pathPattern
 * and is accepted by the user-supplied path filter. Results are sorted by
 * their path names.
 * Return null if pathPattern has no glob and the path does not exist.
 * Return an empty array if pathPattern has a glob and no path matches it. 
 * 
 * @param pathPattern
 *          a regular expression specifying the path pattern
 * @param filter
 *          a user-supplied path filter
 * @return an array of FileStatus objects
 * @throws IOException if any I/O error occurs when fetching file status
 */
public FileStatus[] globStatus(Path pathPattern, PathFilter filter)
    throws IOException {
  return new Globber(this, pathPattern, filter).glob();
}
```


![](assets/hadoop之-hdfs-FilePattern_img_1.png)

hdfs自身提供了许多filter，在hadoop权威指南中，提供一种 正则表达式filter的实现

```
public class RegexExcludePathFilter implements PathFilter {
    private  String regex;
    public RegexExcludePathFilter(String regex) {
        this.regex = regex;
    }
    @Override
    public boolean accept(Path path) {
        return !path.toString().matches(regex);
    }
}
```


利用正则表达式优化结果

```
fileSystem.listStatus(new Path(uri),new RegexExcludePathFilter("^.*/2016/0$"));
```


结果输出如下：

```
hdfs://hadoop:9000/hadoop/2016/04
hdfs://hadoop:9000/hadoop/2016/05
```


过滤器由Path表示，只能作用于文件名以及路径。

---
> 参考链接：[https://www.cnblogs.com/re-myself/p/5527587.html](https://www.cnblogs.com/re-myself/p/5527587.html)
