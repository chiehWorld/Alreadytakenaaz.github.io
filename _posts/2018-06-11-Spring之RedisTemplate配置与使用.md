---
layout:     post
title:      Spring之RedisTemplate配置与使用
date:       2018-06-11
author:     Chieh
header-img: assets/180611-Spring之RedisTemplate配置与使用_header.png
catalog: true
tags:
    - Java
    - Spring
    - Redis
    - 技术
    - 转载
---

# Spring之RedisTemplate配置与使用

Spring针对Redis的使用，封装了一个比较强大的Template以方便使用；之前在Spring的生态圈中也使用过redis，但直接使用Jedis进行相应的交互操作，现在正好来看一下RedisTemplate是怎么实现的，以及使用起来是否更加便利

## I. 基本配置

### 1. 依赖

依然是采用Jedis进行连接池管理，因此除了引入 `spring-data-redis`之外，再加上jedis依赖，pom文件中添加

```
<dependency>
    <groupId>org.springframework.data</groupId>  
    <artifactId>spring-data-redis</artifactId>    
    <version>1.8.4.RELEASE</version>
</dependency>

<dependency>   
    <groupId>redis.clients</groupId>    
    <artifactId>jedis</artifactId>    
    <version>2.9.0</version>
</dependency>
```


如果需要指定序列化相关参数，也可以引入jackson，本篇为简单入门级，就不加这个了

### 2. 配置文件

准备redis相关的配置参数，常见的有host, port, password, timeout…，下面是一份简单的配置，并给出了相应的含义

```
redis.hostName=127.0.0.1
redis.port=6379
redis.password=https://blog.hhui.top
# 连接超时时间
redis.timeout=10000
# 最大空闲数
redis.maxIdle=300
# 用来替换上面的redis.maxActive, 如果是jedis 2.4以后用该属性
redis.maxTotal=1000
# 最大建立连接等待时间。如果超过此时间将接到异常。设为 -1 表示无限制。
redis.maxWaitMillis=1000
# 连接的最小空闲时间 默认1800000毫秒(30分钟)
redis.minEvictableIdleTimeMillis=300000
# 每次释放连接的最大数目,默认3
redis.numTestsPerEvictionRun=1024
# 逐出扫描的时间间隔(毫秒) 如果为负数,则不运行逐出线程, 默认-1
redis.timeBetweenEvictionRunsMillis=30000
# 是否在从池中取出连接前进行检验,如果检验失败,则从池中去除连接并尝试取出另一个
redis.testOnBorrow=true
# 在空闲时检查有效性, 默认false
redis.testWhileIdle=true
```


说明

* redis密码请一定记得设置，特别是在允许远程访问的时候，如果没有密码，默认端口号，很容易就被是扫描注入脚本，然后开始给人挖矿（亲身经历…）

## II. 使用与测试

根据一般的思路，首先是得加载上面的配置，创建redis连接池，然后再实例化RedisTemplate对象，最后持有这个实力开始各种读写操作

### 1. 配置类

使用JavaConfig的方式来配置，主要是两个Bean，读取配置文件设置各种参数的`RedisConnectionFactory`以及预期的`RedisTemplate`

```
@Configuration
@PropertySource("classpath:redis.properties")
public class RedisConfig extends JCacheConfigurerSupport {
    @Autowired
    private Environment environment;

    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        JedisConnectionFactory fac = new JedisConnectionFactory();
        fac.setHostName(environment.getProperty("redis.hostName"));
        fac.setPort(Integer.parseInt(environment.getProperty("redis.port")));
        fac.setPassword(environment.getProperty("redis.password"));
        fac.setTimeout(Integer.parseInt(environment.getProperty("redis.timeout")));
        fac.getPoolConfig().setMaxIdle(Integer.parseInt(environment.getProperty("redis.maxIdle")));
        fac.getPoolConfig().setMaxTotal(Integer.parseInt(environment.getProperty("redis.maxTotal")));
        fac.getPoolConfig().setMaxWaitMillis(Integer.parseInt(environment.getProperty("redis.maxWaitMillis")));
        fac.getPoolConfig().setMinEvictableIdleTimeMillis(
                Integer.parseInt(environment.getProperty("redis.minEvictableIdleTimeMillis")));
        fac.getPoolConfig()
                .setNumTestsPerEvictionRun(Integer.parseInt(environment.getProperty("redis.numTestsPerEvictionRun")));
        fac.getPoolConfig().setTimeBetweenEvictionRunsMillis(
                Integer.parseInt(environment.getProperty("redis.timeBetweenEvictionRunsMillis")));
        fac.getPoolConfig().setTestOnBorrow(Boolean.parseBoolean(environment.getProperty("redis.testOnBorrow")));
        fac.getPoolConfig().setTestWhileIdle(Boolean.parseBoolean(environment.getProperty("redis.testWhileIdle")));
        return fac;
    }

    @Bean
    public RedisTemplate<String, String> redisTemplate(RedisConnectionFactory redisConnectionFactory) {
        RedisTemplate<String, String> redis = new RedisTemplate<>();
        redis.setConnectionFactory(redisConnectionFactory);
        redis.afterPropertiesSet();
        return redis;
    }
}
```


### 2. 测试与使用

```
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = {RedisConfig.class})
public class RedisTest {

    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    @Test
    public void testRedisObj() {
        Map<String, Object> properties = new HashMap<>();
        properties.put("123", "hello");
        properties.put("abc", 456);
    
        redisTemplate.opsForHash().putAll("hash", properties);
    
        Map<Object, Object> ans = redisTemplate.opsForHash().entries("hash");
        System.out.println("ans: " + ans);
    }
}
```


执行后输出如下

```
ans: {123=hello, abc=456}

```


从上面的配置与实现来看，是很简单的了，基本上没有绕什么圈子，但是使用redis-cli连上去，却查询不到 `hash` 这个key的内容

```
127.0.0.1:6379> get hash
(nil)
127.0.0.1:6379> keys *
1) "\xac\xed\x00\x05t\x00\x04hash"
```

使用代码去查没问题，直接控制台连接，发现这个key和我们预期的不一样，多了一些前缀，why ?

### 3. 序列化问题

为了解决上面的问题，只能debug进去，看下是什么引起的了.

对应源码位置:

```
// org.springframework.data.redis.core.AbstractOperations#rawKey

byte[] rawKey(Object key) {
    Assert.notNull(key, "non null key required");
    return this.keySerializer() == null && key instanceof byte[] ? (byte[])((byte[])key) : this.keySerializer().serialize(key);
}

```

可以看到这个key不是我们预期的 `key.getBytes()`, 而是调用了`this.keySerializer().serialize(key)`，而debug的结果，默认Serializer是`JdkSerializationRedisSerializer`

![](assets/180611_SpringRedisTemplate01.jpg)

然后就是顺藤摸瓜一步一步深入进去，链路如下:

```
// org.springframework.core.serializer.support.SerializingConverter#convert

// org.springframework.core.serializer.DefaultSerializer#serialize

public class DefaultSerializer implements Serializer<Object> {
    public DefaultSerializer() {
    }

    public void serialize(Object object, OutputStream outputStream) throws IOException {
        if (!(object instanceof Serializable)) {
            throw new IllegalArgumentException(this.getClass().getSimpleName() + " requires a Serializable payload but received an object of type [" + object.getClass().getName() + "]");
        } else {
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(outputStream);
            objectOutputStream.writeObject(object);
            objectOutputStream.flush();
        }
    }
}
```


所以具体的实现很清晰了，就是 `ObjectOutputStream`,这个东西就是Java中最原始的序列化反序列流工具，会包含类型信息，所以会带上那串前缀了

所以要解决这个问题，也比较明确了，替换掉原生的`JdkSerializationRedisSerializer`,改为String的方式，正好提供了一个`StringRedisSerializer`,所以在RedisTemplate的配置处，稍稍修改

```
@Bean
public RedisTemplate<String, String> redisTemplate(RedisConnectionFactory redisConnectionFactory) {
    RedisTemplate<String, String> redis = new RedisTemplate<>();
    redis.setConnectionFactory(redisConnectionFactory);

    // 设置redis的String/Value的默认序列化方式
    StringRedisSerializer stringRedisSerializer = new StringRedisSerializer();
    redis.setKeySerializer(stringRedisSerializer);
    redis.setValueSerializer(stringRedisSerializer);
    redis.setHashKeySerializer(stringRedisSerializer);
    redis.setHashValueSerializer(stringRedisSerializer);

    redis.afterPropertiesSet();
    return redis;
}
```


再次执行，结果尴尬的事情出现了，抛异常了，类型转换失败

```
java.lang.ClassCastException: java.lang.Integer cannot be cast to java.lang.String

	at org.springframework.data.redis.serializer.StringRedisSerializer.serialize(StringRedisSerializer.java:33)
	at org.springframework.data.redis.core.AbstractOperations.rawHashValue(AbstractOperations.java:171)
	at org.springframework.data.redis.core.DefaultHashOperations.putAll(DefaultHashOperations.java:129)
	...
```


看前面的测试用例，map中的value有integer，而`StringRedisSerializer`接收的参数必须是String，所以不用这个，自己照样子重新写一个兼容掉

```
public class DefaultStrSerializer implements RedisSerializer<Object> {    

    private final Charset charset;

    public DefaultStrSerializer() {        
        this(Charset.forName("UTF8"));    
    }

    public DefaultStrSerializer(Charset charset) {        
        Assert.notNull(charset, "Charset must not be null!");        
        this.charset = charset;    
    }
       
    public byte[] serialize(Object o) throws SerializationException {        
        return o == null ? null : String.valueOf(o).getBytes(charset);    
    }
      
    public Object deserialize(byte[] bytes) throws SerializationException {        
        return bytes == null ? null : new String(bytes, charset);     
    }
}
```


然后可以开始愉快的玩耍了,执行完之后测试

```
keys *
1) "\xac\xed\x00\x05t\x00\x04hash"
2) "hash"
127.0.0.1:6379> hgetAll hash
1) "123"
2) "hello"
3) "abc"
4) "456"
```


## III. RedisTemplate使用姿势

### 1. opsForXXX

简单过来一下RedisTemplate的使用姿势，针对不同的数据结构(String, List, ZSet, Hash）读封装了比较使用的调用方式 `opsForXXX`

```
// hash 数据结构操作
org.springframework.data.redis.core.RedisTemplate#opsForHash

// list
org.springframework.data.redis.core.RedisTemplate#opsForList

// string
org.springframework.data.redis.core.RedisTemplate#opsForValue

// set
org.springframework.data.redis.core.RedisTemplate#opsForSet

// zset
org.springframework.data.redis.core.RedisTemplate#opsForZSet
```


### 2. execute

除了上面的这种使用方式之外，另外一种常见的就是直接使用execute了，一个简单的case如下

```
@Test
public void testRedis() {
    String key = "hello";
    String value = "world";
    redisTemplate.execute((RedisCallback<Void>) con -> {
        con.set(key.getBytes(), value.getBytes());
        return null;
    });

    String asn = redisTemplate.execute((RedisCallback<String>) con -> new String(con.get(key.getBytes())));
    System.out.println(asn);


    String hkey = "hKey";
    redisTemplate.execute((RedisCallback<Void>) con -> {
        con.hSet(hkey.getBytes(), "23".getBytes(), "what".getBytes());
        return null;
    });

    Map<byte[], byte[]> map = redisTemplate.execute((RedisCallback<Map<byte[], byte[]>>) con -> con.hGetAll(hkey.getBytes()));
    for (Map.Entry<byte[], byte[]> entry : map.entrySet()) {
        System.out.println("key: " + new String(entry.getKey()) + " | value: " + new String(entry.getValue()));
    }
}
```


输出结果如下

```
world
key: 23 | value: what

```


### 3. 区别

一个自然而然能想到的问题就是上面的两种方式有什么区别？

opsForXXX 的底层，就是通过调用execute方式来做的，其主要就是封装了一些使用姿势，定义了序列化，使用起来更加的简单和便捷；

---
> 参考链接：[https://liuyueyi.github.io/hexblog/2018/06/11/180611-Spring%E4%B9%8BRedisTemplate%E9%85%8D%E7%BD%AE%E4%B8%8E%E4%BD%BF%E7%94%A8/](https://liuyueyi.github.io/hexblog/2018/06/11/180611-Spring%E4%B9%8BRedisTemplate%E9%85%8D%E7%BD%AE%E4%B8%8E%E4%BD%BF%E7%94%A8/)
