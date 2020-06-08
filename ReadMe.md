## flask-utils

**flask-utils 是对Flask应用中常用的功能进行封装，方便使用，目前主要提供了四个类：**

* RoutingSQLAlchemy
> 基于flask-sqlalchemy的封装，可实现Flask应用的读写分离，非常轻量且灵活，并且完全兼容 flask-sqlalchemy的使用方式

* Form
> 自定义表单验证 以及 传参校验, 可通过 Column的 validator参数自定义验证器

* Serializer
> 参考Django的 serializer，实现简单的serializer，可以方便的进行由model 到json以及由json到model的转换

* LoopCall
> 定期执行某任务，可用于热加载之类的操作