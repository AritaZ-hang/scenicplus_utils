目前已探查出来的问题：

1. 本地工作站根目录下储存空间过小
2. python脚本中调用ray无法连接到head node

第一个问题很好解决，别什么东西都存桌面上就行了（对，我说的是我自己）

第二个问题基本是207和其他主机现在都跑不了scenicplus的问题，可能是本地根本没有启动的ray集群，也可能是好几个scenicplus都想调默认的ray集群然后冲突了，因为python中的ray.init其实是连接到已经启动的ray集群上，不是给你创一个新的。

一个探明的解决方法：

1. 在终端中启动ray 

   ```shell
   ray start
   ```

2. 在python中显式的调用ray

   ```python
   import ray
   ray.init('auto') # ray start后会给你一个Head节点位置，填进来就行
   # 别在python中init两次，不然报错
   ```

3. 最麻烦的一步之去掉pycistopic, pycistarget & scenicplus中所有调用ray的函数中的ray.init和ray.shutdown，已经得自己手动连了就别让它再调用了（遑论还会报错

   207的scenicplus: `/home/ggj/Desktop/ZS/softwares/scenicplus`下已经改了scenicplus这个包里需要调ray的函数，应该可以直接复制；另外两个包中需要改的函数可以参见207`/media/ggj/Guo-4T-C2/scenicplus/dm6/pre-scenicplus.ipynb`中写的。
