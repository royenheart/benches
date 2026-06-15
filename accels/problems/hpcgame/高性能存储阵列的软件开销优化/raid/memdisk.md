# 附件A：使用内核模块`brd`创建内存盘

`block ram disk`，缩写为`brd`，是Linux kernel中提供的创建内存盘的模块，代码可以在`kernel`中`drivers/block/brd.c`找到。

由`brd`创建的内存盘和`brd`模块的生命周期相同重启时会消失，具体来说：

1. 加载模块、创建内存盘：`modprobe brd`

    这个命令有三个可选参数：

     `rd_nr` : 创建内存盘的数量
     `rd_size` : 内存盘的最大大小，单位为kb
     `max_part` : 每个内存盘的最多分区数

    下面例子在创建了5个大小为2G的单分区内存盘，位于`/dev/ram0`到`/dev/ram4`

    ```
    modprobe brd rd_size=2048000 max_part=1 rd_nr=5
    ```

2. 卸载模块、删除所有内存盘：`rmmod brd`

3. 分区与fdisk的使用：https://wiki.archlinux.org/title/fdisk，本题中，可以使用如下命令进行分区

```shell
TGTDEV=/dev/ram0
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk ${TGTDEV}
  n # new partition
  p # primary partition
  1 # partition number 1
    # default - start at beginning of disk 
    # default - default size
  t # change partition type
  fd# to Linux raid autodetect
  w # write the partition table
  q # and we're done
EOF
```

