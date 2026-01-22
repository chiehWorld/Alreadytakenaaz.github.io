---
layout:     post
title:      "Kesoyuh/Gomoku: iOS五子棋游戏，支持人机对战、双人对战、联机对战。iOS Gomuku game with amazing AI, developed in Objective-C"
subtitle:   "归档于：技术"
date:       2026-01-22
author:     Chieh
header-img: assets/KesoyuhGomoku-iOS五子棋游戏，支持人机对战、双人对战、联机对战。iOS-Gomuku-game-with-amazing-AI,-develop_header.jpg
catalog: true
tags:
    - 技术
---

# 五子棋大师

Developed by @张添 and @王唱畅

### 1. 人机对战

在人机模式下，AI 共有三种难度可供选择。简单难度的 AI 由贪心算法实现，中等和困难难度的 AI 基于极小化极大算法实现。算法通过多种方式优化，在困难难度下，博弈树深度可达8层。

#### 1.1 贪心算法

贪心算法的主要思路是，评价当前棋局中所有可以下的位置，依据一个评分表对该位置进行打分，然后随机选取一个分数最高的位置落子。对于五子棋来说，我们把五个连续的位置称为五元组，对于一个可以下的位置来说，我们对于所有包含它的五元组，根据五元组中黑棋和白棋的数量进行评分，这个位置的最终得分就是所有这些五元组的评分的和。下面是游戏中所用的针对黑棋的评分表：

```
// tuple is empty  
GGTupleTypeBlank
 =
 7
,  
// tuple contains a black chess  
GGTupleTypeB
 =
 35
,  
// tuple contains two black chesses  
GGTupleTypeBB
 =
 800
,  
// tuple contains three black chesses  
GGTupleTypeBBB
 =
 15000
,  
// tuple contains four black chesses  
GGTupleTypeBBBB
 =
 800000
,  
// tuple contains a white chess  
GGTupleTypeW
 =
 15
,  
// tuple contains two white chesses  
GGTupleTypeWW
 =
 400
,  
// tuple contains three white chesses  
GGTupleTypeWWW
 =
 1800
,  
// tuple contains four white chesses  
GGTupleTypeWWWW
 =
 100000
,  
// tuple contains at least one black and at least one white  
GGTupleTypePolluted
 =
 0
```


#### 1.2 极小化极大算法

对于五子棋这种零和游戏，极小化极大算法是最常用的算法，维基百科上已有详细介绍：极小化极大算法，在此不再详细解释。

游戏在博弈树搜索的基础之上，进行了许多优化，用于提升搜索树的深度：

Alpha-Beta 剪枝，维基百科上的详细介绍：Alpha-Beta 剪枝。

启发式搜索函数：在博弈树中，对于每一层的节点来说，如果粗略的按照好坏对其进行一个排序，Alpha-Beta 算法就可以减去更多的节点，游戏中，我们用贪心算法对于每一个节点上一步所下的位置进行评分，根据这个评分对节点进行排序，从而进一步提升博弈树搜索的效率。

缩减子节点：游戏中所使用的贪心算法效果很好，基本可以保证最优解在评分前十的点中，所以我们可以缩减博弈树中的每个节点的子节点数量，只取评分前十的点，这大大的减少了节点的数量，并且将博弈树的搜索深度提升到了8层。

迭代加深：在游戏中有时候会发生如下情况：明明 AI 已经快要胜利，但是会选择一些其他的点并且多下几部才取胜，看起来像是在调戏玩家，实际上这是由于在博弈树中已经找到一个解之后便没有考虑其他层数较小的解。归根结底是因为极小化极大算法是深度优先搜索，不保证可以找到最优解。对此我们使用迭代加深博弈树搜索深度的方法，确保 AI 可以返回最优解。

### 2. 双人同屏

此模式支持两位玩家在同一手机上一同下棋。

### 3. 联机游戏

在局域网联机模式下，两台处于同一子网的手机可通过网络进行连接并一同下棋。游戏使用Bonjour（维基页面）作为局域网内广播服务（棋局）和寻找棋局的解决方案。当找到棋局后，游戏使用GCDAsyncSocket来建立网络连接，进而进行网络通信。

游戏定义了网络间包的类型与内容，以确保通信的简介与准确。包的类型分为三中：下棋，悔棋和重赛。当游戏的任何一方希望进行悔棋或重赛时，需得到对方同意。因此网络包有以下定义：

```
//
 GGPacket.h
......
//
 包类型
typedef
 NS_ENUM
(NSInteger
, GGPacketType) {
//
 未知类型
    GGPacketTypeUnknown,
//
 下棋
    GGPacketTypeMove,
//
 重赛
    GGPacketTypeReset,
//
 悔棋
    GGPacketTypeUndo
};
//
 包具体动作
typedef
 NS_ENUM
(NSInteger
, GGPacketAction) {
    GGPacketActionUnknown,
//
 重赛请求/同意/拒绝
    GGPacketActionResetRequest,
    GGPacketActionResetAgree,
    GGPacketActionResetReject,
//
 悔棋请求/同意/拒绝
    GGPacketActionUndoRequest,
    GGPacketActionUndoAgree,
    GGPacketActionUndoReject
};
@interface
 GGPacket
 : NSObject
//
 data用来在下棋类型的包中存放棋的坐标
@property
 (strong
, nonatomic
) id
 data;
@property
 (assign
, nonatomic
) GGPacketType type;
@property
 (assign
, nonatomic
) GGPacketAction action;
......
@end
```


### 4. 其他功能

#### 4.1 界面设计

由于没有美工，游戏没有华丽的特效，但整体界面依然不失简洁优雅大方，五子棋的棋盘使用 Core Graphics 画出，并使用 NSTimer 对游戏双方进行计时，落子指示图标也可以方便的提醒玩家最新落子。

#### 4.2 游戏设置

在设置界面可以设置游戏的难度，游戏的音乐以及音效，玩家的偏好设置通过 NSUsersDefaults 进行存储。游戏的音乐使用 AVAudioPlayer 进行播放与控制。

该五子棋游戏具有人机、人人、联机等多种功能，并且棋力不俗，在实际测试中可以轻松战胜大多数网络上的五子棋程序。

下面是我们的五子棋与 Google 搜索 Gomoku 排名第一的五子棋游戏进行对战的截图：

先手情况下，轻松取胜。

后手情况下，经过一番鏖战，取得胜利。

下面是与 Github 上面有名的五子棋程序 Gobang 进行对战的截图：

由于 GoBang 不能设置先后手，这是在我方后手的情况下，最终取得了胜利。

Core Graphics

五子棋项目参考1

五子棋项目参考2

五子棋AI设计

如何设计一个还可以的五子棋AI

五子棋AI算法系列

人机版五子棋两种算法概述

计算机五子棋博奕系统的研究与实现

Gomoku AI Player

十四步实现拥有强大AI的五子棋游戏

Creating a Game with Bonjour and GCDAsyncUdpSocket - Server and Client Setup

Creating a Game with Bonjour and GCDAsyncUdpSocket - Sending Data

---
> 参考链接：[https://github.com/Kesoyuh/Gomoku](https://github.com/Kesoyuh/Gomoku)
