# Quagent: Quantum Agent

Quantum network local agency software (web operation software)

English | [简体中文](README_CN.md)

![](static/images/profile.png)

[![](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE) [![](https://img.shields.io/badge/build-passing-green)]() ![](https://img.shields.io/badge/Python-3.7--3.8-blue) ![](https://img.shields.io/badge/dev-v1.0.0-blue)

Quagent is the shorthand of "Quantum Agent", a universal operation software for application in Quantum Local Network.
While it depends on some necessary hardware at the same time. Currently, the `qugent-v1.0.0` is a development plan
aiming to facilitate multi-access research and teaching on quantum information experiments, initially for the demand of
the National Science Foundation (
NSF) [Major Research Instrumentation (MRI) #1828132](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1828132&HistoricalAwards=false)
award project. This operation software will be hopefully applied to the series of experimental platforms of
the [Center of Quantum Network](https://cqn-erc.org/) at the University of Arizona. Our final goal is to provide a
universal technical prototype for quantum networks in terms of the local agent terminal.

## Quagent v1.0.0

[comment]: <> (![]&#40;https://release-data.bd.bcebos.com/Quanlse_architecture_en.png&#41;)

We have been trying to enrich and improve Quagent's architecture. The figure below presents its domain framework.

**framework**:

1. Application cases:
2. Function
3. Soft-Hardware interface:
4. Hardware Platform: 3 Entangled-Photon Sources, 8 Single-Photon Detector Channels

## Usage

### Usage via Agilent iLab operation software in UA

Although Quagent can run independently in some internal laboratories at the University of Arizona, it is actually a
technical prototype but not a released business software. And the independent project "Quanget" is mainly aimed to
develop and test continuously. In the stable application scenarios of U Arizona, Quagent is integrated with iLab
operation software supported by Agilent Inc. Thus if you are a supported user of the iLab system of U Arizona, you can
begin to use it conveniently via iLab.

### Download and install via GitHub

For development and research necessity, downloading the last universal prototype software is from GitHub.

```bash
git clone git@github.com:Youngcius/quagent.git
```


## Feedbacks

Users are encouraged to contact us through [Github Issues](https://github.com/Youngcius/quagent) or
zhy@email.arizona.edu with general questions, bugs, and potential improvements. We hope to make quagent better together
with the community!

## Frequently Asked Questions

**Q: Where should I get to know more about Quagent?**

**A:** The [NSF MRI #1828132](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1828132&HistoricalAwards=false) award
project description is a good illustration. If you have more demand or cooperation willingnes, please contact to
the [Quantum Information and Materials Group](https://quantum.lab.arizona.edu) of U Arizona.

**Q: How can I get to start Quagent if I am faculty or student of U Arizona?**

**A:** You can contact ot related people at U Arizona or get more information from
the [corresponding website](https://ua.ilab.agilent.com/landing/3645).

**Q: Can I use Quagent via iLab if I am not a faculty or student in U Arizona?**

**A:** Quagent is not a pure-software application. It's framework and application scenarios are closely dependent on
corresponding hardware platforms. Currently it is applied to the serial systematically linked laboratories of U Arizona.
So if you are not a person in U Arizona, there is no necessity for you to use it. But if you are a researcher in related
fields, you can build your own hardware supports and modify Quagent accordingly if possible.


## Copyright and License

Quagent uses [Apache-2.0 license](LICENSE).


