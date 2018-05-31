# dice_world
## 2018.05.29
* 预想场景：
用户登录大厅，可以上传管理自身游戏角色信息，每个用户可以管理多个游戏角色。
大厅具有多个房间，房间由用户创建，用户可以创建多个房间，也可以加入多个房间。
房间包含一个以上团队，团队与用户之间为多对多关系，用户通过不同的团队关联游戏角色。
* 涉及实体：
    * 用户类(id,用户名,密码,....)
    * 房间(id,房间号,房间名,管理员/创建者,标签,添加时间)
    * 团队(id,用户表,所属房间,团队类型,添加时间)
    * 游戏角色(id,角色名,角色头像,角色资料,上传者,添加时间,修改者,修改时间)
    * 游戏文本(id,上传者,文本内容,上传时间)
——（用户组与用户多对多，建立中间类）——
    * 团队信息(id,用户,团队,游戏角色,队长,标签,加入时间)
* 房间号生成问题
    * 目前只能生成uuid，但uuid太复杂不利于用户搜索
    * 考虑数据库递增，但是django设置自增似乎就直接是主键了。。

----
## 2018.05.30
学习Django自动化测试中，一个测试例子写半天。。。而且因为每次测试都要全部建库所以，等待测试的时候依样画葫芦的写写markdown文档（真难写）。
————（另外，房间号采用uuid随机取3位+时间戳整数部分组成）————

* 总结如下：
    1. 测试时，不管选择测试单一或多个app，都会建立全部的测试数据库，建库依据是`makemigrations`生成的依赖文件。
    2. 因为要生成测试数据库，所以需要将数据库连接调通。简单说，就是事先跑通`python manage.py check`
    3. 因为生成了全部的数据库，所以在`tests.py`中，可以如同正常工作环境一般的调用模块，而非不能跨应用调用。（刚刚开始写的时候，因为第一个实体关联用户类外键，还以为用户类对象不能生成保存写库呢。。）
    4. 每个测试方法中，数据互不影响，即，在方法a中创建了10个对象，在方法b开始测试时，数据对象为0。
    5. 测试数据库会在结束测试后删除。
    6. Django默认自增id作为主键，在之前项目开发中，发现以自增int作为主键在有些地方不太方便，所以准备以无实际意义值作为id，首选的就是UUID。Django1.8之后model类提供了`UUIDField`用于存放UUID类对象，于是尝鲜用了一回，然后发现一些问题。
        * 首先，`UUIDField`只是Django中约定的字段解析方式，其在数据库中存放方式还是`char`类型。Django会自动解析为`742fb7b3-3fa5-5822-8adc-744232667ffb`形式的string；从数据库读取时由Django转化为UUID类型对象。但是在获取时，可以通过字符串`742fb7b33fa558228adc744232667ffb`来获取，也是因为在获取时Django对字符串进行了处理。
        * Django中，通过以下代码所得到的model对象与数据库对象不是同一个东西，虽然在model_1.save()时，会根据model定义类中的default数值进行填充属性，但是在存到数据时还要经过Django处理。举个例子，uuid的default值设置为uuid.uuid4().hex，所得到的是一个uuid字符串，（比如`742fb7b33fa558228adc744232667ffb`），type是str类型，这时model_1的id属性值便为这个字符串。而数据库中存放的是`742fb7b3-3fa5-5822-8adc-744232667ffb`。此时虽然可以通过model_1的id进行对象获取，但实际在获取过程中，这个字符串是被Django处理了的，且从数据库读取model_2时，其id类型为UUID。（如果没有关闭系统时区，那么在时间相关字段上也会出现差异）
```python
        model_1 = Model(**kwargs)
        ...
        model_1.save()
        model_2 = Model.object.get(id=model_1.id)
        model_3 = Model.object.all()[0]
        print(model_1 == model_2)   # False
        print(model_2 == model_3)   # True
        type(model_1.id)    # str
        type(model_2.id)    # UUID
        type(model_3.id)    # UUID
```
----
##2018.05.31
今天测试自定义Field。（参考[官方文档](https://docs.djangoproject.com/zh-hans/2.0/howto/custom-model-fields/#writing-a-field-subclass)）

因为在很多地方使用了json格式存储数据，而Django中没有JSONField类，json数据只能以字符串类型存储到数据库中（其实mysql在某个版本之后已经有json字段了，不过下次再研究mysql的json字段）

* 期待实现如下效果：
    * Python对象存放时，JSONField字段属性值通过json序列化为string类型存放。
    * 从数据库读取对象时，JSONField字段属性通过json反序列化为结构体赋值到对象对应属性。
    * 查询相关
————（啃了一下午的英文文档+动手测试后）————
* 归纳一下知识点：
    * init()、deconstruct()
        * 用于自定义Field结构的，添加、删除、预设各种属性
    * **db_type()**
        * 用于设置生成数据库sql语句时对应到的数据库字段类型
        * 在生成表、修改表等操作时会调用到，平时不会被调用
        * 如果返回None，则会让sql语句生成器忽略这个字段
        * rel_db_type()，与此类似，用于指定如外键等关联时字段类型指定
        * get_internal_type()，一般不怎么用这个
    * **from_db_value()**
        * 处理数据库值转化为python数据的逻辑
        * 每次从数据库中读取数据都会调用这个方法，包括统计和values()等方法
        * 处理失败时，必须抛出ValidationError异常
    * to_pyhton()
        * 文档中说的是value_to_string()反序列化和Model.clean()时调用，讲道理我是没发现调用了。
        * 处理失败时，必须抛出ValidationError异常
    * get_db_prep_value()
        * python数据转化为数据库数据（先调用）
        * 这个主要是用于处理一些需要特殊转换的字段，比如时间字段这种，一般来说都是直接调用get_prep_value()
        * 但是不管怎么说，也是先调用这个，再进get_prep_value()逻辑
    * **get_prep_value()**
        * python数据转化为数据库数据
        * 一般是写在get_db_prep_value()中被默认调用
        * 请确保返回使用数据库能够支持的类型（比如string）
    * pre_save()
        * 存储前预处理值，比如DateField里面的auto_now属性等就是通过这个实现
    * formfield()、value_to_string()、value_from_object()等
        * 没用上，不清楚
* JSONField代码如下
```python
class JSONField(models.Field):
    description = "field to store json obj(list/dict)"

    def __init__(self, verbose_name=None, **kwargs):
        super().__init__(verbose_name, **kwargs)

    '''
     用于生成数据库sql语句时指定字段类型
    '''
    def db_type(self, connection):
        return 'longtext'

    '''
     每次从数据库读取数据时，都会调用这个函数（但是不会调用to_python()）
    '''
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.to_python(value)

    '''
     反序列化时调用，forms clean()时调用
      ·对一切异常均需要抛出ValidationError
    '''
    def to_python(self, value):
        if value is not None and isinstance(value, str):
            try:
                value = value.replace("'", '"')
                return json.loads(value)
            except Exception as e:
                raise ValidationError(
                    "'%s' is not a valid UUID." % value,
                )
        else:
            return value

    '''
     针对某些需要准备的字段调用的方法
     ·比如date时间等
     ·默认的父类方法是直接调用get_prep_value()
     ·用于保存时需要特殊转换的字段
    '''
    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value

    '''
     Python值转数据库字段存储值
     ·请返回数据库支持的字段类型，如string
    '''
    def get_prep_value(self, value):
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value
```
另外在看代码时，发现了如下代码：
>'invalid': _("'%(value)s' is not a valid UUID."),

其中，_似乎与延迟加载有关，指向：
>gettext_lazy = ugettext_lazy = lazy(gettext, str)

需要研究一下。