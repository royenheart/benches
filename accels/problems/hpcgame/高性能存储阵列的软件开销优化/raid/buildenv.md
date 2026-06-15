# 如何搭建测试环境

## 一、安装内核

评测中将使用的内核版本为`linux-5.11-46`，请在测试中尽量使用相同的内核版本。mdraid模块默认是不可修改的，如果想要修改，需要在编译内核文件时将相关配置设置为[M]。我们提供的ubuntu环境已经配置完成，如果你想使用自己的设备，请自行编译内核。

我们在附件中提供了`linux-image`的deb包，可用于`ubuntu 20.04`版本安装，具体步骤如下。

```
dpkg -i linux-image-unsigned-5.11.0-46-generic_5.11.0-46.51~20.04.1_amd64.deb linux-modules-5.11.0-46-generic_5.11.0-46.51~20.04.1_amd64.deb
apt install linux-headers-5.11.0-46-generic linux-modules-extra-5.11.0-46-generic linux-buildinfo-5.11.0-46-generic linux-tools-5.11.0-46-generic
```

## 二、优化 & 编译

我们允许参赛者优化md文件夹下的任何代码，我们已经写好了Makefile文件，优化完成后，参赛者可以直接通过`make`指令进行编译。编译完成后会生成一系列`.ko`文件，这就是内核模块文件。请参赛者仔细阅读Makefile文件，确定自己的修改涉及到哪几个`.ko`文件，并安装这些修改后的模块。

## 三、安装模块

1. 首先进入存放mdraid相关模块的文件夹：`cd /lib/modules/5.11.0-46-generic/kernel/drivers/md/ `；

2. 假设我们修改的模块是`md-mod.ko`。我们先备份这个文件：`cp md-mod.ko md-mod.ko.bak`；

3. 然后我们删除原有的未经修改的md-mod模块。由于许多模块依赖于md-mod模块，因此我们需要先删除这些依赖的模块，并最后删除md-mod。参赛者可以通过`lsmod | grep md`来查看模块的依赖关系。假设md-mod被模块linear，raid0，raid456，...依赖：

   ```bash
   # 删除依赖md-mod的模块
   rmmod raid1
   rmmod raid10
   rmmod raid0
   rmmod linear
   rmmod raid456
   rmmod multipath
   # 请检查自己系统，查看是否有其他依赖
   
   # 删除md-mod模块
   rmmod md-mod
   ```

4. 然后我们将之前编译产生的`md-mod.ko`复制的这里：`sudo cp path/md-mod.ko ./`；

5. 最后我们安装md-mod模块以及之前删除的模块：

   ```bash
   // 安装md-mod模块
   insmod md-mod.ko
   
   // 安装之前删除的模块
   insmod raid1.ko.
   insmod raid10.ko
   insmod raid0.ko
   insmod linear.ko
   insmod raid456.ko
   insmod multipath.ko
   ```



至此，你的修改已经嵌入到内核中，可以通过mdadm创建RAID5并使用fio进行测试。 