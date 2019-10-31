【天使去重】可以做什么？
=======================
资料文件夹越来越臃肿？
自己存的照片文档和小电影复制来复制去占了一大堆空间又不知道删除哪些好？
多个备份文件夹和文件有重叠但又不敢随便删除又懒得一个个查看而导致浪费空间？

让 【天使去重】 拯救你！

 - 无差别去重：不限制文件类型，去除一切重复文件，图片视频音乐文档等等，安全又高效。

 - 多个模式可选，可以设置：
   - 自动检测并处理重复文件，
   - 自动检测只返回重复文件（不删除），
   - 交互模式下自动删除，
   - 交互模式下提示删除
   
 - 速度快：可设置编码抽样或者多进程，转眼就完成

懒人福音有木有！

预先提醒！这个版本确认删除后不可恢复！请谨慎操作！！！（之后版本会增加恢复功能敬请期待）

怎么安装？
=========
```linux shell
$ pip install duplremover
```
或者直接下载 duplremover 文件夹到你的项目目录下也行

怎么使用
=========

导入并实例化：
```python
from duplremover.duplicate_remover import DuplRm

DR = DuplRm(directory='your file path',   # 需要去重的文件夹地址
            recursive_traversal=True,     # 是否检查子文件夹，默认是
            types=None,                   # 指定检查的文件类型列表，例如['jpg', 'png']，默认为None，即检查所有类型
            sampling_matching=True,       # 是否以文件二进制抽样的方式去重，默认是
            interactive_mode=False,       # 是否以交互模式调用，默认否
            auto_delete=False,            # 是否允许自动删除，默认否
            remove_zero_size_file=False,  # 是否自动删除0kb的废文件，默认否
            remove_empty_dirs=False,      # 是否自动删除空白文件夹，默认否
            multiprocess=False,           # 是否启用多进程（启用后日志输入有影响），默认否
            log_level=None,               # 日志级别，默认info级别
            )
```
在实例化时指定相应的选项，设置相关功能，特别说明以下这几个：

    recursive_traversal     如果子文件夹的内容是其他的东西，或者肯定没有重复的，那可以设置为False比较保险
    sampling_matching       以二进制抽样的方式去重，当待去重的文件之间的区别较小的时候（例如超高速连拍的照片），建议设置为False，否则在抽样时很可能错过这些微小的差别，当然速度会慢很多很多。
    interactive_mode        交互模式下，输出是终端打印（非交互模式输出的是log）。一些情况下需要手动输入字符进行操作确认
    auto_delete             建议仅在目标文件夹内的文件是非重要的，或者自动化部署时使用（再次提醒！本次版本删除后文件暂时无法恢复，数据无价，谨慎！）
    multiprocess            启用多进程时，日志输出不正常（将来版本改进），建议在自动化部署时考虑使用

一般情况下，如果只是想确认一下文件夹内是否包含重复文件，只需要设置一个或两个参数即可:
```python
from duplremover.duplicate_remover import DuplRm

DR = DuplRm('your file path')                           # 只检查并输出重复文件，不进行任何操作
DR_2 = DuplRm('your file path', interactive_mode=True)  # 检查重复，并且在提示下输入操作字符完成操作
```
实例化完成后，便可以直接调用对象的start方法即可:
```python
DR.start()
```
为了更好的说明效果，我弄了一些测试用的文件（环境是windows，当然linux下也是不成问题的）。
文件夹结构如下，有一些jpg，mp3，mp4和ini文件，有些是重复的，有些重复文件在子文件夹sub下面：

![Markdown](http://i2.tiimg.com/702641/a989ce5c7d9cebba.jpg)
![Markdown](http://i2.tiimg.com/702641/6ae55047fbf9d3ca.jpg)


以交互模式下实例化并传入文件夹路径：
```python
from duplremover.duplicate_remover import DuplRm

DR = DuplRm('E:\\test\\', interactive_mode=True)
DR.start()
```

输出如下图：
![Markdown](http://i2.tiimg.com/702641/59e98b647b2e0ec7.jpg)

程序成功检查出文件夹内的文件类型和对应的数目，这时候你可以冒号后面输入想要去重的文件类型的编号，例如“0”，或者多种类型，用任意符号分割：“0,2,3”，
直接回车，或者输入其他字符（包括不在选项内的数字，例如“5”），将跳过手动选择，自动选择全部的文件类型。

接下来我要检查全部的文件的重复情况，下图是直接按下回车键的效果：
![Markdown](http://i2.tiimg.com/702641/9215a609f9a0c6dd.jpg)

可以看见程序开始执行去重检查，先检查了ini文件类型，并且发现了重复的文件，一个位于test文件夹下，另一个位于其子文件夹sub下，
接下来可以选择需要保留的文件，"0" 或者 "0,1"，逻辑与上一步一样，留空则保留所有文件。注意如果一旦输入了要保留的文件编号，未被选中的将会被删除

输入“1”按下回车：
![Markdown](http://i2.tiimg.com/702641/08ad8babbdfb378f.jpg)

程序提示是否确认删除，输入“yes”或者“y”，文件会立马被删除，其他任意字符则或直接回车则跳过

输入“y”并按下回车：
![Markdown](http://i2.tiimg.com/702641/c914ef6a300b2c35.jpg)
程序提示文件已经被成功删除掉了，并且立即进入下一个重复文件检测循环，发现ini文件只有这两个重复，则自动进入下一个类型的判断中（JPG类型）。

后面的操作都大同小异，只是确认输入的编号是正确的就行。

最后处理完成，程序会提示总共删除的文件个数：
![Markdown](http://i2.tiimg.com/702641/319215728fbe3e1b.jpg)


如果在交互模式下，auto_delete参数也设置为True的话，除了在开始类型选择时有提示输入检测类型之外，后面的删除都是自动完成，将不会给输入的选项：
![Markdown](http://i2.tiimg.com/702641/dc54ac1f9f0fdd0d.jpg)

非交互模式下，auto_delete设置为False的输出效果如下：
![Markdown](http://i1.fuimg.com/702641/7df61b7ec840ef7b.jpg)

此前如果你用一个变量接收调用start方法返回的数据的话，你会发现它是一个字典（如果不是这个模式，返回的使个None值），包含了检测到的重复文件的类型和路径，例如：
```python
from duplremover.duplicate_remover import DuplRm

DR = DuplRm('E:\\test\\', interactive_mode=False, auto_delete=False)
res = DR.start()
print(res)
```

res的值为：
```python
{'jpg': ['E:\\test\\sub\\IMG_0003 - 副本.JPG', 'E:\\test\\IMG_0003 - 副本.JPG', 'E:\\test\\sub\\IMG_0003.JPG', 'E:\\test\\IMG_0003.JPG'], 'mp3': ['E:\\test\\test_mp3_file_4.8Mb - 副本.mp3', 'E:\\test\\test_mp3_file_4.8Mb.mp3'], 'mp4': ['E:\\test\\test_mp4_file_20Mb - 副本.mp4', 'E:\\test\\test_mp4_file_20Mb.mp4']}
```

最后一种模式，非交互模式下启用自动删除，仅建议在非重要数据或者自动程序调用时使用，输出效果如下：
![Markdown](http://i1.fuimg.com/702641/ce82d7e172b471f6.jpg)

最后再啰嗦一下，数据高无价，操作需谨慎！（删错了重要文件别找我╮（╯＿╰）╭，争取下个版本增加恢复功能）
===="# duplremover" 
