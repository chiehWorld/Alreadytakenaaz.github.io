---
layout:     post
title:      "Java> ArrayList的扩容因子为什么是1.5？"
subtitle:   "归档于：面经"
date:       2026-01-22
author:     Chieh
header-img: assets/Java-ArrayList的扩容因子为什么是1.5？_header.jpg
catalog: true
tags:
    - Interview
    - Java
    - 面经
---

ArrayList底层是数组elementData，用于存放插入的数据。初始大小是0，当有数据插入时，默认大小DEFAULT\_CAPACITY = 10。

```
/**
     * The array buffer into which the elements of the ArrayList are stored.
     * The capacity of the ArrayList is the length of this array buffer. Any
     * empty ArrayList with elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA
     * will be expanded to DEFAULT_CAPACITY when the first element is added.
     */
    transient Object[] elementData; // non-private to simplify nested class access
```


### 什么时候进行扩容？

当插入数据，导致size + 1 > elementData.length，也就是需要从容量超过目前数组长度时，需要进行扩容。

```
public boolean add(E e) {
    ensureCapacityInternal(size + 1);  // Increments modCount!! // add一个元素时，size + 1
    elementData[size++] = e;
    return true;
}
private void ensureCapacityInternal(int minCapacity) {
    ensureExplicitCapacity(calculateCapacity(elementData, minCapacity)); 
}
private void ensureExplicitCapacity(int minCapacity) {
    modCount++;
    // overflow-conscious code
    if (minCapacity - elementData.length> 0)
        grow(minCapacity);
}
private static int calculateCapacity(Object[] elementData, int minCapacity) { // 计算新容量
    if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) { // 代表elementData数组还是一个空数组，没有任何数据
        return Math.max(DEFAULT_CAPACITY, minCapacity); // elementData为空时，会扩容到DEFAULT_CAPACITY = 10和minCapacity的最大值，而minCapacity在插入数据时第一次值为1（size + 1 = 1），会扩容为10
    }
    return minCapacity;
}
```


### 如何扩容？

新数组容量为旧数组的1.5倍：newCapacity = 1.5 \* oldCapacity ，并且将旧数组内容通过Array.copyOf全部复制到新数组。此时，size还未真正+1，新旧数组长度（size一致），不过容量不同。  
把这里的系数1.5，称作扩容因子k = newCapacity / oldCapacity

```
/**
 * Increases the capacity to ensure that it can hold at least the
 * number of elements specified by the minimum capacity argument.
 *
 * @param minCapacity the desired minimum capacity
 */
private void grow(int minCapacity) {
    // overflow-conscious code
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity>> 1);
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE> 0)
        newCapacity = hugeCapacity(minCapacity);
    // minCapacity is usually close to size, so this is a win:
    elementData = Arrays.copyOf(elementData, newCapacity);
}
private static int hugeCapacity(int minCapacity) {
    if (minCapacity < 0) // overflow
        throw new OutOfMemoryError();
    return (minCapacity> MAX_ARRAY_SIZE) ?
        Integer.MAX_VALUE :
        MAX_ARRAY_SIZE;
}
```


### 扩容因子k为何是1.5？

参考[C++ STL 中 vector 内存用尽后, 为什么每次是 2 倍的增长, 而不是 3 倍或其他值? - Milo Yip的回答 - 知乎](https://www.zhihu.com/question/36538542/answer/67994276) ，有一个很通俗的解释，扩容因子最适合范围为(1, 2)。

下面举一组对比的例子，取不同扩容因子和初始容量的内存分配情况，当然容量不可能是4，只是方便说明：

```
k = 2, capacity = 4
0123
    01234567
            0123456789101112131415
                                  012345678910111213141516171819202122232425262728293031
                                                                                        0123...
k = 1.5, capacity = 4
0123
    012345
          012345678
                <--(0123456789101112)
0123456789101112
                ...
```


k=1.5时，就能充分利用前面已经释放的空间。如果k >= 2，新容量刚刚好永远大于过去所有废弃的数组容量。

* 为什么不取扩容固定容量呢？  
  扩容的目的需要综合考虑这两种情况：

1. 扩容容量不能太小，防止频繁扩容，频繁申请内存空间 + 数组频繁复制
2. 扩容容量不能太大，需要充分利用空间，避免浪费过多空间；

而扩容固定容量，很难决定到底取多少值合适，取任何具体值都不太合适，因为所需数据量往往由数组的客户端在具体应用场景决定。依赖于当前已经使用的量 \* 系数， 比较符合实际应用场景。  
比如，我现在已经用到一个数组100的容量，接下来很可能会有这个数量级的数据需要插入。

* 为什么是1.5，而不是1.2，1.25，1.8或者1.75？  
  因为1.5 可以充分利用移位操作，减少浮点数或者运算时间和运算次数。

```
// 新容量计算
int newCapacity = oldCapacity + (oldCapacity>> 1);
```

---
> 参考链接：[https://www.cnblogs.com/fortunely/p/14279231.html](https://www.cnblogs.com/fortunely/p/14279231.html)
