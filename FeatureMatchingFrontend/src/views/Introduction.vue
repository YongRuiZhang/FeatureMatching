<template>
    <el-tabs class="demo-tabs">
        <el-tab-pane>
            <template #label>
                <span class="custom-tabs-label">
                    <el-icon>
                        <calendar />
                    </el-icon>
                    <span>检测器算法</span>
                </span>
            </template>
            <el-scrollbar height="86vh">
                <el-row>
                    <el-col :span="20" :offset="2">
                        <el-alert title="检测器算法的主要任务为检测图像中的特征，一般分为简单的角点检测以及复杂一点的细纹理检测等。通常认为是特征匹配任务的视觉特征提取前端。"
                            type="success" :closable="false">
                        </el-alert>
                    </el-col>
                    <el-col>
                        <p v-for="p in Apapers" key="p.id">
                            <IntroItem :paper="p" @update-language="handleLanguageUpdate"></IntroItem>
                        </p>
                    </el-col>
                </el-row>
            </el-scrollbar>
        </el-tab-pane>
        <el-tab-pane>
            <template #label>
                <span class="custom-tabs-label">
                    <el-icon>
                        <calendar />
                    </el-icon>
                    <span>特征匹配算法</span>
                </span>
            </template>
            <el-scrollbar max-height="86vh">
                <el-row>
                    <el-col :span="20" :offset="2">
                        <el-alert title="特征匹配算法的主要任务为匹配图像中的特征点。这里介绍需要检测器的匹配算法。通常检测器得到的结果为特征点的坐标与描述子，匹配器算法根据描述子进行匹配"
                            type="success" :closable="false">
                        </el-alert>
                    </el-col>
                    <el-col>
                        <p v-for="p in Bpapers" key="p.id">
                            <IntroItem :paper="p" @update-language="handleLanguageUpdate"></IntroItem>
                        </p>
                    </el-col>
                </el-row>
            </el-scrollbar>
        </el-tab-pane>
        <el-tab-pane>
            <template #label>
                <span class="custom-tabs-label">
                    <el-icon>
                        <calendar />
                    </el-icon>
                    <span>无检测器特征匹配算法</span>
                </span>
            </template>
            <el-scrollbar max-height="86vh">
                <el-row>
                    <el-col :span="20" :offset="2">
                        <el-alert title="无检测器的特征匹配算法通常是直接利用深度学习方法，从图像中直接获取匹配对。" type="success" :closable="false">
                        </el-alert>
                    </el-col>
                    <el-col>
                        <p v-for="p in Cpapers" key="p.id">
                            <IntroItem :paper="p" @update-language="handleLanguageUpdate"></IntroItem>
                        </p>
                    </el-col>
                </el-row>
            </el-scrollbar>
        </el-tab-pane>
    </el-tabs>
</template>

<script lang='ts' setup name='Introduction'>
import IntroItem from "@/components/IntroItem.vue";
import { reactive } from "vue"

const handleLanguageUpdate = (id: string, value: boolean) => {
    const paper = Apapers.find((p) => p.id === id);
    if (paper) {
        paper.language = value;
    }
};

let Apapers = reactive([
    { id: 'A01', name: 'Harris', paperTitle: 'A Combined Corner and Edge Detector', tag: 'Alvey Vision Conference 1988', content: 'Consistency of image edge filtering is of prime importance for 3D interpretation of image sequences using feature tracking algorithms. To cater for image regions containing texture and isolated features, a combined corner and edge detector based on the local auto-correlation function is utilised, and it is shown to perform with good consistency on natural imagery.', content_ch: '图像边缘过滤的一致性对于使用特征跟踪算法对3D解释的3D解释至关重要。为了满足包含纹理和孤立特征的图像区域，利用了基于局部自动相关功能的组合角和边缘检测器，并且显示出对自然成像的良好一致性。', language: true },
    { id: 'A02', name: 'Shi-Tomasi', paperTitle: 'Good features to track', tag: 'CVPR 1994', content: 'No feature-based vision system can work unless good features can be identified and tracked from frame to frame. Although tracking itself is by and large a solved problem, selecting features that can be tracked well and correspond to physical points in the world is still hard. We propose a feature selection criterion that is optimal by construction because it is based on how the tracker works, and a feature monitoring method that can detect occlusions, disocclusions, and features that do not correspond to points in the world. These methods are based on a new tracking algorithm that extends previous Newton-Raphson style search methods to work under affine image transformations. We test performance with several simulations and experiments.', content_ch: '除非可以从框架之间识别和跟踪良好的功能，否则无法使用基于功能的视觉系统。尽管跟踪本身是一个解决问题的问题，但选择可以很好地跟踪并与世界上物理点相对应的功能仍然很难。我们提出了一个特征选择标准，该标准是根据构造最佳的，因为它基于跟踪器的工作方式，以及一种可以检测遮挡，分离和不对应于世界上点的功能的功能监视方法。这些方法基于一种新的跟踪算法，该算法将以前的牛顿 - 拉夫森风格搜索方法扩展到仿射图像转换下的工作。我们通过几个模拟和实验测试性能。', language: true },
    { id: 'A03', name: 'Sift', paperTitle: 'Scale-Invariant Feature Transform', tag: 'Springer, London 2016', content: 'Many real applications require the localization of reference positions in one or more images, for example, for image alignment, removing distortions, object tracking, 3D reconstruction, etc. We have seen that corner points1 can be located quite reliably and independent of orientation. However, typical corner detectors only provide the position and strength of each candidate point, they do not provide any information about its characteristic or “identity” that could be used for matching. Another limitation is that most corner detectors only operate at a particular scale or resolution, since they are based on a rigid set of filters.', content_ch: '许多实际应用都需要在一个或多个图像中定位参考位置，例如，用于图像对齐，删除失真，对象跟踪，3D重建等。我们已经看到，Corner Points1可以非常可靠地位于方向上。但是，典型的角探测器仅提供每个候选点的位置和强度，它们没有提供有关其特征或“身份”可用于匹配的任何信息。另一个限制是，大多数转角检测器仅以特定的比例或分辨率运行，因为它们是基于刚性过滤器的。', language: true },
    { id: 'A04', name: 'ORB', paperTitle: 'ORB: An efficient alternative to SIFT or SURF', tag: 'ICCV 2011', content: 'Feature matching is at the base of many computer vision problems, such as object recognition or structure from motion. Current methods rely on costly descriptors for detection and matching. In this paper, we propose a very fast binary descriptor based on BRIEF, called ORB, which is rotation invariant and resistant to noise. We demonstrate through experiments how ORB is at two orders of magnitude faster than SIFT, while performing as well in many situations. The efficiency is tested on several real-world applications, including object detection and patch-tracking on a smart phone.', content_ch: '功能匹配是许多计算机视觉问题的基础，例如对象识别或运动结构。当前方法依靠代价高昂的描述符进行检测和匹配。在本文中，我们提出了一个非常快速的二进制描述符，该描述符基于简短（称为Orb），它是旋转不变且对噪声的抵抗力。我们通过实验表明，在许多情况下，ORB的表现要比SIFT快两个数量级。该效率在几个现实世界应用程序上进行了测试，包括对象检测和智能手机的补丁跟踪。', language: true },
    { id: 'A05', name: 'SuperPoint', paperTitle: 'SuperPoint: Self-Supervised Interest Point Detection and Description', tag: 'CVPR 2018', content: 'This paper presents a self-supervised framework for training interest point detectors and descriptors suitable for a large number of multiple-view geometry problems in computer vision. As opposed to patch-based neural networks, our fully-convolutional model operates on full-sized images and jointly computes pixel-level interest point locations and associated descriptors in one forward pass. We introduce Homographic Adaptation, a multi-scale, multi-homography approach for boosting interest point detection repeatability and performing cross-domain adaptation (e.g., synthetic-to-real). Our model, when trained on the MS-COCO generic image dataset using Homographic Adaptation, is able to repeatedly detect a much richer set of interest points than the initial pre-adapted deep model and any other traditional corner detector. The final system gives rise to state-of-the-art homography estimation results on HPatches when compared to LIFT, SIFT and ORB.', content_ch: '本文提出了一个自我监督的框架，用于培训兴趣点检测器和描述符，适用于计算机视觉中的大量多视图几何问题。与基于斑块的神经网络相反，我们的全趋验证模型在全尺寸图像上运行，并在一个正向通道中共同计算像素级的兴趣点位置和相关的描述符。我们介绍了同型适应性，这是一种多尺度的多阶段方法，用于提高兴趣点检测可重复性和执行跨域适应性（例如，合成对真实）。我们的模型使用同型适应在MS-Coco通用图像数据集上进行训练时，能够反复检测比初始预先适应的深层模型和任何其他传统的角落检测器相比，可以反复检测一套丰富的兴趣点。与升降，筛和球相比，最终系统会引起HPATCHES的最新同构估计结果。', language: true }
])

let Bpapers = reactive([
    { id: 'B01', name: 'BF', paperTitle: 'A Fuzzy Brute Force Matching Method for Binary Image Features', tag: 'CVPR 2017', content: 'Matching of binary image features is an important step in many different computer vision applications. Conventionally, an arbitrary threshold is used to identify a correct match from incorrect matches using Hamming distance which may improve or degrade the matching results for different input images. This is mainly due to the image content which is affected by the scene, lighting and imaging conditions. This paper presents a fuzzy logic based approach for brute force matching of image features to overcome this situation. The method was tested using a well-known image database with known ground truth. The approach is shown to produce a higher number of correct matches when compared against constant distance thresholds. The nature of fuzzy logic which allows the vagueness of information and tolerance to errors has been successfully exploited in an image processing context. The uncertainty arising from the imaging conditions has been overcome with the use of compact fuzzy matching membership functions.', content_ch: '在许多不同的计算机视觉应用程序中，二进制图像功能的匹配是重要的一步。通常，使用任意阈值来使用锤距离匹配的正确匹配来确定可以改善或降低不同输入图像的匹配结果的正确匹配。这主要是由于图像内容受到场景，照明和成像条件的影响。本文提出了一种基于模糊逻辑的方法，用于蛮力匹配图像特征以克服这种情况。使用具有已知地面真相的众所周知的图像数据库对该方法进行了测试。与恒定距离阈值相比，该方法显示出可产生更高数量的正确匹配。模糊逻辑的性质在图像处理环境中成功利用了信息模糊性和对错误的宽容性。通过使用紧凑的模糊匹配成员函数，已经克服了成像条件产生的不确定性。', language: true },
    { id: 'B02', name: 'FLANN', paperTitle: 'FLANN: Fast approximate nearest neighbour search algorithm for elucidating human-wildlife conflicts in forest areas', tag: 'ICSCN 2017', content: 'Elephant accidents have been an increasing phenomenon in recent years. To mitigate these casualties, we propose a system Flann Based Matcher and FLANN (Fast Approximate Nearest Neighbor Search Library) using image processing to monitor the path of elephant movements. This involves the following functionalities 1. Monitoring elephant movement over the track 2. Alerting the nearby railway station, the locomotive pilot and the forest range officer if any such movement is detected Monitoring involves elephant detection using image processing by applying the techniques of background subtraction and foreground enhancement. The result shows significant improvement in detecting and preventing elephant accidents compared to the existing system (without FLANN).', content_ch: '近年来，大象事故一直是一种现象。为了减轻这些伤亡，我们建议使用图像处理来监视大象运动的路径。这涉及以下功能1。监测轨道2上的大象运动。提醒附近的火车站，机车飞行员和森林范围官员（如果检测到任何此类运动监测）涉及通过应用图像处理的大象检测，通过应用背景亚收集技术和前景增强。与现有系统（没有绒布）相比，结果显示出检测和预防大象事故的显着改善。', language: true },
    { id: 'B03', name: 'SuperGlue', paperTitle: 'SuperGlue: Learning Feature Matching with Graph Neural Networks', tag: 'CVPR 2020', content: 'This paper introduces SuperGlue, a neural network that matches two sets of local features by jointly finding correspondences and rejecting non-matchable points. Assignments are estimated by solving a differentiable optimal transport problem, whose costs are predicted by a graph neural network. We introduce a flexible context aggregation mechanism based on attention, enabling SuperGlue to reason about the underlying 3D scene and feature assignments jointly. Compared to traditional, hand-designed heuristics, our technique learns priors over geometric transformations and regularities of the 3D world through end-to-end training from image pairs. SuperGlue outperforms other learned approaches and achieves state-of-the-art results on the task of pose estimation in challenging real-world indoor and outdoor environments. The proposed method performs matching in real-time on a modern GPU and can be readily integrated into modern SfM or SLAM systems. The code and trained weights are publicly available at this https URL.', content_ch: '本文介绍了SuperGlue，这是一个神经网络，通过共同查找对应关系并拒绝不可匹配的点，它匹配了两组局部特征。通过解决一个可区分的最佳运输问题来估算作业，该问题由图神经网络预测其成本。我们基于注意力引入了灵活的上下文聚合机制，使Superglue可以推理基础3D场景并共同特征分配。与传统的手工设计的启发式方法相比，我们的技术通过图像对的端到端培训来了解3D世界的几何变换和规律性的先验。 Superglue的表现优于其他学习的方法，并实现了最先进的结果，即在挑战现实世界和室外环境中姿势估算的任务。所提出的方法在现代GPU上实时执行匹配，并且可以轻松地集成到现代SFM或SLAM系统中。该HTTPS URL公开可用代码和训练的权重。', language: true },
])

let Cpapers = reactive([
    { id: 'C01', name: 'LoFTR', paperTitle: 'LoFTR: Detector-Free Local Feature Matching with Transformers', tag: 'CVPR 2021', content: 'We present a novel method for local image feature matching. Instead of performing image feature detection, description, and matching sequentially, we propose to first establish pixel-wise dense matches at a coarse level and later refine the good matches at a fine level. In contrast to dense methods that use a cost volume to search correspondences, we use self and cross attention layers in Transformer to obtain feature descriptors that are conditioned on both images. The global receptive field provided by Transformer enables our method to produce dense matches in low-texture areas, where feature detectors usually struggle to produce repeatable interest points. The experiments on indoor and outdoor datasets show that LoFTR outperforms state-of-the-art methods by a large margin. LoFTR also ranks first on two public benchmarks of visual localization among the published methods.', content_ch: '我们提出了一种用于局部图像特征匹配的新方法。我们提议首先在粗级上建立像素密度匹配，然后在良好的水平上完善良好的匹配，而不是顺序地进行图像特征检测，描述和匹配，而是先进行像素密度匹配。与使用成本量来搜索对应关系的密集方法相反，我们使用变形金刚中的自我和跨注意层来获取在这两个图像上进行条件的特征描述符。 Transformer提供的全球接受场使我们的方法能够在低文本区域产生密集的匹配，其中功能探测器通常难以产生可重复的兴趣点。室内和室外数据集的实验表明，LOFTR优于最先进的方法。 LOFTR在已发表的方法中的两个视觉定位公共基准中也排名第一。', language: true },
    { id: 'C02', name: 'MatchFormer', paperTitle: 'MatchFormer: Interleaving Attention in Transformers for Feature Matching', tag: 'ACCV 2022', content: 'Local feature matching is a computationally intensive task at the subpixel level. While detector-based methods coupled with feature descriptors struggle in low-texture scenes, CNN-based methods with a sequential extract-to-match pipeline, fail to make use of the matching capacity of the encoder and tend to overburden the decoder for matching. In contrast, we propose a novel hierarchical extract-and-match transformer, termed as MatchFormer. Inside each stage of the hierarchical encoder, we interleave self-attention for feature extraction and cross-attention for feature matching, yielding a human-intuitive extract-and-match scheme. Such a match-aware encoder releases the overloaded decoder and makes the model highly efficient. Further, combining self- and cross-attention on multi-scale features in a hierarchical architecture improves matching robustness, particularly in low-texture indoor scenes or with less outdoor training data. Thanks to such a strategy, MatchFormer is a multi-win solution in efficiency, robustness, and precision. Compared to the previous best method in indoor pose estimation, our lite MatchFormer has only 45% GFLOPs, yet achieves a +1.3% precision gain and a 41% running speed boost. The large MatchFormer reaches state-of-the-art on four different benchmarks, including indoor pose estimation (ScanNet), outdoor pose estimation (MegaDepth), homography estimation and image matching (HPatch), and visual localization (InLoc).', content_ch: '本地功能匹配是在子像素级别上的计算密集任务。尽管基于检测器的方法和特征描述符在低文本场景中挣扎，但具有顺序提取到匹配管道的基于CNN的方法，无法利用编码器的匹配能力，并且倾向于覆盖用于匹配的解码器。相比之下，我们提出了一种新型的分层提取和匹配变压器，称为火柴场。在层次编码器的每个阶段，我们将自我注意事项与特征提取和特征匹配的跨注意事项进行了交流，从而产生了人直觉提取和匹配方案。这种匹配感知的编码器释放了过载的解码器，并使模型高效。此外，在层次结构中将自我和交叉注意相结合，可以提高匹配的鲁棒性，尤其是在低文本的室内场景或更少的室外培训数据中。得益于这样的策略，MatchFormer是效率，鲁棒性和精度的多赢解决方案。与以前的室内姿势估计中的最佳方法相比，我们的Lite Matchformer只有45％的GFLOPS，但获得了 +1.3％的精度增益和41％的运行速度提升。大型火柴配件在四个不同的基准上达到了最新的基准，包括室内姿势估计（SCANNET），室外姿势估计（Megadepth），同型估计和图像匹配（HPATCH）和视觉定位（INLOC）。', language: true },
    { id: 'C03', name: 'Efficient LoFTR', paperTitle: 'Efficient LoFTR: Semi-Dense Local Feature Matching with Sparse-Like Speed', tag: 'CVPR 2024', content: 'We present a novel method for efficiently producing semi-dense matches across images. Previous detector-free matcher LoFTR has shown remarkable matching capability in handling large-viewpoint change and texture-poor scenarios but suffers from low efficiency. We revisit its design choices and derive multiple improvements for both efficiency and accuracy. One key observation is that performing the transformer over the entire feature map is redundant due to shared local information, therefore we propose an aggregated attention mechanism with adaptive token selection for efficiency. Furthermore, we find spatial variance exists in LoFTR’s fine correlation module, which is adverse to matching accuracy. A novel two-stage correlation layer is proposed to achieve accurate subpixel correspon-dences for accuracy improvement. Our efficiency optimized model is∼2.5×faster than LoFTR which can even surpass state-of-the-art efficient sparse matching pipeline Super-Point + LightGlue. Moreover, extensive experiments show that our method can achieve higher accuracy compared with competitive semi-dense matchers, with considerable efficiency benefits. This opens up exciting prospects for large-scale or latency-sensitive applications such as image retrieval and 3D reconstruction. Project page: https://zju3dv.github.io/efficientloftr/.', content_ch: '我们提出了一种新型方法，可有效地跨图像产生半密度匹配。以前的无探测器匹配器LOFTR在处理大视点变化和纹理差的方案方面表现出了显着的匹配能力，但效率低。我们重新审视其设计选择，并为效率和准确性提供多个改进。一个关键的观察结果是，由于共享的本地信息，在整个特征图上执行变压器是多余的，因此我们提出了一种具有自适应令牌选择的聚合注意机制以提高效率。此外，我们发现LOFTR的FINE相关模块中存在空间差异，这与匹配的精度不利。提出了一个新型的两阶段相关层，以实现准确的子像素相关性，以提高准确性。我们的效率优化模型比LOFTR快2.5倍，它甚至可以超过最先进的稀疏匹配管道超点 + Lightglue。此外，广泛的实验表明，与竞争性的半密集匹配器相比，我们的方法可以达到更高的精度，并具有相当大的效率优势。这为大规模或对潜伏期敏感的应用（例如图像检索和3D重建）打开了令人兴奋的前景。', language: true },
    { id: 'C04', name: 'ASpanFormer', paperTitle: 'Detector-Free Image Matching with Adaptive Span Transformer', tag: 'ECCV 2022', content: 'Generating robust and reliable correspondences across images is a fundamental task for a diversity of applications. To capture context at both global and local granularity, we propose ASpanFormer, a Transformer-based detector-free matcher that is built on hierarchical attention structure, adopting a novel attention operation which is capable of adjusting attention span in a self-adaptive manner. To achieve this goal, first, flow maps are regressed in each cross attention phase to locate the center of search region. Next, a sampling grid is generated around the center, whose size, instead of being empirically configured as fixed, is adaptively computed from a pixel uncertainty estimated along with the flow map. Finally, attention is computed across two images within derived regions, referred to as attention span. By these means, we are able to not only maintain long-range dependencies, but also enable fine-grained attention among pixels of high relevance that compensates essential locality and piece-wise smoothness in matching tasks. State-ofthe-art accuracy on a wide range of evaluation benchmarks validates the strong matching capability of our method.', content_ch: '在图像中生成稳健可靠的对应关系是许多应用程序的基本任务。为了在全局和局部粒度上捕获上下文，我们提出了一种基于跨度的无检测器匹配器spanformer，该匹配器建立在分层注意结构上，采用了一种新颖的注意操作，能够以自适应的方式调整注意跨度。为了实现这一目标，首先，在每个交叉注意力阶段对流图进行回归，以定位搜索区域的中心。接下来，在中心周围生成一个采样网格，其大小，而不是根据经验配置为固定，是根据与流图估计的像素不确定性自适应计算的。最后，注意力是在派生区域内的两幅图像上计算的，称为注意力跨度。通过这种方式，我们不仅能够保持长期依赖关系，而且还能够在高度相关性的像素之间进行细粒度的注意，以补偿匹配任务中的基本局部性和分段平滑度。在广泛的评估基准上最先进的准确性验证了我们方法的强匹配能力。', language: true },
    { id: 'C05', name: 'DKM', paperTitle: 'Dense Kernelized Feature Matching for Geometry Estimation', tag: 'CVPR 2023', content: 'Feature matching is a challenging computer vision task that involves finding correspondences between two images of a 3D scene. In this paper we consider the dense approach instead of the more common sparse paradigm, thus striving to find all correspondences. Perhaps counter-intuitively, dense methods have previously shown inferior performance to their sparse and semi-sparse counterparts for estimation of two-view geometry. This changes with our novel dense method, which outperforms both dense and sparse methods on geometry estimation. The novelty is threefold: First, we propose a kernel regression global matcher. Secondly, we propose warp refinement through stacked feature maps and depthwise convolution kernels. Thirdly, we propose learning dense confidence through consistent depth and a balanced sampling approach for dense confidence maps. Through extensive experiments we confirm that our proposed dense method, Dense Kernelized Feature Matching, sets a new state-of-the-art on multiple geometry estimation benchmarks. In particular, we achieve an improvement on MegaDepth-1500 of +4.9 and +8.9 AUC@5◦ compared to the best previous sparse method and dense method respectively. Our code is provided at the following repository:https://github.com/Parskatt/DKM .', content_ch: '功能匹配是一项具有挑战性的计算机视觉任务，涉及在3D场景的两个图像之间找到对应关系。在本文中，我们考虑了密集的方法，而不是更常见的稀疏范式，从而努力找到所有对应关系。也许在违反直觉上，密集的方法先前显示出与稀疏和半帕斯对应物相比的性能，以估计两视频几何形状。这是我们新颖的致密方法的变化，在几何估计上，它的表现优于密集和稀疏方法。新颖性是三倍：首先，我们提出了一个内核回归全球匹配器。其次，我们通过堆叠的特征地图和深度卷积内核提出了经线细化。第三，我们通过一致的深度和平衡的采样方法来提出密集的信心，以进行密集的置信图。通过广泛的实验，我们确认我们提出的密集方法，密集的核特征匹配，为多个几何估计基准设置了新的最新方法。特别是，与最佳以前的稀疏方法和密集方法相比，我们对+4.9和+8.9 AUC的Megadepth-1500进行了改进。', language: true },
    { id: 'C06', name: 'RoMA', paperTitle: 'Dense Kernelized Feature Matching for Geometry Estimation', tag: 'CVPR 2024', content: 'Feature matching is an important computer vision task that involves estimating correspondences between two images of a 3D scene, and dense methods estimate all such correspondences. The aim is to learn a robust model, i.e., a model able to match under challenging real-world changes. In this work, we propose such a model, leveraging frozen pretrained features from the foundation model DINOv2. Although these features are significantly more robust than local features trained from scratch, they are inherently coarse. We therefore combine them with specialized ConvNet fine features, creating a precisely localizable feature pyramid. To further improve robustness, we propose a tailored transformer match decoder that predicts anchor probabilities, which enables it to express multimodality. Finally, we propose an improved loss formulation through regression-byclassification with subsequent robust regression. We conduct a comprehensive set of experiments that show that our method, RoMa, achieves significant gains, setting a new state-of-the-art. In particular, we achieve a 36% improvement on the extremely challenging WxBS benchmark. Code is provided at github.com/Parskatt/RoMa.', content_ch: '特征匹配是一项重要的计算机视觉任务，涉及估计3d场景的两幅图像之间的对应关系，密集方法估计所有这些对应关系。目标是学习一个稳健的模型，即能够在具有挑战性的现实世界变化下匹配的模型。在这项工作中，我们提出了一个模型，利用来自基础模型 dinov2 的冻结预训练特征。尽管这些特征比从头开始训练的局部特征更稳健，但它们本质上是粗糙的。因此，我们将它们与专门的卷积网络精细特征相结合，创建了一个精确的可本地化特征金字塔。为了进一步提高鲁棒性，我们提出了一种定制的Transformer匹配解码器，该解码器预测锚点概率，使其能够表达多模态。最后，我们通过回归分类和随后的稳健回归提出了一种改进的损失公式。我们进行了一组全面的实验，表明我们的方法 roma 取得了显着的进步，创造了新的最先进技术。特别是，我们在极具挑战性的 wxbs 基准上实现了 36% 的改进。代码在 github.com/parskatt/roma。', language: true },
])
</script>

<style scoped>
.demo-tabs {
    height: 88vh;
}


.demo-tabs>.el-tabs__content {
    padding: 32px;
    color: #6b778c;
    font-size: 32px;
    font-weight: 600;
}

.demo-tabs .custom-tabs-label .el-icon {
    vertical-align: middle;
}

.demo-tabs .custom-tabs-label span {
    vertical-align: middle;
    margin-left: 4px;
}
</style>