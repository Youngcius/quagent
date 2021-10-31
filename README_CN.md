# Quagent: Quantum Agent
Quantum network local agency software (web operation software)


[English](README.md) | 简体中文


[![](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE) [![](https://img.shields.io/badge/build-passing-green)]() ![](https://img.shields.io/badge/Python-3.7--3.8-blue) ![](https://img.shields.io/badge/release-v1.0.0-blue)

[comment]: <> ([quagent &#40;Quantum Agent&#41;]&#40;https://quanlse.baidu.com&#41; is a cloud-based platform for quantum control developed by the [Institute for Quantum Computing]&#40;https://quantum.baidu.com&#41; at Baidu Research. Quanlse aims to bridge the gap between quantum software and hardware. It provides efficient and professional quantum control solutions via an open-source SDK strengthened by Quanlse Cloud Service.)

Quagent (Quantum Agent) 是一个用于量子局域网络 (Quantum Local Agent) 是通用操作软件。


## Quagent v1.0.0

**注意：本次量脉v2.1的升级，进行了大幅更新与完善，我们强烈建议用户升级至量脉v2.1版本！**

![](https://release-data.bd.bcebos.com/Quanlse_architecture_cn.png)

我们一直致力于丰富并完善量脉的架构。在本次2.1版本的升级中，我们对量脉基础架构进行升级，进一步提升了用户体验并完善了实验室坐标系下的建模与仿真；在超导平台方面，我们新增了含读取腔的量子比特标定与脉冲校准功能，并提供了完整的教程；并新增了两量子比特含噪模拟器、含可调耦合器件的两量子比特模拟器及其分析工具。

## 安装

为了提供最佳用户体验，我们强烈建议使用 [Anaconda](https://www.anaconda.com/) 作为研发环境并更新依赖项到最新版本。

### 通过 pip 安装

我们推荐通过 `pip` 完成安装

```bash
pip install Quanlse
```

### 版本更新

如果已经安装了 Quanlse，那么可以用如下命令更新

```
pip install --upgrade Quanlse
```

### 通过 GitHub 下载安装

用户也可以通过 GitHub 下载全部文件后进行本地安装

```bash
git clone http://github.com/baidu/Quanlse
cd Quanlse
pip install -e .
```

### 运行示例程序

现在，您可以尝试运行示例程序来验证量脉是否已成功安装

```bash
cd Example
python 1-example-pi-pulse.py
```

## 入门和开发

### 概述
在开始使用量脉之前，我们建议用户首先通过阅读[简介](https://quanlse.baidu.com/#/doc/overview)了解该平台。然后，[快速入门](https://quanlse.baidu.com/#/doc/quickstart)将会一步一步地引导您如何使用量脉云服务，以及如何使用量脉来构建您的第一个程序。接下来，我们鼓励用户在[教程](https://quanlse.baidu.com/#/doc/tutorial-construct-ham)里学习量脉提供的更多应用案例。最后，我们鼓励用户能够使用量脉解决科研和工程问题。有关量脉 API 的完整文档，请阅读我们的 [API 文档页](https://quanlse.baidu.com/api/).

### 教程

量脉提供了从基础到进阶主题的详尽教程，用户可以通过我们的[网站](https://quanlse.baidu.com)进行学习。对于有兴趣的科研工作者或开发者，我们建议下载并且使用 [Jupyter Notebooks](https://jupyter.org/)。教程的内容如下：

+ **量脉超导**
  + [构造哈密顿量](https://quanlse.baidu.com/#/doc/tutorial-construct-hamiltonian)
  + **单量子比特控制**
    + [单量子比特门](https://quanlse.baidu.com/#/doc/tutorial-single-qubit)
    + [基于梯度算法的脉冲优化](https://quanlse.baidu.com/#/doc/tutorial-GRAPE)
    + [校准 $\pi$ 脉冲](https://quanlse.baidu.com/#/doc/tutorial-pi-pulse)
    + [DRAG 脉冲](https://quanlse.baidu.com/#/doc/tutorial-drag)
  + **双量子比特门控制**
    + [iSWAP 门](https://quanlse.baidu.com/#/doc/tutorial-iswap)
    + [Controlled-Z 门](https://quanlse.baidu.com/#/doc/tutorial-cz)
    + [Cross-Resonance 门](https://quanlse.baidu.com/#/doc/tutorial-cr)
  + [量脉调度器](https://quanlse.baidu.com/#/doc/tutorial-scheduler)
  + **误差处理**
    + [误差分析](https://quanlse.baidu.com/#/doc/tutorial-error-analysis)
    + [随机基准测试](https://quanlse.baidu.com/#/doc/tutorial-randomized-benchmarking)
    + [零噪声外插抑噪方法](https://quanlse.baidu.com/#/doc/tutorial-ZNE)
  + **含噪模拟器**
    + [单量子比特含噪模拟器](https://quanlse.baidu.com/#/doc/tutorial-single-qubit-noisy-simulator)
    + [多量子比特含噪模拟器](https://quanlse.baidu.com/#/doc/tutorial-multi-qubit-noisy-simulator)
    + [含耦合器的两量子比特模拟器](https://quanlse.baidu.com/#/doc/tutorial-two-qubit-simulator-with-coupler-architecture)
  + **量子比特标定与脉冲校准**
    + [读取腔标定](https://quanlse.baidu.com/#/doc/tutorial-readout-cavity-calibration)
    + [单量子比特标定](https://quanlse.baidu.com/#/doc/tutorial-single-qubit-calibration)
    + [Controlled-Z 门脉冲校准](https://quanlse.baidu.com/#/doc/tutorial-calibration-cz)
  + [基于脉冲的 VQE 算法](https://quanlse.baidu.com/#/doc/tutorial-pbvqe)
+ **量脉离子阱**
  + [单/双量子比特门](https://quanlse.baidu.com/#/doc/tutorial-ion-trap-single-and-two-qubit-gate)
  + [广义 Mølmer-Sørensen 门](https://quanlse.baidu.com/#/doc/tutorial-general-MS-gate)
+ [量脉核磁](https://quanlse.baidu.com/#/doc/nmr)

## 反馈

我们鼓励用户通过 [Github Issues](https://github.com/baidu/Quanlse/issues) 或 quanlse@baidu.com 联系我们反馈一般问题、错误和改进意见和建议。我们希望通过与社区的合作让量脉变得更好！

## 常见问题
**Q：我应该如何开始使用量脉？**

**A：** 我们建议用户访问我们的[网站](https://quanlse.baidu.com)并遵循以下路线图：

- **步骤1：** 进入[快速入门](https://quanlse.baidu.com/#/doc/quickstart)了解如何访问量脉云服务。
- **步骤2：** 学习[单量子比特控制](https://quanlse.baidu.com/#/doc/tutorial-single-qubit)和[双量子比特控制](https://quanlse.baidu.com/#/doc/tutorial-iswap)的例子来熟悉量脉。
- **步骤3：** 研究更多进阶应用，探索量脉更多的可能性，例如：[量脉调度器](https://quanlse.baidu.com/#/doc/tutorial-scheduler)、[误差处理](https://quanlse.baidu.com/#/doc/tutorial-error-analysis)、[多比特含噪模拟器](https://quanlse.baidu.com/#/doc/tutorial-multi-qubit-noisy-simulator)、[含耦合器件的两比特模拟器](https://quanlse.baidu.com/#/doc/tutorial-two-qubit-simulator-with-coupler-architecture)、[量子比特标定与脉冲校准](https://quanlse.baidu.com/#/doc/tutorial-readout-cavity-calibration)以及[基于脉冲的 VQE 算法](https://quanlse.baidu.com/#/doc/tutorial-pbvqe)

**Q：我的 credit points 用完了该怎么办？**

**A:** 请通过 [Quantum Hub](https://quantum-hub.baidu.com) 联系我们。首先，登录 [Quantum Hub](https://quantum-hub.baidu.com)，然后进入“意见反馈”页面，点击“获取点数”，然后输入必要的信息。提交您的反馈并等待回复。

**Q：我应该如何在研究工作中引用量脉？**

**A：** 我们鼓励研发人员使用量脉进行量子控制领域的相关工作，请通过如下 [BibTeX 文件](Quanlse.bib)引用量脉。


## 版权和许可证

量脉使用 [Apache-2.0 license](LICENSE) 作为许可证。

## 参考文献

[1] [Quantum Computing - Wikipedia](https://en.wikipedia.org/wiki/Quantum_computing).

[2] [Nielsen, Michael A., and Isaac L. Chuang. *Quantum Computation and Quantum Information: 10th Anniversary Edition*. Cambridge: Cambridge UP, 2010. Print.](https://doi.org/10.1017/CBO9780511976667)

[3] [Werschnik, J., and E. K. U. Gross. "Quantum optimal control theory." *Journal of Physics B: Atomic, Molecular and Optical Physics* 40.18 (2007): R175.](https://doi.org/10.1088/0953-4075/40/18/R01)

[4] [Wendin, Göran. "Quantum information processing with superconducting circuits: a review." *Reports on Progress in Physics* 80.10 (2017): 106001.](https://doi.org/10.1088/1361-6633/aa7e1a)

[5] [Krantz, Philip, et al. "A quantum engineer's guide to superconducting qubits." *Applied Physics Reviews* 6.2 (2019): 021318.](https://doi.org/10.1063/1.5089550)