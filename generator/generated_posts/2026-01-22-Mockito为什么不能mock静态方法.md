---
layout:     post
title:      "Mockito为什么不能mock静态方法"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/Mockito为什么不能mock静态方法_header.jpg
catalog: true
tags:
    - java
    - testing
    - 技术
---

因为Mockito使用继承的方式实现mock的，用CGLIB生成mock对象代替真实的对象进行执行，为了mock实例的方法，你可以在subclass中覆盖它，而static方法是不能被子类覆盖的，所以Mockito不能mock静态方法。

但PowerMock可以mock静态方法，因为它直接在bytecode上工作。

**PowerMock**是一个JUnit扩展，它利用了EasyMock和Mockito模拟静态method的方法对Java中的静态method进行Mock，而且它还有更多的功能（详见[github/powermock](https://github.com/powermock/powermock)）。

首先我们设计一个静态类如下(Utility.java)：

```
public class Utility {
    public static <T> boolean listIsNullOrEmpty(List<T> objectList) {
        return objectList == null || objectList.isEmpty();
    }
    public static <T> boolean listIsNotNullOrEmpty(List<T> objectList) {
        return objectList != null && !objectList.isEmpty();
    }
}
```


  被测试类如下(UtilityHelper.java)：

```
public class UtilityHelper {
    public int sum(List<Integer> dataLst) {
        if (Utility.listIsNullOrEmpty(dataLst)) {
            return 0;
        }
        int total = 0;
        for (Integer data : dataLst) {
            total += data;
        }
        return total;
    }
    public int product(List<Integer> dataList) {
        int total = 1;
        if (Utility.listIsNotNullOrEmpty(dataList)) {
            for (Integer data : dataList) {
                total *=data;
            }
        }
        return total;
    }
}
```


  在被测试类中分别定义了两个方法，分别调用了Utility类里面的两个静态方法，下面我们通过对这两个方法进行测试，来介绍下使用Powermock对静态方法进行mock的各种用法。

  测试类如下(UtilityHelperTest.java)：

```
@RunWith(PowerMockRunner.class)
@PrepareForTest({Utility.class})
public class UtilityHelperTest {
    private UtilityHelper utilityHelper;
    private List<Integer> dataList;
    @Before
    public void setUp() {
        PowerMockito.mockStatic(Utility.class);
        dataList = new ArrayList<Integer>();
        dataList.add(1);
        dataList.add(2);
        dataList.add(3);
        utilityHelper = new UtilityHelper();
    }
    @Test
    public void testSum_1() {
        PowerMockito.when(Utility.listIsNullOrEmpty(Mockito.anyList())).thenReturn(true);
        int sum = utilityHelper.sum(dataList);
        Assert.assertEquals(0, sum);
        PowerMockito.verifyStatic(Mockito.times(1));
        Utility.listIsNullOrEmpty(Mockito.anyList());
    }
    @Test
    public void testSum_2() {
        PowerMockito.when(Utility.listIsNullOrEmpty(Mockito.anyList())).thenReturn(false);
        int sum = utilityHelper.sum(dataList);
        Assert.assertEquals(6, sum);
    }
    @Test
    public void testProduct_1() {
        int product = utilityHelper.product(dataList);
        Assert.assertEquals(1, product);
    }
    @Test
    public void testProduct_2() {
        PowerMockito.spy(Utility.class);
        int product = utilityHelper.product(dataList);
        Assert.assertEquals(6, product);
    }
    @Test
    public void testProduct_3() {
        PowerMockito.when(Utility.listIsNotNullOrEmpty(Mockito.anyList())).thenCallRealMethod();
        int product = utilityHelper.product(dataList);
        Assert.assertEquals(6, product);
    }
}
```


1. 如果想要对某个类的静态方法进行mock，则必须在PrepareForTest后面加上相应的类名, 比如此例的Utility.class。
2. 在对该类的某个方法进行mock之前，还必须先对整个类进行mock：

```
PowerMockito.mockStatic(Utility.class);
```


3. 在testSum\_1方法中，我们对listIsNullOrEmpty进行了mock：

```
PowerMockito.when(Utility.listIsNullOrEmpty(Mockito.anyList())).thenReturn(true);
```


可以看到虽然入参非空，但是由于返回值返回了true，使得调用sum方法返回的值是0。  
  另外，如果我们想要验证某静态方法是否被调用，或者被调用了几次，我们可以用如下方式验证：

```
PowerMockito.verifyStatic(Mockito.times(1));
Utility.listIsNullOrEmpty(Mockito.anyList());
```


  先使用verifyStatic方法表明要验证静态方法，可以带参数，也可以不带参数，其参数可以使用Mockito的times方法或never方法来表示其调用次数。下面紧跟着的一行则表示要验证的是哪个已经mock的静态方法。

4. 在test\_sum2方法中，由于我们mock的返回值为false，所以调用sum方法返回的是实际值。
5. 在test\_product1中，我们可以看到并没有对product中调用的listIsNotNullOrEmpty进行mock，那么为什么返回值是 ***1*** 呢？  
     这个主要是因为我们在setup方法中对使用mockStatic方法对Utility.class进行了mock，那么此时该类中的所有方法实际上都已经被mock了，如果没有对某个方法进行具体mock返回值，则调用该方法时，会直接返回对应返回类型的默认值，并不会执行真正的方法。此例对于listIsNotNullOrEmpty方法来说，其返回类型为boolean型，其默认值为false，所以product方法返回 ***1*** 。

  那么如果我们想对已经mock的类的某个方法调用真实的方法，而不是调用mock方法，那么该如何处理呢？此处我们介绍两种实现：

6. 在test\_product2中，我们看到相对test\_product1来说，多了一行：

```
PowerMockito.spy(Utility.class);
```


  加了上面一行后，虽然也没有对listIsNotNullOrEmpty进行mock，但此时返回值是真正的值，说明没有调用默认的mock方法。使用spy后，虽然已经对该类做了mockStatic处理，但此时该类中的所有方法仍然都会调用真实的方法，而不是默认的mock方法。这种用法主要适用于只想要对某个类的少量方法进行mock，其他方法仍然执行真正的方法，平常写时，可以紧跟在mockStatic方法后。

7. 我们在看下test\_product3中，该方法相对test\_product1中，多了一行：

```
PowerMockito.when(Utility.listIsNotNullOrEmpty(Mockito.anyList())).thenCallRealMethod();
```


  此行的含义就是调用到mock类的该方法执行真正的方法，而不是mock方法。这种方式就是需要对每个要执行的方法都要进行相应的mock处理。  
  上述两种方式，可以根据自己的需要进行选择使用哪一种。但是一定要记得，只要使用了mockStatic某类时，该类中的所有方法就已经都默认被mock了， 在调用该类的方法时，必须根据具体方法进行相应的处理。  
  另外，重要的事说三遍： **如果要mock静态方法，必须要在PrepareForTest后面加上该方法所在的类**。

---
> 参考链接：[https://www.cnblogs.com/duanxz/p/3552590.html](https://www.cnblogs.com/duanxz/p/3552590.html)
