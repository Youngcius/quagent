# User Manual


> Last updated: May, 2022<br>
> Editor: [Zhaohui Yang](https://youngcius.com) (zhy@email.arizona.edu)

In comparison with the [design document](./design.md), this manual 



[Demonstration Video](Demonstration%20-%20Quantum%20Network%20Testbed.mp4)







## Interface with Agilent iLab


#### Usage of iLab API

1. Customer: initiate a service *request* in iLab
2. Core: review the request and provide a *quote*
3. PI/Lab/Admin: approve *financials* when required
4. Core: 处理request，通过API下载加密文件和数据from custom forms，
5. Core: 更新service数量delivered in iLab，通过API，添加charges收费
6. Core: review the request, click "complete" on the project in iLab and then creates a billing event with those charges at hte end tof the month



#### Necessary ingredients

- Client ID: identify a client application to your core's API (识别客户端对core's API的申请)
- Token: associated with the client, provide a designated level of access to data through the API



## Operation Example

The former section demonstrates the general pipeline of high-level request, response and monitoring. 
Herein we illustrate how users conduct an entire quantum experiment only using this local Quagent software.


### Resources request and response


### Data acquisition







