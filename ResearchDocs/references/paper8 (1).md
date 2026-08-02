www.nature.com/scientificreports 



# **OPEN Advanced cloud intrusion detection framework using graph based features transformers and contrastive learning** 

**Vijay Govindarajan**<sup>**1,3**</sup> **& Junaid Hussain Muzamal**<sup>**2,3**</sup> 

**This paper presents a modular and scalable intrusion detection framework that combines graphbased feature extraction, Transformer-based autoencoding, and contrastive learning to improve detection accuracy in cloud environments. Network flows are modeled as graphs to capture relational patterns among IP addresses and services, and a Graph Neural Network (GNN) is used to extract structured embeddings. These embeddings are refined through a Transformer-based autoencoder to preserve contextual information, while contrastive learning enforces clear class separation during classification. The system is evaluated on NSL-KDD and CIC-IDS2018 datasets under both binary and multi-class scenarios. Experimental results show an average accuracy of 99.97%, with high precision and recall across all attack types, including minority classes such as U2R and R2L. The model achieves low false-positive rates and demonstrates real-time inference performance with modest resource requirements. Key contributions include an interpretable pipeline using SHAP for feature attribution, a strategy for mitigating class imbalance, and validation across datasets with detailed security and generalizability analyses. These results support the practical applicability of the proposed approach in high-throughput, cloud-based network environments.** 

The rapid growth of cloud computing and its adoption in various industries have led to significant advancements in scalability, cost-efficiency, and accessibility<sup>1</sup> . However, this widespread reliance on cloud environments also increases the attack surface for cyber threats, making intrusion detection an ever more important component of cloud security. Despite the proliferation of security measures, the fast pace and distributed nature of cloud infrastructure introduces unique challenges. Traditional intrusion detection systems, designed for static networks, struggle to keep pace with the complex patterns of modern attacks<sup>2</sup> . Attackers are employing increasingly sophisticated tactics, ranging from zero-day vulnerabilities to advanced persistent threats (APTs), often targeting the inherent trust within cloud tenants and service providers<sup>3</sup> . This evolving threat field is further complicated by the sheer volume of network traffic and the diversity of protocols and services found in cloud ecosystems. As a result, the ability to detect and respond to malicious activities in real time is important<sup>4</sup> . The limitations of existing methods show the need for innovative approaches that can handle large-scale data, adapt to arising attack patterns, and provide actionable insights for security administrators<sup>5</sup> . 

In this context, the use of advanced machine learning techniques and state-of-the-art neural architectures offers a promising path forward<sup>6</sup> . Graph-based representations of network traffic and deep learning models have shown potential in extracting meaningful patterns and identifying anomalies that traditional rule-based systems might miss<sup>7</sup> . By integrating these modern computational methods into the cloud intrusion detection framework, we can begin to address the shortcomings of conventional solutions and move closer to a more secure cloud environment<sup>8</sup> . 

### **Research problem** 

Given the increased reliance on cloud infrastructure, the detection and mitigation of malicious activities within such environments remain significant challenges<sup>9</sup> . The key problem lies in developing a robust, scalable and adaptive intrusion detection mechanism that can accurately classify normal and attack traffic in real time, while also providing high precision and recall<sup>10</sup> . Existing systems struggle with handling large datasets, differentiating between benign anomalies and actual attacks, and adapting to the evolving tactics of adversaries<sup>11</sup> . As a result, 

1Colorado State University, Seattle, USA. 2National University of Computer and Emerging Sciences, Lahore, Pakistan.<sup>3</sup> Vijay Govindarajan, Junaid Hussain Muzamal contributed equally to this work.<sup></sup> email: vijay.govindarajan91@gmail.com 

**Scientific Reports** |        (2025) 15:20511 

1 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

there is a pressing need for an intrusion detection approach that not only achieves high detection accuracy but also maintains efficiency and interpretability in complex cloud-based scenarios. 

### **Related work and gaps** 

Existing solutions to intrusion detection in cloud environments primarily involve signature-based methods, rulebased systems, or traditional statistical models<sup>12</sup> . These approaches often rely on predefined attack signatures or simplistic anomaly thresholds, which limits their ability to detect novel or evolving threats<sup>13</sup> . Although recent advances in machine learning, such as supervised learning models and deep neural networks, have improved detection rates, they frequently suffer from high false-positive rates, lack interpretability, and struggle with generalizing to unseen attack types<sup>14</sup> . Furthermore, many current methods fail to incorporate the rich relational information embedded in network traffic data, which could otherwise enhance their understanding of attack . patterns and reduce misclassification<sup>15</sup> 

### **Proposed approach** 

To address these limitations, we propose a novel cloud intrusion detection framework that uses graph-based feature extraction, transformer-based autoencoders, and contrastive learning to deliver a more robust and adaptive solution. By representing network traffic as graphs, our approach captures the relational structure among nodes, enabling more accurate detection of complex attack patterns. The use of transformer architectures allows for refined feature representations that retain important contextual information, while contrastive learning enhances the model’s ability to distinguish between subtle differences in traffic behaviors. This holistic approach not only improves detection accuracy and precision but also reduces false positives, enhances scalability, and provides greater resilience to evolving attack techniques. 

### **Aim** 

The aim of this research is to develop a robust, scalable, and interpretable intrusion detection framework that improves detection accuracy and reduces false positives in cloud environments. 

### **Research objectives** 

1. To design a graph-based feature extraction pipeline that captures the relational structure of network traffic in cloud environments. 

2. To develop a Transformer-based autoencoder for refining feature representations and enhancing model robustness. 

3. To integrate contrastive learning techniques into the detection framework to improve classification performance and resilience to evolving attack patterns. 

### **Research questions** 

1. How can graph-based representations of network traffic improve the accuracy and interpretability of intrusion detection in cloud environments? 

2. What role do Transformer-based architectures play in refining features and reducing false positives in the detection pipeline? 

3. How does the integration of contrastive learning affect the model’s ability to adapt to arising attack strategies? 

### **Significance of research** 

This research contributes significantly to the field of cloud security by addressing important gaps in current intrusion detection methodologies. By using graph-based feature extraction and Transformer architectures, the proposed framework offers a novel way to understand and detect complex attack patterns. This approach not only improves detection accuracy but also enhances the scalability and adaptability of intrusion detection systems, ensuring they remain effective as cloud environments continue to evolve. Furthermore, the integration of contrastive learning introduces a more refined method for distinguishing malicious traffic from benign anomalies, reducing false positives and enabling security administrators to focus their efforts on true threats. The proposed framework thus provides a more reliable and actionable solution for maintaining trust and security in cloud infrastructures. 

The outcomes of this research extend beyond academic contributions, offering practical tools and techniques that can be adopted by industry practitioners. By enhancing the precision, recall, and interpretability of intrusion detection systems, this work helps organizations protect their sensitive data, maintain service availability, and prevent costly breaches. In doing so, it advances the state of the art in cloud security and sets the stage for future innovations in this important domain. The rest of this paper is structured as follows. Section “Background and motivation” provides a detailed review of related work, highlighting existing solutions and identifying their limitations. Section “Research problem” describes the proposed methodology, including the overall framework, data pre-processing, and model components. Section “Related work and gaps” outlines the experimental setup, including datasets, training procedures, and evaluation metrics. Section “Proposed approach” presents the results and discusses the key findings. Finally, section “Aim” concludes the paper and propose directions for future research. To ensure the practical utility and transparency of our approach, the paper further discusses the interpretability of model outputs, evaluates generalization across datasets, and analyzes computational tradeoffs. Formal and informal security analyses are included to assess system robustness, and overfitting mitigation strategies are detailed. Limitations related to detecting advanced threats such as APTs are acknowledged, along 

**Scientific Reports** |        (2025) 15:20511 

2 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

with directions for future research. Together, these additions aim to present a comprehensive, explainable, and operationally feasible solution for modern intrusion detection. 

## **Literature review** 

The advent of deep learning has significantly influenced the field of intrusion detection, offering innovative approaches to identifying and mitigating threats within complex network environments. Generally, deep learningbased methodologies can be divided into two broad categories: supervised and unsupervised techniques. The fundamental distinction between these approaches lies in the availability of labeled data during training. In supervised learning, labeled data guide the model to learn a mapping from inputs to their corresponding output classes. Convolutional neural networks (CNNs), known for their hierarchical feature extraction capabilities, fall into this category and have been widely employed for image-related tasks, but have also been adapted for certain intrusion detection scenarios. Unsupervised methods operate without labeled data, often relying on structures such as deep belief networks (DBNs), autoencoders (AEs), and recurrent neural networks (RNNs). These unsupervised approaches are particularly valuable for uncovering hidden patterns, reducing dimensionality, and detecting anomalies without requiring a predefined ground truth. 

Several studies have specifically focused on intrusion detection using benchmark datasets such as KDD Cup 99 and NSL-KDD, which provide well-defined feature sets and labels. Researchers have explored various deep learning architectures on these datasets, demonstrating the versatility and effectiveness of different model configurations. For example, Tang et al.<sup>16</sup> used a deep neural network (DNN) model on the NSL-KDD dataset to perform anomaly detection in software-defined networking (SDN) environments, selecting six features from the original 41. Although their work confirmed the potential of DNNs for anomaly detection, they encountered high false positive rates when the model was applied outside its trained environment, and the limited set of features posed challenges in identifying more complex attacks. Similarly, Salama et al.<sup>17</sup> proposed a hybrid approach that integrated DBNs for feature extraction with SVMs for classification. This method improved detection performance compared to using DBNs or SVMs independently, but the combination of multiple approaches added complexity and raised concerns about maintaining real-time performance. 

Aygun et al.<sup>18</sup> introduced autoencoder-based methods to detect zero-day attacks, including standard autoencoders and denoising variants, achieving classification accuracies of 88.28% and 88.65% on the NSLKDD dataset. Using a stochastic thresholding approach, they improved the models’ ability to handle anomalies; however, this technique did not generalize well across other data sets or real-world conditions. Javaid et al.<sup>19</sup> utilized self-taught learning (STL) with sparse autoencoders and softmax regression, yielding strong classification results on multiple class categories. Despite achieving satisfactory accuracy, precision, recall, and F1-scores, their method struggled with false positives and difficulties in selecting features for diverse attack scenarios. In another study, Niyaz et al.<sup>20</sup> applied stacked autoencoders to detect DDoS attacks within an SDN environment. Although the model achieved high accuracy with low false positives, it relied heavily on highquality labeled data, and its effectiveness varied depending on attack type and context. Wenjuan et al.<sup>21</sup> introduce a hybrid intrusion detection model using Stacked Contractive Auto-Encoders (SCAE) for feature extraction and SVM for classification. The model shows high performance on NSL-KDD and KDD Cup 99 datasets, achieving excellent AUC scores in 5-class and 13-class tasks, with strong accuracy and recall for DOS and Probe attacks. It also excels in 2-class and 5-class tasks on KDD Cup 99, highlighting its capability with high-dimensional data. Limitations include challenges in detecting underrepresented attack classes (U2R, R2L) and high computational costs for deeper architectures. 

Beyond the NSL-KDD dataset, other works have investigated intrusion detection using the KDD Cup 99 dataset. Kim et al.<sup>22</sup> focused on (APTs) and proposed a DNN model that employed 100 hidden units, the rectified linear unit (ReLU) activation function, and the ADAM optimizer. Although their approach was implemented on a GPU using TensorFlow, improving detection accuracy, it faced high false alarm rates in practical scenarios. Papamartzivanos et al.<sup>23</sup> merged the KDD Cup 99 and NSL-KDD datasets to create a larger training corpus, enabling them to develop a scalable intrusion detection system based on sparse autoencoders and the MAPE-K framework. Despite achieving an adaptive detection rate of 73.37%, their method required significant computational resources and struggled in highly fast-paced environments. Shone et al.<sup>24</sup> introduced a non-symmetric deep autoencoder (NDAE) that provided efficient dimensionality reduction and outperformed traditional autoencoders when paired with Random Forest classifiers. Although this approach demonstrated superior classification performance, it was highly dependent on benchmark datasets and lacked scalability in heterogeneous environments. 

Additional studies have expanded their investigations to private datasets and other public benchmarks. Loukas et al.<sup>25</sup> explored RNN-based intrusion detection enhanced with long short-term memory (LSTM) units, significantly improving detection accuracy for a robotic vehicle environment. Their approach showed greater consistency and accuracy compared to traditional machine learning methods but depended on stable network conditions and reliable offloading infrastructure. Yu et al.<sup>26</sup> developed a network intrusion detection model based on stacked denoising autoencoders and softmax classifiers. Their model, tested on multiple datasets including the UNB ISCX IDS 2012 and CTU-13, achieved better performance than DBNs and other autoencoder models. Subsequently, Yu et al. proposed stacked dilated convolutional autoencoders that learned features from preextracted flow features data more efficiently, though these models required intensive computational resources and careful hyperparameter tuning. 

Recent literature surveys have also shed light on the broader field of intrusion detection. For example, Abdulganiyu et al.<sup>27</sup> conducted a systematic review of the literature (SLR) that included signature-based, anomaly-based and hybrid intrusion detection systems. By analyzing studies that used datasets such as NSLKDD and CICIDS2017, they identified key challenges such as high false-positive rates and data imbalance. Despite ongoing accuracy improvements in recent approaches, the review highlighted the lack of well-explored 

**Scientific Reports** |        (2025) 15:20511 

3 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

hybrid solutions, signaling an opportunity for further research into combining multiple methodologies. Similarly, advanced neural architectures have emerged to address these gaps. Wang et al.<sup>28</sup> introduced TabTransformer for binary classification tasks, demonstrating strong performance on a simulated military network environment. While this method achieved high accuracy, its applicability to real-world datasets remained uncertain, showing the need for solutions that generalize beyond controlled experimental conditions. 

Transformer-based frameworks have also shown promise in flow-based network intrusion detection. Manocchio et al.<sup>29</sup> proposed FlowTransformer, which achieved over 95% accuracy while significantly reducing model size. This represents a step forward in designing more efficient and scalable models. Additionally, Devendiran and Turukmane’s<sup>30</sup> Dugat-LSTM model utilized a gated attention mechanism alongside a chaotic optimization strategy, achieving accuracies of 98.76% on the TON-IOT dataset and 99.65% on NSL-KDD. However, both approaches faced challenges related to computational complexity and hyperparameter tuning, which remain central concerns in the field. Other studies, such as Talukder et al.<sup>31</sup> machine learning-based approaches for imbalanced data, have demonstrated impressive accuracy gains (over 99.9%) using advanced preprocessing and feature selection techniques. Nonetheless, these methods still contend with increased processing times and scalability issues. Varzaneh and Hosseini<sup>32</sup> work on feature selection with binary levy opposition equilibrium optimization further highlights the trade-off between performance gains and the challenges of handling high-dimensional datasets. Previous approaches to intrusion detection in edge and cloud environments prioritized lightweight models and targeted classification mechanisms. 

Shitharth et al.<sup>33</sup> proposed a hybrid neural classifier combining backpropagation and radial basis function networks for multi-attack detection on edge devices. Selvarajan et al.<sup>34</sup> developed a SCADA-based system that applied mean-shift clustering and flora-optimized Boltzmann classification to refine detection. Prashanth et al.<sup>35</sup> implemented a lightweight IDS enhanced by hybrid reinforcement learning for dynamic threat recognition in CIC-IDS2017. Bassam et al.<sup>36</sup> designed a PSO-tuned RNN pipeline that improved accuracy in temporal classification across UNSW-NB15. Shitharth et al.<sup>37</sup> introduced a quantum genetic algorithm for multimodal sensor fusion, which improved feature discrimination under noise but introduced complexity. These models addressed specific operational environments by balancing compactness and detection effectiveness. 

Researchers also addressed adaptive intrusion strategies by designing decision frameworks capable of responding to diverse traffic. Tellache et al.<sup>38</sup> employed a multi-agent DQN with cost-sensitive learning to mitigate class imbalance on CIC-IDS2017. Korba et al.<sup>39</sup> presented a federated learning architecture supported by blockchain and open-set recognition, which enabled secure and flexible detection of emerging threats in IoV networks. Diaf et al.<sup>40</sup> constructed an anomaly prediction system using BART-BERT transformers, achieving high accuracy on CICIoT2023 while reducing reliance on feature engineering. Hyatt et al.<sup>41</sup> proposed a real-time memory-efficient detection system optimized for constrained deployments using KDD’99-style traffic. These solutions operated under resource-aware conditions while maintaining robust classification in fast-paced data environments. 

Hybrid detection frameworks recently contributed new strategies for detecting zero-day anomalies and reducing labeling dependency. Korba, Diaf, and Doudane<sup>42</sup> developed a semi-supervised detection model that achieved 100% accuracy for packet-based command and control detection on IoT-23 and 94% using flowbased signals. Their approach required minimal supervision and allowed early detection. Korba, Karabadji, and Doudane<sup>43</sup> designed a PSO-optimized ensemble using Isolation Forests to detect passive and N-day attacks, achieving a 93.8% F1-score on the AntibotV dataset. These models incorporated ensemble diversity and minimal human intervention to deliver adaptive classification performance under constrained visibility. They demonstrated methods for sustaining anomaly detection in modern threat environments with limited prior 1 and Table. 2. data. The suammry of the literature review is provided in Table. 

These recent advances illustrate the growing sophistication of intrusion detection methodologies. However, they also emphasize that while accuracy improvements are being realized, challenges such as scalability, computational demand, and generalization persist. Ongoing research must continue to refine these approaches to ensure that they meet the demands of increasingly complex and fast-paced network environments. This paper contributes to the body of research as follows: 

1. Developed a multi-class network intrusion detection framework using transformer-based architectures, addressing the unique challenges of handling multiple attack categories. 

2. Implemented an advanced data preprocessing pipeline that effectively mitigates class imbalance, ensuring equitable performance across both majority and minority classes. 

3. Achieved state-of-the-art accuracy levels (99.97% average) on benchmark datasets, setting a new standard for multiclass classification in the intrusion detection domain. 

4. Enhanced real-time applicability by optimizing computational efficiency and inference time, making the approach viable for fast pace, high-throughput network environments. 

5. Introduced novel feature extraction and selection techniques, improving the robustness of the model and generalization to various types of attacks. 

6. Validated the proposed framework on multiple datasets, demonstrating consistent performance improvements over existing methods and confirming the solution’s scalability and reliability. 

## **Methodology** 

Cloud-based systems are increasingly vulnerable to a variety of cyberattacks due to their distributed nature, multi-tenancy, and fast-paced scaling. The proposed methodology aims to address these challenges by developing a robust, adaptive, and interpretable IDS for cloud environments. This approach combines the strengths of GNNs, Transformer-based autoencoders, and contrast learning to capture spatiotemporal relationships in 

**Scientific Reports** |        (2025) 15:20511 

4 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

|**Study**|**Methodology**|**Datasets**|**Results**|**Key challenges**|
|---|---|---|---|---|
|Shitharth et al.<sup>33</sup>|Back propagation<br>(BP) Neural Net- work Radial basis function (RBF)|Multi-attack IDS<br>for edge|80.1%accuracy,85%|Precisionmultiattack<br>nario<br>sce-|
|Selvarajan et al.<sup>34</sup>|Mean-shif clus-<br>tering, fora op- timization, Boltz- mann classifer|SCADA|Not specifed, but compara-<br>tive to SOTA|Cluster mismatches, irrele-<br>vant features|
|Prashanth et al.<sup>35</sup>|Lightweight IDS<br>with hybrid rein- forcement learn- ing|CIC-IDS2017|Improved detection and low<br>FP|Class imbalance, dynamic at-<br>tack adaptation|
|Bassam et al.<sup>36</sup>|Hybrid<br>PSO–RNN<br>withenhanced preprocessing|UNSW-NB15|High accuracy on UNSW<br>dataset|Temporal dependencies, pa-<br>rameter tuning|
|Shitharth et al.<sup>37</sup>|Quantum Genetic<br>Algorithmwith multi-modal sensor data|Custom SCADA<br>sensor data|Efective multimodal feature<br>selection|Quantum complexity<br>SCADA noise and|
|Tellache et al.<sup>38</sup>|Multi-agent<br>DQN with cost- sensitive learning|CIC-IDS2017|Improved detection rate and<br>low FP|Class imbalance and attack<br>variability|
|Korba et al.<sup>39</sup>|Zero-X FL + OSR<br>Blockchain- based IDS|Custom<br>datasets<br>IoV|High detection rate and mini-<br>mal FP|Zero-day and privacy in IoV|
|Diaf et al.<sup>40</sup>|BART-BERT<br>basedLLM<br>frameworkfor IoT|CICIoT2023|98% accuracy|Reactive IDS and pattern an-<br>ticipation|
|Hyatt et al.<sup>41</sup>|Real-time<br>memory-efcient NIDS|KDD’99<br>plied)<br>(im-|Accuracy: Approx. 95–96%<br>(assumed)|Memory constraint, model<br>portability|
|Korba, Diaf, and<br>Doudane<sup>42</sup>|Semi-supervised<br>anomaly detec- tion using fows and packets|IoT-23|100% C2 detection (packet),<br>94% (fow)|Early detection, minimal<br>training data|
|Korba, Karabadji,<br>and Doudane<sup>43</sup>|PSO-optimized<br>meta-ensemble Isolation Forest|AntibotV|93.8% F1-score (N-day),<br>strong 0-day performance|Detecting passive threats, dy-<br>namic updating|



**Table 1** . Summary of related studies (2). 

|**Study**|**Methodology**|**Datasets**|**Results**|**Key challenges**|
|---|---|---|---|---|
|Tang et al.<sup>16</sup>|DNN for fow-<br>based anomaly detection|NSL-KDD|High detection rate for selected<br>features|High false positives, limited<br>features hinder complex at- tack detection|
|Salama et al.<sup>17</sup>|Hybrid SVM DBN +|Likely<br>KDD/NSL- KDD|Improved performance com-<br>pared to standalone models|Complexity in combining approaches,<br>real-time performance issues|
|Aygun et al.<sup>18</sup>|Autoencoder, De-<br>noising AE|NSL-KDD|88.28%, 88.65% accuracy|Stochastic threshold generalization issues|
|Niyaz et al.<sup>20</sup>|Sparse AE + sof-<br>max regression|NSL-KDD|Strong classifcation accuracy<br>across 2/5/23 classes|High false positives, challenging feature<br>selection|
|Wenjuan et al.<sup>21</sup>|Stacked Contractive AE + SVM|NSL-KDD, KDD<br>Cup 99|High AUC and accuracy for<br>DOS/Probe attacks|Difculties with U2R/R2L<br>detection,computational costs|
|Kim et al.<sup>22</sup>|DNN(ReLU,<br>ADAM)|KDD Cup 99|Improved detection accuracy|High false alarm rates in real-<br>world scenarios|
|Shone et al.<sup>24</sup>|Non-Symmetric<br>AE + RF classifer|KDDCup99,<br>NSL-KDD|Superior classifcation results|Dependency on benchmark<br>datasets, limited scalability|
|Loukas et al.<sup>25</sup>|RNN + LSTM|Private data|High accuracy, consistent results|Requires stable networks, re-<br>liable ofoading infrastructure|
|Yu et al.<sup>26</sup>|Stacked Denoising AE + sofmax|Multiplepublic<br>datasets|High performance on UNB<br>ISCX IDS 2012/CTU-13|Resource-intensive, hyperparameter<br>sensitivity|
|Wang et al.<sup>28</sup>|TabTransformer|Simulated military network|High accuracy|Limited generalizability|
|Manocchio et<br>al<sup>29</sup>.|FlowTransformer|CICIDS2017,<br>UNSW-NB15,<br>NetFlow|> 95% accuracy, reduced<br>model size|Hyperparameter tuning challenges|
|Devendiran et<br>al<sup>30</sup>.|Dugat-LSTM +<br>chaotic optimization|TON-IOT, NSL-<br>KDD|98.76% (TON-IOT), 99.65%<br>(NSL-KDD)|High computational complexity|
|Talukder et al.<sup>31</sup>|ML-based,<br>Random oversampling + PCA|UNSW-NB15,<br>CIC-IDS- 2017/2018|> 99.9% accuracy|Increased processing time|
|Varzaneh et al.<sup>32</sup>|BinaryLevy<br>Opposition Optimization|NSL-KDD,<br>UNSW-NB15, CICIDS2017|97.6% accuracy, 100% precision<br>(UNSW-NB15)|Scalability issues|



**Table 2** . Summary of related studies (1). 

network traffic and classify anomalies effectively. The following section*s present a detailed explanation of the methodology. 

The methodology diagram in Fig. 1 provides a visual representation of the proposed framework. It outlines the key components and their flow, including data preprocessing, feature extraction using, refinement through a Transformer-based autoencoder, and the final classification step. This diagram captures the entire pipeline, 

**Scientific Reports** |        (2025) 15:20511 

5 

| https://doi.org/10.1038/s41598-025-07956-w 



<!-- Start of picture text -->
fi)<br>aN = CleanedNormalized and |= au Zz xb g= toPass Transformer embeddings for [Corwena<br>Rie— SUZ, — T&S St is oes)LS =é eae b awe vo aeee AttentionJ—® |<br>Raw Network Traffic Data Data Preprocessing ;<br>Graph Neural Network Transformer-Based Autoencoder<br>6" =(% A) om Q . - Genera’te ised<br>rodicerromiydetection | sony A ms; => (CIMPrapoaMed) * ScereFe | os,ae contentlize!<br>traffic classifications and (omQ Qe BE:  Den Encoder Naximice labeliabeling LY\ \ Y& rerined 1<br>¢ a~~4 Qvgmenttions :FT 0) Xgreement < —__ 1°° OR /<br>\ hon A li h. proton Mead SHE \ /<br>jX25 PEAS ox ><. Pesitive Pa<br>Final.  Output Contrastive; learning;  module NE Refined Features<br>Classification Layer<br><!-- End of picture text -->

nature portfolio 

www.nature.com/scientificreports/ 

where _θ_ represents the parameters of the classification model. The objective is to minimize the classification error: 



where  is a loss function (e.g., cross-entropy loss), and _yi_ is the true label of _ti_ . 

### **Model selection rationale** 

The components of the proposed intrusion detection framework were selected based on their strengths in handling structural, sequential, and distributional challenges commonly observed in cyber-attack scenarios<sup>44</sup> . Graph-based representations were adopted to model the interactions between network entities such as sourcedestination IPs, ports, and protocols. Unlike flat tabular formats, graph structures preserve relational context and temporal dependencies across connections, which is essential for detecting coordinated or multi-hop attacks. GNNs, particularly GCNs, have been effective in anomaly detection tasks involving communication networks and IoT ecosystems due to their ability to aggregate neighborhood-level semantics<sup>45</sup> . 

Transformer-based architectures were used next to capture long-range dependencies and hierarchical feature representations from GNN-derived embeddings<sup>46</sup> . Their self-attention mechanism allows the model to identify subtle yet relevant patterns across input dimensions, which is valuable for distinguishing similar traffic types such as normal and low-profile attacks. Transformers have shown competitive performance in both time-series anomaly detection and flow-based intrusion detection<sup>47</sup> . Contrastive learning was incorporated to enhance representation robustness by teaching the model to discriminate between similar and dissimilar traffic profiles without relying solely on labeled data<sup>48</sup> . This technique helps tighten intra-class cohesion while maximizing inter-class separation in the embedding space, which is particularly beneficial for imbalanced datasets or lowfrequency attacks. Prior research has shown contrastive loss to be effective in improving minority-class recall and overall generalization in intrusion and fraud detection systems<sup>49</sup> . The integration of these three techniques— graph modeling, Transformers, and contrastive learning—was motivated by their complementary capabilities, each contributing toward accurate, scalable, and interpretable intrusion detection. 

### **Feature extraction using GNNs** 

Although individual network flows are typically modeled as independent observations, many security-relevant behaviors emerge from structured relationships across flows, such as repeated communications between the same IP pairs, scanning across port ranges, or coordinated actions across hosts. We construct a graph where nodes represent unique IP addresses, ports, or services, and edges represent communication events (e.g., flows between a source-destination pair). This results in a dynamic interaction graph where features such as connection frequency, service overlap, and traffic directionality can be embedded. GNNs enable the model to aggregate neighborhood context (e.g., patterns of communication from or to a node) and detect relational anomalies—such as a benign node suddenly initiating high-volume traffic to multiple targets. Such structure is difficult to model with flat or sequence-based approaches, making GNNs well-suited for capturing distributed attack behaviors and interdependent anomalies. 

Network traffic data is inherently relational, as it involves interactions between multiple entities such as source IPs, destination IPs, and ports. These relationships can be effectively modeled using a graph representation. Let _G_ = ( _V, E_ ) denote the graph representation of the network traffic, where: _−V_ = _{v_ 1 _, v_ 2 _, ..., v|V |}_ represents the set of nodes. Each node corresponds to a network entity, such as an IP address or a device. _−E_ = _eij_ represents the set of edges, where _eij ∈ E_ indicates a communication link between nodes _vi_ and _vj_ . The edge _eij_ can be weighed by a metric _wij_ , such as the number of packets transferred or the total data volume exchanged between the nodes. The adjacency matrix _A ∈ R_<sup>_|V |×|V |_</sup> encodes the graph structure, where _Aij_ = _wij_ . Node features _X ∈ R_<sup>_|V |×d_</sup> represent the attributes of each node, such as traffic statistics, protocol types, and port information. A GCN is used to extract meaningful features from _G_ . The GCN aggregates information from a node’s neighbors and updates its representation at each layer. The feature update at layer _l_ is given by: 



where _A_<sup>�</sup> = _A_ + _I_ is the adjacency matrix with self-loops, _D_<sup>�</sup> is the degree matrix of _A, H_<sup>�</sup><sup>_l_</sup> denotes the node features at layer (with _H_<sup>(0)</sup> = _X_ ), _W_<sup>_l_</sup> is the trainable weight matrix, and _σ_ is an activation function such as ReLU. After _L_ layers, the output _H_<sup>(</sup><sup>_L_)</sup> represents the learned node embeddings. 

The GCN learns to capture both the structural information of the graph and the attributes of individual nodes. These embeddings are then used as input to the next stage of the IDS pipeline. The overall pseudo-code is <u>provided in Algo. 1.</u> 

**Scientific Reports** |        (2025) 15:20511 

7 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 



### **Transformer-based autoencoder** 

The features extracted by the GCN are further refined using a Transformer-based Autoencoder. Transformers are particularly effective in capturing long-range dependencies and contextual relationships within the data. The autoencoder consists of an encoder-decoder architecture with self-attention mechanisms. The overview of feature extraction is provided in Algo. 2 



#### _Self-attention mechanism_ 

The self-attention mechanism computes pairwise interactions between all input features, enabling the model to focus on the most relevant parts of the sequence. For an input sequence _{f_ ( _t_ 1) _, f_ ( _t_ 2) _, ..., f_ ( _tn_ ) _}_ , the attention scores are computed as: 



where _Q, K, V_ are the query, key, and value matrices are derived from the input features, and _dk_ is the dimensionality of the keys. 

#### _Loss functions_ 

The autoencoder is trained to minimize a combination of reconstruction and regularization losses: 

#### _Reconstruction loss_ 

Reconstruction loss ensures the encoder-decoder mapping preserves the input: 

**Scientific Reports** |        (2025) 15:20511 

8 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 



where _f_<sup>ˆ</sup> ( _ti_ ) is the reconstructed feature. 

_Regularization loss_ 

Regularization loss penalizes deviations between the original and reconstructed distributions: 



where _KL_ ( _· ∥·_ ) is the Kullback–Leibler divergence, and _α_ is a regularization parameter. 

### **Classification using contrastive learning** 

Contrastive learning is employed to enhance the robustness of the classifier by learning to differentiate between similar and dissimilar pairs of features. The contrastive loss is given by: 



where _yij_ = 1 if _ti_ and _tj_ belong to the same class, and _yij_ = 0 otherwise. The similarity _sim_ ( _f_ ( _ti_ ) _, f_ ( _tj_ )) is typically computed using cosine similarity. The final classification loss combines cross-entropy loss and contrastive loss: 

_Lclass_ = _LCE_ + _β · Lcontras_ (10) 

where _β_ balances the two loss components. The overview is provided in Algo. 3. 



## **Experimental settings** 

The proposed methodology is evaluated on the KDD Cup 99 and NSL-KDD datasets, both of which are widely used benchmarks for intrusion detection systems. This section* details the experimental setup, including preprocessing steps, model parameters, training configurations, and evaluation criteria. 

### **Datasets and preprocessing** 

The KDD Cup 99 dataset contains 41 features, including both continuous and categorical attributes, and is divided into normal and attack classes. The detailed descriptions of all 41 features in the NSL-KDD dataset are provided in Table 3, which shows the comprehensive range of network flow characteristics used for intrusion detection. It is important to note that we do not work directly with packet-level raw traffic (e.g., PCAP files), but rather use the pre-processed flow-level feature sets provided in the official NSL-KDD and CIC-IDS2018 distributions. These datasets 4 contain statistical summaries and extracted features derived from traffic capture sessions, including port activity, byte counts, and temporal metrics. Due to its large size and redundancy, a subset consisting of 10% of the data is used to address the over-representation of Denial-of-Service (DoS) attacks in Tab. 4 

**Scientific Reports** |        (2025) 15:20511 

9 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

|**Metric**|**With outliers**|**IQR-clipped**|
|---|---|---|
|Accuracy|99.97%|99.62%|
|Recall (U2R/R2L)|99.85%|97.52%|
|F1-score (Macro)|99.91%|98.68%|



**Table 3** . Effect of outlier removal on model performance (NSL-KDD, 5-class). 

|**Column name**|**Description**|
|---|---|
|Duration|Length (in seconds) of the connection|
|Protocol_type|Type of protocol used (e.g., TCP, UDP, ICMP)|
|Service|Network service on the destination (e.g., http, fp, smtp)|
|Flag|Status of the connection (e.g., SF for successful, REJ for rejected)|
|Src_bytes|Number of bytes sent from source to destination|
|Dst_bytes|Number of bytes sent from destination to source|
|Land|Boolean indicating whether source and destination IPs/ports are the same|
|Wrong_fragment|Number of “wrong” or fragmented packets|
|Urgent|Number of urgent packets|
|Hot|Number of hot indicators (e.g., accessing system fles, creating shells)|
|Num_failed_logins|Number of failed login attempts|
|Logged_in|Boolean indicating if login was successful|
|Num_compromised|Number of compromised conditions|
|Root_shell|Boolean indicating if root shell was obtained|
|Su_attempted|Boolean indicating if ‘su ‘ command was attempted|
|Num_root|Number of root accesses|
|Num_fle_creations|Number of fle creation operations|
|Num_shells|Number of shell prompts invoked|
|Num_access_fles|Number of access control fle operations|
|Num_outbound_cmds|Number of outbound commands in an FTP session|
|Is_host_login|Boolean indicating if the login belongs to the host|
|Is_guest_login|Boolean indicating if the login belongs to a guest account|
|Count|Number of connections to the same host in a 2-s window|
|Srv_count|Number of connections to the same service in a 2-s window|
|Serror_rate|Percentage of connections with SYN errors|
|Srv_serror_rate|Percentage of connections to the same service with SYN errors|
|Rerror_rate|Percentage of connections with REJ errors|
|Srv_rerror_rate|Percentage of connections to the same service with REJ errors|
|Same_srv_rate|Percentage of connections to the same service|
|Dif_srv_rate<br>|Percentage of connections to diferent services<br>|
|Srv_dif_host_rate|Percentage of connections to diferent hosts|
|Dst_host_count|Number of connections to the same destination host|
|Dst_host_srv_count|Number of connections to the same service on the destination host|
|Dst_host_same_srv_rate|Percentage of destination host connections to the same service|
|Dst_host_dif_srv_rate|Percentage of destination host connections to diferent services|
|Dst_host_same_src_port_rate|Percentage of destination host connections from the same source port|
|Dst_host_srv_dif_host_rate|Percentage of destination host connections to diferent hosts|
|Dst_host_serror_rate|<br>Percentage of destination host connections with SYN errors|
|Dst_host_srv_serror_rate|Percentage of destination host connections to the same service with SYN errors|
|Dst_host_rerror_rate|Percentage of destination host connections with REJ errors|
|Dst_host_srv_rerror_rate|Percentage of destination host connections to the same service with REJ errors|



**Table 4** . Dataset columns and their descriptions. 

Preprocessing involves scaling all continuous features to a range of [0, 1] using min-max normalization, ensuring numerical stability during training. Categorical features, such as protocol type, service, and flag, are encoded using one-hot encoding, converting them into numerical formats suitable for input to machine learning models. These preprocessing steps standardize the input data while ensuring the preservation of key characteristics necessary for effective learning. Outliers were retained Table 3 during preprocessing to avoid 

**Scientific Reports** |        (2025) 15:20511 

10 

| https://doi.org/10.1038/s41598-025-07956-w 



<!-- Start of picture text -->
Raw: dst_host_srv_count Normalized: dst_host_srv_count<br>100 100<br>[ 1<br>> 80 7 > 80<br>UV U<br>cc<br>D60 f 1 G 60<br>Do<br>2<br>aot-[ ‘e 2 40<br>20}, = 20<br>°° 50 100I al. 150 °'0.0 0.2 0.4 0.6 0.8 1.0<br>Value Value<br>Raw: srv_serror_rate Normalized: srv_serror_rate<br>300 300<br>>><br>U<br>Cc cSUV<br>© 200 © 200<br>lox lox<br>2 v<br>LL vs<br>100 100<br>°00 01 02 03 04 05 06 0.7 °'0.0 0.2 0.4 0.6 0.8 1.0<br>Value Value<br>Raw: num_root Normalized: num_root<br>400 400<br>5, 300 5, 300<br>VU VU<br>Cc c<br>oO2.200 ov2.200<br>2 2<br>LL Le<br>100 100<br>0 0<br>0 1 2 3 4 5 0.0 0.2 0.4 0.6 0.8 1.0<br>Value Value<br><!-- End of picture text -->

nature portfolio 

www.nature.com/scientificreports/ 

across different environments. Results were not combined but reported individually for binary and multi-class classification tasks. NSL-KDD was primarily used for 5-class experiments to benchmark against prior literature, while CIC-IDS2018 was used to validate performance under more realistic traffic conditions. Each dataset was split using a 70%−30% train-test split with stratified sampling to preserve class distributions. No data leakage occurred between splits, and all preprocessing (normalization, encoding) was applied after splitting. We acknowledge in this research study both NSL-KDD and CIC-IDS2018 have limitations. NSL-KDD lacks real packet variability and modern attack types, while CIC-IDS2018 includes synthetic traffic generated in controlled environments. Despite these shortcomings, they remain widely adopted benchmarks that allow reproducibility and comparison with existing methods. In future work, we plan to include real-time datasets such as CICIoT2023 and TON-IoT and explore online learning techniques for adaptive evaluation. 

### **Model architecture and parameters** 

The proposed system comprises three components: a GNN for feature extraction, a Transformer-based autoencoder for refinement, and a contrastive learning module for classification. Each component is configured to balance computational efficiency and performance. 

### **Overfitting mitigation strategies** 

To ensure generalization and avoid overfitting, several regularization and training control methods were applied across all major model components. Dropout layers were used with a rate of 0.3 after GNN and Transformer modules to suppress neuron co-adaptation. Additionally, L2 weight regularization (with _λ_ = 0 _._ 001) was applied to dense layers to discourage the model from forming excessively sharp decision boundaries. Early stopping was implemented using validation loss monitoring, with a patience threshold of 10 epochs. If no improvement was observed, training was terminated to prevent degradation. To further support convergence, a learning rate decay strategy reduced the optimizer’s step size by a factor of 0.1 upon five epochs of stagnation. Batch normalization was used after Transformer attention blocks and fully connected layers to improve gradient stability and reduce covariate shifts. Moreover, a 5-fold cross-validation procedure was performed during training to verify that the model achieved consistent results across different partitions of the training data. These combined techniques allowed the model to avoid overfitting to minority or frequent classes and improved generalization across the evaluation sets. 

#### _Graph neural network_ 

The GNN is designed to extract high-level features from the graph representation of network traffic data. The graph is constructed by treating each network entity (e.g., IP addresses or devices) as a node and creating edges based on communication metrics. The adjacency matrix is computed using cosine similarity between feature vectors, and self-loops are added to incorporate node-specific information. The GNN consists of three graph convolutional layers. Each layer has 64 neurons, with ReLU activation applied after each layer to introduce nonlinearity. Dropout with a rate of 0.3 is applied to prevent overfitting, and layer normalization is used to stabilize training. The output embeddings from the GNN serve as input to the Transformer-based autoencoder. The model is trained using the Adam optimizer with a learning rate of 0.001, a batch size of 128, and for 50 epochs. 

### **Generalizability and external validation** 

To assess the generalizability of the proposed model to unseen data, two types of evaluation were conducted. First, a 5-fold cross-validation was performed on the NSL-KDD dataset. The average variation in accuracy across folds remained below 0.2%, indicating that the model’s performance was stable across different partitions. Precision and recall metrics for minority classes such as U2R and R2L also remained consistent, reinforcing that the model did not overfit to a specific data subset. Second, we tested the model on the CIC-IDS-2018 dataset, which includes different attack types, and a more realistic traffic distribution compared to NSL-KDD. Without retraining, the model achieved 99.96% accuracy in the binary classification setting and 99.91% in the multi-class setting, as shown in Table 5. This external validation demonstrates the model’s capacity to maintain high detection performance when applied to data from a different collection environment. The robustness in generalizing both class-disjoint and distribution-shifted traffic sources highlights the framework’s suitability for real-world deployment. 

#### _Transformer-based autoencoder_ 

The Transformer-based autoencoder refines the embeddings extracted by the GNN. The encoder comprises two self-attention layers, each with four attention heads. The attention mechanism is followed by a feed-forward layer with 128 neurons, activated by the Gaussian Error Linear Unit (GELU). Dropout with a rate of 0.2 is applied 

|**Metric**|**NSL-KDD (5-class)**|**CIC-IDS (Bi)**|**CIC-IDS (Multi)**|
|---|---|---|---|
|Accuracy|99.97%|99.96%|99.95%|
|Precision|99.94%|99.93%|99.92%|
|Recall|99.92%|99.91%|99.90%|
|F1-score|99.93%|99.92%|99.91%|
|**False Positive Rate**|**0.05%**|**0.06%**|**0.07%**|



**Table 5** . Overall classification metrics. 

**Scientific Reports** |        (2025) 15:20511 

12 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

to both the attention mechanism and the feed-forward layers to improve generalization. The decoder mirrors the structure of the encoder and reconstructs the input embeddings to ensure that important information is preserved. The autoencoder is trained using the AdamW optimizer with a learning rate of 0.0001, a batch size of 64, and for 100 epochs. Regularization is applied during training to make the system robust to noisy or incomplete data, with hyperparameters fine-tuned based on validation performance. 

#### _Contrastive learning module_ 

The refined embeddings from the autoencoder are fed into a contrastive learning module to further enhance the model’s robustness. Positive and negative pairs of embeddings are generated based on their class labels, with positive pairs belonging to the same class and negative pairs to different classes. Cosine similarity is used to measure the relationship between embeddings, and a loss function penalizes misclassification of both positive and negative pairs. The contrastive learning module is followed by a classification layer comprising a two-layer fully connected neural network. The first layer has 128 neurons with ReLU activation, and the output layer uses a softmax activation function to generate multi-class predictions. This module is trained using the RMSprop optimizer with a learning rate of 0.0005, a batch size of 256, and for 50 epochs. 

### **Training configurations** 

The model training is performed on a high-performance computing system equipped with an Intel Core i912900K processor, NVIDIA RTX 3090 GPU with 24GB VRAM, and 64GB of RAM. The training process involves monitoring the loss and accuracy on the validation set to ensure convergence. Early stopping is employed with a patience of 10 epochs to prevent overfitting, terminating training if the validation performance does not improve. The learning rates for each module are adjusted fast pace using a learning rate scheduler, which reduces the rate by a factor of 0.1 if the validation loss plateaus for five consecutive epochs. Gradient clipping is also applied, with a maximum norm of 5, to prevent exploding gradients during backpropagation. 

### **Evaluation metrics** 

The performance of the proposed system is assessed using a combination of metrics to provide a comprehensive evaluation. Accuracy measures the overall correctness of the system, while precision quantifies the proportion of correctly identified positives out of all predicted positives. Recall, also known as sensitivity, measures the proportion of actual positives correctly identified by the model. The F1-score, which is the harmonic mean of precision and recall, is used to balance these two metrics in cases of class imbalance. Additionally, the false alarm rate (FAR) is calculated to evaluate the system’s ability to distinguish normal traffic from attack traffic. These metrics are computed for both the training and testing datasets to analyze the generalization capability of the model. 

## **Results and evaluation** 

This section presents a detailed analysis of the experimental results obtained using the proposed framework. The performance was measured on multiple benchmark datasets, including NSL-KDD and CIC-IDS-2018, which provide a comprehensive set of normal and attack traffic instances. The evaluation focuses not only on standard metrics such as accuracy, precision, recall, and F1-score, but also considers other important aspects like model efficiency, real-time feasibility, class-wise behavior, and robustness against data imbalance. These results are accompanied by visualizations and tables to ensure a transparent understanding of the framework’s effectiveness. 

The overall accuracy of the model was consistently high across all datasets, reaching an average of 99.97%. This indicates that the model is highly reliable in distinguishing normal traffic from various types of network intrusions. Precision averaged 99.94%, demonstrating that the model rarely flagged benign traffic as malicious, thereby reducing false positives. Similarly, recall averaged 99.92%, showing that the model successfully identified nearly all actual attack instances. This balance between precision and recall is further reflected in the F1-score, which also maintained an average of 99.93%. These metrics highlight the system’s ability to not only detect attacks with high certainty but also to avoid unnecessary alerts that could burden security analysts. 

In addition to standard classification metrics, the false positive rate (FPR) was included to measure the system’s precision under operational settings. Across datasets, the FPR remained below 0.07%, confirming that the model produces very few incorrect alerts for normal traffic. This supports the framework’s real-world applicability, where a high FPR can lead to alert fatigue and resource drain on security teams. The detailed breakdown of performance by class, as shown in Table 6, reveals that even the most challenging attack types— such as User-to-Root (U2R) and Remote-to-Local (R2L)—were detected with precision and recall exceeding 99.85%. This outcome shows the framework’s ability to handle minority classes effectively, a feat that is often difficult due to the inherent imbalance in network traffic datasets. The weighted loss functions and data 

|**Class**|**Precision**|**Recall**|**F1-score**|
|---|---|---|---|
|Normal|99.95%|99.96%|99.95%|
|DoS|99.93%|99.90%|99.91%|
|Probe|99.92%|99.94%|99.93%|
|U2R|99.88%|99.85%|99.87%|
|R2L|99.89%|99.87%|99.88%|



**Table 6** . Per-class performance on NSL-KDD dataset (5-class). 

**Scientific Reports** |        (2025) 15:20511 

13 

| https://doi.org/10.1038/s41598-025-07956-w 



<!-- Start of picture text -->
100 GE Precision<br>Mm Recall<br>Mmm =F1-Score<br>80<br><= 60<br>YY<br>Ss<br>Ww<br>=<br>40<br>20<br>0<br>NSL-KDD (5-class) CIC-IDS (Binary). cIC-IDS (Multi-class)<br>Datasets<br><!-- End of picture text -->

nature portfolio 



<!-- Start of picture text -->
12000<br>oS<br>i 12 10000<br>ie]<br>8000<br>Oo<br>2<br>&<br>ou<br>Ee - 6000<br>4 - 4000<br>a - 33<br>ie]<br>- 2000<br>'<br>Class 0 Class 1<br>Predicted label<br><!-- End of picture text -->



<!-- Start of picture text -->
&<br>F 17354 47 50 45 42 49 43 16000<br>g- 8 2401 6 9 10 10 7 sain<br>8 12000<br>e 2 3 1262 2 4 3 5<br>5<br>S 10000<br>cote<br>a z - 2 1 2 1310 2 6 4<br>eg - 8000<br>g- 1 2 4 4 1233 3 3 Lae<br>5<br>®- 2 3 2 1 1 617 3 io<br>=<br>- 2000<br>Ww<br>8- 1 2 1 2 0 1 620<br>a<br>i) 1 ' 1 ' 1 1 sont 0<br>Benign Dos Brute Force Web Attack Bot Infiltration DDos<br>Predicted label<br><!-- End of picture text -->

nature portfolio 



<!-- Start of picture text -->
o 222 1 2 0 0 200<br>175<br>a- 1 194 1 ) )<br>150<br>3 125<br>2<br>= N - 1 ) 189 1 1<br>=| - 100<br>- 75<br>m- 1 1 1 184 1<br>-50<br>+ - 1 1 2 1 194 -25<br>' ' ' ' = 0<br>fe) 1 2 3 4<br>Predicted label<br><!-- End of picture text -->

nature portfolio 

www.nature.com/scientificreports/ 

|**Metric**|**Value**|
|---|---|
|Model parameters|12.5 million|
|Inference memory usage|1.2 GB|
|Training time (1 RTX 3090)|24 h|
|Inference time Per Flow|2.3 ms|



**Table 7** . Memory and computational efficiency. 

added components, the model’s runtime remained suitable for near real-time intrusion detection tasks. In terms of complexity, the GNN introduces _O_ ( _V_<sup>2</sup> ) operations during message passing, the Transformer introduces _O_ ( _n_<sup>2</sup> ) self-attention cost, and contrastive loss requires pairwise similarity computations. These steps are parallelized during batch processing using modern deep learning libraries. Moreover, each component was lightweight in design: GCN layers used sparse adjacency matrices, the Transformer used 2 layers with 4 attention heads, and contrastive learning was applied only at the embedding stage. This modular architecture ensured that computational costs remained bounded while enabling a multi-perspective learning approach that boosted performance across all major metrics. The marginal increase in computational cost is justified by the observed gains in accuracy, interpretability, and robustness—especially in detecting minority-class and zero-day attacks. Therefore, the framework achieves a practical balance between performance and overhead, making it suitable for operational cloud or edge-based deployments. 

### **Justification of evaluation metrics** 

The evaluation metrics—accuracy, precision, recall, and F1-score—were chosen to capture both overall performance and the model’s behavior under class imbalance. While accuracy offers a broad view, it can be misleading when benign traffic dominates. Precision helps reduce false positives, minimizing alert fatigue, whereas recall is more critical in intrusion detection, where missing actual attacks poses greater risk than raising false alarms. The F1-score balances these concerns and is particularly useful for minority classes like U2R and R2L. By analyzing all four metrics, the evaluation provides a realistic and security-focused assessment of detection capability. 

## **Discussion and comparison** 

Compared to the studies described in Table 1, our proposed approach achieves consistently higher accuracy and precision, even under challenging conditions. For instance, while the Dugat-LSTM approach by Devendiran et al. achieves impressive results on TON-IOT and NSL-KDD, it suffers from high computational complexity. In contrast, our method maintains comparable accuracy levels without the need for excessive computational resources. Similarly, although the method of Talukder et al. to handle imbalanced data achieves high precision, it is highly dependent on oversampling, increasing processing time. Our model instead employs advanced loss functions and feature extraction techniques that effectively handle imbalances without inflating resource usage. 

Furthermore, unlike the studies by Wang et al. and Manocchio et al., which focus on smaller or highly controlled datasets, our framework demonstrates superior generalization capabilities across multiple public datasets, including NSL-KDD and CIC-IDS-2018. This robustness shows our framework’s ability to handle various types of traffic patterns and attacks, a important requirement for real-world deployment. 

A key differentiator lies in our method’s low false-positive rate. Although studies such as Tang et al. and Kim et al. have reported challenges with false positives, our approach consistently reduces these errors, resulting in a more reliable intrusion detection system. Additionally, our results confirm that even under multiclass classification scenarios, often a weak point for many models, our framework achieves high precision and recall across all categories. 

By consistently outperforming other approaches in terms of accuracy, computational efficiency, and robustness against class imbalance, our framework establishes a new benchmark for network intrusion detection. The inclusion of Figure 7 visually demonstrates these improvements, clearly showing how our model not only achieves state-of-the-art performance but also sets a higher standard for future research in this domain. 

### **Uniqueness of the proposed framework compared to related methods** 

The uniqueness of the proposed framework lies in its integrated use of graph-based embeddings, Transformer autoencoding, and contrastive learning within a unified pipeline. Traditional IDS models often rely on either feature-based deep neural networks or sequence-based LSTMs, which are limited in capturing relational dependencies and long-range interactions. In contrast, our use of allows the model to encode communication patterns across hosts and services, which is particularly valuable for identifying lateral movement and multi-hop attacks. 

While some recent works have used Transformers for packet sequence modeling, they typically rely on flat, tokenized input and do not benefit from structured graph inputs. Our method uses a Transformer-based autoencoder to refine graph-derived embeddings, preserving both structural and contextual relationships. Additionally, most existing IDS models optimize only for classification loss. By integrating contrastive learning, our framework encourages better class separation in the latent space, leading to improved recall on underrepresented attack types. Compared to methods such as DBNs, CNNs, or sparse autoencoders that treat input independently, our architecture maintains end-to-end relational reasoning, temporal abstraction, and 

**Scientific Reports** |        (2025) 15:20511 

17 

| https://doi.org/10.1038/s41598-025-07956-w 



<!-- Start of picture text -->
Our Results<br>Varzaneh et al.<br>Talukder et al.<br>Devendiran et al.<br>Manocchio et al.<br>Wang et al.<br>wet al.<br>: Loukas et al.<br>Shone et al.<br>Kim et al.<br>Wenjuan et al.<br>Niyaz et al.<br>Aygun et al.<br>Salama et al.<br>Tang et al.<br>i) 20 40 60 80 100<br>Accuracy (%)<br><!-- End of picture text -->

nature portfolio 

www.nature.com/scientificreports/ 

current model operates primarily at the flow level and relies on static labeled datasets, it may not capture the full temporal context or dynamic threat chains needed to identify stealthy multi-stage intrusions. Additionally, adversarial attacks and adaptive evasion strategies were not within the current evaluation scope. Future research will explore continual learning mechanisms, temporal graph modeling, and memory-augmented detection systems to address such evolving threats. Real-time adaptation, combined with formal security validation and deployment on distributed edge devices, also represents a promising direction to enhance operational utility. This research establishes a high-performance foundation while outlining the next steps toward more resilient, context-aware intrusion detection systems. 

## **Data availability** 

The datasets generated and/or analyzed during the current study are available in the following repositories:— NSL-KDD dataset:  h t t p s : / / w w w . k a g g l e . c o m / d a t a s e t s / h a s s a n 0 6 / n s l k d d — C I C - I D S - 2 0 1 8 dataset:  h t t p s : / / w w w . u n b . c a / c i c / d a t a s e t s / i d s - 2 0 1 8 . h t m l . 

Received: 9 February 2025; Accepted: 18 June 2025 



## **References** 

1. Obi, O. C. et al. Review of evolving cloud computing paradigms: Security, efficiency, and innovations. _Comput. Sci. & IT Res. J._ **5** , 270–292 (2024). 

2. Sharif, F. The role of ensemble learning in strengthening intrusion detection systems: A machine learning perspective. _Int. J. Comput. Eng. Technol._ (2024). 

3. Sharma, H. The evolution of cybersecurity challenges and mitigation strategies in cloud computing systems. _Int. J. Comput. Eng. Technol._ **15** , 118–127 (2024). 

4. Kandhro, I. A. et al. Detection of real-time malicious intrusions and attacks in iot empowered cybersecurity infrastructures. _IEEE Access_ **11** , 9136–9148 (2023). 

5. Chukwunweike, J. N., Adewale, A. & Osamuyi, O. Advanced modelling and recurrent analysis in network security: Scrutiny of data and fault resolution. _World J. Adv. Res. Rev._ **23** , 2373–2390 (2024). 

6. Sengupta, S. et al. A review of deep learning with special emphasis on architectures, applications and recent trends. _Knowl. Based Syst._ **194** , 105596 (2020). 

7. Zhang, C., Wang, N., Hou, Y. T. & Lou, W. Machine learning-based intrusion detection systems: Capabilities, methodolo- gies, and open research challenges. _Authorea Prepr._ 

8. Attou, H. et al. Towards an intelligent intrusion detection system to detect malicious activities in cloud computing. _Appl. Sci._ **13** , 9588 (2023). 

9. Tabrizchi, H. & Kuchaki Rafsanjani, M. A survey on security challenges in cloud computing: issues, threats, and solutions. _J. supercomput._ **76** , 9493–9532 (2020). 

10. Shamshirband, S. et al. Computational intelligence intrusion detection techniques in mobile cloud computing environments: Review, taxonomy, and open research issues. _J. Inf. Secur. Appl._ **55** , 102582 (2020). 

11. Ennaji, S., De Gaspari, F., Hitaj, D., Kbidi, A. & Mancini, L. V. Adversarial challenges in network intrusion detection systems: Research insights and future prospects. arXiv preprint arXiv:2409.18736 (2024). 

12. Ahmed, U. et al. Signature-based intrusion detection using machine learning and deep learning approaches empowered with fuzzy clustering. _Sci. Reports_ **15** , 1726 (2025). 

13. Buchta, R., Gkoktsis, G., Heine, F. & Kleiner, C. Advanced persistent threat attack detection systems: A review of approaches, challenges, and trends. _Digit. Threat. Res. Pract._ **5** , 1–37 (2024). 

14. Kocher, G. & Kumar, G. Machine learning and deep learning methods for intrusion detection systems: recent developments and challenges. _Soft Comput._ **25** , 9731–9763 (2021). 

15. Qaddos, A. et al. A novel intrusion detection framework for optimizing iot security. _Sci. Rep._ **14** , 21789 (2024). 

16. Tang, T. A., Mhamdi, L., McLernon, D., Zaidi, S. A. R. & Ghogho, M. Deep learning approach for network intrusion de- tection in software defined networking. In _2016 international conference on wireless networks and mobile communications (WINCOM)_ , 258–263 (IEEE, 2016). 

17. Salama, M. A., Eid, H. F., Ramadan, R. A., Darwish, A. & Hassanien, A. E. Hybrid intelligent intrusion detection scheme. In _Soft computing in industrial applications_ , 293–303 (Springer, 2011). 

18. Aygun, R. C. & Yavuz, A. G. Network anomaly detection with stochastically improved autoencoder based models. In _2017 IEEE 4th international conference on cyber security and cloud computing (CSCloud)_ , 193–198 (IEEE, 2017). 

19. Javaid, A., Niyaz, Q., Sun, W. & Alam, M. A deep learning approach for network intrusion detection system. In _Proceedings of the 9th EAI International Conference on Bio-inspired Information and Communications Technologies (formerly BIONETICS)_ , 21–26 (2016). 

20. Niyaz, Q., Sun, W. & Javaid, A. Y. A deep learning based ddos detection system in software-defined networking (sdn). arXiv preprint arXiv:1611.07400 (2016). 

21. Wang, W., Du, X., Shan, D., Qin, R. & Wang, N. Cloud intrusion detection method based on stacked contractive auto-encoder and support vector machine. _IEEE Trans. Cloud Comput._ **10** , 1634–1646 (2020). 

22. Kim, J., Shin, N., Jo, S. Y. & Kim, S. H. Method of intrusion detection using deep neural network. In _2017 IEEE international conference on big data and smart computing (BigComp)_ , 313–316 (IEEE, 2017). 

23. Papamartzivanos, D., Mármol, F. G. & Kambourakis, G. Introducing deep learning self-adaptive misuse network intrusion detection systems. _IEEE access_ **7** , 13546–13560 (2019). 

24. Shone, N., Ngoc, T. N., Phai, V. D. & Shi, Q. A deep learning approach to network intrusion detection. _IEEE Trans. Emerg. Top. Comput. Intel._ **2** , 41–50 (2018). 

25. Loukas, G. et al. Cloud-based cyber-physical intrusion detection for vehicles using deep learning. _Ieee Access_ **6** , 3491–3508 (2017). 

26. Yu, Y., Long, J. & Cai, Z. Network intrusion detection through stacking dilated convolutional autoencoders. _Secur. Commun. Networks_ **2017** , 4184196 (2017). 

27. Abdulganiyu, O. H., Tchakoucht, T. A. & Saheed, Y. K. Towards an efficient model for network intrusion detection system (ids): Systematic literature review. _Wirel. Netw._ **30** , 453–482 (2024). 

28. Wang, X. et al. Advanced network intrusion detection with tabtransformer. _J. Theory Pract. Eng. Sci._ **4** , 191–198 (2024). 29. Manocchio, L. D. et al. Flowtransformer: A transformer framework for flow-based network intrusion detection systems. _Expert. Syst. with Appl._ **241** , 122564 (2024). 

30. Devendiran, R. & Turukmane, A. V. Dugat-lstm: Deep learning based network intrusion detection system using chaotic optimization strategy. _Expert. Syst. with Appl._ **245** , 123027 (2024). 

**Scientific Reports** |        (2025) 15:20511 

19 

| https://doi.org/10.1038/s41598-025-07956-w 

www.nature.com/scientificreports/ 

31. Talukder, M. A. et al. Machine learning-based network intrusion detection for big and imbalanced data using oversampling, stacking feature embedding and feature extraction. _J. big data_ **11** , 33 (2024). 

32. Varzaneh, Z. A. & Hosseini, S. An improved equilibrium optimization algorithm for feature selection problem in network intrusion detection. _Sci. Rep._ **14** , 18696 (2024). 

33. Shitharth, S., Mohammed, G. B., Ramasamy, J. & Srivel, R. Intelligent intrusion detection algorithm based on multi-attack for edgeassisted internet of things. In _Security and risk analysis for intelligent edge computing_ , 119–135 (Springer, 2023). 

34. Selvarajan, S., Shaik, M., Ameerjohn, S. & Kannan, S. Mining of intrusion attack in scada network using clustering and genetically seeded flora-based optimal classification algorithm. _IET Inf. Secur._ **14** , 1–11 (2020). 

35. Prashanth, S., Shitharth, S., Praveen Kumar, B., Subedha, V. & Sangeetha, K. Optimal feature selection based on evolutionary algorithm for intrusion detection. _SN Comput. Sci._ **3** , 439 (2022). 

36. Rabie, O. B. J. et al. A novel iot intrusion detection framework using decisive red fox optimization and descriptive back propagated radial basis function models. _Sci. Rep._ **14** , 386 (2024). 

37. Shitharth, S., Kshirsagar, P. R., Balachandran, P. K., Alyoubi, K. H. & Khadidos, A. O. An innovative perceptual pigeon galvanized optimization (ppgo) based likelihood naïve bayes (lnb) classification approach for network intrusion detection system. _IEEE Access_ **10** , 46424–46441 (2022). 

38. Tellache, A., Mokhtari, A., Korba, A. A. & Ghamri-Doudane, Y. Multi-agent reinforcement learning-based network intrusion detection system. In _NOMS 2024–2024 IEEE Network Operations and Management Symposium_ , 1–9 (IEEE, 2024). 

39. Korba, A. A., Boualouache, A. & Ghamri-Doudane, Y. Zero-x: A blockchain-enabled open-set federated learning framework for zero-day attack detection in iov. _IEEE Trans. Veh. Technol._ **73** , 12399–12414 (2024). 

40. Diaf, A., Korba, A. A., Karabadji, N. E. & Ghamri-Doudane, Y. Bartpredict: Empowering iot security with llm-driven cyber threat prediction. In _GLOBECOM 2024–2024 IEEE Global Communications Conference_ , 1239–1244 (IEEE, 2024). 

41. Hyatt, J.-P. K., Bienenstock, E. J. & Tilan, J. U. A student guide to proofreading and writing in science. _Adv. Physiol. Educ._ (2017). 42. Diaf, A., Ghamri-Doudane, Y. _et al._ Ai-driven fast and early detection of iot botnet threats: A comprehensive network traffic analysis approach. arXiv preprint arXiv:2407.15688 (2024). 

43. Karabadji, N. E., Ghamri-Doudane, Y. _et al._ Zero-day botnet attack detection in iov: A modular approach using isolation forests and particle swarm optimization. arXiv preprint arXiv:2504.18814 (2025). 

44. Korba, A. A., Diaf, A. & Ghamri-Doudane, Y. Ai-driven fast and early detection of iot botnet threats: A comprehensive network traffic analysis approach. In _2024 International Wireless Communications and Mobile Computing (IWCMC)_ , 1779–1784 (IEEE, 2024). 

45. Manda, V. K., Christy, V. & Hlali, A. Current trends, opportunities, and futures research directions in geospatial technologies for smart cities. _Recent Trends Geospatial AI_ 239–270 (2025). 

46. Zhou, G. & Barbieri, S. Generating clinically realistic ehr data via a hierarchy-and semantics-guided transformer. arXiv preprint arXiv:2502.20719 (2025). 

47. Kheddar, H. Transformers and large language models for efficient intrusion detection systems: A comprehensive survey. arXiv preprint arXiv:2408.07583 (2024). 

48. Yue, Y., Chen, X., Han, Z., Zeng, X. & Zhu, Y. Contrastive learning enhanced intrusion detection. _IEEE Trans. Netw. Serv. Manag._ **19** , 4232–4247 (2022). 

49. Abdulganiyu, O. H., Tchakoucht, T. A., Saheed, Y. K. & Ahmed, H. A. Xidintfl-vae: Xgboost-based intrusion detection of imbalance network traffic via class-wise focal loss variational autoencoder. _The J. Supercomput._ **81** , 1–38 (2025). 

## **Author contributions** 

VG conceptualized the research, designed the intrusion detection framework, conducted primary experiments and analysis, and wrote the manuscript. JHM contributed to methodology refinement, conducted additional experiments, and assisted with manuscript revision. Both authors reviewed and approved the final manuscript. 

## **Declarations** 

## **Competing interests** 

The authors declare no competing interests. 

## **Additional information** 

**Correspondence** and requests for materials should be addressed to V.G. 

**Reprints and permissions information** is available at www.nature.com/reprints. 

**Publisher’s note** Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations. 

**Open Access** This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/. 

- © The Author(s) 2025 

**Scientific Reports** |        (2025) 15:20511 

20 

| https://doi.org/10.1038/s41598-025-07956-w 

