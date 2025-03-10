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
                        <p v-for="p in Apapers" key="p.id">
                            <IntroItem :paper="p"></IntroItem>
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
                <p v-for="p in Bpapers" key="p.id">
                    <IntroItem :paper="p"></IntroItem>
                </p>
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
                <p v-for="p in Cpapers" key="p.id">
                    <IntroItem :paper="p"></IntroItem>
                </p>
            </el-scrollbar>
        </el-tab-pane>
    </el-tabs>
</template>

<script lang='ts' setup name='Introduction'>
import IntroItem from "@/components/IntroItem.vue";
import { reactive } from "vue"

let Apapers = reactive([
    { id: 'A01', name: 'Harris', paperTitle: 'A Combined Corner and Edge Detector', tag: 'Alvey Vision Conference 1988', content: 'Consistency of image edge filtering is of prime importance for 3D interpretation of image sequences using feature tracking algorithms. To cater for image regions containing texture and isolated features, a combined corner and edge detector based on the local auto-correlation function is utilised, and it is shown to perform with good consistency on natural imagery.' },
    { id: 'A02', name: 'Shi-Tomasi', paperTitle: 'Good features to track', tag: 'CVPR 1994', content: 'No feature-based vision system can work unless good features can be identified and tracked from frame to frame. Although tracking itself is by and large a solved problem, selecting features that can be tracked well and correspond to physical points in the world is still hard. We propose a feature selection criterion that is optimal by construction because it is based on how the tracker works, and a feature monitoring method that can detect occlusions, disocclusions, and features that do not correspond to points in the world. These methods are based on a new tracking algorithm that extends previous Newton-Raphson style search methods to work under affine image transformations. We test performance with several simulations and experiments.' },
    { id: 'A03', name: 'Sift', paperTitle: 'Scale-Invariant Feature Transform', tag: 'Springer, London 2016', content: 'Many real applications require the localization of reference positions in one or more images, for example, for image alignment, removing distortions, object tracking, 3D reconstruction, etc. We have seen that corner points1 can be located quite reliably and independent of orientation. However, typical corner detectors only provide the position and strength of each candidate point, they do not provide any information about its characteristic or “identity” that could be used for matching. Another limitation is that most corner detectors only operate at a particular scale or resolution, since they are based on a rigid set of filters.' },
    { id: 'A04', name: 'ORB', paperTitle: 'ORB: An efficient alternative to SIFT or SURF', tag: 'ICCV 2011', content: 'Feature matching is at the base of many computer vision problems, such as object recognition or structure from motion. Current methods rely on costly descriptors for detection and matching. In this paper, we propose a very fast binary descriptor based on BRIEF, called ORB, which is rotation invariant and resistant to noise. We demonstrate through experiments how ORB is at two orders of magnitude faster than SIFT, while performing as well in many situations. The efficiency is tested on several real-world applications, including object detection and patch-tracking on a smart phone.' },
    { id: 'A05', name: 'SuperPoint', paperTitle: 'SuperPoint: Self-Supervised Interest Point Detection and Description', tag: 'CVPR 2018', content: 'This paper presents a self-supervised framework for training interest point detectors and descriptors suitable for a large number of multiple-view geometry problems in computer vision. As opposed to patch-based neural networks, our fully-convolutional model operates on full-sized images and jointly computes pixel-level interest point locations and associated descriptors in one forward pass. We introduce Homographic Adaptation, a multi-scale, multi-homography approach for boosting interest point detection repeatability and performing cross-domain adaptation (e.g., synthetic-to-real). Our model, when trained on the MS-COCO generic image dataset using Homographic Adaptation, is able to repeatedly detect a much richer set of interest points than the initial pre-adapted deep model and any other traditional corner detector. The final system gives rise to state-of-the-art homography estimation results on HPatches when compared to LIFT, SIFT and ORB.' }
])

let Bpapers = reactive([
    { id: 'B01', name: 'BF', paperTitle: 'A Fuzzy Brute Force Matching Method for Binary Image Features', tag: 'CVPR 2017', content: 'Matching of binary image features is an important step in many different computer vision applications. Conventionally, an arbitrary threshold is used to identify a correct match from incorrect matches using Hamming distance which may improve or degrade the matching results for different input images. This is mainly due to the image content which is affected by the scene, lighting and imaging conditions. This paper presents a fuzzy logic based approach for brute force matching of image features to overcome this situation. The method was tested using a well-known image database with known ground truth. The approach is shown to produce a higher number of correct matches when compared against constant distance thresholds. The nature of fuzzy logic which allows the vagueness of information and tolerance to errors has been successfully exploited in an image processing context. The uncertainty arising from the imaging conditions has been overcome with the use of compact fuzzy matching membership functions.' },
    { id: 'B02', name: 'FLANN', paperTitle: 'FLANN: Fast approximate nearest neighbour search algorithm for elucidating human-wildlife conflicts in forest areas', tag: 'ICSCN 2017', content: 'Elephant accidents have been an increasing phenomenon in recent years. To mitigate these casualties, we propose a system Flann Based Matcher and FLANN (Fast Approximate Nearest Neighbor Search Library) using image processing to monitor the path of elephant movements. This involves the following functionalities 1. Monitoring elephant movement over the track 2. Alerting the nearby railway station, the locomotive pilot and the forest range officer if any such movement is detected Monitoring involves elephant detection using image processing by applying the techniques of background subtraction and foreground enhancement. The result shows significant improvement in detecting and preventing elephant accidents compared to the existing system (without FLANN).' },
])

let Cpapers = reactive([
    { id: 'C01', name: 'LoFTR', paperTitle: 'LoFTR: Detector-Free Local Feature Matching with Transformers', tag: 'CVPR 2021', content: 'We present a novel method for local image feature matching. Instead of performing image feature detection, description, and matching sequentially, we propose to first establish pixel-wise dense matches at a coarse level and later refine the good matches at a fine level. In contrast to dense methods that use a cost volume to search correspondences, we use self and cross attention layers in Transformer to obtain feature descriptors that are conditioned on both images. The global receptive field provided by Transformer enables our method to produce dense matches in low-texture areas, where feature detectors usually struggle to produce repeatable interest points. The experiments on indoor and outdoor datasets show that LoFTR outperforms state-of-the-art methods by a large margin. LoFTR also ranks first on two public benchmarks of visual localization among the published methods.' },
    { id: 'C02', name: 'MatchFormer', paperTitle: 'MatchFormer: Interleaving Attention in Transformers for Feature Matching', tag: 'ACCV 2022', content: 'Local feature matching is a computationally intensive task at the subpixel level. While detector-based methods coupled with feature descriptors struggle in low-texture scenes, CNN-based methods with a sequential extract-to-match pipeline, fail to make use of the matching capacity of the encoder and tend to overburden the decoder for matching. In contrast, we propose a novel hierarchical extract-and-match transformer, termed as MatchFormer. Inside each stage of the hierarchical encoder, we interleave self-attention for feature extraction and cross-attention for feature matching, yielding a human-intuitive extract-and-match scheme. Such a match-aware encoder releases the overloaded decoder and makes the model highly efficient. Further, combining self- and cross-attention on multi-scale features in a hierarchical architecture improves matching robustness, particularly in low-texture indoor scenes or with less outdoor training data. Thanks to such a strategy, MatchFormer is a multi-win solution in efficiency, robustness, and precision. Compared to the previous best method in indoor pose estimation, our lite MatchFormer has only 45% GFLOPs, yet achieves a +1.3% precision gain and a 41% running speed boost. The large MatchFormer reaches state-of-the-art on four different benchmarks, including indoor pose estimation (ScanNet), outdoor pose estimation (MegaDepth), homography estimation and image matching (HPatch), and visual localization (InLoc).' },
    { id: 'C03', name: 'SuperGlue', paperTitle: 'SuperGlue: Learning Feature Matching with Graph Neural Networks', tag: 'CVPR 2020', content: 'This paper introduces SuperGlue, a neural network that matches two sets of local features by jointly finding correspondences and rejecting non-matchable points. Assignments are estimated by solving a differentiable optimal transport problem, whose costs are predicted by a graph neural network. We introduce a flexible context aggregation mechanism based on attention, enabling SuperGlue to reason about the underlying 3D scene and feature assignments jointly. Compared to traditional, hand-designed heuristics, our technique learns priors over geometric transformations and regularities of the 3D world through end-to-end training from image pairs. SuperGlue outperforms other learned approaches and achieves state-of-the-art results on the task of pose estimation in challenging real-world indoor and outdoor environments. The proposed method performs matching in real-time on a modern GPU and can be readily integrated into modern SfM or SLAM systems. The code and trained weights are publicly available at this https URL.' },
    { id: 'C04', name: 'Efficient LoFTR', paperTitle: 'Efficient LoFTR: Semi-Dense Local Feature Matching with Sparse-Like Speed', tag: 'CVPR 2024', content: 'We present a novel method for efficiently producing semi-dense matches across images. Previous detector-free matcher LoFTR has shown remarkable matching capability in handling large-viewpoint change and texture-poor scenarios but suffers from low efficiency. We revisit its design choices and derive multiple improvements for both efficiency and accuracy. One key observation is that performing the transformer over the entire feature map is redundant due to shared local information, therefore we propose an aggregated attention mechanism with adaptive token selection for efficiency. Furthermore, we find spatial variance exists in LoFTR’s fine correlation module, which is adverse to matching accuracy. A novel two-stage correlation layer is proposed to achieve accurate subpixel correspon-dences for accuracy improvement. Our efficiency optimized model is∼2.5×faster than LoFTR which can even surpass state-of-the-art efficient sparse matching pipeline Super-Point + LightGlue. Moreover, extensive experiments show that our method can achieve higher accuracy compared with competitive semi-dense matchers, with considerable efficiency benefits. This opens up exciting prospects for large-scale or latency-sensitive applications such as image retrieval and 3D reconstruction. Project page: https://zju3dv.github.io/efficientloftr/.' }
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