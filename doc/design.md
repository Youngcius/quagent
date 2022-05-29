# Systematic Design of Quagent

> Last updated: May, 2022<br>
> Editor: [Zhaohui Yang](https://youngcius.com) (zhy@email.arizona.edu)

## Hardware Layout

### Quantum Network Layout

The following figure shows which laboratories (nodes) are connected to the central service (hub) that generate entangled
photons and receive photons to detect.

![](../static/images/profile-new.png)

Although Quagent can support 16 terminal users, i.e., 16 laboratories or 16 nodes, currently there are 13 nodes totally,
connected directly to each subhub respectively.

### Current Hardware Resources

- high-quality Entangled-Photon Sources (5 kinds of telecom entangled photons)
- 5×16 & 8×8 fiber switches (for routing control)
- 1 Superconducing Nanowire Single-Photon Detector (8 channels)
- 1 Time Tagger (ultimate counting device with 8 channels)

### Channel Linkage with Fiber Switches

As for the connection capability of our platform, obviously it can support maximum 16 user nodes (16 lab platforms),
each with 5 EPs channels and 4 SNSPD channels linked to fiber switches. While currently there is 13 built laboratory
nodes in
the quantum network at University of Arizona.

![switch-linkage](../static/images/switch-linkage.png)

This network status figure demonstrates that, in the meantime, there are at most 5 nodes occupy the entangled-photon
source channels, and at most 8 nodes occupy the single-photon detector channels, which are supported by the 5x16 fiber switches and 8x8 fiber
switches, respectively.

## Font-end & Back-end Technologies

Unlike a classic Web or Web-based software, dominant points of our system lie in the back-end logic and other supporting
technologies like data visualization.

### Choices & Considerations

- Django: A popular back-end business framework based on Python
- ECharts: A powerful, interactive charting and visualization library for browser, base on JavaScript
- MySQL: Most popular open-source relational database management system
- Axios: Asynchronous request tool library of AJAX
- Semantic UI: A development framework that helps create beautiful, responsive layouts using human-friendly HTML
- Simple UI: A user-friendly administrative UI framework than native backstage UI of Django
- TODO: how to deploy

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. We use Django
framework to support functionalities of HTTP requirements and responses, database operation and real-time monitoring. In
our software, users are provided by a series of friendly interfaces including configuring user-specific parameters of
connected devices as well as real-time data acquisition. Particularly, data acquired by the counting device could be not
only easily shown on the Web dashboard, but real-timely downloaded to users, in form of JSON files.

Apache ECharts is a free, powerful charting and visualization library offering an easy way of adding intuitive,
interactive, and highly customizable charts to serial commercial products. It is natively written by JavaScript, while
it also provides easy-to-use interfaces for Python. The latter is what we mainly used in Quagent, since in this way data
visualization programs can be natively embedded in back-end business logic codes.Specifically, In the `monitor` module,
JavaScript-based ECharts library is used to implement geographical information visualization, integrated with Google
Maps APIs. In the `acquire` module, the series of measurement results are shown via Python-based PyECharts, in forms of
Histogram, Count Rate and other types of figures. This is taken into account to for more convenient when writing
back-end processing logics.

MySQL is the most popular relational database management system at present. It is widely used in small and medium-sized
websites on the Internet. It has the advantages of small volume, fast speed and low overall cost of ownership. This
project involves multiple data tables. MySQL is a good choice. In fact, only on the final distribution stage we will use
MySQL. While in the development and testing stage, we just use the built-in database SQLite of Django, just for
convenience.

Asynchronous requesting and local refreshing are absolutely necessary for Web programs in real scenarios. AJAX (
Asynchronous JavaScript and XML) is a standard and web development technique to realize this. While Axios is a
JavaScript library that helps developers use AJAX easily, or, it is a "promise"-based encapsulation of AJAX. In our
project, functions of Axios library are used in HTML pages to acquire data forms updated by users, which are then sent
ot back-end views functions.

Semantic UI a full semantic-designed front-end framework. Due to its ease of use, flexibility and abundant documents and
examples support, it is chosen to beauty the font-end profile.

The administrative program of Quagent use SimpleUI to implement a more fashion interface. It is easily embedded in this
software by
some additional configurations in the setting program of Quagent.

## Software Architecture

This software consists of four modules:

- `acquire`: data acquisition functionalities
- `hubinfo`: information query and parameter configuration, as the first step for users' operation
- `monitor`: part of back-end management system
- `foreign`: interface connected to iLab Web API

### Functionalities of Modules

#### 1. `acquire` module

The structure of `acquire` module is as follows. Two points are particularly taken into consideration to implement
it: 1) *global variable* presenting the unique but shared hardware resources, e.g., Time Tagger; 2) abstract
*user-specific measurement instances* providing non-conflicting measurement settings and data acquisition operations.

For the first point, a source file `globvar.py` is maintained in this module, whose inner initialized variables might be
called by other views functions.

```text
acquire
├── __init__.py: in this script, global variable "tagger" gets initialized by Swabian TimeTagger API
├── measurement
│   ├── strategy.md
│   ├── views_correlation.py
│   ├── views_countbetweenmarkers.py
│   ├── views_counter.py
│   ├── views_histogram.py
│   ├── views_startstop.py
│   └── views_timedifferences.py
├── admin.py: built-in module, automatically generated by Django
├── apps.py: built-in module, automatically generated by Django
├── globvar.py: global variables, like "tagger" and serial dynamic dictionary data consisting of user-specific measurement cases 
├── models.py: built-in module, automatically generated by Django, in which we define the UserDetector class
├── urls.py: routing function
├── utils.py: a set of directed utility functions for this module
└── views.py: view functions, as processing implementation of routing functions from urls.py
```

For the second point, it is realized based on related data structure and global dynamic variables. We define
the `UserDetector` class to present one specific user-measurement pair.

```python
class UserDetector:
    """
    Pair of one User and one Measurement instance
    """
    detector_types = ['Counter', 'CountBetweenMarkers',
                      'StartStop', 'Correlation',
                      'TimeDifferences', 'Histogram']

    def __init__(self, username: str, mode: str):
        """
        Initialize object, set its username and measurement mode
        """
        self.username = username
        if mode not in self.detector_types:
            raise ValueError('{} is not a supported measurement mode'.format(mode))
        else:
            self.mode = mode
        self.detector = None
        self.config = None

    def create_detector(self, tagger: tt.TimeTagger):
        """
        :param tagger: Time Tagger instance
        """
        if self.config is None:
            raise ValueError('You should set UserDetector.config property before creating it detector instance')
        self.detector = getattr(tt, self.mode)(tagger, **self.config)

    def set_measure_config(self, **kwargs):
        """
        Set configuration parameters for its specific measurement mode
        """
        self.config = kwargs
```

To maintain dynamic updating of user-specific measurement cases, six global variables corresponding to six measurement
modes, named `usr_<detector mode>_map` (`dict` data type in Python) are pre-defined in `globvar.py` file.

```python
user_cnt_map = {
    'u01': user_counter,  # UserDetectorinstance
    'u02': ...,
    ...
}
user_corr_map = {
    'u01': user_correlation,  # UserDetector instance
    'u02': ...,
    ...
}
usr_cbm_map = ...
usr_hist_map = ...
usr_stsp_map = ...
usr_tmdiff_map = ...
```

#### 2. `hubinfo` module

This module is for users to review their personal information, configure parameters and reserve instrument resources.
As mentioned above, each effective lab (we call it a physical user) are connected with ECE hub via 4 detecting channels
and 5 entangled-photon sources channels. Logically, the Web interface for each user is like the following figure.

![](../static/images/usage-hubinfo.png)

For testing and demonstrating, one authorized user can arbitrarily book/release EPs or SPDs resources (channels), and
Quagent will automatically approve that request and process them successfully. In actual scenarios, Quagent will
process strictly by time of approved reservations of iLab and release resources when booked time is end, by means of
Web API of iLab.

In detail, this module is building on two classes: `EPsLinks` and `SPDsLinks`. For instance, four data fields
of `EPsLinks` are:

- `user`: the built-in `User` instance,
- `in_ch`: index of the channel connected to the Entangled-Photon source platform
- `out_ch`: index of the channel connected to the user terminal
- `linkage`: whether the fiber switch changes to this link identified by `in-ch`-`out_ch` pair
- `in_use`: whether the linkage is used in field (not all links whose `linkage` are True are used by users)

Each tuple of the four data fields with represents a fiber link for Entangled-Photon distribution. As the hardware-level
setting, there are totally 80 tuples, i.e., 80 records of the table. When `linkage` is `False`, the `in_user` field must
be `False`;
when `linkage` is `True`, `in_use` might be `True` but not necessarily. Similarly, the role of `SPDsLinks` represents a
data table
recording all links status of the 8*8 fiber switches.

When Quagent is firstly installed on one platform, the two tables will be initialized by two text files `eps.csv`
and `spd.csv`
that are pre-generated by a script. In the 80 `EPsLinks` (and 64 `SPDsLinks`) records, only 5 (and 8) data
fields `linkage` are `True`.
While all the `in_use` data fields are `False`. It means an initial status. Then two switches will change their
connections to
corresponding channels. That is how Quagent initialize status of all the switches links.

#### 3. `monitor` module

This module facilitates the administrator to view the real-time fiber network status, i.e.,
who are using EPs or SPDs links. Since detailed linkage status are demonstrative by the built-in
database views automatically integrated in the administrative page. Currently, the `monitor` module only provide
real-time maps monitoring functionalities, which is algo manually integrated in the administrative page.

![](../static/images/network-status.png)

Like the above figure shows, red circles presents that entangled photons are flowing from ECE hub to terminal labs, and purples circles
shows that photons to be detected are flowing from terminal nodes to ECE hub.

#### 4. `foreign` module

Quagent can realize time-based resource reserving by itself, but for real-scenario usage, more supports need to be considered.
For example, facilities usage requires charge. For another consideration, it is better to be integrated with the existing instruments sharing
platform currently. In that way more accounts and laboratories information can be utilized conveniently. Currently, UArizona use a 
CrossLab (iLab), a mature solution in this field. Here int the steps about how to dynamically allocate/release instrument resources
for users based on their reservation data from iLab.
- Query recent reservation data via iLab Web API every a fixed anticipated interval. For instance, if the interval is 15 minutes, user's reservations cannot be changed if current time is less than 15 minutes from the usage appointment.
- If there is any reservations in this anticipated interval, calculate the specific time interval from its appointment time.
- For such a reservation in the anticipated interval, two timers (for allocating and releasing resources, respectively) are created and will be triggerred in corresponding time intervals.  

Usually, the period of such a query loop is equal to the fixed interval, e.g., 15 minutes. Quagent will also send reminder emails to 
users once their reservations is less than the anticipated interval from the usage appointments when queried. Because the applicable 
reservations on iLab are non-flict ordered, as long as Quagent querying and allocating/releasing operations in order, the scheduling process will not occur conflict in 
resources allocation.


Since 16 terminal nodes corresponds to 16 user groups, for one user logining into Quagent, Quagent will distinguish which laboratory he/she
belongs to and perform an internal logining operation. The desirable loging approach is connecting Google Gmail account logining API, since the 
fundamental email system of UArizona NetID is exactly Gmail. As for the mapping relationships between users and laboratory groups, they can be
acquired from iLab in advance.



[//]: # (每隔15分钟query一下iLab中的数据（request -- response）)

[//]: # (意味着在某个appointment开始前的15分钟之内不能够再变动)

[//]: # (如果有15分钟之内要执行的appointment，就计算具体的时间差（比如9分钟），等待该时间差后把仪器给这个appointment对应的Lab group，)

[//]: # (同时如果查到有15分钟之内的appointment的话即刻发mail remainder)

[//]: # ()
[//]: # (解决冲突方式：先来后到)

[//]: # (某个时间段内某个resource被两个不同user请求时，iLab administration平台中不应该审核通过？)

[//]: # (如果local quagent中确实检查到两个或多个不同user在同一时间段请求同一个resource，或者resource被某个用户的使用周期还没有结束却仍然被他人请求，应该用算法判别然后发mail)

[//]: # (reminder告知资源占用appointment取消)

[//]: # ()
[//]: # (建立起物理user id（16个）和用户组id（也是16个）的映射)

[//]: # ()
[//]: # (Google gmail登录，UANetID登录)

[//]: # (UANetID登录)

[//]: # (登录后根据NetID判断所属用户组id，然后内部实现物理user id的登录，这对用户是透明的，用户以为是自己的登录)

[//]: # ()
[//]: # (十六个用户的密码随机化，自己也不能知道)

[//]: # (### Design Mode)

[//]: # ()
[//]: # (- Single-case mode: we use `globvar.py` to store the dominant abstracted variables ...)

[//]: # (- Multi-case mode: )


## Release Scheme

Docker, ... host PC

访问方式，局域网，域名





## Scheduling Strategy of Quagent

![quagent-shceduling](../static/images/strategy-with-ilab.png)


The internal scheduling strategy has been described previously, which corresponds the connection between "iLab Operations Software" and
"Local Agent Software" two parts in the figure above. For users, what they are directly exposed are also just the two parts.
Both parameter configuration and data acquisition are finished in a consistent manner. That is, other components in the above figure are
transparent to users.

For detailed operations, a demonstrative [video](../doc/Demonstration%20-%20Quantum%20Network%20Testbed.mp4) is for reference.
And the [manual document](./manual.md) illustrates how users conduct an entire quantum experiment only using this local
Quagent software.







