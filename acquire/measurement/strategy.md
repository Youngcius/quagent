# User-Specific Measurement Instance Strategy


## 数据结构

```python
class UserDetector:
    """
    Pair of one User and one Measurement instance
    """
    detector_types = ['Counter', 'CounterBetweenMarkers',
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
        self.detector = getattr(tt, self.mode)(tagger, **self.config)

    def set_measure_config(self, **kwargs):
        """
        Set configuration parameters for some specific measurement mode
        """
        self.config = kwargs
```

`UserDetector` 属性：
- mode: 6 种测量类之一
- username：用户名，important
- detector：与用户绑定的测量 case，e.g. tt.Counter()
- config：作为实例化测量 case 的传入参数，e.g. tt.Counter(**config)

`UserDetector` 方法：
- create_detector: ...
- set_measure_config: ...


## 具体策略

host server 端维护一个 `user_detector_map` 全局变量（dict），其内部数据例如
```python
user_counter = {
        'u01': user_counter, // UserDetector instance
        'u02': ...,
        ...
}
user_correlation = {
        'u01':  user_correlation, // UserDetector instance
        'u02': ...,
        ...
}
```


































