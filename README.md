# Odoo平台集成钉钉应用
**最新说明**
>本分支基于dingtalk-sdk，安装：pip install dingtalk-sdk
>请在odoo.conf配置文件里添加下面三个参数：
din_agentid = xxxxxxx
din_corpid = dingxxxxx
din_appkey = dingxxxxxxx
din_appsecret = xxxx
>token保存在redis里，请在服务器里安装并配置好redis服务器。


**前言**：
>
> 本应用主要基于OdooERP开发，支持社区版和企业版，当前版本仅支持12版本及最新的13版本（master版） 开发者可自行下载后根据实际情况进行增加完善和调整功能。 **但是我希望能尊重作者的劳动成果，不要改动作者信息。谢谢~** 
> 
> 注意： **因功能模块还在测试和开发中，导致功能不完善和存在bug，强烈建议个人测试使用，不要将本模块用于商用！如果私自商用造成的任何问题和后果请自行负责！**
> 
> 在使用本模块前，请先将钉钉中你创建的E应用或微应用权限放开和配置出口ip，得到钉钉应用的 **AppKey**和 **AppSecret**， 至于钉钉后台中的配置请参照：>https://open-doc.dingtalk.com/microapp/bgb96b 
>
> **博客地址： https://sxfblog.com/index.php/archives/371.html**  
> 
> **QQ群：1019231617 欢迎加入群进行钉钉集成Odoo开发、共同努力完善集成钉钉的功能**
> 
> 安装完成后需要设置用户权限才能看到基础配置项

**模块列表**

| 模块名            | 模块功能                                                 |
| ----------------- | -------------------------------------------------------- |
| ali_dindn         | 钉钉主模块(基础资料、配置、参数、同步功能)               |
| dindin_approval   | 审批模块(暂时未开发表单，待后续完善)                     |
| Dindin_attendance | 钉钉考勤模块(依赖odoo原生出勤模块)                       |
| Dindin_calendar   | 钉钉日程模块                                             |
| dindin_callback   | 钉钉回调管理模块                                         |
| dindin_dashboard  | 简单的仪表盘模块                                         |
| dindin_login      | 钉钉扫码登录、免登模块，需要到钉钉后台配置相应的回调域名 |
| dindin_message    | 钉钉消息模块，可发送单据备注消息到指定人或钉钉群会话     |
| dindin_report     | 钉钉日志模块                                             |
| dindin_usersign   | 钉钉用户签到模块                                         |
| dindin_workrecord | 钉钉待办事项管理                                         |
| dingding_health   | 钉钉运动                                                 |
| dingding_hrm      | 钉钉智能人事                                             |

-**主要功能：**

- **仪表盘**  (v1.0)
  > 用于显示**我的待办**、**公告数**、**待审批数**、**消息**等相关信息
  >
- **消息**  (v1.0)
  > 1.工作消息：
  > 工作消息是odoo向钉钉工作通知中推送相关消息
  - 消息通知(v1.1)

  > 1. **工作通知消息**：是以企业工作通知会话中某个微应用的名义通知到员工个人，例如审批通知、任务通知、工作项通知等。
  > 2. **群消息**：向钉钉群发送消息，仅限企业内部开发使用。
  > 3. **普通消息**：员工个人在使用应用时，通过界面操作的方式把消息发送到群里或其他人，例如发送日志的场景。
  >
  > 2.消息模板：
  > 用于odoo各种单据创建后向钉钉推送相关单据的基本信息
  >
- **待办**  (v1.5)
  > 1.待办列表：
  > 显示相关待办列表，并更新相关待办事项
  >
  > 2.发起待办：
  > 在odoo中向钉钉中发起待办
  >
- **考勤**  (v1.4)
  > 1.考勤组：
  > 拉取钉钉相对应的考勤组及考勤组成员
  >
  > 2.打卡列表：
  > 拉取钉钉人员打卡信息，手动进行拉取，每次只能拉取7天的打卡信息
  >
- **签到**  (v1.3)
  > 1.签到记录：
  > 获取钉钉相对应的签到记录
  >
  > 2.用户签到记录：
  > 用户签到记录
  >
  > 3.部门签到记录：
  > 部门签到记录
  >
- **审批**  (v1.3)需结合oa协同办公模块使用
  > 1.审批模板：
  > 获取钉钉相对应的审批模板
  >
  > 2.审批单据关联：
  > 关联协同办公中相关的审批流程
  >
- **回调管理**  (v2.0)
  > 1.回调管理列表：
  > 对应钉钉开放平台相关回调类型**通讯录事件、群会话事件、签到事件、审批事件**
  >
  > 2.钉钉回调管理：
  > 创建、注册、获取钉钉回调事件
  >
- **智能人事**  (v1.3)
  > 1.员工花名册：
  > 获取钉钉员工花名册
  >
  > 2.离职员工信息：
  > 获取钉钉离职员工信息
  >
- **设置**  (v1.0)
  > 1.基础设置：
  > 用于设置钉钉各种API接口信息
  >
  > 2.系统参数列表：   
  > 存放钉钉提供的外部各种接口地址和token值等 （Token值不会马上更新，在钉钉-设置-系统参数列表中查看，默认为0000）(v1.0)
  >
  > 3.钉钉消息类型：
  > 用于和钉钉通讯的消息类型
  
- **手动同步基础信息**   (v1.1)
  >
  >在对应的联系人、员工、部门看板视图或列表视图中可点击同步按钮，拉取钉钉中的数据，也可将odoo系统中的数据上传至钉钉中，目前仅支持单个上传，批量上传将   >会在下个更新版本中体现
  >
- **通讯录管理(用户、部门、联系人)** (v1.2)
  >
  > 实现在odoo中删除(员工、部门、联系人）时，自动将信息传递至钉钉，做到实时将odoo的信息与钉钉同步；该功能需在设置项中灵活开启。
  >
  
### 常见问题：
- **安装odooDingDing或者升级其中模块时候请注意**
  >
  > 1.一定要通过主模块ali_dindin进行安装、升级，以免出现错误！
  >
  >
- **钉钉扫码登录后会报错：Internal Server Error**
  >
  > 1.一般这样的问题不是程序出错，请检查钉钉->设置中的扫码登录AppId、扫码登录appsecret。
  >
  > 2.检查钉钉后台中的。移动接入应用并配置好回调地址(即odoo地址) http://ip:port/web/action_login
  >
  > Ip:port为对应的IP地址和端口    /web/action_login 为回调函数。（现阶段未做优化，在回调管理中创建回调事件的时候请填写对应服务器地址）
  >
  > 安装扫码登录以后，记得修改所有账号的密码，不然会出现Internal Server Error错误！！！！！
  >
- **仪表盘：获取公告失败,详情为:无效的USERID、代审批数、公告数**
  >
  > 这个错误通常情况是在刚安装完成时出现的，但不影响使用，安装完成后在设置->钉钉设置中，配置好钉钉API应用信息。手动或自动同步钉钉上的员工数据到odoo中后就不会出现这样的问题
  >
- **拉取考勤组成员的时候提示： 考勤组有更新,请先拉取最新的考勤组!**
  >
  > 那就点击 拉取考勤组成员 旁的 拉取考勤组即可
  >
- **考勤组成员列表无法更新**
  >
  > 钉钉未提供odoo上更新考勤成员的api。故无法自动推送到钉钉服务器
  >
- **协同办公 提交审批后，已通过钉钉审批单odoo中未更新状态**
  >
  > 1. 检查odoo钉钉中的审批模板是否存在
  > 2. 检查odoo钉钉中审批单据关联是否正确
  > 3. 重要： 钉钉回调管理是否配置正确并已注册
  >
  > 满足以上三点即可正常使用审批同步
  > 
  > odoo中的审批单据中的信息无法回传到钉钉的审批单中，请知悉
  >

- **财务审批中的表单需要自动生成凭证(日记账分录)，则需要配置凭证模板，位置：协同办公->设置->凭证模板**
  >
  > 1.审批表单只支持单行输入框、多行输入框、图片、明细(只能包含单行输入框、图片)三种控件,请对应odoo上的审批模板对钉钉审批模板进行调整
  >
  > 2.拉取钉钉审批单以后，请前往钉钉->审批关联中进行配置
  >
- **若看不到的请检查权限**
  >
  >钉钉回调管理： 注册时一直提示 《返回非susssuccess》
  >
  > 这是因为实际情况拓展了odoo原生的http.py文件而导致的。
  >
  > 解决办法是： 将dindin_callback模块中的file文件夹下的http.py文件 覆盖/替换到`odoo-root/odoo/http.py`文件
  >
  > Odoo-root: 为odoo源码目录
  >
- **关于通讯录管理(员工、部门、联系人)**
  
  >
  > 拉取用户时候，请先拉取部门，再拉取用户不然会报错
  >
  > 拉取用户以后记得和odoo系统中相关账号进行绑定操作（用户-HR设置关联）
  >
  > 已经存在odoo联系人中的联系人如果需要上传到钉钉通讯录，请完善负责人和标签，不然无法进行上传到钉钉
  >
