# 融合可微分递归特征选择的时空斑块Transformer用于NDVI云隙填补

**Spatiotemporal Patch Transformer with Differentiable Recursive Feature Selection for NDVI Cloud-Gap Filling**

You Chenyu<sup>a,\*</sup>，Wang Yaxiong<sup>a</sup>，Zhou Lv<sup>a</sup>，Xiao Yazi<sup>a</sup>，Jiang Bingbo<sup>a</sup>，Long Xuanyu<sup>a</sup>，Xie Yiyi<sup>a</sup>

<sup>a</sup> 中国电建集团中南勘测设计研究院有限公司（PowerChina Zhongnan Engineering Corporation Limited）

\* 通讯作者：You Chenyu，E-mail: msdi_yu@163.com

投稿期刊：*Geocarto International*　稿件类型：研究论文　投稿编号：269427137

---

## 摘要

光学NDVI时间序列是农业与生态监测的重要数据源。然而，北欧高纬度地区持续的云覆盖会造成长时间数据缺失，从而妨碍土地管理事件的识别。现有云隙填补方法难以利用Sentinel-1与Sentinel-2观测之间的物理互补性，也缺乏不确定性量化，跨年验证亦仍不充分。本文提出一种融合可微分递归特征消除的斑块时空Transformer，用于多模态NDVI云隙填补。可学习门控实现端到端多模态融合；蒙特卡洛Dropout与分割共形预测相结合，可给出校准良好的不确定性估计。实验结果表明重建精度得到提升，所学门控权重与传感器的物理重要性高度一致。不确定性表现出显著的物候依赖性。本方法在95%预测区间上的覆盖率为0.952，并具有良好的跨年零样本泛化性能。

**关键词：** NDVI云隙填补；Sentinel-1/2多模态融合；可微分递归特征选择；斑块时空Transformer；不确定性量化；物候

---

## 1. 引言

### 1.1 研究背景与动机

光学卫星时间序列是农业与生态监测的重要数据来源。归一化植被指数（Normalized Difference Vegetation Index, NDVI）由近红外与红光反射率之比得到，被广泛用作植被绿度的代理指标，并支撑作物长势监测、物候识别以及草地管理事件检测等应用（Rouse et al., 1974; Atzberger, 2013）。然而，光学观测常受云和大气条件的干扰，在北欧高纬度地区尤为突出。生长季内，云覆盖可使Sentinel-2观测中断数周甚至更长，从而在NDVI时间序列中形成大范围缺失，显著降低刈割事件检测、生物量估算等下游任务的可靠性（Kolecka et al., 2018）。因此，重建受云污染的NDVI时间序列，仍是多云地区植被监测中的关键难题。

相比之下，合成孔径雷达（synthetic aperture radar, SAR，例如Sentinel-1）（Kaplan et al., 2018）具备全天候、昼夜均可对地观测的能力。由于微波信号可穿透云层，SAR能够在不受天气条件限制的情况下获取地表信息（Torres et al., 2012）。SAR后向散射强度与地表湿度、几何结构及植被生物量密切相关，从而与光学NDVI形成互补（Mandal et al., 2020）：随着植被发育，冠层结构趋于复杂，雷达后向散射会发生系统性变化，与此同时NDVI同步升高。这种互补性使SAR成为填补光学NDVI缺失的天然辅助信息源；在多云条件下融合SAR与光学NDVI以重建连续时间序列，也已成为遥感云隙填补中广泛采用的范式（Garioud et al., 2021）。

在多模态融合的深度学习方法中，CNN–RNN混合架构具有代表性。Tsardanidis et al.（2024）将Sentinel-1 SAR与光学NDVI联合输入CNN–RNN模型，并在立陶宛草地数据集上实现了有效的NDVI云隙填补（MAE ≈ 0.024，R² ≈ 0.92）。然而，与多数现有方法类似，该工作仍局限于像元级时间序列建模：每个像元被当作独立序列，网络仅利用该像元自身的过去与未来观测进行重建，而未考虑空间邻域信息。实际中，同一地块内相邻像元的植被状态具有高度空间相关性；忽略这一空间上下文，等于丢弃了本可用于约束重建的有用信息。尤其在地块边缘或像元信号受噪声干扰时，单像元时间序列往往难以可靠恢复NDVI。这一局限凸显了引入空间邻域建模的必要性，也直接促使本文发展一种具有稳定跨年性能的高效NDVI重建方法。

### 1.2 相关工作

时间序列云隙填补是遥感分析中的经典任务，传统重建方法主要依赖滤波与插值。Suprijanto et al.（2024）将Whittaker平滑与Savitzky–Golay滤波组合成混合滤波器，用于在频繁云覆盖条件下重建缺失NDVI观测，相较单一滤波方案在精度、时间完整性与稳定性方面均有提升。尽管如此，此类方法仅在单像元时间剖面上进行信号拟合，既无法利用SAR等多源输入，也难以充分恢复刈割等事件引起的植被突变动态。Sun et al.（2023）采用随机森林，融合历史时间序列统计量、同期指标与邻域特征，生成了中国1 km月尺度NDVI数据集，产品质量得到明显改善。即便如此，随机森林仍需耗费人力的手工特征工程，难以刻画长程时间依赖，并且仍受限于单源光学输入。Xiong et al.（2023）利用LSTM网络重建了2000—2021年全球250 m、8天分辨率的NDVI/EVI时间序列产品，以Savitzky–Golay输出和GLASS LAI拟合结果为训练目标，时间连续性得到显著增强。然而，该模型仍仅由光学时间序列驱动，未融合SAR等异构传感器，因而在长时间云隙场景下性能下降。总体而言，传统算法与早期机器学习流程在信息利用上存在明显不足：要么局限于逐像元时间序列拟合，要么未能充分利用多源遥感观测。

在多源深度学习研究中，光学与SAR时间序列的互补融合受到越来越多关注。Garioud et al.（2021）提出基于GRU的SenRVM架构，用于由Sentinel时间序列重建连续植被指数，并在草地、农田和森林样点上进行了验证。但该模型按独立像元运行，忽略空间邻域上下文，也无法给出预测不确定性估计。Appel（2024）采用配备三维时空部分卷积的U-Net架构进行卫星时间序列云隙填补，对不规则缺失表现出较强适应性，并能联合利用时空上下文。不过，该研究面向反射率波段重建，并未引入SAR作为辅助数据。Tsardanidis et al.（2024）将Sentinel-1 SAR与光学NDVI序列输入CNN–RNN混合网络，在立陶宛草地样方上取得了有竞争力的云隙填补性能（MAE ≈ 0.024，R² ≈ 0.92），显示出刻画刈割相关植被变化的能力。即便如此，其实现仍停留在像元序列层面，光学与SAR特征只是简单拼接，并未对其各自贡献进行显式加权或区分。总体来看，Sentinel-1与Sentinel-2融合已在作物制图（El Youssfi et al., 2026）、土壤水分反演以及产量稳定性评价（Košánová et al., 2025）等多样多云场景中展现出良好表现。但具体到时间序列云隙填补，多数现有多源模型仍将每个像元视为孤立的时间序列样本，空间邻域信息并未原生嵌入网络结构，从而限制了空间上下文对重建的辅助程度。

### 1.3 研究缺口

上述文献综述表明，现有NDVI云隙填补研究存在四个关键缺口。

第一，空间邻域信息未得到有效利用。代表性方法（Tsardanidis et al., 2024; Garioud et al., 2021; Sun et al., 2023）主要以像元级时间序列为对象，将各像元独立处理，而未显式引入空间邻域信息。由于同一地块内相邻像元的植被状态高度空间相关，此类上下文可为重建提供关键约束，在地块边缘或像元信号受污染时尤为重要。尽管Appel（2024）将时空部分卷积用于光学云隙填补，该方法尚未扩展到SAR–光学多模态融合，空间信息在多源时间序列补全中的潜力仍基本未被挖掘。

第二，模态贡献未被显式建模，融合过程缺乏物理可解释性。多数方法将SAR的VV/VH与光学NDVI特征等权拼接后作为网络输入，既未区分两种模态的差异化贡献，也未解释SAR辅助光学重建的物理机制。尽管“光学主导、SAR辅助”已是普遍共识，这一共识在模型层面仍缺乏数据驱动证据。经典特征选择方法如递归特征消除（recursive feature elimination, RFE）在训练前静态筛选特征，无法适应输入模式的动态变化。可微分特征选择方法（例如Gumbel-Softmax松弛或可学习门控）可嵌入端到端训练，但其在多模态遥感时间序列补全中的应用仍较罕见。

第三，缺乏经过校准的不确定性量化。在草地管理决策支持等实际应用中，仅有重建得到的NDVI数值并不足以支撑决策，还需要其可靠性信息，对长云隙尤为如此。尽管MC Dropout、分割共形预测（Split Conformal Prediction）和深度集成已在其他领域展现出不确定性量化潜力，当前NDVI云隙填补研究仍以点预测为主，既不提供经过校准的预测区间，也不分析不确定性与物候或管理事件之间的联系。

第四，跨年稳定性尚未得到系统验证。草地物候与管理活动具有显著年际变率，单一生长季内的良好表现并不足以证明跨年稳定泛化。现有工作多在同一时期内评价性能，既未开展跨年泛化测试，也未考察模态融合机制在年际变化下是否保持一致。

为应对上述缺口对重建完备性、可解释性、可靠性与时空泛化能力的制约，本文提出一种引入空间邻域与可微分特征选择的斑块时空Transformer，并辅以经过校准的不确定性量化与跨年泛化验证。在结构设计上，模型以5×5像元邻域为处理单元，将29个时间步与25个空间像元联合编码为725个Token，进行时空联合注意力建模，使重建过程能够同时利用时间依赖与空间上下文。与此同时，通过对CNN–RNN、LSTM、Transformer和iTransformer架构的系统比较，进一步明确了时间序列补全任务“保持完整时间分辨率”这一关键设计准则。在模态融合方面，于Transformer前端引入基于sigmoid软门控的可微分RFE模块，端到端学习各模态的保留权重，使光学与SAR模态的差异化贡献可被显式读取，从而在数据层面实证检验“光学主导、SAR辅助”这一物理共识的有效性。在不确定性估计方面，将MC Dropout与分割共形预测相结合，输出无需分布假设的校准预测区间，并通过分析不确定性与物候阶段的关系，揭示重建可靠性的时变特征。在跨年泛化评价方面，采用零样本与微调两种方式，在2021年数据上验证模型的年际迁移能力，并通过考察门控权重跨年稳定性来评估模态融合机制的时间普适性。

---

## 2. 研究区与数据

### 2.1 研究区

立陶宛位于欧洲东北部，国土面积约65 300 km²。其气候同时受海洋气团与大陆气团调制。按柯本气候分类，该国大部分地区为湿润大陆性气候，仅波罗的海沿岸狭窄地带具有海洋性气候特征。低温、频繁降水及多雪冬季，导致Sentinel-2光学获取在整个生长季持续受到云污染。这些特点使立陶宛成为评价多模态云隙填补算法性能的合适试验场。

该国可划分为四个主要气候区：沿海区、萨莫吉希亚区（Samogitian）、中部低地区和东南高地区。草地是立陶宛的主导土地覆被类型之一，空间分布相对均匀。草地被划分为永久草地（连续土地利用超过五年的多年生牧场及天然/半天然草地地块）和临时草地（使用不足五年的覆草地块）。为捕捉上述气候区及两类草地之间的梯度，本文选取了六个研究区（图1）：南部Dzūkija地区的Alytus，土壤偏沙、农业适宜性有限；西部的Klaipėda，受波罗的海影响显著，风暴与降雪频繁；东北部Aukštaitija地区的Panevėžys和Utena，城市化相对明显；以及西北部萨莫吉希亚地区的Telšiai和Šiauliai，湖泊丰富、农业活动密集。

![图1 研究区](figures/fig01.png)

**图1.** 研究区：（a）立陶宛在欧洲东北部的位置（黄色高亮为立陶宛，灰色为邻国，浅蓝色为波罗的海）；（b）立陶宛境内六个研究区（彩色多边形为各区凸包，彩色点为5,339个采样点）。坐标系：LKS94国家格网（EPSG:3346）。底图：Natural Earth。图（b）含比例尺、指北针、坐标格网和图例。

### 2.2 数据源与影像预处理

本研究所用数据包括Sentinel-1 C波段SAR和Sentinel-2多光谱影像（表1），全部在Google Earth Engine（GEE；Gorelick et al., 2017）中检索并预处理。为统一光学与雷达输入的时间分辨率，将生长季（4—9月）划分为29个六日合成间隔。

所用Sentinel-2数据为Level-2A地表反射率产品（COPERNICUS/S2_SR_HARMONIZED），经Sen2Cor处理器进行正射校正与大气校正（Main-Knorn et al., 2017）。每个合成间隔内，基于场景分类（SCL）波段实施云掩膜。仅保留标记为植被（SCL = 4）或裸土（SCL = 5）的像元；云、云影、雪和水等其余类别均标记为无效观测。随后由近红外（B8）与红光（B4）波段计算NDVI（Rouse et al., 1974）。各间隔内有效像元的中值作为合成输出，以抑制残余噪声并保证每个时间步均有有效值。

Sentinel-1数据来自干涉宽幅（Interferometric Wide, IW）模式的地距探测产品（COPERNICUS/S1_GRD），提取VV和VH极化后向散射系数σ⁰（dB）。由于SAR不受云影响，直接对每个窗口内全部可用VV、VH观测取中值合成。进一步计算交叉比 CROSS = VV − VH 和极化比 RATIO = VV/VH，以表征冠层去极化效应和植被结构特征。

预处理后，全部数据重采样至一致的10 m空间分辨率。数据首先由EPSG:4326重投影至立陶宛国家坐标系EPSG:3346（LKS94），以实现与草地地块边界的精确空间配准。

**表1.** 本研究所用Sentinel-1/2特征模态及其物理含义。

| 模态 | 传感器 | 描述 / 公式 |
| --- | --- | --- |
| σ⁰VV | Sentinel-1 | VV极化后向散射系数（dB） |
| σ⁰VH | Sentinel-1 | VH极化后向散射系数（dB） |
| RATIO | Sentinel-1 | σ⁰VV / σ⁰VH，反映植被结构 |
| CROSS | Sentinel-1 | σ⁰VV − σ⁰VH，反映冠层去极化 |
| NDVI | Sentinel-2 | (NIR − RED) / (NIR + RED) |

### 2.3 数据集构建

本研究所用地块边界取自Tsardanidis et al.（2024）公开发布的数据集（Zenodo，DOI: https://doi.org/10.5281/zenodo.11651601）。该数据集包含5,339个矢量多边形，定义于立陶宛国家坐标系（EPSG:3346），原始地块边界由立陶宛国家支付局（National Paying Agency, NPA）正式提供。这些地块完整覆盖立陶宛六个气候区，且空间分布均匀。每个地块面积大于0.1 ha，以保证单个草地单元内像元信号在空间上相对均匀。采用该公开数据集主要基于以下考虑。第一，它支持严谨、一致的跨方法比较。通过采用相同的地块边界、一致的Sentinel-1/2遥感输入以及统一的评价协议，所提方法的性能增益可以可靠地归因于引入的空间邻域建模与可微分特征选择模块，而非数据条件不一致。这一设置保证了公平且完全可复现的对比实验。第二，该数据集与多模态云隙重建的研究目标高度契合。立陶宛位于北欧高纬地带，生长季内持续遭受云污染，年平均云覆盖率介于26.0%（2020年）至34.5%（2021年）。如此频繁且不规则的云隙，为验证SAR–光学融合云隙填补方法提供了理想实验条件。此外，多样气候区的广泛覆盖，也使模型在不同地理环境下的泛化能力可以得到综合评价。

基于这些草地地块边界，通过Google Earth Engine（Gorelick et al., 2017）提取带有邻域上下文信息的空间斑块数据集。对每个地块质心生成5×5像元（50 m × 50 m）空间窗口，构建斑块时空张量，包含五种特征模态和29个合成时间步。全部遥感影像统一重投影至EPSG:3346，以保证与地块几何的精确空间匹配。建立了两个年度数据集，分别用于模型训练与跨年验证。2020年数据集包含5,338个地块，平均云覆盖率为26.0%，用于模型训练和主要评价。2021年数据集保留全部5,339个地块，采样配置相同，平均云覆盖率为34.5%，作为独立跨年测试集用于泛化评估。如表2统计所示，萨莫吉希亚地区的Telšiai云覆盖率最高（32.1%），可由其湖泊密集、大气湿度高来解释。相比之下，沿海Klaipėda地区因海洋气候调节，云覆盖率最低（20.5%）。

**表2.** 各研究区地块数量、像元数、平均面积及自然云覆盖率（2020年数据集）。

| 研究区 | 地块数 | 斑块像元数（×25） | 平均面积（ha） | 平均云覆盖率（%） | 无云NDVI均值 |
| --- | --- | --- | --- | --- | --- |
| Alytus | 2,368 | 59,200 | 0.84 | 25.8 | 0.532 |
| Klaipėda | 817 | 20,425 | 1.47 | 20.5 | 0.520 |
| Panevėžys | 285 | 7,125 | 1.00 | 24.7 | 0.440 |
| Telšiai | 844 | 21,100 | 0.91 | 32.1 | 0.560 |
| Šiauliai | 552 | 13,800 | 1.00 | 25.8 | 0.480 |
| Utena | 472 | 11,800 | 0.89 | 27.0 | 0.442 |
| 合计 | 5,338 | 133,450 | — | 26.0 | 0.516 |

### 2.4 SAR–光学互补性的物理基础

SAR后向散射与光学NDVI之间的互补性，源于二者对植被冠层响应机制的不同。NDVI由红光与近红外反射率的归一化比值得到，对绿色生物量和叶绿素含量敏感。相比之下，C波段SAR（波长约5.6 cm）主要受上层冠层结构、植被含水量和地表粗糙度影响。植被生长过程中，微波信号的体散射与去极化增强，后向散射总体趋于下降，这与同期NDVI升高形成对照（图3）。这种互补行为构成了SAR辅助光学云隙填补的物理基础：当NDVI受云污染时，SAR信号仍可传递冠层状态信息。

图2基于2020年全部有效像元中抽取的50,000个点，展示SAR后向散射与NDVI的关系，左、右两图分别为VV和VH极化；红色曲线为分箱均值。结果表明，VV和VH极化的后向散射均随NDVI升高而趋于下降，说明两种数据源对冠层状态的响应方向相反，因而在信息上互补。这为利用SAR辅助光学云隙填补提供了直接经验证据。然而，互补程度在各模态之间并不均匀：NDVI直接刻画植被绿度，而SAR极化及其组合对植被状态的敏感性各不相同。这种模态间贡献不平衡意味着对全部模态进行简单等权融合并非最优，模型应为各模态学习自适应保留权重。

![图2 SAR与NDVI互补关系](figures/fig02.png)

**图2.** SAR后向散射与NDVI的互补关系。

### 2.5 物候与云覆盖的时空格局

研究区NDVI物候遵循温带草地典型的单峰季节格局（图3）。4月春季返青阶段，区域NDVI平均约为0.35。随后指数稳步升高，于6—7月达到约0.68的季节峰值，对应植被生物量最大、人为管理（如刈割）最密集的时期。此后随植被转入衰老阶段，NDVI在8月之后逐渐下降至约0.61。各气候区物候轨迹的季节趋势一致，但NDVI量级与年变幅存在明显区域差异。Telšiai地区平均NDVI最高（0.56），东北部Panevėžys和Utena相对较低（0.44），反映了局地水热条件的空间异质性。尽管2020年与2021年总体物候曲线可比，但2021年云覆盖率显著更高（34.5%对26.0%），连续无云观测的可得性下降，给时间序列重建带来更大挑战。

图3给出2020年整个生长季的六日合成NDVI物候曲线，并标注返青、峰值生长（易发生刈割）和衰老阶段。这些平滑后的物候曲线为后续跨季节植被动态的不确定性分析提供了可靠基线。如图4所示，云污染具有很强的年内变率，是欧洲高纬度地区光学遥感监测的持续性约束。受云影响观测的比例在时间步和研究区之间大幅波动，某些时段可遮蔽超过50%的草地地块，并形成持续数周的数据缺口。如此长时间的缺失段仅靠光学插值难以稳健恢复，凸显了互补SAR后向散射信息的必要性。总体而言，2021年更高的云频率和更持久的缺口，进一步说明了多模态协同填补策略的实际需求。

![图3 NDVI物候曲线](figures/fig03.png)

**图3.** 各研究区NDVI物候曲线。

![图4 云覆盖率时间序列](figures/fig04.png)

**图4.** 各研究区云覆盖率时间序列（2020年）。

---

## 3. 方法

### 3.1 总体框架

所提出的斑块时空Transformer包含四个依次衔接的阶段（图5）：首先以多模态斑块为输入，继而进行离线掩膜增强；随后由可微分RFE模块通过端到端学习为各模态赋权；最后由斑块时空Transformer联合建模时空依赖。推理阶段，模型引入MC Dropout与分割共形预测校准，输出连续NDVI时间序列以及经过校准的预测区间。

![图5 方法总体流程](figures/fig05.png)

**图5.** 所提方法总体流程。

### 3.2 可微分RFE模块

在多模态云隙填补中，光学NDVI、各SAR极化及其组合的信息量与可靠性差异显著。将全部模态等权拼接，既无法区分各自贡献，也不具备物理可解释性。尽管经典递归特征消除（RFE）（Guyon et al., 2002）可在训练前进行模态选择，但选择结果在训练过程中固定，无法随模型优化动态调整，因而难以适应输入模态分布的差异。为此，本文引入通道级可微分软门控机制，使模态权重可在端到端训练中自适应学习，门控值本身即可作为模态重要性的可解释度量。

设输入张量为 \(X \in \mathbb{R}^{B \times T \times H \times W \times C}\)，其中模态通道数 \(C = 5\)。对每个模态 \(c\)，引入可学习的logit参数 \(\theta_c\)，门控权重定义为：

\[
g_c = \sigma\left(\frac{\theta_c}{\tau}\right),\quad c = 1,\ldots,C \tag{1}
\]

其中 \(\sigma(\cdot)\) 为sigmoid函数，\(\tau\) 为温度系数（本文取 \(\tau = 1\)）。逐模态加权操作为：

\[
\tilde{X}_{b,t,h,w,c} = X_{b,t,h,w,c} \cdot g_c \tag{2}
\]

即门控向量 \(g \in \mathbb{R}^{C}\) 沿通道维广播。整个运算连续可微，不涉及离散化或硬性top-\(k\)选择。为避免冷启动时丢失关键信息，将NDVI通道（\(c = 5\)）的初始logit设为 \(\theta_5 = 2.0\)，对应初始门控值约0.88；其余通道初始化为0。推理时保留软门控权重而不做硬过滤，因此门控值 \(g_c\) 直接反映模型对各模态的依赖程度，支撑后续物理可解释性分析。该模块置于斑块时空Transformer前端，使后续注意力机制能够聚焦于高权重模态通道。

### 3.3 斑块时空Transformer架构

第4.1节实验表明，像元级时间信息已接近饱和，引入空间邻域可提供额外约束。此外，第4.1节比较显示，压缩时间维的iTransformer在补全任务上系统性失败——补全任务需要保持完整时间分辨率，才能恢复被掩膜的模式。

对比实验表明：仅利用像元级时间信息时，NDVI重建精度已接近饱和，引入空间邻域约束可带来额外增益。与此同时，直接压缩时间维的iTransformer在补全任务上系统性失败，因为补全需要保持完整时间分辨率以恢复被掩膜的时间模式。因此，本文采用斑块级时空联合注意力结构。

经可微分RFE加权后，张量仍为 \(\tilde{X} \in \mathbb{R}^{B \times T \times H \times W \times C}\)。每个空间像元的 \(C\) 维特征被线性映射到 \(d_{\mathrm{model}} = 64\) 维，展开后得到 \(T \times H \times W = 29 \times 5 \times 5 = 725\) 个Token。这些Token与时空联合位置编码拼接后，输入2层Transformer Encoder进行时空联合建模。编码器采用Pre-LayerNorm、4头自注意力和GELU激活，自注意力为标准缩放点积注意力（Vaswani et al., 2017）。输出头将每个Token经两层全连接映射为单一NDVI值，并由sigmoid激活约束，最终恢复形状为 \((B, T, H, W)\) 的NDVI时空场。

关键设计在于时间维被完整保留、不做下采样，使725个Token可在空间维与时间维上自由交互，从而同时捕获时间依赖与邻域空间相关。

### 3.4 不确定性量化

在实际应用中，仅输出NDVI点预测并不足以满足对预测可靠性的需求。MC Dropout能够以较低计算成本估计认知不确定性，但其标准差通常被系统性低估，因此需要无需分布假设的事后校准，以保证区间覆盖率。

本文采用MC Dropout（Gal & Ghahramani, 2016）与分割共形预测（Angelopoulos & Bates, 2023）相结合的两阶段方法。训练时施加Dropout（\(p = 0.1\)）；推理时Dropout保持开启，对同一输入进行 \(N = 50\) 次前向传播，得到预测集合 \(y^{(1)},\ldots,y^{(N)}\)，以其均值作为最终预测，以其标准差作为认知不确定性：

\[
\bar{y}_i = \frac{1}{N}\sum_{n=1}^{N} y_i^{(n)} \tag{3}
\]

\[
\sigma_i = \sqrt{\frac{1}{N-1}\sum_{n=1}^{N}\left(y_i^{(n)}-\bar{y}_i\right)^2} \tag{4}
\]

鉴于MC Dropout的标准差被系统性低估，采用分割共形预测进行方差缩放校准：将验证集划分为校准集与测试集，在校准集上搜索缩放因子 \(s\)，使校准后预测区间覆盖率接近名义水平。校准后的预测区间为：

\[
\left[\bar{y}_i - s \cdot z_{1-\alpha/2}\,\sigma_i,\; \bar{y}_i + s \cdot z_{1-\alpha/2}\,\sigma_i\right] \tag{5}
\]

其中 \(z_{1-\alpha/2}\) 为标准正态分布的 \(1-\alpha/2\) 分位数（例如对95%区间，\(z = 1.96\)）。该方法无需分布假设，并在可交换性假定下提供有限样本覆盖保证。

采用预测区间覆盖概率（Prediction Interval Coverage Probability, PICP）和平均预测区间宽度（Mean Prediction Interval Width, MPIW）评价不确定性：

\[
\mathrm{PICP} = \frac{1}{n}\sum_{i=1}^{n}\mathbf{1}\!\left[y_i \in [L_i, U_i]\right] \tag{6}
\]

\[
\mathrm{MPIW} = \frac{1}{n}\sum_{i=1}^{n}(U_i - L_i) \tag{7}
\]

其中 \(L_i, U_i\) 为第 \(i\) 个样本区间的下、上界，\(\mathbf{1}[\cdot]\) 为示性函数。PICP度量真值被预测区间覆盖的比例，应接近名义水平；MPIW反映区间宽度，在满足覆盖要求的前提下应尽可能窄。校准后的 \(s\)、PICP和MPIW在独立测试集上报告。

### 3.5 训练与评价协议

全部模型统一采用Adam优化器（Kingma & Ba, 2015），初始学习率为 \(5\times10^{-4}\)，并配合ReduceLROnPlateau学习率衰减（factor = 0.5，patience = 3–5）、EarlyStopping（patience = 7–10）、梯度裁剪（max_norm = 1.0）以及 batch_size = 32。损失函数为掩膜加权均方误差，仅在人工云掩膜位置 \(M\) 上计算：

\[
\mathcal{L} = \frac{1}{|M|}\sum_{i \in M}\left(\hat{y}_i - y_i\right)^2 \tag{8}
\]

其中 \(|M|\) 为被掩膜位置数量。该设计引导模型聚焦于云隙处的重建学习，避免对天然无云位置做不必要拟合。

采用离线掩膜增强策略：为每个训练样本预先生成10种不同的人工云掩膜，在天然无云位置随机掩膜30%的NDVI时间步，从而将训练样本量有效扩充至42,710。训练/验证集按地块以8:2划分（seed = 42），验证集使用固定掩膜，以保证不同模型在相同评价点上可比。

在验证集的人工云掩膜位置上计算平均绝对误差（MAE）、均方根误差（RMSE）和决定系数（R²）：

\[
\mathrm{MAE} = \frac{1}{n}\sum_{i=1}^{n}\left|\hat{y}_i - y_i\right| \tag{9}
\]

\[
\mathrm{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}\left(\hat{y}_i - y_i\right)^2} \tag{10}
\]

\[
R^2 = 1 - \frac{\sum_{i=1}^{n}(\hat{y}_i - y_i)^2}{\sum_{i=1}^{n}(y_i - \bar{y})^2} \tag{11}
\]

其中 \(\hat{y}_i\) 为第 \(i\) 个像元–时间点的预测值，\(y_i\) 为真值，\(\bar{y}\) 为真值均值。MAE反映平均误差幅度，RMSE对大误差更敏感，R²度量模型解释真值总体方差的能力。

---

## 4. 结果

### 4.1 像元级时间序列架构比较

为系统考察网络架构对NDVI云隙填补精度的内在影响，以Tsardanidis et al.（2024）提出的CNN–RNN混合模型为主要基线，对CNN–RNN、LSTM、vanilla Transformer和iTransformer四种代表性时间序列架构进行对照比较。全部模型采用相同输入特征与统一数据划分策略，得到824,978个训练样本和365,298个验证样本。

**表3.** 四种像元级时间序列架构比较（验证集：365,298个样本）。

| 模型 | 参数量 | MAE ↓ | R² ↑ |
| --- | --- | --- | --- |
| CNN-RNN（基线） | 82,881 | 0.0238 | 0.9196 |
| LSTM | 215,681 | 0.0111 | 0.9622 |
| Transformer | 71,681 | 0.0135 | 0.9525 |
| iTransformer | 234,113 | 0.0622 | 0.4208 |

四种模型的定量比较汇总于表3。LSTM与Transformer均显著优于CNN–RNN基线。相对基线CNN–RNN（MAE = 0.0238），LSTM取得最低MAE 0.0111（误差降低53%），Transformer次之（MAE = 0.0135，误差降低43%）。相应地，决定系数由0.9196（CNN–RNN）提升至0.9622（LSTM）和0.9525（Transformer）。总体而言，LSTM与Transformer的重建性能相当，LSTM略优。相比之下，iTransformer结果最不可靠，MAE明显更高（0.0622），R²严重下降至0.4208，与其余三种架构形成鲜明反差。训练收敛曲线（图6）进一步表明，基于Transformer的云隙填补对训练正则化十分敏感。在施加Layer Normalization和梯度裁剪（max_norm = 1.0）后，Transformer的验证损失由0.058急剧降至0.00085，MAE由0.1535降至0.0135。若无此类正则约束，模型收敛停滞，甚至出现负R²。这些经验结果凸显了植被时间序列云隙填补任务的一条关键原则：特征编码全过程应严格保持完整时间分辨率。iTransformer固有的时间压缩机制将时间维重组为按特征的注意力，抹去了细粒度时间动态，无法准确恢复被掩膜的植被序列。因此，iTransformer不适用于缺失观测破碎且不规则的云隙重建任务。

![图6 四种模型训练曲线](figures/fig06.png)

**图6.** 四种模型的训练曲线。

![图7 逐样本MAE分布](figures/fig07.png)

**图7.** 逐样本MAE分布比较。

### 4.2 可微分RFE消融

第4.1节的像元级实验验证了先进时间建模策略的优越性，但未纳入空间邻域上下文。为进一步考察多模态特征选择对基于斑块的NDVI重建的有效性，本节在空间结构化斑块数据集上设置四种实验配置进行对照：（B1）全波段斑块Transformer基线；（B2）离线Pearson RFE，保留前三模态；（B3）端到端可微分RFE；（B4）可微分RFE并集成MC Dropout不确定性估计。全部配置采用相同的Transformer骨干与训练设置，差异仅限于特征选择模块。

**表4.** RFE消融比较（171,506个人工云评价点）。

| 配置 | 参数量 | MAE ↓ | RMSE ↓ | R² ↑ | val_loss |
| --- | --- | --- | --- | --- | --- |
| B1 全波段 | 69,569 | 0.0217 | 0.0358 | 0.9731 | 0.00128 |
| B2 离线RFE | 69,441 | 0.0216 | 0.0360 | 0.9727 | 0.00130 |
| B3 可微分RFE | 69,574 | 0.0169 | 0.0288 | 0.9825 | 0.00083 |
| B4 可微分RFE + MC | 69,574 | 0.0166 | 0.0291 | 0.9821 | 0.00085 |

如表4所示，可微分RFE方案（B3）相对全波段基线（B1）带来显著精度提升：MAE降低22%，RMSE降低20%，R²由0.973升至0.983。相比之下，基于Pearson相关的离线RFE（B2）MAE为0.0216，几乎与全波段基线（0.0217）相当。这表明静态、由相关驱动的特征筛选无法为多模态时间序列重建带来明显性能增益。将MC Dropout嵌入可微分RFE框架的B4配置取得MAE = 0.0166，与B3相当。这说明引入的不确定性量化模块并不损害重建精度，同时能够提供可靠的概率区间估计。

![图8 重建与真实NDVI物候](figures/fig08.png)

**图8.** 重建NDVI与真实NDVI物候曲线比较。

图8可视化了1,067个验证地块在云隙中心处的重建物候曲线。B4方案在返青、峰值生长和衰老阶段均能紧密再现真实NDVI动态，校准后的95%预测区间成功包络了大多数真值观测。相比之下，全波段基线（B1）重建偏差更大、时间波动更不稳定，在植被过渡期尤为明显。

![图9 模态门控权重](figures/fig09.png)

**图9.** 可微分RFE学得的模态门控权重。

可微分RFE模块学得的模态权重呈现出明确的多模态偏好，降序为NDVI（0.380）、RATIO（0.333）、CROSS（0.298）、SAR_VH（0.267）和SAR_VV（0.223）（图9）。该权重分布与各模态相对NDVI的Pearson相关（r = 0.75）高度一致。结果证实，所提框架能够自适应地优先保留与植被动态强相关、具有物理意义的特征，为草地NDVI重建中SAR–光学多模态融合的合理性提供了可解释证据。

### 4.3 不同地理区域的重建性能

为定量评价模型在异质地理环境下的泛化能力，基于1,067个验证地块的人工云隙样本计算了分区MAE、RMSE和R²（表5；图10）。模型在全部六个研究区均取得稳定且较高的重建精度，分区MAE介于0.0119至0.0183，全部R²均高于0.977。值得注意的是，地块数最多的Alytus（451个样本）MAE最高（0.0183），而样本量最小的Panevėžys（59个地块）重建误差最低（MAE = 0.0119）。这一差异可归因于区域景观与物候异质性：空间覆盖更广、样本量更大的区域，本身包含更复杂的植被动态与土地利用变化，从而增加了一致重建NDVI的难度。此外，图11给出四个典型草地地块的重建示例。结果表明，即使在长时间被云掩膜的时段，所提模型仍能可靠恢复连续NDVI时间剖面，显示出对长期云隙填补场景的稳健性。

**表5.** 各研究区NDVI重建性能（B4最优模型，人工云评价点）。

| 研究区 | 验证地块数 | 评价点数 | MAE ↓ | RMSE ↓ | R² ↑ |
| --- | --- | --- | --- | --- | --- |
| Alytus | 451 | 72,763 | 0.0183 | 0.0321 | 0.9771 |
| Klaipėda | 166 | 29,031 | 0.0150 | 0.0263 | 0.9845 |
| Panevėžys | 59 | 9,725 | 0.0119 | 0.0204 | 0.9928 |
| Telšiai | 178 | 26,070 | 0.0165 | 0.0293 | 0.9809 |
| Šiauliai | 117 | 18,672 | 0.0160 | 0.0276 | 0.9841 |
| Utena | 96 | 15,245 | 0.0151 | 0.0252 | 0.9864 |
| 合计 | 1,067 | 171,506 | 0.0166 | 0.0291 | 0.9821 |

![图10 各区MAE与R²](figures/fig10.png)

**图10.** 各研究区NDVI重建的MAE与R²。

![图11 代表性地块重建](figures/fig11.png)

**图11.** 代表性地块的NDVI云隙重建及校准不确定性。

### 4.4 不确定性量化

为给重建NDVI时间序列提供统计可靠的置信量化，将MC Dropout不确定性估计与分割共形预测（SCP）校准集成到最优B4模型中，并在独立测试集上全面评价区间质量。如表6所示，SCP校准有效校正了原始MC Dropout不确定性中的系统性偏差。校准后，预测区间覆盖概率（PICP）在全部阈值上均与名义置信水平密切吻合。具体而言，95%名义水平下经验PICP为0.952，校准缩放因子为3.835。相比之下，未经校准的MC Dropout区间（固定缩放因子 = 1.0）在95%置信水平下的PICP仅为0.55，覆盖严重不足。这一明显差异证实，朴素MC Dropout倾向于系统性低估预测不确定性，说明有效解释不确定性必须进行共形事后校准。

**表6.** B4不确定性校准结果（独立测试集）。

| 置信水平 | 缩放因子 \(s\) | PICP | 名义水平 | MPIW |
| --- | --- | --- | --- | --- |
| 80% | 2.854 | 0.799 | 0.80 | 0.049 |
| 90% | 3.265 | 0.901 | 0.90 | 0.072 |
| 95% | 3.835 | 0.952 | 0.95 | 0.100 |
| 99% | 5.569 | 0.990 | 0.99 | 0.192 |

![图12 不确定性随物候变化](figures/fig12.png)

**图12.** 不确定性与预测误差随物候阶段的变化（叠加NDVI季节曲线）。

模型不确定性对植被物候表现出清晰的季节依赖（图12）。预测标准差在春季返青阶段相对较低（约0.20），而在仲夏（6—7月）明显升高至0.29–0.32。这种季节变化与NDVI动力学特征在物理上一致。夏季草地系统受刈割扰动和旺盛生物量增长驱动，植被波动迅速。这些突变式时间转折增加了在云隙内精确恢复缺失极值的难度，从而在峰值生长季诱发更高的预测不确定性。

### 4.5 跨年泛化

为进一步评价所提框架的时间泛化潜力，在2021年数据集上进行了跨年零样本预测与微调实验。2021年数据集保留与2020年相同的地块边界、5×5空间斑块配置和29个时间合成，但年云覆盖率更高，达34.5%。零样本推理时，将在2020年数据集上预训练的模型权重直接部署于2021年重建，不做参数更新。微调评价时，网络以2020年预训练权重初始化，随后在2021年数据集上按8:2训练–验证划分进行优化。

**表7.** 跨年泛化结果（2020年训练 → 2021年评价）。

| 模型 | 2020 MAE | 2021零样本MAE | 退化幅度 | 2021 R² | 95% PICP | 2021微调MAE |
| --- | --- | --- | --- | --- | --- | --- |
| C1 斑块Transformer | 0.0217 | 0.0232 | +6.9% | 0.9753 | — | 0.0190 |
| C2 可微分RFE | 0.0169 | 0.0170 | +0.6% | 0.9845 | — | 0.0156 |
| C3 可微分RFE + MC | 0.0166 | 0.0170 | +2.4% | 0.9830 | 0.9521 | 0.0161 |

![图13 跨年泛化MAE](figures/fig13.png)

**图13.** 跨年泛化三阶段MAE比较。

定量结果汇总于表7和图13。最优的基于可微分RFE的模型（C2）在零样本跨年迁移下MAE仅轻微退化0.6%，同时保持高达0.985的R²。这凸显了模型对植被物候年际变化的稳健适应性。此外，由2020年数据集校准得到的方差缩放因子（\(s = 3.835\)）可直接迁移至2021年测试集，稳定给出95% PICP = 0.9521。这表明共形不确定性校准具有很强的跨年可迁移性，无需按年重新调参。在2021年观测上微调后，全部模型精度进一步提升，C2模型MAE降至0.0156（图13）。值得注意的是，可微分RFE得到的模态门控权重在2020年与微调后的2021年情景之间高度一致（表8）。这种稳定的特征偏好表明，网络学到的多模态依赖模式反映的是草地植被的内在物理特征，而非针对特定数据集的过拟合。综合来看，这些跨年评价证实，所提方法具备可靠的时间泛化性能，并具有面向业务化年度NDVI云隙填补应用的较大潜力。

**表8.** 可微分RFE门控权重的跨年比较（微调后）。

| 模态 | 2020 | 2021微调后 | 变化 |
| --- | --- | --- | --- |
| NDVI | 0.380 | 0.380 | 不变 |
| RATIO | 0.333 | 0.333 | 不变 |
| CROSS | 0.298 | 0.298 | 不变 |
| SAR_VH | 0.267 | 0.267 | 不变 |
| SAR_VV | 0.223 | 0.223 | 不变 |

---

## 5. 讨论

### 5.1 模态贡献的物理机制与可解释性

可微分RFE模块推断出的模态加权层次——NDVI > RATIO > CROSS > VH > VV——为多模态特征对云隙重建的差异化贡献提供了内在量化证据，且所学排序与遥感中既有物理原理一致。作为植被绿度的直接代理，NDVI在特征加权中自然占据主导地位。相比之下，RATIO、CROSS等SAR极化衍生量比单独的VV或VH更能刻画冠层结构属性与去极化现象，从而为植被反演提供更稳健的结构线索。模型学得的门控权重与Pearson相关系数（r = 0.75）之间的强对应，进一步表明所提架构会自适应地优先保留具有物理意义的特征，而非不加区分地聚合冗余输入。这一性质增强了基于深度学习的重建的可解释性——该范式常被批评为黑箱。

尽管如此，鉴于SAR衍生特征固有的共线性，对稳定加权模式仍应谨慎解读。因为全部极化指数均源自同一对VV–VH观测，被赋予较低权重的模态仍可能被隐式编码于排序更高的特征通道中。因此，当前排序不应被当作完全独立的特征重要性证据。未来工作可引入更具物理独立性的SAR变量——例如InSAR相干性和多时相纹理度量——以在扩展特征空间中进一步评估模态偏好的稳定性与可推广性。

### 5.2 时空建模的有效性

像元级消融实验表明，LSTM与Transformer均显著优于传统CNN–RNN基线，尽管二者重建精度在数值上仍相当。这一结果说明，在单点时间序列输入约束下，纯像元时间建模已接近性能上限。相比之下，显式引入空间邻域上下文的斑块Transformer框架，在空间一致约束下于斑块层面取得更优重建性能（MAE = 0.0166，R² = 0.982）。模型能够准确捕捉刈割扰动引起的植被突变动态，所得物候轨迹与真值观测密切吻合。这些发现证实，空间上下文信息提供了孤立像元时间序列所无法给予的互补约束，在植被快速过渡阶段尤为如此。

此外，iTransformer相对有限的性能为云隙填补任务提供了有价值的方法学启示。与由历史观测外推未来趋势的常规时间序列预报不同，云隙填补旨在从不完整数据中恢复被掩膜或缺失的时间片段。压缩原始时间维必然抹去细粒度局地变化和突变扰动信号，从而严重制约重建精度。因此，保持完整时间分辨率成为遥感时间序列云隙填补的核心设计原则。所提斑块Transformer框架在特征编码全过程中保留完整时间粒度，与这一任务特定要求相一致，在很大程度上解释了其稳健的重建能力。

### 5.3 不确定性的地学含义

预测不确定性的物候依赖性具有显著的地学含义。在立陶宛草地，仲夏（6—7月）与刈割事件高峰期重合，连续时相获取之间会出现NDVI的突然下降。由此产生的高动态变率本身使重建更复杂，表现为预测区间变宽。相反，春季返青阶段植被动态相对平缓，时间插值更为可靠，不确定性相应降低。因此，校准后的预测区间不仅是统计覆盖保证，也可作为稳定物候窗口内模型可靠性、以及突变过渡时段适当保守性的指示。

不确定性对云掩膜比例大体不敏感（标准差介于0.231至0.244）这一观察表明，模型并不依赖同期邻域像元观测来填补缺失，而主要依靠目标像元自身的时间轨迹进行插值。即使在空间成片云覆盖、邻域像元同时被遮蔽时，重建精度也不会显著下降。这一发现与第5.2节讨论的空间上下文收益并不矛盾：空间信息的作用在于帮助模型识别物候阶段和空间一致的时间模式，而非在缺失时间步上直接进行数值替代。这一特性对业务应用尤为重要，因为云覆盖往往在空间上成簇。若模型依赖空间外推，大范围云系将迅速引发性能退化；相反，以时间插值为导向的策略可在高云覆盖条件下保持稳定。

### 5.4 跨年稳定性的含义

可微分RFE模块在跨年零样本设置下几乎无损，MAE仅退化0.6%。此外，在2020年数据上校准的不确定性参数应用于云覆盖更高的2021年数据集时，仍保持PICP = 0.9521。这些结果表明，模型学到的是不依赖于特定年份的模态融合关系，而非过拟合于某一云况体制。更重要的是，微调后门控权重与2020年所得完全相同，说明“光学主导、SAR辅助”的融合机制在年际转换中保持稳定。这一性质意味着一次校准得到的参数可在后续年份直接复用，无需逐年重新校准，从而满足业务化部署的一项关键前提。

### 5.5 区间差异的成因

重建性能的区间差异（MAE介于0.0119至0.0183）总体不大，且所有区域R²均超过0.977，表明模型并未对某一特定气候区产生系统性偏向。Alytus地区尽管样本量最大，MAE仍略高，这一模式可能归因于沙质土壤背景引起的混合像元效应。Telšiai云覆盖率最高（32.1%），但MAE处于中等水平，说明SAR辅助信息有效缓解了频繁云覆盖的不利影响。但应承认，这些归因目前主要基于定性推断；各区域的土壤、地形和管理相关因子尚未被定量纳入分析。未来研究可引入此类辅助数据集，为区间精度差异提供更严谨的统计解释。

### 5.6 局限与未来工作

本研究存在若干局限。第一，GEE平台不提供InSAR相干性产品；因此仅考虑了五种模态，一些相关研究中使用的相干性特征未被纳入。相干性对土壤水分和植被结构敏感，有可能进一步提升云隙填补精度。第二，由MC Dropout得到的原始不确定性估计被系统性低估。尽管SCP校准将覆盖率恢复至名义水平，相对较大的方差缩放因子（\(s = 3.835\)）表明不确定性估计本身仍有待改进。采用深度集成或变分推断有望得到更可靠的分布输出。第三，跨年验证覆盖了时间维，但未评估跨区域或跨气候区泛化。门控权重的时间稳定性并不自动意味着空间稳定性，后者仍需在异质地理设置中加以验证。

针对上述局限，未来研究拟沿四个方向展开：第一，利用Copernicus Data Space的SLC产品补充InSAR相干性模态，并在共线性条件下考察门控排序的稳健性；第二，引入Eurocrops等跨国数据集以验证空间泛化能力；第三，探索更严谨的贝叶斯方法——深度集成或变分推断——作为MC Dropout的替代，以改进不确定性量化；第四，将可微分RFE迁移至土地覆被分类、作物识别等任务，评估其在更广谱遥感应用中的可推广性。

---

## 6. 结论

北欧持续的云污染阻碍了仅由光学遥感观测生成无缺口NDVI时间序列，单源输入往往不足以稳健重建植被物候。为缓解这一局限，本文发展了一种融合可微分递归特征选择的斑块时空Transformer，并在覆盖六个气候区的立陶宛草地数据集上进行了系统评价。在统一的时间序列重建框架内，所提模型融合光学与SAR模态，并采用门控机制自适应量化各特征的相对贡献。主要结论概括如下：

1. **时间建模是提升云隙填补性能的核心驱动力。** 在相同输入设置下，LSTM与vanilla Transformer均显著优于CNN–RNN基线，MAE降低43%–53%。这说明有效表征时间依赖对重建质量的贡献，大于单纯扩大模型容量。尽管如此，两种时间架构之间的性能差距很小，表明单像元时间信息已接近其性能饱和点。恰当的训练正则化可将重建误差大约降低一个数量级（11倍），显示训练策略对此类时间序列模型至关重要。时间维被压缩的iTransformer表现不佳，进一步证实云隙填补任务本质上要求完整保留原生时间分辨率。

2. **可微分特征选择在提高重建精度的同时增强了模型可解释性。** 相对全特征基线，端到端学习的门控机制使MAE降低23%、RMSE降低19%，而离线静态特征选择未带来实质性性能提升。所学模态权重排序与各特征相对NDVI的物理相关（r = 0.75）高度一致，其中NDVI和SAR极化比特征获得最高权重。这从定量上揭示了“光学主导、SAR互补”的多模态融合模式。这种一致性表明，所提模块在减轻特征冗余的同时，保持了与遥感物理原理相容的特征利用模式。

3. **模型导出的不确定性表现出显著的物候依赖性。** 不确定性在仲夏刈割事件期间升高，频繁的NDVI突变增加了重建难度并拓宽预测区间；相比之下，不确定性在平缓的春季返青阶段达到最低。经MC Dropout与分割共形预测校准后，95%预测区间覆盖概率（PICP）为0.952，验证了概率输出的统计有效性。除报告误差界外，校准区间还可作为检测突变物候扰动的辅助指标。

4. **模型在跨年泛化中表现出很强的时间稳定性。** 直接部署于下一年度数据时，MAE仅增加0.6%；再经轻度微调即可获得最优重建性能。跨年稳定的模态门控权重表明，网络学到的是可推广的多模态融合规则，而非过拟合于特定年份的数据分布。这为“一次校准、多年复用”的业务化流程奠定了实践基础。

综上所述，可微分特征选择与时空Transformer的结合，为多云地区NDVI时间序列重建提供了一种兼顾精度与可解释性的方案。所提方法在精度、物理可解释性与跨年可迁移性上均具有竞争力，对北欧生物群区内的长期草地监测与物候分析具有实际意义。

---

## 致谢

作者声明未获得资助。本研究使用了Sentinel-1/2影像（由ESA提供，经Google Earth Engine平台获取）。

## 数据与代码可用性声明

Sentinel-1/2影像经Google Earth Engine获取；草地地块矢量数据取自Tsardanidis et al.（2024）的公开数据集（Zenodo，https://doi.org/10.5281/zenodo.11651601）。

## 利益冲突声明

作者报告不存在竞争性利益。作者声明本研究及本论文撰写过程中未使用生成式人工智能。

---

## 参考文献

Appel, M. 2024. Efficient data-driven gap filling of satellite image time series using deep neural networks with partial convolutions. *Artificial Intelligence for the Earth Systems*, 3(2), 220055. https://doi.org/10.1175/AIES-D-22-0055.1

Benzhair, F., El Youssfi, H., et al. 2026. Crop mapping using Sentinel-1 and Sentinel-2 imagery: A systematic review of machine learning classification methods (2015–2025). *Geocarto International*, 41(1), 2690363. https://doi.org/10.1080/10106049.2026.2690363

Kaplan, G., Avdan, U. 2018. Sentinel-1 and Sentinel-2 data fusion for wetland monitoring. *The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences*, XLII-3: 729–734. https://doi.org/10.5194/isprs-archives-XLII-3-729-2018

Garioud, A., Giordano, S., Lopez-Lopez, L., Mallet, C. 2021. Recurrent-based regression of Sentinel time series for continuous vegetation monitoring. *Remote Sensing of Environment*, 257, 112367. https://doi.org/10.1016/j.rse.2021.112367

Košánová, S., et al. 2025. Assessment of yield stability patterns using Sentinel-2 over a 7-year period under cloud-affected conditions. *Geocarto International*, 40(1), 2532529. https://doi.org/10.1080/10106049.2025.2532529

Kolecka, N., Ginzler, C., Pazur, R., Price, B., Verburg, P. H. 2018. Grassland mapping with high temporal resolution satellite time series. *Remote Sensing*, 10(8), 1221. https://doi.org/10.3390/rs10081221

Mandal, D., Kumar, V., Ratha, D., Dey, S., Bhattacharya, A., Lopez-Sanchez, J. M., McNairn, H., Rao, Y. S. 2020. Dual polarimetric radar vegetation index for crop growth monitoring using Sentinel-1. *Remote Sensing of Environment*, 247, 111954. https://doi.org/10.1016/j.rse.2020.111954

Sun, M., Gong, A., Zhao, X., Liu, N., Si, L., Zhao, S. 2023. Reconstruction of a monthly 1 km NDVI time series product in China using random forest methodology. *Remote Sensing*, 15(13), 3353. https://doi.org/10.3390/rs15133353

Suprijanto, A., et al. 2024. A new hybrid filter for NDVI time series reconstruction and data quality enhancement in cloud-prone areas. *Geomatics, Natural Hazards and Risk*, 15(1), 2410359. https://doi.org/10.1080/19475705.2024.2410359

Tsardanidis, I., Koukos, A., Sitokonstantinou, V., Drivas, T., Kontoes, C. 2025. Cloud gap-filling with deep learning for improved grassland monitoring. *Computers and Electronics in Agriculture*, 230, 109732. https://doi.org/10.1016/j.compag.2024.109732

Xiong, C., Ma, H., Zhang, G., Xu, J., et al. 2023. Improved global 250 m 8-day NDVI and EVI products from 2000–2021 using the LSTM model. *Scientific Data*, 10, 800. https://doi.org/10.1038/s41597-023-02695-x

Hochreiter, S., Schmidhuber, J. 1997. Long short-term memory. *Neural Computation*, 9(8), 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735

Liu, Y., Hu, T., Zhang, H., Wu, H., Wang, S., Ma, L., Long, M. 2024. iTransformer: Inverted transformers are effective for time series forecasting. International Conference on Learning Representations (ICLR).

Nie, Y., Nguyen, N. H., Sinthong, P., Kalagnanam, J. 2023. A time series is worth 64 words: Long-term forecasting with transformers (PatchTST). International Conference on Learning Representations (ICLR).

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., Polosukhin, I. 2017. Attention is all you need. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 5998–6008.

Bengio, Y., Léonard, N., Courville, A. 2013. Estimating or propagating gradients through stochastic neurons for conditional computation. arXiv preprint, arXiv:1308.3432.

Guyon, I., Weston, J., Barnhill, S., Vapnik, V. 2002. Gene selection for cancer classification using support vector machines. *Machine Learning*, 46(1–3), 389–422. https://doi.org/10.1023/A:1012487302797

Jang, E., Gu, S., Poole, B. 2017. Categorical reparameterization with Gumbel-Softmax. International Conference on Learning Representations (ICLR).

Maddison, C. J., Mnih, A., Teh, Y. W. 2017. The Concrete distribution: A continuous relaxation of discrete random variables. International Conference on Learning Representations (ICLR).

Angelopoulos, A. N., Bates, S. 2023. Conformal prediction: A gentle introduction. *Foundations and Trends in Machine Learning*, 16(4), 494–591. https://doi.org/10.1561/2200000101

Gal, Y., Ghahramani, Z. 2016. Dropout as a Bayesian approximation: Representing model uncertainty in deep learning. International Conference on Machine Learning (ICML), 48, 1050–1059.

Lakshminarayanan, B., Pritzel, A., Blundell, C. 2017. Simple and scalable predictive uncertainty estimation using deep ensembles. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 6402–6413.

Vovk, V., Gammerman, A., Shafer, G. 2005. *Algorithmic learning in a random world*. Springer.

Atzberger, C. 2013. Advances in remote sensing of agriculture: Context description, existing operational monitoring efforts and major information needs. *Remote Sensing*, 5(2), 949–981. https://doi.org/10.3390/rs5020949

Drusch, M., Del Bello, U., Carlier, S., Colin, O., Fernandez, V., Gascon, F., et al. 2012. Sentinel-2: ESA's optical high-resolution mission for GMES operational services. *Remote Sensing of Environment*, 120, 25–36. https://doi.org/10.1016/j.rse.2011.11.026

Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., Moore, R. 2017. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031

Main-Knorn, M., Pflug, B., Louis, J., Debaecker, V., Müller-Wilm, U., Gascon, F. 2017. Sen2Cor for Sentinel-2. *Image and Signal Processing for Remote Sensing XXIII*, 10427, 1042704. https://doi.org/10.1117/12.2278218

Rouse, J. W., Haas, R. H., Schell, J. A., Deering, D. W. 1974. Monitoring vegetation systems in the Great Plains with ERTS. *Third Earth Resources Technology Satellite-1 Symposium*, 1, 309–317.

Torres, R., Snoeij, P., Geudtner, D., Bibby, D., Davidson, M., Attema, E., et al. 2012. GMES Sentinel-1 mission. *Remote Sensing of Environment*, 120, 9–24. https://doi.org/10.1016/j.rse.2011.05.028

Kingma, D. P., Ba, J. 2015. Adam: A method for stochastic optimization. International Conference on Learning Representations (ICLR).

---

**译者说明：** 作者姓名按原文拉丁字母转写保留，因稿件未提供汉字写法。公式已按原文数学含义整理（原稿PDF抽取时部分符号发生错位）。图1–图13沿用原文插图，中文图题见正文。参考文献条目保持原文著录，未译刊名与论文题名。
