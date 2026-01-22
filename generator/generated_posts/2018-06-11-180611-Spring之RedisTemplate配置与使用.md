---
layout:     post
title:      "180611-Spring之RedisTemplate配置与使用"
subtitle:   "归档于：技术"
date:       2018-06-11
author:     Chieh
header-img: assets/180611-Spring之RedisTemplate配置与使用_header.png
catalog: true
tags:
    - MD5 1
    - CURL
    - Android 4
    - Redis 9
    - BloomFilter
    - 编程技巧 15
    - ProtoStuff
    - WebView 2
    - Spring
    - ImageMagic
    - hexo
    - Backend
    - Mysql
    - MongoDb
    - 工具
    - 二维码
    - FastJson 1
    - jdk
    - 爬虫
    - 爬虫 5
    - python 2
    - zsh 1
    - Grafana 3
    - ReactJS
    - 技术方案 22
    - MongoDB
    - HashMap 1
    - Map 1
    - ssh
    - BufferedImage
    - LRU 1
    - Gson 5
    - Solr 1
    - Socket
    - 问题记录
    - Email 1
    - RabbitMQ
    - 反射
    - named 1
    - ssh 1
    - Yaml 1
    - Node
    - RMI 3
    - OGNL
    - 内购
    - IDEA
    - MongoDb 10
    - MD5
    - InputStream 1
    - QuickAlarm
    - 乱码
    - Json
    - google 1
    - Mysql 21
    - ssl 1
    - 并发 3
    - google
    - ffmpeg
    - JavaWeb 2
    - Jackson
    - LRU
    - dns
    - GitHub
    - 技术
    - 代理 1
    - CURL 2
    - 随笔 1
    - tmux
    - 手记 6
    - Android
    - Yaml
    - 专业词汇
    - hostname
    - ReactJS 1
    - Email
    - 子系统
    - FastJson
    - SSL 1
    - DNS 1
    - JVM 3
    - WebView
    - Arthas 1
    - jdk 1
    - Prometheus
    - 并发
    - Guava
    - SpringBoot 2
    - Mybatis 2
    - 方案设计 1
    - 问题记录 1
    - git 2
    - Java
    - 随笔
    - Redis
    - grep
    - JDK 36
    - gitalk
    - 手记
    - 证书
    - Linux 11
    - Chrome 2
    - BeanUtil 2
    - IO 2
    - MongoDB 4
    - time 1
    - Win10 2
    - Jquery
    - InputStream
    - GitHub 1
    - Jquery 1
    - gitalk 1
    - JavaAgent 2
    - AutoCloseable 1
    - Shell
    - 内购 1
    - InfluxDB
    - IO
    - JVM
    - logger
    - ElasticSearch
    - 技术方案
    - JavaScript
    - InfluxDB 17
    - 子系统 1
    - Mongo 2
    - named
    - Chrome
    - 吐槽
    - git
    - Win10
    - Spring 26
    - Shell 21
    - 二维码 3
    - 代理
    - Jackson 1
    - ncat 1
    - JNDI
    - Iterator 1
    - OGNL 4
    - QuickMedia 3
    - Map
    - AES 1
    - logger 1
    - QlExpress
    - Bugfix 2
    - 乱码 1
    - AutoCloseable
    - Guava 5
    - time
    - 时间窗口
    - Bugfix
    - ncat
    - markdown 1
    - 工具 5
    - 指南
    - Groovy
    - MySql
    - 序列化
    - Mybatis
    - 方案设计
    - Socket 2
    - 教程
    - JavaScript 2
    - Linux
    - WebSocket
    - curl 1
    - SpringBoot
    - ImageMagic 2
    - Grafana
    - curl
    - Json 1
    - Python
    - Dubbo 1
    - grep 1
    - 分库分表 1
    - 序列化 1
    - ElasticSearch 7
    - Vue 1
    - Vue
    - Git 3
    - 指南 6
    - DNS
    - AES
    - WebSocket 1
    - 时区
    - Docker 5
    - ZooKeeper
    - 时区 1
    - Maven
    - BloomFilter 1
    - List 1
    - RabbitMQ 9
    - css
    - 教程 21
    - IDEA 4
    - BugFix
    - 吐槽 1
    - QuickAlarm 1
    - tmux 2
    - Python 142
    - Docker
    - markdown
    - 分库分表
    - css 3
    - Mongo
    - dns 1
    - Node 1
    - JavaWeb
    - Prometheus 1
    - Git
    - JNDI 3
    - SSL
    - 编程技巧
    - Arthas
    - Dubbo
    - 时间窗口 3
    - List
    - Iterator
    - python
    - Nginx 7
    - 反射 3
    - JDK
    - zsh
    - Solr
    - 专业词汇 1
    - RMI
    - hexo 1
    - Nginx
    - QuickMedia
    - BugFix 2
    - BufferedImage 2
    - QlExpress 4
    - JavaAgent
    - Groovy 1
    - Java 75
    - BeanUtil
    - HashMap
    - MySql 3
    - ffmpeg 1
    - Maven 4
    - ProtoStuff 2
    - hostname 1
    - 证书 1
    - ZooKeeper 1
    - Gson
    - ssl
---

# Spring之RedisTemplate配置与使用

Spring针对Redis的使用，封装了一个比较强大的Template以方便使用；之前在Spring的生态圈中也使用过redis，但直接使用Jedis进行相应的交互操作，现在正好来看一下RedisTemplate是怎么实现的，以及使用起来是否更加便利

## I. 基本配置

### 1. 依赖

依然是采用Jedis进行连接池管理，因此除了引入 `spring-data-redis`之外，再加上jedis依赖，pom文件中添加

```
<dependency>\n    
<groupId>org.springframework.data</
groupId>\n    
<artifactId>spring-data-redis</
artifactId>\n    
<version>1.8.4.RELEASE</
version>\n
</
dependency>\n \n
<dependency>\n    
<groupId>redis.clients</
groupId>\n    
<artifactId>jedis</
artifactId>\n    
<version>2.9.0</
version>\n
</
dependency>\n
```


如果需要指定序列化相关参数，也可以引入jackson，本篇为简单入门级，就不加这个了

### 2. 配置文件

准备redis相关的配置参数，常见的有host, port, password, timeout…，下面是一份简单的配置，并给出了相应的含义

```
redis.hostName=127.0.0.1
\nredis.port=6379
\nredis.password=https://blog.hhui.top
\n# 连接超时时间
\nredis.timeout=10000
\n \n#最大空闲数
\nredis.maxIdle=300
\n#控制一个pool可分配多少个jedis实例,用来替换上面的redis.maxActive,如果是jedis 2.4以后用该属性
\nredis.maxTotal=1000
\n#最大建立连接等待时间。如果超过此时间将接到异常。设为-1表示无限制。
\nredis.maxWaitMillis=1000
\n#连接的最小空闲时间 默认1800000毫秒(30分钟)
\nredis.minEvictableIdleTimeMillis=300000
\n#每次释放连接的最大数目,默认3
\nredis.numTestsPerEvictionRun=1024
\n#逐出扫描的时间间隔(毫秒) 如果为负数,则不运行逐出线程, 默认-1
\nredis.timeBetweenEvictionRunsMillis=30000
\n#是否在从池中取出连接前进行检验,如果检验失败,则从池中去除连接并尝试取出另一个
\nredis.testOnBorrow=true
\n#在空闲时检查有效性, 默认false
\nredis.testWhileIdle=true
\n
```


说明

* redis密码请一定记得设置，特别是在允许远程访问的时候，如果没有密码，默认端口号，很容易就被是扫描注入脚本，然后开始给人挖矿（亲身经历…）

## II. 使用与测试

根据一般的思路，首先是得加载上面的配置，创建redis连接池，然后再实例化RedisTemplate对象，最后持有这个实力开始各种读写操作

### 1. 配置类

使用JavaConfig的方式来配置，主要是两个Bean，读取配置文件设置各种参数的`RedisConnectionFactory`以及预期的`RedisTemplate`

```
\n (
"classpath:redis.properties"
)\n
public
class
 RedisConfig
 extends
 JCacheConfigurerSupport
 {\n \n    
private
 Environment environment;\n \n \n    
public
 RedisConnectionFactory redisConnectionFactory
()
 {\n        JedisConnectionFactory fac = 
new
 JedisConnectionFactory();\n        fac.setHostName(environment.getProperty(
"redis.hostName"
));\n        fac.setPort(Integer.parseInt(environment.getProperty(
"redis.port"
)));\n        fac.setPassword(environment.getProperty(
"redis.password"
));\n        fac.setTimeout(Integer.parseInt(environment.getProperty(
"redis.timeout"
)));\n        fac.getPoolConfig().setMaxIdle(Integer.parseInt(environment.getProperty(
"redis.maxIdle"
)));\n        fac.getPoolConfig().setMaxTotal(Integer.parseInt(environment.getProperty(
"redis.maxTotal"
)));\n        fac.getPoolConfig().setMaxWaitMillis(Integer.parseInt(environment.getProperty(
"redis.maxWaitMillis"
)));\n        fac.getPoolConfig().setMinEvictableIdleTimeMillis(
\n                Integer.parseInt(environment.getProperty(
"redis.minEvictableIdleTimeMillis"
)));\n        fac.getPoolConfig()
\n                .setNumTestsPerEvictionRun(Integer.parseInt(environment.getProperty(
"redis.numTestsPerEvictionRun"
)));\n        fac.getPoolConfig().setTimeBetweenEvictionRunsMillis(
\n                Integer.parseInt(environment.getProperty(
"redis.timeBetweenEvictionRunsMillis"
)));\n        fac.getPoolConfig().setTestOnBorrow(Boolean.parseBoolean(environment.getProperty(
"redis.testOnBorrow"
)));\n        fac.getPoolConfig().setTestWhileIdle(Boolean.parseBoolean(environment.getProperty(
"redis.testWhileIdle"
)));\n        
return
 fac;\n    }
\n \n \n    
public
 RedisTemplate<String, String> redisTemplate
(RedisConnectionFactory redisConnectionFactory)
 {\n        RedisTemplate<String, String> redis = 
new
 RedisTemplate<>();\n        redis.setConnectionFactory(redisConnectionFactory);
\n        redis.afterPropertiesSet();
\n        
return
 redis;\n    }
\n}
\n
```


### 2. 测试与使用

```
(SpringJUnit4ClassRunner
.
class
)\n
@
ContextConfiguration
(classes
 = {RedisConfig.
class
})\n
public
 class
 RedisTest
 {\n \n \n    
private
 RedisTemplate<String, String> redisTemplate;\n \n \n    
public
 void
 testRedisObj
()
 {\n        Map<String, Object> properties = 
new
 HashMap<>();\n        properties.put(
"123"
, "hello"
);\n        properties.put(
"abc"
, 456
);\n \n        redisTemplate.opsForHash().putAll(
"hash"
, properties);\n \n        Map<Object, Object> ans = redisTemplate.opsForHash().entries(
"hash"
);\n        System.out.println(
"ans: "
 + ans);\n    }
\n}
\n
```


执行后输出如下

```
ans: {123=hello, abc=456}
\n
```


从上面的配置与实现来看，是很简单的了，基本上没有绕什么圈子，但是使用redis-cli连上去，却查询不到 `hash` 这个key的内容

```
127.0.0.1:6379> get 
hash
\n(nil)
\n127.0.0.1:6379> keys *
\n1) 
"\xac\xed\x00\x05t\x00\x04hash"
\n
```


使用代码去查没问题，直接控制台连接，发现这个key和我们预期的不一样，多了一些前缀，why ?

### 3. 序列化问题

为了解决上面的问题，只能debug进去，看下是什么引起的了

对应源码位置:

```
\n \n
byte
[] rawKey(Object key) {\n    Assert.notNull(key, 
"non null key required"
);\n    
return
 this
.keySerializer() == null
 && key instanceof
 byte
[] ? (byte
[])((byte
[])key) : this
.keySerializer().serialize(key);\n}
\n
```


可以看到这个key不是我们预期的 `key.getBytes()`, 而是调用了`this.keySerializer().serialize(key)`，而debug的结果，默认Serializer是`JdkSerializationRedisSerializer`

然后就是顺藤摸瓜一步一步深入进去，链路如下

```
// org.springframework.core.serializer.support.SerializingConverter
\n \n// org.springframework.core.serializer.DefaultSerializer
\n \npublic class DefaultSerializer implements Serializer<Object> {
\n    public 
DefaultSerializer
() {\n    }
\n \n    public void serialize(Object object, OutputStream outputStream) throws IOException {
\n        
if
 (!(object instanceof Serializable)) {\n            throw new IllegalArgumentException(this.getClass().getSimpleName() + 
" requires a Serializable payload but received an object of type ["
 + object.getClass().getName() + "]"
);\n        } 
else
 {\n            ObjectOutputStream objectOutputStream = new ObjectOutputStream(outputStream);
\n            objectOutputStream.writeObject(object);
\n            objectOutputStream.flush();
\n        }
\n    }
\n}
\n
```


所以具体的实现很清晰了，就是 `ObjectOutputStream`,这个东西就是Java中最原始的序列化反序列流工具，会包含类型信息，所以会带上那串前缀了

所以要解决这个问题，也比较明确了，替换掉原生的`JdkSerializationRedisSerializer`,改为String的方式，正好提供了一个`StringRedisSerializer`,所以在RedisTemplate的配置处，稍稍修改

```
\n
public
 RedisTemplate<String, String> redisTemplate
(RedisConnectionFactory redisConnectionFactory)
 {\n    RedisTemplate<String, String> redis = 
new
 RedisTemplate<>();\n    redis.setConnectionFactory(redisConnectionFactory);
\n \n \n    StringRedisSerializer stringRedisSerializer = 
new
 StringRedisSerializer();\n    redis.setKeySerializer(stringRedisSerializer);
\n    redis.setValueSerializer(stringRedisSerializer);
\n    redis.setHashKeySerializer(stringRedisSerializer);
\n    redis.setHashValueSerializer(stringRedisSerializer);
\n \n    redis.afterPropertiesSet();
\n    
return
 redis;\n}
\n
```


再次执行，结果尴尬的事情出现了，抛异常了，类型转换失败

```
java.lang.ClassCastException: java.lang.Integer cannot be cast to java.lang.String
\n \n	at org.springframework.data.redis.serializer.StringRedisSerializer.serialize(StringRedisSerializer.java:33)
\n	at org.springframework.data.redis.core.AbstractOperations.rawHashValue(AbstractOperations.java:171)
\n	at org.springframework.data.redis.core.DefaultHashOperations.putAll(DefaultHashOperations.java:129)
\n	...
\n
```


看前面的测试用例，map中的value有integer，而`StringRedisSerializer`接收的参数必须是String，所以不用这个，自己照样子重新写一个兼容掉

```
public
class
 DefaultStrSerializer
 implements
 RedisSerializer
<Object> {\n    
private
 final
 Charset charset;\n \n    
public
 DefaultStrSerializer
()
 {\n        
this
(Charset.forName("UTF8"
));\n    }
\n \n    
public
 DefaultStrSerializer
(Charset charset)
 {\n        Assert.notNull(charset, 
"Charset must not be null!"
);\n        
this
.charset = charset;\n    }
\n \n \n \n    
public
 byte
[] serialize(Object o) throws
 SerializationException {\n        
return
 o == null
 ? null
 : String.valueOf(o).getBytes(charset);\n    }
\n \n \n    
public
 Object deserialize
(
byte
[] bytes) throws
 SerializationException {\n        
return
 bytes == null
 ? null
 : new
 String(bytes, charset);\n \n    }
\n}
\n
```


然后可以开始愉快的玩耍了,执行完之后测试

```
keys *
\n1) 
"\xac\xed\x00\x05t\x00\x04hash"
\n2) 
"hash"
\n127.0.0.1:6379> hgetAll 
hash
\n1) 
"123"
\n2) 
"hello"
\n3) 
"abc"
\n4) 
"456"
\n
```


## III. RedisTemplate使用姿势

### 1. opsForXXX

简单过来一下RedisTemplate的使用姿势，针对不同的数据结构(String, List, ZSet, Hash）读封装了比较使用的调用方式 `opsForXXX`

```
\norg.springframework.data.redis.core.RedisTemplate#opsForHash
\n \n \norg.springframework.data.redis.core.RedisTemplate#opsForList
\n \n \norg.springframework.data.redis.core.RedisTemplate#opsForValue
\n \n \norg.springframework.data.redis.core.RedisTemplate#opsForSet
\n \n \norg.springframework.data.redis.core.RedisTemplate#opsForZSet
\n
```


### 2. execute

除了上面的这种使用方式之外，另外一种常见的就是直接使用execute了，一个简单的case如下

```
\n
public
 void
 testRedis
()
 {\n    String key = 
"hello"
;\n    String value = 
"world"
;\n    redisTemplate.execute((RedisCallback<Void>) con -> {
\n        con.set(key.getBytes(), value.getBytes());
\n        
return
 null
;\n    });
\n \n    String asn = redisTemplate.execute((RedisCallback<String>) con -> 
new
 String(con.get(key.getBytes())));\n    System.out.println(asn);
\n \n \n    String hkey = 
"hKey"
;\n    redisTemplate.execute((RedisCallback<Void>) con -> {
\n        con.hSet(hkey.getBytes(), 
"23"
.getBytes(), "what"
.getBytes());\n        
return
 null
;\n    });
\n \n    Map<byte
[], byte
[]> map = redisTemplate.execute((RedisCallback<Map<byte
[], byte
[]>>) con -> con.hGetAll(hkey.getBytes()));\n    
for
 (Map.Entry<byte
[], byte
[]> entry : map.entrySet()) {\n        System.out.println(
"key: "
 + new
 String(entry.getKey()) + " | value: "
 + new
 String(entry.getValue()));\n    }
\n}
\n
```


输出结果如下

```
world
\nkey: 23 | value: what
\n
```


### 3. 区别

一个自然而然能想到的问题就是上面的两种方式有什么区别？

opsForXXX 的底层，就是通过调用execute方式来做的，其主要就是封装了一些使用姿势，定义了序列化，使用起来更加的简单和便捷；

## IV. 其他

### 0. 项目

一灰灰的个人博客，记录所有学习和工作中的博文，欢迎大家前去逛逛

### 2. 声明

尽信书则不如，已上内容，纯属一家之言，因个人能力有限，难免有疏漏和错误之处，如发现bug或者有更好的建议，欢迎批评指正，不吝感激

### 3. 扫描关注

---
> 参考链接：[https://liuyueyi.github.io/hexblog/2018/06/11/180611-Spring%E4%B9%8BRedisTemplate%E9%85%8D%E7%BD%AE%E4%B8%8E%E4%BD%BF%E7%94%A8/](https://liuyueyi.github.io/hexblog/2018/06/11/180611-Spring%E4%B9%8BRedisTemplate%E9%85%8D%E7%BD%AE%E4%B8%8E%E4%BD%BF%E7%94%A8/)
