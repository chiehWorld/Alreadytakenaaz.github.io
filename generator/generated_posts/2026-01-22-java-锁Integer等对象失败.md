---
layout:     post
title:      "java 锁Integer等对象失败"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/java-锁Integer等对象失败_header.png
catalog: true
tags:
    - Java
    - 技术
---

在学习并发编程时，多个线程对同一个Integer对象进行操作时，我想当然的直接对这个Integer对象加锁。然而最终结果让我百思不得其解，加锁无效。

```
public class TestJoin {
    static A testA = new A();
    public volatile static Integer t = 0;
    public static void main(String[] args) throws InterruptedException {
        Thread[] threads = new Thread[10];
        for (int j = 0; j < 10; j++) {
            threads[j] = new Thread(testA);
            threads[j].start();
        }
        for (int j = 0; j < 10; j++) {
            threads[j].join();
        }
        System.out.println(t);
    }
    static class A implements Runnable {
        @Override
        public void run() {
            for (int f = 0; f < 2000; f++) {
                synchronized (t) {
                    t++;
                }
            }
        }
    }
}
```


　　最终输出为：![](assets/java-锁Integer等对象失败_img_1.png)

并不是所预期的20000.

```
原因：java的自动封箱和解箱操作在作怪。这里的t++实际上是i = new Integer(t+1)，所以执行完t++后，t已经不是原来的对象了，同步块自然就无效了
解决方法：将synchronized（t）变为synchronized（testA）即可
```

---
> 参考链接：[https://www.cnblogs.com/DoJavaByHeart/p/8515020.html](https://www.cnblogs.com/DoJavaByHeart/p/8515020.html)
