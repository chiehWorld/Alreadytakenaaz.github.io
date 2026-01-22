---
layout:     post
title:      "spring boot:从yaml配置文件中读取数据的四种方式(spring boot 2.4.3)"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/spring-boot从yaml配置文件中读取数据的四种方式(spring-boot-2.4.3)_header.png
catalog: true
tags:
    - environment
    - java
    - Value
    - application.yml
    - Java
    - 配置文件
    - yaml
    - spring boot
    - spring
    - 技术
---

## 一，从配置文件中读取数据有哪些方法？

通常有3种用法：

1，直接使用value注解引用得到配置项的值

2,  封装到Component类中再调用:

     可以通过value注解或ConfigurationProperties注解两种方式访问

3,  用Environment类从代码中直接访问

生产环境中推荐使用第二种，用一个统一的文件来加载，

而不必写死到代码中，如果配置有变更时可以统一修改也更方便

说明：刘宏缔的架构森林是一个专注架构的博客，

网站：[https://blog.imgtouch.com](https://blog.imgtouch.com/)  
本文: <https://blog.imgtouch.com/index.php/2023/05/26/spring-boot-cong-yaml-pei-zhi-wen-jian-zhong-du-qu-shu-ju/>

         对应的源码可以访问这里获取： <https://github.com/liuhongdi/>

说明：作者:刘宏缔 邮箱: 371125307@qq.com

## 二，演示项目的相关信息

1,地址:

https://github.com/liuhongdi/yaml

2,功能说明：演示了从yaml配置文件读取数据的方法

3,项目结构：如图:

![](assets/spring-boot从yaml配置文件中读取数据的四种方式(spring-boot-2.4.3)_img_1.png)

## 三，配置文件说明

1,application.yml

```
#server
server:
  port: 8081
  error:
    include-stacktrace: always
#profile
spring:
  profiles:
    active: prd
```


2,application-dev.yml

```
#images
app:
  goods:
    imagesUrlHost: http://127.0.0.1:81/goods
    imagesOrigDir: /data/file/html/goods/images
    imagesTmbDir: /data/file/html/goods/tmb
    extendNames:
      - jpg
      - gif
      - png
      - webp
    extendNames2: jpg,gif,png
```


3,application-prd.yml

```
#images
app:
  goods:
    imagesUrlHost: http://file.lhdtest.com/goods
    imagesOrigDir: /data/estore/file/html/goods/images
    imagesTmbDir: /data/estore/file/html/goods/tmb
    extendNames:
        - jpg
        - gif
        - png
        - webp
    extendNames2: jpg,gif,png
```


## 四，java代码

1,constant/ConfigValue.java

```
package com.yaml.demo.constant;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
/*
 * 从配置文件中读取的变量
 *  lhd
 *  2020.10.15
 * */
@Component
public class ConfigValue {
    //imagesUrlHost
    @Value("${app.goods.imagesUrlHost}")
    public String imagesUrlHost;
    //imagesOrigDir
    @Value("${app.goods.imagesOrigDir}")
    public String imagesOrigDir;
    //imagesTmbDir
    @Value("${app.goods.imagesTmbDir}")
    public String imagesTmbDir;
    @Value("${app.goods.extendNames2}")
    public String[] extendNames2;
}
```


2,constant/ConfigProperties.java

```
package com.yaml.demo.constant;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import java.util.List;
/*
 * 从配置文件中读取的变量
 *  lhd
 *  2020.10.15
 * */
@Component
@ConfigurationProperties(prefix = "app.goods")
public class ConfigProperties {
    private String imagesUrlHost;
    public String getImagesUrlHost() {
        return this.imagesUrlHost;
    }
    public void setImagesUrlHost(String imagesUrlHost) {
        this.imagesUrlHost = imagesUrlHost;
    }
    private List<String> extendNames;
    public List<String> getExtendNames() {
        return this.extendNames;
    }
    public void setExtendNames(List<String> extendNames) {
        this.extendNames = extendNames;
    }
}
```


3,controller/HomeController.java

```
@Controller
@RequestMapping("/home")
public class HomeController {
    @Resource
    private ConfigValue configValue;
    @Resource
    private ConfigProperties configProperties;
    @Resource
    private Environment environment;
    //从配置文件读取变量imagesUrlHost
    @Value("${app.goods.imagesUrlHost}")
    private String imagesUrlHost;
    //四种方式打印从配置文件中读取到的变量值
    @GetMapping("/home")
    @ResponseBody
    public String home() {
        String res = "第一种方法:直接用value引用:"+imagesUrlHost+":<br/>";
        res += "第二种方法:封装到Component类中,Value注解:"+configValue.imagesUrlHost+":<br/>";
        res += "第三种方法:封装到Component类中,ConfigurationProperties注解:"+configProperties.getImagesUrlHost()+":<br/>";
        res += "第四种方法:environment:"+environment.getProperty("app.goods.imagesUrlHost")+":<br/>";
        System.out.println("图片类型:extendNames:");
        List<String> list = configProperties.getExtendNames();
        for (int i = 0; i <list.size(); i++) {
            String s = (String)list.get(i);
            System.out.println(i+":"+s);
        }
        System.out.println("图片类型2:extendNames2:");
        for (int i = 0; i <configValue.extendNames2.length; i++){
            System.out.println(i+":"+configValue.extendNames2[i]);
        }
        return res;
    }
}
```


## 五，测试效果

1,访问:

```
http://127.0.0.1:8081/home/home
```


返回:

![](assets/spring-boot从yaml配置文件中读取数据的四种方式(spring-boot-2.4.3)_img_2.png)

 查看控制台:

![](assets/spring-boot从yaml配置文件中读取数据的四种方式(spring-boot-2.4.3)_img_3.png)

## 六，查看spring boot版本

```
.   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.4.3)
```

---
> 参考链接：[https://www.cnblogs.com/architectforest/p/14441490.html](https://www.cnblogs.com/architectforest/p/14441490.html)
