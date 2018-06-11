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
        method: form.attr("method"),
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
(`JsonResponse`是自定义的一个放回格式，方便统一处理返回数据)
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
