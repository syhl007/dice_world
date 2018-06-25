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
    * ER图如下
![ER图](/ER.png)

* 房间号生成问题
    * 目前只能生成uuid，但uuid太复杂不利于用户搜索
    * 考虑数据库递增，但是django设置自增似乎就直接是主键了。。

---

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
---

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
>from django.utils.translation import gettext_lazy as _

一路找下去
>gettext_lazy = ugettext_lazy = lazy(gettext, str)

需要研究一下。

---

##2018.06.01
Django中延迟加载如之前所述，核心实现在lazy函数，该函数的包为`django.utils.functional`
里面很绕。。。实际上，lazy方法返回的就是一个装饰器，所以平时也可以使用@lazy来装饰需要延迟的函数，这里直接使用lazy(gettext, str)实际上就是把gettext给装饰了，返回一个代理对象，之后调用的都是这个代理对象了。
这个对象修改了自身的`__str__`函数，因为是调用是才会执行对象的`__str__`函数，所以实现了延迟加载，即调用时加载。
另外，gettext是python国际化函数，即翻译成不同语言的函数。
（是真的绕。。。。。）
实际的lazy函数为：
>def lazy(func, *resultclasses):

涉及这么几个知识点：

* （核心）返回的是一个代理类，而不再func运行结果（哪怕本来返回的就是一个类）
 1. 代理类的`@total_ordering`装饰器
    * 表示对象可进行比较大小，需要对象实现`__lt__`、`__eq__`等方法。实现后，该装饰器会解析允许对象实例进行<、=等运算符号操作。
    * 这样返回的代理类就可以进行运算符比较了，用于实现原本返回结果的运算符比较
 2. 代理类初始化的`__prepare_class__(cls)`方法
    * 这个方法在代理类被初始化时被调用。这个方法主要的作用，就是将resultclasses，即返回对象，的方法函数全部拷贝到这个代理类中
    * 另外就是确定返回对象的序列化方式，`str` or `bytes`
    * 这样就可以直接通过代理类调用原本返回对象的方法函数（而且调用方式一致，对外看不出区别）
    * ~~不得不说这里面是真的绕，在这里看了好久才大致理清逻辑~~
 3. lazy返回装饰器上的`@wraps(func)`装饰器
    * 这个装饰器属于Python内置包`functools`，作用就是把func的属性拷贝到装饰器对象中，避免了一些如`__name__`等属性调用异常
    * ~~这个是拷贝原本func的属性方法，`__prepare_class__`是拷贝返回对象的属性方法，你们真是够了~~

————（今天完全在看源码了。。说些看的过程中涉及的觉得需要记一下的东西）————

* mro()
    * 这个方法是获取类的继承列表的，类调用，实例不具有该方法
    * python中的继承是列表式，在类、实例调用自身不具有的方法或属性时，会依次查找该基础表，由左至右返回第一个找到的调用结果。所以在python可以是用多继承，实际继承结果按照此规则实现。
* `hasattr(cls, method_name)`、`getattr(cls, method_name)`、 `setattr(cls, method_name, meth)`
    * 判断类是否具有对应名称的属性/方法、获取对应名称的属性/方法、动态绑定属性/方法到类对应名称上。
    * 上面那些拷贝操作基本就是靠这三个方法实现的。~~秀我一脸~~
* 另外有个比较在意的地方，lazy不能作用于同时返回str和bytes的func，这个应该是由于lazy自身`__cast(self)`方法通过if单分歧返回导致，该部分源码如下：
```python
        def __text_cast(self):
            return func(*self.__args, **self.__kw)

        def __bytes_cast(self):
            return bytes(func(*self.__args, **self.__kw))
            
        def __cast(self):
            if self._delegate_bytes:
                return self.__bytes_cast()
            elif self._delegate_text:
                return self.__text_cast()
            else:
                return func(*self.__args, **self.__kw)
```

---

##2018.06.04
今天主要是看了下视图测试部分。
因为之前项目使用的是前后端分离的开发技术，后台Django只用返回json数据给前端，所以使用了rest_framework框架做Rest数据层，开发起来倒是很方便，不过对前端就是一片白了。这次自己开发，抄着教程里面的前端代码，感觉Django自己对于前端的开发支持也是很给力的，开发起来很轻松（前提是我还没有加入样式等复杂的东西。。。）
总之，先来总结一下Django里面关于视图的测试吧。
 
* shell
    还是从shell说起，首先要说的是：因为视图内容往往是加载数据库内容，而shell操作中，不会生成测试用数据库，所以__读写的都是实际数据库__。
    测试环境加载：
>from django.test.utils import setup_test_environment
>setup_test_environment()
>from django.test import Client
>client = Client()
    
    之后就可以通过client实体对象的`get()`、`post()`方法进行模拟请求。
    另外，对于url地址可以使用reverse('app_name:name')，（使用前需要通过`from django.urls import reverse`导入方法），来动态解析url地址，其中，`app_name`在每个`urls.py`中自定义，`name`为`path()`函数的可选参数
    client对象请求后会返回一个response对象，通过response对象的属性来检查视图是否正确运行。
    response对象中，比较重要的有如下属性：
    * status_code
    response状态码，int类型。200_OK，404_NOT_FOUND之类的([详细状态码说明](http://www.runoob.com/http/http-status-codes.html))，一般作为最初的判断页面是否已加载、权限认证之类的。
    * context
    response所包含的上下文信息，比如包含的列表信息等。dict类。一般的测试都是对这个里面的内容进行检测，检测返回内容是否正确。
    * request
    发送的request请求，dict类，可以看到请求信息
* TestCast类
    在测试类中，不用加载测试环境，TestCase类自带self.client对象用于测试请求，而且，在测试环境下使用的__测试数据库__不会再实际数据库中生成数据。
    对于response对象的属性与shell中说明的一致。说下几种新的断言方法：
    * assertEqual(a,b)
    判断a与b是否相等，一般用于status_code值判断
    * assertContains(response, str)
    判断返回结果中是否包含str
    * assertQuerysetEqual(responsec.context['key_word'], [])
    判断返回上下文中数据列表是否与参数2相等（例子中是判断是否为空列）
    __注意__：这个判断方式很神奇的使用的是str匹配的相等判断。。也就是，显示出来的数据库列表是`['< Model: model.__str_ _ >', '...']`，大小写不同、空格不同、字符不同都会导致匹配失败，很是神奇，个人觉得不好用。。。

另外，在今天的测试中，测试的都是`get`接口，前端向后端传递的数据也是固定在`urls.py`中写死了的，目前还不清楚如何灵活的传递，而至于`post`接口，由于django自带的crsf_token机制，使用postman无法测试，client却可以避开这个机制，或者说，他本身就带有了crsf验证。后续需要在这几个方向做研究：
* 尝试在client中添加新的数据信息，然后在TestCase中进行测试。
* 重写基础视图，比如利用ListView实现接收post过滤信息返回过滤后的列表等自定义功能，而不影响原因的分页等功能。

---

## 2018.06.05

从post视图说起走。首先，python的web开发是基于python的web接口——`WSGI`，这个接口的定义非常简单，如下：
```python
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'<h1>Hello, web!</h1>']
```

environ是存放HTTP请求信息的dict类，读取处理请求信息之后构造HTML，通过start_response()发送Header，最后返回Body。

当然，在Django中对这基础框架进行了封装，Django中基础view类的结构为：
```python
# views.py
def view(request, *args, **kwargs):
....
# urls.py 
...
# 注意，传递的是view这个函数
path('test/', views.view, name='test')
...
```

其中，request就是经过Django封装之后的HTTP请求类对象了，args和kwargs是用于解析urls中传递的参数。
然而，每个视图都按照基础视图来书写，很费时费力，所以Django提供了通用视图，如ListView等，可以很快捷的实现视图书写。
在使用通用视图时，对urls.py里视图的绑定需要进行修改，以上面的例子修改一下：
```python
# views.py
class TestView(generic.ListView):
....
# urls.py 
...
# 注意，传递的是as_view()的结果值
path('test/', views.TestView.as_view(), name='test')
...
```

* `as_view()`函数
    * 这个函数是View类的类函数，在启动Django服务，运行到urls.py时执行，用于初始化视图对象并进行绑定。
    * 其他的流程暂时不管，主要的是其内部定义的一个内部函数`view`，源码如下，`as_view()`函数返回的就是加工后的内部view对象。
    ```python
            def view(request, *args, **kwargs):
                self = cls(**initkwargs)
                if hasattr(self, 'get') and not hasattr(self, 'head'):
                    self.head = self.get
                self.request = request
                self.args = args
                self.kwargs = kwargs
                return self.dispatch(request, *args, **kwargs)
    ```

* `dispatch()`函数
    * 如上文所述，`urls.py`中绑定的是view方法和url地址，而不是view()函数结果。所以，通过`as_view()`绑定后，请求实际是传递到了view方法中，最终返回的实际是这个`dispatch()`函数的执行结果。
    * 那么看`dispatch()`函数的源码，可以发现，请求到了TestView这一层时，才会根据其请求方式`request.method`来调用具体的执行方式，例如，GET请求调用`get()`方法。同时，可以通过修改`self.http_method_names`来限制请求，或在对应方法中自定义处理方式。
    ```python
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
    ```

~~说了一堆废话，其实就是想说明，就算通用视图不支持GET或POST请求，你也能自己写支持的方式~~
在本次工程中，有这么需求：列出房间列表，并可以通过某些检索方式过滤房间列表。
首先，列出房间列表，通过`generic.ListView`可以很简单的实现，而检索过滤就需要接收前端的额外参数，当然也可以复写`get()`函数，但是一是GET方式数据全在url里面；二是`generic.ListView`复写起来挺麻烦的~~（其实主要还是url太长不好看）~~
于是，在视图中添加`post()`使其具有接收POST请求的方式，通过接收POST数据来进行筛选过滤。
~~因为之前用的`rest_framework`框架，这个框架在中间数据交互上面做了处理，所以改写他的View类很方便，而Django自己带的View要差些~~
总之借鉴一下`get()`函数源码：
```python
def get(self, request, *args, **kwargs):
    self.object_list = self.get_queryset()
    allow_empty = self.get_allow_empty()

    if not allow_empty:
        if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
            is_empty = not self.object_list.exists()
        else:
            is_empty = len(self.object_list) == 0
        if is_empty:
            raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                'class_name': self.__class__.__name__,
            })
    context = self.get_context_data()
    return self.render_to_response(context)
```

主要的地方有这么几个：

* `self.object_list = self.get_queryset()`
    其中，`self.get_queryset()`返回的是一个数据库结果集，若已定义`self.queryset`便返回自身（若设置排序，则返回排序后结果），若未定义`self.queryset`则检查`self.model`，并返回model的全部结果集（排序同上）。
    `self.object_list`属性在后续的`self.get_context_data()`中将加载到返回的response的上下文context中。
* `context = self.get_context_data()`
    生成返回的上下文，是dict类型数据。
    `object_list`默认为`self.object_list`，也可以在函数调用时传入。
    检查视图是否设置分页，若设置分页，将返回分页处理后的数据。
    若设置`context_object_name`属性，则会将数据额外赋值一份到该属性为key的字段中，供前端调用。
* `self.render_to_response(context)`
    通过context生成response。

综上，忽视空集检查，post函数如下：
```python
    def post(self, request, *args, **kwargs):
        filter = request.POST['filter']
        print("[filter]", filter)
        if filter is not None:
            filter = json.loads(filter)
            print("[filter_loads]", filter)
        self.object_list = Room.objects.filter(**filter)
        context = self.get_context_data()
        return self.render_to_response(context)
```

说明：

 1. POST请求的数据，存放于request.POST中，是dict类数据，通过关键字获取，值一定是str类型。
 2. 这里我前端传递的是一个json格式字符串，通过python的json模块进行转换。
 3. Model.objects.filter()中的参数一般格式为(keyword=value)，根据python基础中的函数参数形式，其实等同于(**{'keyword':value})，所以，只要前端传递的格式正确，就可以一次筛选了。~~不过由于dict类型的key值唯一，所以每个key值的筛选只能进行一次~~


存在问题：

 1. tag是一个自定义的JSONField数据，一般来说存放的应该是一个list的json化string，如何实现检索？
 2. **filter方式每个key值只能检索一次的问题。~~（虽然我觉得不是问题）~~
 

---

##2018.06.06

~~前端是个坑，但是我还是得跳进去。。。~~

简单设计一下大致界面，首先主页大致如下：
![布局图](/main_page.png)

* 布局说明
头部是标题栏，一些无关紧要的欢迎词之类的。
左侧是房间列表，显示现有的房间列表。
右侧是用户列表，显示当前在线用户。
下侧是信息栏，用于显示聊天记录。

* 动作说明
可以通过点击房间列表中的房间名进入不同的房间。
进入房间之后，房间列表刷新为房间内部页面。
用户列表页面刷新为房间内角色页面。
信息栏进入房间信息列表。

接下来是相关技术点：
~~晚上回去补~~

* AJAX（jQuery）
    * 首先，AJAX是现有标准的新方法，而不是新的编程语言。
    * AJAX提供的一种异步请求方式，经常用在页面动态获取、局部更新的地方。
    * AJAX中的核心对象为XMLHttpRequest，实现了异步与服务器交互数据
        * 在低版本ie中，使用new ActiveXObject("Microsoft.XMLHTTP");创建对象。
        * 在高版本ie中，使用new XMLHttpRequest();创建对象。
        * 构建request的函数`open(method, url, async)`
            * `method`——请求类型：GET/POST
            * `url`——请求地址
            * `async`——同步（false）/异步（true）
        * 编辑请求头函数`setRequestHeader(header, value)`，如定义form表单提交POST等。
            * `header`——头字段名
            * `value`——头参数值
        * 发送request的函数`send(string)`
            * `string`——仅用于POST请求，用于附加参数（GET请求的参数附加在url中）
        * 服务器返回文本：`xmlhttp.responseText`
        * 服务器返回XML：`xmlhttp.responseXML`，可以通过`getElementsByTagName()`等方式解析
        * __状态变化`onreadystatechange`事件__：
            * `xmlhttp.readyState`状态（他的变化触发绑定在`onreadystatechange`上的函数）
                * 0-请求未初始化（还没有调用 open()）
                * 1-服务器连接已建立（还没有调用 send()）
                * 2-请求已接收（通常现在可以从响应中获取内容头）
                * 3-请求处理中
                * 4-请求已完成，且响应就绪
            * `xmlhttp.status`状态
                * 200-OK
                * 404-未找到页面
                * 其他参见html状态码
    * 虽然AJAX是浏览器通用规范，但是自己实现和调用很繁琐，jQuery是在JavaScript语法中便捷实现了多种AJAX方法的库，能让程序员快捷的使用AJAX方法，需要引入jQuery的相关js文件，[参见其官网](https://jquery.com/)。
    ```html
    <script src="/static/js/jquery-3.3.1.js" type="text/javascript"></script>
    ```
    * `$(selector).load(URL,data,callback);`
        * `selector`是jQuery选择器，用于选择页面元素（参见[jQuery选择器](http://www.w3school.com.cn/jquery/jquery_selectors.asp)）
        * `URL`——必须，用于指定需要加载的地址
        * `data`——可选，一同发送的数据键值对
        * `callback`——可选，`load()`完成后的回调函数
            * `responseTxt`——包含调用成功时的结果内容
            * `statusTXT`——包含调用的状态
            * `xhr`——包含 XMLHttpRequest 对象
        * `$.get(URL,callback);`和`$.post(URL,data,callback);`，获取GET结果和POST结果，返回的是OBJ。
        * __$.ajax({settings_dict}) 自定义的AJAX方法__，settings_dict为可选配置选项
            * `url`——请求地址
            * `type`——请求方式GET/POST
            * `data`——（POST）需要上传的数据
            * `async`——是否异步（true/false）
            * `contentType`——发送到服务器的内容类型
            * `dataType`——预期返回结果类型，如"script"
            * `success(result,status,xhr)`——成功后的处理函数
            * `error(xhr,status,error)`——失败后的处理函数
            * `complete(xhr,status)`——完成后调用的函数（在`success`和`error`后调用）
            
            ```html
            <!--示例-->
            $.ajax({
                url:'test/test.js',
                type:'get',
                dataType:'script',
                success: function(data){
                    console.log(data);
                },
                error: function(xhr){
			        alert("错误提示： " + xhr.status + " " + xhr.statusText);
		        },
		        complete: function(xhr){
			        alert("完成状态： " + xhr.status + " " + xhr.statusText);
		        }
            });
            ```


---

##小插曲

Django2中静态文件放到了工程目录下的static目录，但是在工程启动时却读取不到。
原来在setting.py中设置`STATIC_URL = '/static/'`还不够，还需要补上静态文件地址：
```python
STATICFILES_DIRS = (
    os.path.join('static'),
)
```
然后，在页面加载时，需要先加载static属性：
```html
{% load static %}
<link rel="stylesheet" type="text/css" href="{% static 'polls/style.css' %}" />
```
这样才能获取到地址~~（当然也可以写硬编码就是了。）~~

晚上想在另一台电脑上跑一下工程，安装了最新的MySQL8.0.11，然后发现Navicat12居然连接不上，一搜才发现是MySQL的密码加密方式变了，需要更改加密方式回到5.0版本，[方式连接在此](https://www.cnblogs.com/shiysin/p/shiysin.html)。不过没有尝试不修改加密方式，工程是否能连接到数据库，修改后工程能访问，看来没修改前可能不能访问吧，这个是由连接类实现的，可能中间件并没有更新到8.0吧。

---

## 2018.06.07

~~高考居然没下雨，希望各位考得不错
然后下午就暴雨。。~~
接着昨天的内容继续

* iframe
    iframe是html中的一个标签，基本的浏览器都能支持这个标签，iframe 元素会创建包含另外一个文档的内联框架（即行内框架）。用于实现页面内嵌其他页面，比如实现本工程所需的主页面架构。
    关于iframe和ajax的选择，在CSDN上也有讨论，当然，最后的结果也趋于“看实际情况选择使用”这么一个结论。（[差异见此](https://blog.csdn.net/theoldfuture/article/details/75647034)）
    总的来说，在构建固定板式框架时，用iframe能让前端看着自然而且便于管理一些，比如blog页面之类的。
    不过在这个工程中，我想实现的是主窗口中的按键点击能刷新其他窗口的内容，iframe在相互之间的传值上似乎有点难实现。

好，有关jQuery的基础理论已经了解，那么开始实现如下功能：

![布局图](/main_page.png)

·进入主页之后，自动加载房间列表到room_list，~~（同时加载在线用户列表到user_list）~~。
·房间列表中每个房间附加一个“加入房间”按钮，可以点击进入房间，目前就是请求/room/detail/信息，并将room_list窗口内容替换为房间内部内容，同时将user_list替换为房间内的用户列表。

首先，是实现分栏窗口的加载，如前文所述，可以使用iframe或者ajax，这里我使用的jQuery的ajax，代码如下：
```JavaScript
$(document).ready(function () {
           $("#main_window").load('/room/list/');
           $("#nav_window").load('/user/list/');
        });
```
简单的说就是，页面加载完毕后开始读取房间列表和用户列表。
[说明]
·这里要说明一个问题，无论是`load()`还是`html($.ajax())`，子页面的头样式都会影响到整个页面，即，相当于主页面加载了子页面的css信息。而iframe没有这个问题。目前还不清楚如何避免这个问题，只能选择一个比较完善的框架用于整体了。

然后就是房间列表新增“加入房间”按钮了，当然可以直接在子页面中写按钮的跳转onclick事件，但是还是同一个问题，按钮事件影响的不止是一个子页面，所以先仅仅在子页面中增加按钮，代码如下
```html
...
<td>
    <button class="btn btn-primary join_room" id="{{ room.id }}">加入房间</button>
</td>
...
```
~~class中前面几个是框架样式，不用理会，~~ class中最后一个join_room是我定义的一个类名，让主页jQuery选择器能方便的选择全部“加入房间”按钮。id设置为房间id（因为房间id也是唯一，当然，设置其他属性也可以，~~这是我后面才知道的~~）

好了，最后一步就是关联按钮方法了，我要炫酷的使用动态绑定~~（然后失败了好久）~~。
先给最后的主页JavaScript代码吧，~~（因为还没写加载房间内角色的接口，就先随便写个代替）~~：
```JavaScript
<script type="text/javascript">
        $(document).ready(function () {
           $("#main_window").load('/room/list/', function () {
               $("button.join_room").on('click', function () {
                   var url = '/room/'+ $(this).attr("id");
                   $("#main_window").load(url)
                   $("#nav").load('/user/list/')
               });
           });
        });
    </script>
```
说明：

* 利用`load(url,data,callback)`机制中的回调函数，确保主窗口加载房屋列表完毕之后再调用callback方法。
* 通过`$(button.join_room)`选择全部class含有join_room的button对象。
* 通过`$().on('click', function)`来动态绑定点击事件的方法。
* 获取按钮附加的房间id，（注意，这里的`this`是触发点击事件的对象，即，__被点击的按钮对象__），然后通过`$().attr("id")`来获取`id`值~~（惊了，居然不能直接$().id，那我设置id为房间id毫无意义啊。。）~~
* 通过id构建不同的url，通过`load()`刷新多个页面。

这两天基本工作就是这些，实现主页的前端方式基本路铺通了，接下来就是完善后台提供的网络接口~~和添加测试~~。
期间学了尝试了很多之前没试过的前端知识，算起来这算我3入前端坑了，然而却是第一次自己写JavaScript和找css框架引入。。遇到了很多莫名其妙的bug，什么页面没加载完找不到元素啊，什么选择class使用#去选择返回undefined啊，什么load的callback不执行了啊，总之一步一个坑。~~但是看着一点一点功能实现还是很不错的。~~
Django官网上初步知识剩下一篇是/admin/后台管理页面的配置，这个我准备先放放，所以Django2.0的文档就看了5%~~（已汉化部分）~~，接下来应该就不会一篇一篇的啃了~~（英文差）~~，应该是遇到什么问题再去查相关文档了。
现在准备的就是完善这个页面前后端功能，~~虽然最麻烦的实时聊天功能还不知道怎么来实现，websocket吧，~~之后可能关于理论学习的东西会更新少点，更多的是一些写代码时遇到的问题吧。

~~神™转身遇到坑~~
CreateView，这是Django提供的通用视图之一，用于创建一个Model对象存放到数据库中。当然，对于简单的Model对象，浏览器表单页面与数据库字段一一对应即可。然而在本工程中，以Room类来说，其中gm字段为外键，关联User表，而且这个字段应该默认为发出请求者的User对象。
所以，就需要对这个类进行一定的改造，然而，事情却很麻烦。。。。~~第一，官方文档没汉化这部分（当然内容也不多）~~，第二，网上也没太多2.0相关的。~~我差点就想不用这个类，自己重新写个view，顺便骂一句Django真sb。~~所以我一点一点的看源码。
先梳理一个大致逻辑，CreateView是允许接收GET和POST请求的。

* GET请求默认返回表单页面，页面名由`self.template_name`属性决定，如此一来免去了再写一个关联到表单的借口~~（真香！）~~。
    * `self.template_name`——str类型，同其他View一样，指向了html页面文件
* POST请求则会检查表单内容，生成一个对象存入数据库中。
    * `self.model`属性——生成的模型对象类、不设置这个的话就会去检测self.object和self.queryset来确定。
    * `self.fields`属性——（必需）可遍历类型，表示需要从请求表中获取的字段以及其对应的Model字段。
    * `get_form_class()`函数——获取对象（Model）的form格式，返回一个动态表单类对象（`django.forms.widgets.XXXXForm`）。
    * `get_form_kwargs()`函数——解析request表单内容，生成关键字键值对，传入上面获得动态表单类对象中，生成一个`form`对象，将对象传入`form_valid()`函数中。
    * `form_valid()`函数——简单的操作就是`form.save()`，然后跳转请求到`get_success_url()`函数返回的成功跳转url地址中去。然而，如果需要对输入的值进行处理或者是附加其他属性值，那么就需要在这里进行处理。
        * `form.instance`是一个已经生成，但还没存进数据库的对象，其属性值为request表单中提交的值，未提交的若有default则为default的值__（请记住之前【测试】一段中说的，这个并未存入数据库，故其属性与最终存入数据库字段属性可能存在差异）__，若未提交也无default则为None。~~（顺带说一句，看网上以往的文章，Django2之前似乎具有一个`self.instance`属性来实现这个功能而不是`form.instance`，当然在Django2里面一句没了）~~
    * `form_invalid()`函数——如果request提交的表单中，不满足`self.fields`中的字段，则会跳转到这个函数，通常的操作是返回到表单页面。[需要说明的是，如果`self.fields`异常，即写入的字段在Model不存在，则在进入这个View时就会报错，而不会进入处理流程。]

---

##2018.06.08

* jQuery属性获取：`$().attr('attr_name')`
* jQuery属性修改：`$().attr('attr_name', value)`
* alert——通知栏，仅有一个“确定”返回，用于发布一次性提示。
* confirm——确认栏，具有`true`和`false`返回，可以用于需要用户确认操作的地方。
* `window.location.reload();`整体页面刷新。
* HttpResponseRedirect会导致整个页面跳转，需要找到一个仅刷新某个窗口的方式，可能需要用jQuery来隔断form表单的提交和返回。
    * `e.preventDefault()`阻断浏览器基本操作，如提交表单、连接跳转等。
    * `$.ajax({setting})`中的`dataType`字段取值（一般的表单数据就使用html或直接使用默认）：
        * "xml": 返回 XML 文档，可用 jQuery 处理。
        * "html": 返回纯文本 HTML 信息；包含的 script 标签会在插入 dom 时执行。
        * "script": 返回纯文本 JavaScript 代码。不会自动缓存结果。除非设置了 "cache" 参数。注意：在远程请求时(不在同一个域下)，所有 POST 请求都将转为 GET 请求。（因为将使用 DOM 的 script标签来加载）
        * "json": 返回 JSON 数据 。
        * "jsonp": JSONP 格式。使用 JSONP 形式调用函数时，如 "myurl?callback=?" jQuery 将自动替换 ? 为正确的函数名，以执行回调函数。
        * "text": 返回纯文本字符串

————————
创建房间并进入创建房间的功能实现：

* 前端：
```JavaScript
$("form#create_room").submit(function (e) {
    e.preventDefault();
    var form = $(this);
    $.ajax({
        url: form.attr("action"),
        type: form.attr("method"),
        data: form.serialize(),
        dataType: "html",
        success: function (data) {
            var obj = JSON.parse(data);
            if (obj.state == 0) {
                var room_id = JSON.parse(obj.data).room_id
                var url = /room/ + room_id
                $("input.exit_room").attr('value', "退出房间");
                $("#main_window").load(url)
            }
        },
    })
});
```
* 服务器端
(`JsonResponse`是自定义的一个返回格式，方便统一处理返回数据)
```python
    def form_valid(self, form):
        form.instance.gm = User.objects.all()[0]
        form.save()
        id = Room.objects.get(id=form.instance.id).id
        return HttpResponse(JsonResponse(0, data={'room_id': str(id)}))
```

[说明]
1.`e.preventDefault()`——阻断表单的默认提交操作
2.`form.serialize()`——获取表单内容序列化结果（一般表单就是xxx=xx&x=xxx这样的格式，所以使用html的dataType来上传）
3.服务器的`CreateView`里的`form_valid()`方法生成Room对象存入数据库，通过Room类默认生成的id读取其存放到数据库内的实际id（·UUID在默认对象中的值和数据库实际存放的值可能格式不一样·中间件会解析UUID的不同格式）
4.服务器返回json，因为请求成功，进入`$.ajax`的`success()`函数处理。
5.前端通过`JSON.parse(data)`函数将json_str解析为obj，可以通过obj.key直接访问对应key的value值。
6.判断obj.state是否为0（也可以设置为true/false，不过考虑到后续可能拓展，所以就用int了），然后解析obj.data获取room_id,再通过room_id生成url进行页面跳转。

[存在问题]
·JavaScript越写越长了，主页看着很笨重，而且多层嵌套，每次都要写很多重复的编码，这个必须要解决。

---


##2018.06.11

简化JavaScript，肯定是要模块化，像这种`$(document).ready()`加载的临时匿名函数，对于固定不变的页面上可以使用，而像这种动态绑定子页面的元素，子页面还不时变化，那不是每次切换回子页面都得重新绑定，子页面刷新也得重新绑定，不合适。
所以讲JavaScript方法提取出来，生成一个`join_room()`的funcation，在子类的html代码中直接绑定到这个方法，这样就不用每次加载时自己写绑定了。
```JavaScript
function join_room() {
    var url = '/room/' +  $(this).attr('id');
    $("input.create_room").hide();
    $("input.exit_room").show();
    $("#main_window").load(url)
    $("#nav").load('/user/list/')
};
```
然而在实际测试时候发现，`$(this).attr('id')`获取的是undefined。
秘制尴尬，当然，也好解决，函数传参嘛，修改一下html和JavaScript代码。
```html
<button class="btn btn-primary join_room" onclick="join_room(this.id)" id="{{ room.id }}">加入房间</button>
...
function join_room(id) {
    var url = '/room/' +  id;
    $("input.create_room").hide();
    $("input.exit_room").show();
    $("#main_window").load(url)
    $("#nav").load('/user/list/')
};
```

设计了一下房间详情页面（和旁边的用户列表页面），如下图

![房间详情页面图](/room_detail.png)

重新讨论一下生成一个游戏房间的初始化过程：

* 生成房间实体类，请求者为房间gm
* 创建房间用户组，基本的游戏玩家组、旁观者组（根据创建时选择是否允许旁观）
* 玩家组默认添加gm
修改代码如下：
```python
def form_valid(self, form):
    form.instance.gm = User.objects.all()[0]
    form.save()
    room = Room.objects.get(id=form.instance.id)
    game_players = Group()
    game_players.room = room
    game_players.type = 1
    game_players.save()
    GroupMember.objects.create(group=game_players, user=room.gm)
    if form.data.get('sidelines_allowed'):
        bystanders = Group()
        bystanders.room = room
        bystanders.save()
    return HttpResponse(JsonResponse(0, data={'room_id': str(room.id)}))
```

另外还要为房间创建基础的记录文本信息。
代码规整如下：
```python
def form_valid(self, form):
    form.instance.gm = User.objects.all()[0]
    form.save()
    room = Room.objects.get(id=form.instance.id)
    game_players = Group()
    game_players.room = room
    game_players.type = 1
    game_players.save()
    GroupMember.objects.create(group=game_players, user=room.gm)
    if form.data.get('sidelines_allowed'):
        bystanders = Group()
        bystanders.room = room
        if form.data.get('sidelines_sendmsg'):
            bystanders.send_msg = False
        bystanders.save()
    dir_path = os.path.join(BASE_DIR, "txt/" + room.gm.username)
    os.makedirs(dir_path)
    txt_path = os.path.join(dir_path, "[" + room.name + "]" + str(time.time()) + ".txt")
    with open(txt_path, 'w') as txt:
        pass
    GameTxt.objects.create(user=room.gm, file=txt_path)
    return HttpResponse(JsonResponse(0, data={'room_id': str(room.id)}))
```

~~前端是真的烦，除了JavaScript之外还有什么便捷的关联两个页面元素的方式呢？~~


看代码的过程中，发现一个问题。
```python
user = User.objects.create()
Room.objects.create(gm=user)    # 这句的objects报了警告，第一句没有
```
其实本来应该没这个异常，网上的解释也很多归结于编译器（可能的确是因为我这里没有设置好django编译器环境）
回看`Room`和`User`类的差异，`Room`类是直接继承于基础的`model.Model`类，而`User`类继承于`AbstractUser`类，后者在基础类上做了进一步加工实现，添加了`UserManager()`作为其`objects`对象，而前者却没有对`objects`的定义。
实际上，`objects`属性即是Django对Model的管理器，在未作出定义的时候，会默认生成一个`Manager()`赋予`objects`对象，这一操作是在`model.Model`的元类`ModelBase`中实现的。

* 关于元类
首先，python一切皆对象：对象是对象，属性是对象，函数是对象，类也是对象。
其次，对象都可以动态生成、赋值、改变。
那么，类也是可以被动态生成、赋值、改变的，而在python中，`class`关键字默认调用了类对象创建过程，生成了一个类对象，因为其具有__创建对象（类实例）的能力__，而这就是为什么它是一个类的原因。
python中对象之间的关系如下:
![python对象之间关系图](/python对象之间的关系.png)
所有的类，都有一个统一的“父类”，（或者这里说“父类”不合适，因为所有类继承于`object`，而`object`才是一个实际的父类），或者用刚刚的说法，“类的默认创建方法”——`type`（当然，他自己也由他自己定义了创建方法）。
`type`以及其继承者，称为__元类__，他们定义了类的创建方法，通过继承`type`，就可以动态的对类对象进行生成。__元类的存在使得类的生成变得灵活以适应更多的需求环境，但是灵活带来的问题也很大，直接影响的就是子类的创建，子类是看不到父类继承的元类的，但子类的创建方式却会使用父类的创建方式，即父类的元类，这种看不见的继承是很难排错的。__
`type`工作方式如下：
`type(类名, 父类的元组（针对继承的情况，可以为空），包含属性的字典（名称和值）)`
比如：
    ```python
    class fclass:
        f = True
        
    x = type('xxxx',(fclass,),{'a':1})
    print(x)   # <class '__main__.xxxx'>
    print(x.a)  # 1
    print(x.f)  $ True
    ```
使用元类，定义类时加入`metaclass`参数，生成的类及其以后继承于他的子类在生成实体对象时，都会调用元类中的`__new__`函数：
    ```python
    class ListMetaclass(type):
        def __new__(cls, name, bases, attrs):
            attrs['add'] = lambda self, value: self.append(value)
            return type.__new__(cls, name, bases, attrs)
    
    class MyList(list, metaclass=ListMetaclass):
        pass
    ```
__为什么父类的元类会改变子类的创建方式？__
元类的机制（Python解释器实现元类的方式）：
·先从类的dict中查找`__metaclass__`，否则从基类的dict查找，否则从global作用域查找，否则使用默认的创建方式。
如果，在父类的元类中向父类注入了一个方法，若继承的子类中定义了同名方法，那么子类在生成实例时，会由于查找调用父类的元类重新注入同名方法导致方法被覆盖，直观的感受就是——重载失败，却没有提示。

回到工程中的问题，`Room`类中的属性`objects`是在父类`model.Model`的元类`ModelBase`中被添加的（添加条件是子类中没有定义自己的`objects`，所以和`User`不冲突）。

---

##2018.06.12

今天的主题是__《Celery从入门到~~放弃~~》__
先说起因：
本来是准备写房间详情中的聊天模块，虽然基本通过多线程控制并发也能实现基本功能，但是想试试新的东西——消息队列。逻辑大致是：request提交对话信息，写入聊天记录的操作请求写入消息队列，由消息队列逐一处理。
Celery就是python使用的一个第三方消息队列，据廖雪峰老师评为“利器”的玩意。
看了下基础python中的实现，的确简单：
```python
# tasks.py
import time
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def sendmail(main):
    print('sengding mainl to %s...' % mail['to'])
    time.sleep(2)
    print('mail sent')
```
启动Celery
>celery -A tasks worker -l info

发送任务
```python
from tasks import sendmail
sendmail.delay(dict(to='xxx@xx.com'))   # celery.task装饰器方法
```
显得非常的美好，也当得上利器之名，好，开始往Django上弄。
一开始也是很顺利的样子：有一个django的中间件django-celery。
安装之后照着网上一通配置。
__失败。。。__
Django2.0之后Django方面变化挺多的，导致之前有的一些教程方法不适用。
然后发现了Celery4.0+Django2的配置教程，顺带一手`pip list`发现django-celery关联的Celery只有3.x。
__唔。。。__
卸载了django-celery，安装上Celery4.1。
失败。。。。原因是Celery4.1不支持windows（简单说就是有些过程没有做跨平台的分歧处理导致有些windows下没有的属性被调用）
一通搜索，发现在4.1.1中修复了这个问题。。。。
升级到Celery4.1.1
配置开始：
0、修改`setting.py`
```python::setting
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672'
```
1、新建`celery.py`文件（工程目录下）
```python::manage.py
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_world.settings')

# 注册Celery的APP
app = Celery('dice_world')
# 绑定配置文件
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各个app下的tasks.py文件
app.autodiscover_tasks()
```
2、修改`__init__.py`文件
```python::__init__.py
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ['celery_app']
```
3、app目录新建`tasks.py`
```python::tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def add(x, y):
    return x + y
```
4、在工程目录下启动celery
>celery -A tasks worker -l info

5、shell测试
```python::shell
from apps.game_manager.tasks import add
add.delay(2, 3)
```
成功发出。
6、查看celery处理结果
__异常。。。。~~简直想把这个吃了！神™之前一路正常最后一步出错了~~__
~~冷静~~
看控制台打印，启动时，celery找到了工程中被task注释的方法：
>[tasks]
  . game_manager.tasks.add

却报出异常：
>[2018-06-12 13:31:57,394: ERROR/MainProcess] Received unregistered task of type 'apps.game_manager.tasks.a
dd'.
The message has been ignored and discarded.

>Did you remember to import the module containing this task?
Or maybe you're using relative imports?

>Please see
http://docs.celeryq.org/en/latest/internals/protocol.html
for more information.

>The full contents of the message body was:
'[[1, 2], {}, {"callbacks": null, "errbacks": null, "chain": null, "chord": null}]' (81b)
Traceback (most recent call last):
  File "C:\Users\Yu\Envs\django2\lib\site-packages\celery\worker\consumer\consumer.py", line 557, in on_ta
sk_received
    strategy = strategies[type_]
KeyError: 'apps.game_manager.tasks.add'

看上去，原因应该是，celery检查task是以app路径开始的，但是传输的key是以工程目录作为根路径，导致了key不匹配。。。。。完美。

在深入研究到可以修改设置或源码来解决这一问题之前，我先选择妥协的创建了一个专门管理celery_tasks的app，非常屈辱。。。

4、在工程目录下启动celery
>celery -A tasks worker -l info

5、shell测试
```python::shell
from celery_tasks.tasks import add
add.delay(2, 3)
```
成功发出
6、查看celery处理结果
__异常。。。。~~我™~~__
~~冷静~~
查看控制台输出：
>[2018-06-12 14:53:12,036: ERROR/MainProcess] Task handler raised error: ValueError('not enough values to u
npack (expected 3, got 0)',)

好嘞，又是windows不兼容问题，简单说就是这个使用的池子windows里面没有，解决方案就是用别的池子。
>pip install eventlet

4、在工程目录下启动celery
>celery -A tasks worker -l info -P eventlet

5、shell测试
```python::shell
from celery_tasks.tasks import add
add.delay(2, 3)
```
成功发出
6、查看celery处理结果
__异常的成功了！__
咳咳，居然成功了。
以下是add.delay(2,5)和add.delay(6,7)的控制台打印：
>[2018-06-12 14:55:40,633: INFO/MainProcess] Received task: celery_tasks.tasks.add[404a5bcc-cb5b-432c-aa0d-
4edd0c98b1c8]
[2018-06-12 14:55:40,635: INFO/MainProcess] Task celery_tasks.tasks.add[404a5bcc-cb5b-432c-aa0d-4edd0c98b1
c8] succeeded in 0.0s: 7
[2018-06-12 14:55:48,948: INFO/MainProcess] Received task: celery_tasks.tasks.add[e30586ef-6205-4257-a86c-
d4fedcbb0257]
[2018-06-12 14:55:48,949: INFO/MainProcess] Task celery_tasks.tasks.add[e30586ef-6205-4257-a86c-d4fedcbb02
57] succeeded in 0.0s: 13


总结：
一路曲折，还没算之前就搭建好的RabbitMQ环境([参考](https://www.cnblogs.com/yunweiqiang/p/7248141.html))，最终还是跑起来基本用例，要运用于实际的功能中还得花时间研究一下，主要就是celery的配置文件之类的，当然还有celery的处理结果数据库存储也还没配置。此外，celery还有定时任务等可配置的功能。
总的来说，celery功能还是比较强大的样子。
但是，性能方面，看网上有人说celery在处理大量数据时会有未知异常发生。可以说的确是从入门到放弃了。
不过就这个工程来说，还是想把他用上，顺便还能复习一下redis相关知识和redis在python中的调用之类的知识。

附录
`__init__.py`的功能：
~~其实我本来只是觉得`__init__.py`这个文件就是一个标识目录为python包的标志，然而这次配置celery的过程中却发现居然还要在`__init__.py`里面写代码，惊了。~~
·标志目录为python包，让程序中可以`import`导入【__然后惊讶的发现python3.3之后已经可以不需要这个文件了，不过出于后面的考虑，还是加上的好__】
·也就是说，`import`操作其实执行的是`__init__.py`文件内容，那么：
    1.可以在`__init__.py`文件中写`import`，当目录包被`import`时，`__init__.py`文件中`import`的类会自动导入。同理，也可以在`__init__.py`中进行别的编码，都会在其目录包被`import`时执行。需要注意的是，因为python中会经常用到`import`，所以不应该在`__init__.py`中写太多编码，尽量留空。
    2.具有一个`__all__`的列表属性，用于实现`from xx import *`的导入操作，该操作实际导入的就是`__all__`列表中的类。

---

##2018.06.13

工作中遇到了一个bug，正好可能以后这工程也会用上，就在此记录一下。
__python的动态引入`__import__`__
python中，一般的包引入是通过`import`关键字进行，引入之后实际上是在当前环境中引入了引入内容，其实际的执行方式为：
>import sys # ===> sys = __import\__('sys')

所以，import其实就是`__import__`

`__import__`是一个函数，接收一个`str`作为参数，返回值是一个模块对象，可以通过返回值调用。

 1. `__import__`只会在第一次执行时新引入对象到内存中，之后再次`__import__`实际上只是将内存地址引用过来而已。这就导致了，对于一个程序，如果已经执行了`__import__`语句，且一直在运行，那么，原模块发生变化，这个程序在重新加载模块之前是不会发现变化的。
    * 重新加载，`reload()`，会重新加载已加载的模块，但原来已经使用的实例还是会使用旧的模块，而新生产的实例会使用新的模块；
        * `reload()` 后还是用原来的内存地址；
        * `reload()` 不支持 `from ××× import ×××` 格式的模块进行重新加载。
 2. `__import__`的查找顺序：sys.path
 

~~惊了，$.ajax怎么上传表单数据。。。。form有没有onsubmit属性。。。。。~~
今天弄了一个房间的对话文本内存记录，用于临时记录对话文本，然而发现前端通过ajax发送表单后端获取不到数据。。。因为是写在`main.html`的js中，所以只定义了一个方法，由`form`中的`button`type按钮触发的`onclick`事件调用。
然而。。。。没有submit的form获取不了其他input标签的输入内容。。。。。。。

---

##2018.06.14

`onsubmit`句柄倒是有，但是是提交之前时点触发。
然后我发现是因为前段form表单中的`<input>`标签如果其`name`字段为空，则不会出现在表单中，异常现实。。。。。

处理房间页面功能，主要就是实现一个聊天室功能，还是先走通路。

定义了一个Model类用于记录每个房间的文本，考虑到文本属性和数据库性能，采用文件形式存储文本内容，数据库记录文本路径。
然而用于html页面显示的话，使用服务器返回文本似乎有点傻，而且也不便于添加，于是定义了一个`GameTxtPhantom`用于记录房间的文本，后期可以设置内容超过多少条便写入文件存储，或是由房主通过“保存”功能存储。
大致设计结构描述如下：每个__房间（Room实例）__具有一个__`GameTxtPhantom`__，__`GameTxtPhantom`__中具有一个文本字典，字典存放多个列表，列表元素为__`CharaterTxt`__。
```python
class GameTxtPhantom:
    txt_dict = {}   # {'state' : CharaterTxt}

    def get_by_state(self, state):
        if not self.txt_dict.get(state):
            self.txt_dict[state] = []
        return self.txt_dict.get(state)


class CharaterTxt:

    def __init__(self, name, content, time):
        self.name = name
        self.content = content
        self.time = time

    def __str__(self):
        return self.name + "(" + str(self.time) + ")" + ":" + self.content

...
txt_board_storeroom = {}    # {'room_id': GameTxtPhantom}
```

另外，由于之前脑子抽了，直接返回了JsonResponse，导致Django的render在解析返回时失败。应该的形式是HTTPResponse(JsonResponse)。
虽然是自己脑子抽了，但是的确说明个问题，为什么不重构一下JsonResponse来直接返回呢。。。

```python
class JsonResponse(HttpResponse):
    '''
        {'state':0,'msg':'xxxx', 'data': 'JsonObj'}
    '''

    def __init__(self, state, msg=None, data=None):
        super().__init__()
        self.state = state
        self.msg = str(msg)
        self.data = data
        self.content = self.__str__()

    def __str__(self):
        res = {}
        res['state'] = self.state
        if self.msg:
            res['msg'] = self.msg
        if self.data:
            res['data'] = json.dumps(self.data)
        return json.dumps(res)
```

接下来就是关于聊天室实现的方法了。
有下面这些需求：

* 留言板周期刷新，添加显示新文本，周期不宜过长。
* 发送文本之后立即刷新留言板，应能显示发送的文本。
* 准备了两个不同的聊天版面，两个的内容互不影响。（先把基础的实现了再说。。）
* 针对游戏文本，应该能显示GM这次游戏开始到当前的全部信息；针对闲聊文本，可以只用显示加入房间以后的文本。（还是先实现了基础的再说）

虽然JavaScript的周期任务实现还没看，但那是技术实现的问题，现在在考虑如何设置请求能实现添加新文本的功能，是由前端记录显示了的文本，还是前端通过什么方式发送状态给后端让后端来返回不同的数据显示。（因为存在多个客户端同时访问的情况，所以不能由服务器来决定返回，必须基于客户端的状态来决定）

前端传递时间戳，第一次传递null，获取`GameTxtPhantom`存放的全部文本，获取返回值时，从返回值中解析新的时间戳作为下一次请求参数。

 1. python中的`str`转`datetime`的方法：`datetime.datetime.strptime()`
    * 函数接收两个参数（必须），`date_string`和`format`，前者为字符串时间，后者为解析格式。`%Y-%m-%d %H:%M:%S.%f`接收'1900-01-01 23:30:24.123234'格式的时间字符串。主要的就是，不同的字母（大小写有关）代表了不同的接收范围，比如%y是[00,99]，而%Y是四位数记年。([参考](https://zhidao.baidu.com/question/384981086.html))
 2. datetime的时间增减，当前时间往前推7天：
 >datetime.datetime.now() + datetime.timedelta(day=-7)

---

##2018.06.15


JavaScript设置定时和周期任务的方式：`setTimeout`和`setInterval`。


* 定时任务（延迟任务）:`setTimeout()`
    * 启动语法 
    >var delay_task = setTimeout("function()", delay_time);

    * 停止语法 
    >clearTimeout(delay_task);

    * 执行效果，function会延后delay_time(毫秒)开始执行，只执行一次。
* 周期任务：`setInterval()`
    * 启动语法 
    >var cycle_task = setInterval("function()", interval_time);

    * 停止语法 
    >clearInteral(cycle_task);

    * 执行效果，function会延后interval_time(毫秒)开始执行，执行完毕后，再过interval_time(毫秒)再次执行。

看着很简单，但是用起来却有几个要注意的点。

 1. function可以传入参数，虽然整体是以字符串形式传递给JavaScript，但是参数会正确解析，包括对其他元素值引用的参数也一样。
 2. JavaScript并不是多线程，所以，对于周期任务和延迟任务，其实现并不是通过多线程实现，而是通过一个类似于消息队列的形式实现。setTimeoue和setInterval实际上是将function插入到队列中，在设置的延时时间到达后，尝试执行function，但若当时主线程没有空闲，则会进入等待，等待主线程空闲后再执行（setInterval的任务会在执行完成后重置计时器）。所以，__设定的延时时间到达后，任务不一定会按时执行，切记。__


---

##2018.06.20

正则表达式获取骰子指令：`.ndm text`，其中，n为骰子数目，m为骰子面数，text为骰点原因。
n可选且默认为1，m必须，text可选。
正则表达式为：`r'^\.([1-9][0-9]*)?d([1-9][0-9]*)(\s)*(.+)?$'`
说明：

* .在正则表达式中为任意非\n字符，所以需要用\.来转义匹配.
* n为可选项且默认为1，首位不能为0，允许大于1整数，且允许为空
* m与n一致，只是不允许为空
* 贪心匹配任意数量空白字符后获取text文本

django自带的用户认证系统：
```python
from django.contrib.auth import authenticate, login

class Login(generic.View):

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/html/main.html")
        else:
            return HttpResponseRedirect("/html/login.html")
```

方便倒是很方便写，通过自带的authenticate函数认证用户名和密码，返回user对象，通过login函数将用户绑定到request上（通过session）
当然，django也自带了很多通用的登录视图，有多种方法可以实现([官方文档](https://docs.djangoproject.com/zh-hans/2.0/topics/auth/default/#django.contrib.auth.forms.AuthenticationForm))，然而，问题是，原生的django中，对需求登录认证的视图、请求，是通过`login_required`装饰器实现的。。主要问题在于，没找到这个装饰器全局设置的方式，这就很难受了。
另外，在实际使用的时候，发现报了异常，debug发现request在验证user属性的时候，当user为空时，报错。。。但在看异常返回时，request又加上了user属性。。所以这个user属性是在什么时候附加的？？


---

##2018.06.21

debug之后发现，传入装饰器的对象居然是View类对象实例。仔细看`login_required`源码：
```python
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
```
这个装饰器方法将第一个参数作为`request`，然而，在通用视图类中，第一个参数为`self`即，类实例本身，故引起bug。
解决办法是：因为`login_required`作用的是原生的view方法，所以，在urls.py中添加限制即可（因为`as_view`返回的就是一个标准view对象，因此可以被`login_required`装饰），如下：
```python
app_name = 'room'
urlpatterns = [
    path('list/', login_required(views.ListRoom.as_view()), name='room_list'),
    path('create/', login_required(views.CreateRoom.as_view()), name='room_create'),
    ...
]
```

发现前端setInterval和setTimeout有时候会发生重复请求，即同一时间点两个请求都执行，导致了聊天记录重复（因为在自己发送信息之后，会刷新聊天记录，如果时间点正好到周期刷新时，就会添加两条刚刚发送的信息，然而实际的服务器记录只有一条）说好的js单线程呢。
状况不明，只能在每次发送完毕的complete回调函数中取消之前的setInterval对象，再重新建立。
```JavaScript
function post_message() {
    $.ajax({
        url: room_chat_form.attr('action'),
        type: room_chat_form.attr('method'),
        data: room_chat_form.serialize(),
        complete: function () {
            clearInterval(refresh_txt)
            setTimeout("refresh_txt_board(room_chat_form.attr('action'))", 0);
            refresh_txt = setInterval("refresh_txt_board(room_chat_form.attr('action'))", 1500);
       }
    });
}
```

Django的CreateView真好用~~（真香）~~，可以自动接收前端页面的表单文件上传并保存到对应字段，可以说很不错了。
一些注意的点：

* 在CreateView的`fields`属性列表中，会自动检查数据的有效性性，比如字段为UUID，则会要求表单提交的也是UUID
* 前端表单在提交上传文件时，需要增加属性`enctype="multipart/form-data"`
* `input`标签的`type='image'`并不是上传图片。。。。上传图片请依然使用`type='file'`，并加上`accept="image/png, image/jpg, image/jpeg"`来筛选文件
* `accpet="text/csv"`在chrome上似乎没有起效
* CreateView中接收的文件会默认保存到工程根目录，可以在model中修改字段设置来规定默认目录
* 另外，由于想要复用这个页面，我增加了一个hidden的id字段在前端表单中，由Django在解析页面时填写值，添加上下文的方式。

    ```python
    return render(request, 'index.html', {'data': data})
    ```
    然后就可以在前端像下面这样获取
    ```HTML
    <div>{{ data }}</div>
    ```
* 但是在传递给js时，需要进行修改，首先js传递的是json：

    ```python
    return render(request, 'index.html', {
                'List': json.dumps(list),
            })
    ```
    然后前端获取的时候要添加safe过滤
    ```JavaScript
    var List = {{ List|safe }};
    ```
    
    ---
    
    ##2018.06.22
    
    [好文共享](http://daily.zhihu.com/story/9686651)
    
    ---
    
    [关于协程](http://python.jobbole.com/87310/)
    关于协程，虽然生成器部分大致掌握了基本，然而协程却没了解多少，至少，在之前的开发中，最终平没用用到协程，而是通过生成器同步完成的功能。
    其原因就在于，没有用到asyncio包。
    在没有调用这个包的情况下，底层的yield由自己来写，并没有生成如asyncio.sleep这样的异步操作。而是仅仅把yield作为生成器使用，不间断返回处理状态，实际上依然是同步操作，和直接写子程序for循环没有区别。
    那么，应该要做的就是了解asyncio包内容，看里面有没有能够用上的方法函数，让这个操作异步起来。
    在async/await语法中，await所修饰对象有限制([详细参见](http://python.jobbole.com/86481/))，需要返回一个具有`__await__(self)`函数的对象（即awaitable对象），而这个对象必须返回一个非协程迭代器。当然，协程本身也是一个awaitable对象。
    很迷。
    
---

##2018.06.25

最近感觉又陷入重复机械劳动循环中了，没有获取新的知识，只是在反复的调试和码代码，困扰。

今天添加了几个新的model对象，用于管理游戏相关数据，以文本形式存放如任务物品信息等，另外创建一个关联房间、任务的中间model对象记录任务进度。
然后就是开始写单元测试，说实话之前一直说写都没有写，因为觉得很麻烦，特别是加入了登录认证之后，的确不知道怎么来写，不过今天还是去啃了一下。
client的登录通过，client.login(username=, password=)来实现，登录之后client保存session数据，client为已认证状态。
需要注意的是，由于在测试中使用的是测试数据库所以，在登录之前需要生成一个用户，生成用户需要使用`create_user`，而不是`create`，不然password不会加密，使用password登录异常。
因为登录之后client是保存的session，目前我还不知道如何获取其中的user信息，所以，在创建一些关联到用户表的数据时，外键比较麻烦，不过正好测试对象的生成表单页面，也就没管了。但是就有下面这个问题了，单元测试中的文件传输问题。
因为很多解构是关联了文件field的，所以需要上传文件作为输入，虽然在数据库中是以`str`路径来保存的就是了。。。
解决方式如下：
```python_test
User.objects.create_user(username='test', password='123456')
        self.client.login(username='test', password='123456')
        with open('文件上传测试.txt', 'r') as f:
            response = self.client.post(reverse("character:character_create"),
                                        {'name': 'test1', 'sex': 0, 'head': None, 'detail': f})
```
另外，今天看了Django的Form表单类，发现很是方便，笔记如下：

Form表单类是Django中用于连接数据库model和前端html的一个胶水类，能够很方便的生成html表单代码，并提供输入验证等实用功能。
定义Form类有两种方式：

* 继承forms.Form
    ```python
    from django import forms
    class ContactForm(forms.Form):
        subject = forms.CharField(max_length=100,label='主题')
        message = form.CharField(widget=forms.TextArea)
        sender = form.EmailField()
        cc_myself = forms.BooleanField(required=False)
    ```
    
    其中，每个需要输入的字段都由forms中相关字段（field）生成，这些field与model中的field基本可以相互对应，Form类也就是通过这些field来进行数据的输入验证、html代码转化等操作。
* 继承forms.ModelForm
    ```python
    #models.py
    class Contact(models.Model):
        title = models.CharField(max_length=30)
        content = models.CharField(max_length=20)
     
    #form.py
    class ConotactForm(forms.ModelForm):
        class Meta:
            model = Contact
            field = ('title','content') #只显示model中指定的字段
    ```
    
    forms.ModelForm简化了Form的生成，直接用Model中的field来生成Form中的field，很是方便。CreateView中就使用的第二种方法，动态生成一个ModelForm用于生成和接收表单，调用的方法为`get_form`。

Form类可以通过传入request.POST数据（一个dict类）来生成一个关联至model的实例，通过实例的`is_vaild`方式来进行数据输入验证。或者直接空数据生成表单数据返回前端，通过`as_p`等方法在前端调用转化为对应标签显示。

* Form的前端显示
    简单的方式直接就是在前端通过`{{ form }}`来获取上下文中的'form'对象用于显示，需要注意的是，这种显示就是最基础的显示，没有做任何的改动修饰。通常使用中，会通过`as_p`等方法将form每一个属性加上`<p>`标签，同理还有`as_ul`等方法。
    
实际使用中，由于使用的CreateView，所以很多操作由Django代为完成，总得来说效果不错，但是有些字段，如性别、状态码字段，为了方便以后拓展，设置为int类型，CreateView转化的就是一个数值输入，对用户不友好，需要改为选择窗口，需要对`get`方法进行改写。
```python
def get(self, request, *args, **kwargs):
    # 在get_context_data时，会注入一个object对象，然而这个类不具有这个属性，需要设置为None不然会报AttributeError，莫名其妙。
    self.object = None
    form = self.get_form()
    # form的字段存放在fields中，是一个dict类型数据，更换为选择field
    # choices元祖中的元素元祖，第一个值为实际传值数据，第二个值为显示值。
    # label为显示到html中的名称。
    form.fields['sex'] = forms.ChoiceField(choices=((0, '男'), (1, '女'), (2, '其他')), label='性别')
    # CreateView的get_context_data方法，在不传入form时，会自动调用get_form方法获取form并填入。
    return self.render_to_response(self.get_context_data(form=form))
```
通过`as_p`生成的前端代码如下（居然自己生成了个id）：：
```html
<form id="create_character" action="/character/create/" method="post" enctype="multipart/form-data">
    <p><label for="id_name">角色姓名:</label> <input type="text" name="name" maxlength="64" required id="id_name" /></p>
<p><label for="id_sex">性别:</label> <select name="sex" id="id_sex">
  <option value="0">男</option>
  <option value="1">女</option>
  <option value="2">其他</option>
</select></p>
<p><label for="id_head">角色头像:</label> <input type="file" name="head" id="id_head" /></p>
<p><label for="id_detail">角色资料文件:</label> <input type="file" name="detail" required id="id_detail" /></p>
    <input type='hidden' name='csrfmiddlewaretoken' value='Jc1JrI6nZn6CBKVy6y6N0fTwJ9744QrNSpoMFZP3yu44RvB5tdVBNRnokSe9pRv4' />
    <input type="submit" value="提交">
</form>
```