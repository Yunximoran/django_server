# Django 笔试项目
### 场景
    - 当用户访问文章详情页时，统计用户人次、每人对应的阅读次数、总阅读次数。
    - 阅读量相关统计数据需实时显示（可以只给一个数据接口，或者简单html展示）
    - 需设计缓存更新数据库，数据库异步更新，要保证数据一致性安全，防止数据丢失或错误。
    - 系统需监控缓存命中率，redis统计、接口查询命中率百分比。
  
### 要求
    1. 缓存设计：使用Redis缓存阅读量数据，减少数据库IO。
    2. 读写分离：读操作优先访问缓存，写操作异步更新数据库。
    3. 缓存命中率：优化缓存策略提高命中率，设计数据最终一致性方案。
    4. 异常分级处理：区分缓存/数据库异常级别并降级处理。
    5. 面向对象封装：模块化设计，分离缓存操作、数据库操作和异常处理。
   
### 设计
##### API接口([后端地址](http://localhost:8000))
* [demopage](http://localhost:8000/demopage/yumo?usrid=123456): 模拟详情页面点击，触发数据更新操作
* [realtime](http://localhost:8000/realtime): 数据实时显示接口(websockt实现)，显示统计数据， 缓存命中率

##### 数据库
* [database](./database.py): 数据库操作模块，实现数据库相关操作([缓存](./lib/database//redis/workbench.py)：Redis / [磁盘](./lib/database/mysql/workbench.py)：MySQL)
  * _get_cache_ & _set_cache_: 封装Redis数据库读&写方法，添加异常捕获模块，实现异常分级
  * get_detial_message & set_detial_message: 实现应用层读&写方法，针对表结构设计，兼容Redis和MySQL数据格式，实现数据缓存读写功能
  * _get_detial_message & _set_detial_messgae: 针对表结构单独实现的MySQL读&写，只在Redis无法使用时被调用
  * check_now_userids & check_now_detial: 查询用户数据和文章数据全部索引
* 缓存策略：
  * 通过将JSON格式将复杂表进行序列化操作，存储在Redis Hash表中
    * jsondumps & jsonloads: 递归实现json 序列化 & 反序列化，处理多层嵌套数据
  * 将不需要进行写操作的数据（查询数据），设置缓存过期时间，10内没有数据更新时，删除缓存
* [异步存储](./manage.py)：
  * 后台运行数据更新服务，通过队列传递参数， 根据数据更新次数(30)|数据条目(10)|超时时间， 更新数据
  * 引入时间戳校验，处理异常分级时，替换更新任务，保证最新数据
* 异常分级：
  * 对复写redis_command方法，引入异常捕获控制功能
  * 单独封装处理MySQL读&写方法
  * 实现catch.DataBase装饰器，转递MySQL读&写方法， 当Redis缓存不可用时调用
  * 
* 设计数据表：
  * detialindex: 文章信息
    detial: 文章名称
    views: 当前文章阅读详情(连接到[xxx_views]())
    count: 当前文章全部阅读量
  * [文章名称]_views: 当前文章不同用户的阅读次数
    * usrid: 用户唯一标识
    * count：用户浏览当前文章次数
  * userdata: 用户信息
    * userid: 用户唯一标识，提高查询准确性
    * 



### 环境配置
* 数据库配置路径
  ./lib/_init/.config.xml

* python 依赖
```bash
pip install django uvicorn redis pymysql psutil channels websocket requests asgiref
```

* 目录结构
* core: 后端工作核心模块： 定义视图 -> 事件
* lib: 项目依赖库， 异常捕获、日志输出、数据库原始操作台，自定义多进程，配置文件解析
* redis：编译后的redis， 运行./redis/bin/redis-server ./redis/redis.conf 端口 6369
* service: Django配置模块， 配置路由，agsi服务器
* static: 静态资源目录
* clean.py: 清理数据库
* database.py: 数据库操作模块，根据项目需求定制的多数据复合应用
* init.py: 初始化操作，第一次部署时运行，初始化MySQL表，也可以自定义
* manage.py: 项目启动入口， 启动Django服务器， 和数据更新服务
* realtime.py: 测试实时数据
* test.py: 测试高并发
