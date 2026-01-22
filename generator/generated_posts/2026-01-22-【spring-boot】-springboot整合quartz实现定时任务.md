---
layout:     post
title:      "【spring-boot】 springboot整合quartz实现定时任务"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/【spring-boot】-springboot整合quartz实现定时任务_header.jpg
catalog: true
tags:
    - Java
    - spring-boot
    - 技术
---

在做项目时有时候会有定时器任务的功能，比如某某时间应该做什么，多少秒应该怎么样之类的。

spring支持多种定时任务的实现。我们来介绍下使用spring的定时器和使用quartz定时器

　　1.我们使用spring-boot作为基础框架，其理念为零配置文件，所有的配置都是基于注解和暴露bean的方式。

　　2.使用spring的定时器:

　　　　spring自带支持定时器的任务实现。其可通过简单配置来使用到简单的定时任务。

```
@Component
@Configurable
@EnableScheduling
public class ScheduledTasks{
    @Scheduled(fixedRate = 1000 * 30)
    public void reportCurrentTime(){
        System.out.println ("Scheduling Tasks Examples: The time is now " + dateFormat ().format (new Date ()));
    }
    //每1分钟执行一次
    @Scheduled(cron = "0 */1 *  * * * ")
    public void reportCurrentByCron(){
        System.out.println ("Scheduling Tasks Examples By Cron: The time is now " + dateFormat ().format (new Date ()));
    }
    private SimpleDateFormat dateFormat(){
        return new SimpleDateFormat ("HH:mm:ss");
    }
}
```


          没了，没错，使用spring的定时任务就这么简单，其中有几个比较重要的注解：

@EnableScheduling：标注启动定时任务。

          @Scheduled(fixedRate = 1000 \* 30)  定义某个定时任务。

　　3.使用quartz实现定时任务。  
　　　　Quartz设计者做了一个设计选择来从调度分离开作业。Quartz中的触发器用来告诉调度程序作业什么时候触发。框架提供了一把触发器类型，但两个最常用的是SimpleTrigger和CronTrigger。SimpleTrigger为需要简单打火调度而设计。典型地，如果你需要在给定的时间和重复次数或者两次打火之间等待的秒数打火一个作业，那么SimpleTrigger适合你。另一方面，如果你有许多复杂的作业调度，那么或许需要CronTrigger。  
　　　　CronTrigger是基于Calendar-like调度的。当你需要在除星期六和星期天外的每天上午10点半执行作业时，那么应该使用CronTrigger。正如它的名字所暗示的那样，CronTrigger是基于Unix克隆表达式的。

　　　　使用quartz说使用的maven依赖。

```
<dependency>
    <groupId>org.quartz-scheduler</groupId>
    <artifactId>quartz</artifactId>
    <version>1.8.4</version>
</dependency>
```


　　　　由于我们使用的是spring-boot框架，其目的是做到零配置文件，所以我们不使用xml文件的配置文件来定义一个定时器，而是使用向spring容器暴露bean的方式。

　　　　向spring容器暴露所必须的bean

```
@Configuration
public class SchedledConfiguration {
    // 配置中设定了
    // ① targetMethod: 指定需要定时执行scheduleInfoAction中的simpleJobTest()方法
    // ② concurrent：对于相同的JobDetail，当指定多个Trigger时, 很可能第一个job完成之前，
    // 第二个job就开始了。指定concurrent设为false，多个job不会并发运行，第二个job将不会在第一个job完成之前开始。
    // ③ cronExpression：0/10 * * * * ?表示每10秒执行一次，具体可参考附表。
    // ④ triggers：通过再添加其他的ref元素可在list中放置多个触发器。 scheduleInfoAction中的simpleJobTest()方法
    @Bean(name = "detailFactoryBean")
    public MethodInvokingJobDetailFactoryBean detailFactoryBean(ScheduledTasks scheduledTasks){
        MethodInvokingJobDetailFactoryBean bean = new MethodInvokingJobDetailFactoryBean ();
        bean.setTargetObject (scheduledTasks);
        bean.setTargetMethod ("reportCurrentByCron");
        bean.setConcurrent (false);
        return bean;
    }
    @Bean(name = "cronTriggerBean")
    public CronTriggerBean cronTriggerBean(MethodInvokingJobDetailFactoryBean detailFactoryBean){
        CronTriggerBean tigger = new CronTriggerBean ();
        tigger.setJobDetail (detailFactoryBean.getObject ());
        try {
            tigger.setCronExpression ("0/5 * * * * ? ");//每5秒执行一次
        } catch (ParseException e) {
            e.printStackTrace ();
        }
        return tigger;
    }
    @Bean
    public SchedulerFactoryBean schedulerFactory(CronTriggerBean[] cronTriggerBean){
        SchedulerFactoryBean bean = new SchedulerFactoryBean ();
        System.err.println (cronTriggerBean[0]);
        bean.setTriggers (cronTriggerBean);
        return bean;
    }
}
```


MethodInvokingJobDetailFactoryBean：此工厂主要用来制作一个jobDetail，即制作一个任务。由于我们所做的定时任务根本上讲其实就是执行一个方法。所以用这个工厂比较方便。

　　　　　　注意：其setTargetObject所设置的是一个对象而不是一个类。

CronTriggerBean：定义一个触发器。

　　　　　　注意：setCronExpression：是一个表达式，如果此表达式不合规范，即会抛出异常。

SchedulerFactoryBean：主要的管理的工厂，这是最主要的一个bean。quartz通过这个工厂来进行对各触发器的管理。

　　4.对quartz的封装

　　　　由上面代码可以看出来，此处我们设置的是一个固定的cronExpression，那么，做为项目中使用的话，我们一般是需要其动态设置比如从数据库中取出来。

　　　　其实做法也很简单，我们只需要定义一个Trigger来继承CronTriggerBean。顶用其setCronExpression方法即可。

　　　　那么另外一个问题，如果我们要定义两个定时任务则会比较麻烦，需要先注入一个任务工厂，在注入一个触发器。

　　　    为了减少这样的配置，我们定义了一个抽象的超类来继承CronTriggerBean。

　　　　具体代码如下：

```
public abstract class BaseCronTrigger extends CronTriggerBean implements Serializable {
    private static final long serialVersionUID = 1L;
    public void init(){
        // 得到任务
        JobDetail jobdetail = new JobDetail (this.getClass ().getSimpleName (),this.getMyTargetObject ().getClass ());
        this.setJobDetail (jobdetail);
        this.setJobName (jobdetail.getName ());
        this.setName (this.getClass ().getSimpleName ());
        try {
            this.setCronExpression (this.getMyCronExpression ());
        } catch (java.text.ParseException e) {
            e.printStackTrace ();
        }
    }
    public abstract String getMyCronExpression();
    public abstract Job getMyTargetObject();
}
```


　　　　其init()方法，来为这个触发器绑定任务。其任务为一个Job类型的，也就是说其执行的任务为实现了Job接口的类，这个任务会有一个execute()方法，来执行任务题。

```
public class ScheduledTasks implements Job {
    @Override
    public void execute(JobExecutionContext context) throws JobExecutionException{
        System.out.println ("Scheduling Tasks Examples By Cron: The time is now " + dateFormat ().format (new Date ()));
    }
   private SimpleDateFormat dateFormat(){
        return new SimpleDateFormat ("HH:mm:ss");
    }
}
```


　　　　为了给触发器添加任务，我们需要在子类中调用init()方法，由于spring容器注入时是使用的空参的构造函数，所以我们在此构造函数中调用init（）方法。

```
@Component
public class InitializingCronTrigger extends BaseCronTrigger implements Serializable {
    private static final long    serialVersionUID = 1L;
    @Autowired
    private SchedulerFactoryBean schedulerFactoryBean;
    public InitializingCronTrigger() {
        init ();
    }
    @Override
    public String getMyCronExpression(){
        return "0/5 * * * * ?";
    }
    @Override
    public Job getMyTargetObject(){
        return new ScheduledTasks ();
    }
    public void parse(){
        try {
            schedulerFactoryBean.getObject ().pauseAll ();
        } catch (SchedulerException e) {
            e.printStackTrace ();
        }
    }
}
```


　　　　此时我们只需要在配置类中加入一个配置就可以了。

```
@Bean
  public SchedulerFactoryBean schedulerFactory(CronTriggerBean[] cronTriggerBean){
      SchedulerFactoryBean bean = new SchedulerFactoryBean ();
      System.err.println (cronTriggerBean[0]);
      bean.setTriggers (cronTriggerBean);
      return bean;
  }
```


　　4.介绍一个cronExpression表达式。

　　　　这一部分是摘抄的：

> | 字段 |  | 允许值 |  | 允许的特殊字符 |
> | --- | --- | --- | --- | --- |
> | `秒` |  | `0-59` |  | `, - * /` |
> | `分` |  | `0-59` |  | `, - * /` |
> | `小时` |  | `0-23` |  | `, - * /` |
> | `日期` |  | `1-31` |  | `, - *   / L W C` |
> | `月份` |  | `1-12 或者 JAN-DEC` |  | `, - * /` |
> | `星期` |  | `1-7 或者 SUN-SAT` |  | `, - *   / L C #` |
> | `年（可选）` |  | `留空, 1970-2099` |  | `, - * /` |
>
> 如上面的表达式所示:   
>   
> “\*”字符被用来指定所有的值。如：”\*“在分钟的字段域里表示“每分钟”。   
>   
> “-”字符被用来指定一个范围。如：“10-12”在小时域意味着“10点、11点、12点”。  
>    
> “,”字符被用来指定另外的值。如：“MON,WED,FRI”在星期域里表示”星期一、星期三、星期五”.   
>   
> “?”字符只在日期域和星期域中使用。它被用来指定“非明确的值”。当你需要通过在这两个域中的一个来指定一些东西的时候，它是有用的。看下面的例子你就会明白。   
>   
>   
> “L”字符指定在月或者星期中的某天（最后一天）。即“Last ”的缩写。但是在星期和月中“Ｌ”表示不同的意思，如：在月子段中“L”指月份的最后一天-1月31日，2月28日，如果在星期字段中则简单的表示为“7”或者“SAT”。如果在星期字段中在某个value值得后面，则表示“某月的最后一个星期value”,如“6L”表示某月的最后一个星期五。  
>   
> “W”字符只能用在月份字段中，该字段指定了离指定日期最近的那个星期日。  
>   
> “#”字符只能用在星期字段，该字段指定了第几个星期value在某月中
>
> 每一个元素都可以显式地规定一个值（如6），一个区间（如9-12），一个列表（如9，11，13）或一个通配符（如\*）。“月份中的日期”和“星期中的日期”这两个元素是互斥的，因此应该通过设置一个问号（？）来表明你不想设置的那个字段。表7.1中显示了一些cron表达式的例子和它们的意义：
>
> | 表达式 |  | 意义 |
> | --- | --- | --- |
> | `"0 0 12 * * ?"` |  | `每天中午12点触发` |
> | `"0 15 10 ? * *"` |  | `每天上午10:15触发` |
> | `"0 15 10 * * ?"` |  | `每天上午10:15触发` |
> | `"0 15 10 * * ? *"` |  | `每天上午10:15触发` |
> | `"0 15 10 * * ? 2005"` |  | `2005年的每天上午10:15`触发 |
> | `"0 * 14 * * ?"` |  | `在每天下午2点到下午2:59期间的每1分钟触发` |
> | `"0 0/5 14 * * ?"` |  | `在每天下午2点到下午2:55期间的每5分钟触发` |
> | `"0 0/5 14,18 * * ?"` |  | `在每天下午2点到2:55期间和下午6点到6:55期间的每5分钟触发` |
> | `"0 0-5 14 * * ?"` |  | `在每天下午2点到下午2:05期间的每1分钟触发` |
> | `"0 10,44 14 ? 3 WED"` |  | `每年三月的星期三的下午2:10和2:44触发` |
> | `"0 15 10 ? * MON-FRI"` |  | `周一至周五的上午10:15触发` |
> | `"0 15 10 15 * ?"` |  | `每月15日上午10:15触发` |
> | `"0 15 10 L * ?"` |  | `每月最后一日的上午10:15触发` |
> | `"0 15 10 ? * 6L"` |  | `每月的最后一个星期五上午10:15触发` |
> | `"0 15 10 ? * 6L 2002-2005"` |  | `2002年至2005年的每月的最后一个星期五上午10:15触发` |
> | `"0 15 10 ? * 6#3"` |  | `每月的第三个星期五上午10:15触发` |

每天早上6点 0 6 \* \* \* 

　　　　　　　　　　 　每两个小时 0 \*/2 \* \* \* 

　　　　　　　　　　　　晚上11点到早上8点之间每两个小时，早上八点 0 23-7/2，8 \* \* \* 

                                                     每个月的4号和每个礼拜的礼拜一到礼拜三的早上11点 0 11 4 \* 1-3 

　　　　　　　　　　　　1月1日早上4点 0 4 1 1 \*

---
> 参考链接：[https://www.cnblogs.com/lic309/p/4089633.html](https://www.cnblogs.com/lic309/p/4089633.html)
