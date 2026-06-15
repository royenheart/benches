# 高性能存储阵列的软件开销优化

## 一、背景介绍

近些年来，SSD因其高带宽、低延迟、低能耗的特点，已经成为了高性能计算、数据中心、云服务等场景下的主要存储设备。但不幸的是，由于其自身的物理性质，相较于HDD，SSD通常更容易损坏，导致数据丢失。

存储阵列（RAID）是解决这个问题的手段之一。通过条带化技术，RAID可以聚合多个SSD的性能，同时对外提供服务，以驱动高性能计算中大量I/O的场景；通过校验和技术，RAID可以保证存储阵列具有一定的容错性，即使其中的一个磁盘损坏，也能从剩余的磁盘中恢复数据。

Linux software RAID（mdraid）是Linux内核中自带的RAID引擎，设计于二十多年前，因其高昂的软件开销，已不再适合用来创建和管理现有的高性能存储设备（如NVMe SSD）。如何优化mdraid，使得高性能SSD组成的存储阵列能够发挥出优异的性能，是现在学术界和工业界关注和研究的重点。 

## 二、赛题描述

  本次比赛允许优化mdraid中的任何软件开销，考虑到比赛时间限制，参赛者可以通过阅读论文[1][2]了解到mdraid中已知的可优化的开销。同时，我们鼓励参赛者自己通过perf，fio等工具剖析RAID软件栈，找出其他可优化的部分。

  下面简单介绍一下mdraid中的一个和锁相关开销，该开销的详细分析和说明可见论文[1]。如下图所示，在mdraid中，当I/O线程在处理写请求时，它首先会将数据分割为多个stripe unit。拥有相同offset的stripe unit属于同一个条带，它们会被一起处理 ①。但在处理之前，I/O线程需要向守护进程获取一个名为stripe_head的数据结构 ②。但是，为了防止多线程之间的冲突，mdraid使用全局的锁去管理stripe_head的分配。因此，如果我们使用多个线程来处理I/O请求，它们就会被这个锁阻塞，无法并行处理，造成大量的软件开销。解决这个问题的办法很简单，我们可以给每个stripe_head都分配一个锁，单独进行管理，再使用hash算法让不同的线程去找到不同的stripe_head，从而最大化线程的并行度。

![img](/Users/leavelet/Pictures/typora%E5%9B%BE%E7%89%87%E5%BA%93/clip_image001.png)

  类似的软件开销还有很多，请参赛者务必阅读论文[1][2]，以对mdraid相关的设计和开销形成初步的了解。除此之外，这里推荐查看资料[3]，辅助阅读mdraid相关的代码。

## 三、评测说明

1. 我们允许修改附件中md文件夹下的任何代码，但其中很多代码只是因为编译需要而存在，和本次比赛相关度较低，因此我们建议参赛者关注文件raid5.*，md*.*；

2. 修改代码后，参赛者可以根据附件README安装测试环境，测试自己代码的正确性。评测过程中也会使用相同的内核（linux-5.11-46）；

3. 在评测过程中，我们会使用mdadm创建RAID5，参赛者可以参考[4]学习mdadm的使用方法；

4. 在评测过程中，我们会使用高性能的NVMe SSD组建RAID,如果参赛者自己的Coding环境没有足够的磁盘，可以参考附录A，使用RAM模拟磁盘;

5. [1]的代码是开源的，我们允许参赛者整合该开源代码作为基础继续修改，但必须有其他的设计以作为此次参赛的内容；

6. 在评测过程中，我们会使用fio产生IO请求，参赛者可以参考[5]学习fio的使用。

## 四、评分标准

  我们会用高性能的NVMe SSD组成2+1，4+1两种RAID5，并使用fio评估I/O的带宽和完成时延。带宽越高分数越高，延迟越低分数越高，按排名正态分布给分。我们使用到的测试参数如下表所示，其中worker thread的定义可以参考论文[1][2],并通过修改文件/sys/block/mdx/md/group_thread_cnt修改，这里mdx是你通过mdadm创建的RAID：

| RAID类型 | I/O Size | No. of I/O threads | No. of Worker threads | IO depth | 类别   | 指标 | 分数占比 |
| -------- | -------- | ------------------ | --------------------- | -------- | ------ | ---- | -------- |
| 2+1      | 64 KB    | 8                  | 8                     | 32       | 随机写 | 带宽 | 6.25 %   |
| 2+1      | 128 KB   | 8                  | 8                     | 32       | 随机写 | 带宽 | 6.25 %   |
| 4+1      | 64 KB    | 8                  | 8                     | 32       | 随机写 | 带宽 | 6.25 %   |
| 4+1      | 256 KB   | 8                  | 8                     | 32       | 随机写 | 带宽 | 6.25 %   |
| 2+1      | 64 KB    | 8                  | 8                     | 32       | 顺序写 | 带宽 | 6.25 %   |
| 2+1      | 128 KB   | 8                  | 8                     | 32       | 顺序写 | 带宽 | 6.25 %   |
| 4+1      | 64 KB    | 8                  | 8                     | 32       | 顺序写 | 带宽 | 6.25 %   |
| 4+1      | 256 KB   | 8                  | 8                     | 32       | 顺序写 | 带宽 | 6.25 %   |
| 2+1      | 4 KB     | 1                  | 1                     | 1        | 随机写 | 延迟 | 12.5 %   |
| 4+1      | 4 KB     | 1                  | 1                     | 1        | 随机写 | 延迟 | 12.5 %   |
| 2+1      | 4 KB     | 1                  | 1                     | 1        | 顺序写 | 延迟 | 12.5 %   |
| 4+1      | 4 KB     | 1                  | 1                     | 1        | 顺序写 | 延迟 | 12.5 %   |

附件fio.conf，给出了第一组测试的fio配置文件。

### 五、参考文献

[1] Yi, Shushu, et al. "ScalaRAID: optimizing linux software RAID system for next-generation storage." Proceedings of the 14th ACM Workshop on Hot Topics in Storage and File Systems. 2022.（编者注：https://dl.acm.org/doi/10.1145/3538643.3539740，已在附件中包含，仅供学习研究之用）

[2] Wang, Shucheng, et al. "{StRAID}: Stripe-threaded Architecture for Parity-based {RAIDs} with Ultra-fast {SSDs}." 2022 USENIX Annual Technical Conference (USENIX ATC 22). 2022.（编者注：https://www.usenix.org/conference/atc22/presentation/wang-shucheng，文档开放获取）

[3] https://blog.csdn.net/chenyouxu

[4] https://raid.wiki.kernel.org/index.php/A_guide_to_mdadm

[5] https://fio.readthedocs.io/en/latest/index.html

 