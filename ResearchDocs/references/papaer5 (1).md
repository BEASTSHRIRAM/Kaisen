Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ https://doi.org/10.1186/s13677-024-00699-5 

Journal of Cloud Computing: Advances, Systems and Applications 

## **Open Access** 

## **RESEARCH** 



# I-MPaFS: enhancing EDoS attack detection in cloud computing through a data-driven approach 

Md. Sharafat Hossain<sup>1</sup> , Md. Alamgir Hossain<sup>1,2*</sup> and Md. Saiful Islam<sup>1</sup> 

### **Abstract** 

Cloud computing offers cost-effective IT solutions but is susceptible to security threats, particularly the Economic Denial of Sustainability (EDoS) attack. EDoS exploits cloud elasticity and the pay-per-use billing model, forcing users to incur unnecessary costs. This research introduces the Integrated Model Prediction and Feature Selection (I-MPaFS) framework to address EDoS attacks. I-MPaFS framework enhances an existing dataset to improve performance, using the generated data to build a Random Forest model for EDoS detection. Our investigation employs the UNSW-NB15, CSE-CIC-IDS18 and NSL-KDD datasets, demonstrating the proposed method’s superiority over existing techniques. The model achieved recall scores of 99.45% on the UNSW-NB15 dataset, 98.19% on the CSE-CIC-IDS18 dataset, and 99.82% on the NSL-KDD dataset, highlighting its reliability and efficacy in safeguarding cloud users from financial exploitation. This study contributes to the field by evaluating current EDoS detection methods, introducing the I-MPaFS framework, validating its performance with benchmark datasets, and comparing its effectiveness against state-of-the-art techniques. The findings affirm the significant potential of I-MPaFS in enhancing cloud security and protecting users from EDoS attacks. 

**Keywords** Economic denial of sustainability (EDoS), Machine learning in cloud security, Financial impact of cyberattacks, EDoS detection framework, Cloud security, Cloud service economic safety 

### **Introduction** 

Cloud computing is a distributed computing model with the aim of providing computing services over the Internet as a utility like public users obtain services from traditional public utility services such as water, electricity, gas, and telephone. The advent of cloud computing has fundamentally transformed the abstraction and utilization of complex computing architecture, allowing it to be accessed on remote infrastructure provided by third 

*Correspondence: Md. Alamgir Hossain alamgir.cse14.just@gmail.com 1 Institute of Information and Communication Technology (IICT), Bangladesh University of  Engineering and Technology (BUET), Dhaka, Bangladesh 

2 Department of Computer Science and Engineering, State University of Bangladesh, South Purbachal, Kanchan, Dhaka-1461, Bangladesh 

parties. It has unique properties such as self-service on demand, widespread network access, and rapid scalability, resource pooling, and measured service [1, 2]. To effectively cater to various customer needs, cloud computing primarily offers three main types of services. These services are Software as a Service (SaaS), Platform as a Service (PaaS), and Infrastructure as a Service (IaaS). 

1. SaaS: This service offers software applications on a subscription basis via the Internet. It is not necessary for users to install or manage the software because they can access these applications through their web browsers. 

2. PaaS: This service provides online access to hardware and software tools that are frequently needed for application development. It gives developers a setting in which they may create, test, and release applica- 

> © The Author(s) 2024. **Open Access** This article is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License, which permits any non-commercial use, sharing, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if you modified the licensed material. You do not have permission under this licence to share adapted material derived from this article or parts of it. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/4.0/. 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 2 of 21 

   - tions without having to worry about maintaining the supporting infrastructure. 

3. IaaS: Through the internet, this service offers virtualized computer resources. Renting virtual computers and storage allows users to manage data and run programs without worrying about the actual underlying hardware. 

In the world of information technology, cloud computing is revolutionary in the way services are managed and provided. SaaS improves operational efficiency and productivity by streamlining application access and eliminating the need for extensive setups and continuous maintenance. PaaS fosters innovation and shortens time-to-market by offering a stable environment for developing, testing, and deploying software. This speeds up application development. Without having to make an investment in physical hardware, organizations may effectively manage workloads and save costs by utilizing IaaS, which provides scalable and flexible computing resources. When combined, these cloud services improve the IT landscape’s scalability, agility, and affordability. In addition, all cloud computing services provide a costeffective solution with minimal initial expenses, rapid deployment, customizable features as well as adaptability. These innovative environments bring additional benefits, including scalability, automatic updates, and enhanced collaboration capabilities. 

These enticing features make cloud services attractive to a diverse range of companies [3–5]. In particular, the low upfront costs associated with cloud services appeal to businesses, especially small and medium enterprises, as an alternative to constructing and managing their own IT infrastructure [6]. As reported in [7], cloud computing can result in cost savings of up to 40 times compared to operating in-house IT infrastructure for small and medium-sized businesses. During the COVID-19 pandemic in 2020 significantly accelerated global digital transformation, leading to a substantial increase in reliance on cloud computing applications and other related technologies [8, 9]. 

However, security concerns related to the cloud computing environment serve as a demotivating factor for companies considering a shift from traditional infrastructure to cloud solutions. The predominant challenge for the cloud computing model is identified as security concern, according to a survey conducted by the International Data Corporation [10]. Approximately 87% of IT executives identified cloud security as the primary obstacle to the adoption of cloud computing [11]. In a report (2021) by Bader Alouffi et al. [12], it is found that numerous service owners continue to exhibit reluctance in fully embracing cloud computing, pointing to the 

underdeveloped state of pertinent security technologies as a significant inhibiting factor. 

Some security issues in cloud computing overlap with conventional internet and network security, while others are specific to the cloud environment. An example of a cloud-specific attack is the EDoS attack. Chris Hoff [13] first introduced the concept of a unique denial-of-service threat in the cloud computing environment, terming it as EDoS attack. An EDoS is a type of cyberattack that targets the financial resources of an organization by exploiting the elasticity of cloud computing environments. In this attack, the assailant floods the system with a substantial volume of illegitimate or false traffic, aiming to prompt the cloud VM manager to allocate unnecessary additional resources in response to the fabricated data. Consequently, this results in additional costs for the cloud user due to the pay-as-you-go billing mechanism. An EDoS attack exploits cloud elasticity and payper-use models by generating excessive requests, causing the cloud system to allocate additional resources and 1. significantly increase operational costs shown in Fig. An example scenario of EDoS attack can be that in case of SaaS, a cloud-based application may automatically scale up its resources to manage an increasing load if an attacker sends several false requests to it on a regular basis. This scalability is based on the pay-per-use model of the cloud, which means that the user’s bill increases with the amount of resources used. An EDoS attack on PaaS can include running several instances of databases and development tools, or excessively utilizing platform resources for continuous deployment and testing. Since the platform provider is charged according to the resources used, this may result in increased expenses for them. Because IaaS involves renting virtualized hardware resources like virtual machines, storage, and bandwidth, it is especially susceptible to EDoS attacks. Attackers have the ability to start up a lot of virtual machines, use a lot of storage, or send a lot of data, all of which increase the service provider’s expenses. The main objective is to deplete the target’s financial reserves to the point where maintaining the service becomes economically unfeasible. The responsibility for implementing detection and mitigation systems for EDoS attacks depends on the terms outlined in the Service Level Agreement (SLA) between the cloud user and the cloud service provider. 

Defending against EDoS attacks proves challenging as they do not exploit specific vulnerabilities in the cloud infrastructure. This type of attack remains a major security concern regarding the financial aspect of cloud service consumers and is more difficult to detect than conventional DoS/DDoS attacks, as it does not make services unavailable as DDoS attacks do [14–16]. Another significant concern regarding EDoS attacks is that 



<!-- Start of picture text -->
(68 (a8)<br>200ee e200 ceed<br><!-- End of picture text -->

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 4 of 21 

this study, we have utilized the RF ensemble model constructed using a reengineered version of the original data, employing an innovative framework known as Integrated Model Prediction and Feature Selection (I-MPaFS), for the purpose of detecting EDoS attacks. Here is a summary of our contributions to this paper: 

- Examining the most recent EDoS detection techniques and identifying their benefits as well as their drawbacks. 

- Providing a novel framework called I-MPaFS for generating a dataset from the original dataset and building a RF model based on the generated dataset. 

- Using three benchmark datasets to demonstrate the effectiveness of the generated dataset’s performance over the original dataset. 

- Establishing a comparison between existing state-ofthe-art studies and our work to highlight the effectiveness of our approach. 

In essence, the research seeks to improve the precision and effectiveness of EDoS attack detection by implementing an innovative data-driven framework that incorporates machine learning models. This approach intends to save cloud users from incurring unnecessary expenses while safeguarding the overall cloud environment. 

This paper is organized into six sections. A brief introduction is provided in Sect. "Introduction", and a literature review is discussed in Sect. "Literature Review". Sect. "Proposed Methodology" describes the proposed method and materials. The experimental results, evaluation of the proposed framework, comparative analysis, and model validation are presented in Sect. "Experimental Performance Analysis". The paper concludes followed by the discussion, limitations, and potential improvements of this study in Sect. "Discussion and Future Work" and Sect. "Conclusion". 

In the world of information technology, cloud computing is revolutionary in the way services are managed and provided. SaaS improves operational efficiency and productivity by streamlining application access and eliminating the need for extensive setups and continuous maintenance. PaaS fosters innovation and shortens time-to-market by offering a stable environment for developing, testing, and deploying software. This speeds up application development. Without having to make an investment in physical hardware, organizations may effectively manage workloads and save costs by utilizing IaaS, which provides scalable and flexible computing resources. When combined, these cloud services improve the IT landscape’s scalability, agility, and affordability. In addition, all 

cloud computing services provide a cost-effective solution with minimal initial expenses, rapid deployment, customizable features as well as adaptability. These innovative environments bring additional benefits, including scalability, automatic updates, and enhanced collaboration capabilities. 

These enticing features make cloud services attractive to a diverse range of companies [3–5]. In particular, the low upfront costs associated with cloud services appeal to businesses, especially small and medium enterprises, as an alternative to constructing and managing their own IT infrastructure [6]. As reported in [7], cloud computing can result in cost savings of up to 40 times compared to operating in-house IT infrastructure for small and medium-sized businesses. During the COVID-19 pandemic in 2020 significantly accelerated global digital transformation, leading to a substantial increase in reliance on cloud computing applications and other related technologies [8, 9]. 

In the world of information technology, cloud computing is revolutionary in the way services are managed and provided. SaaS improves operational efficiency and productivity by streamlining application access and eliminating the need for extensive setups and continuous maintenance. PaaS fosters innovation and shortens time-to-market by offering a stable environment for developing, testing, and deploying software. This speeds up application development. Without having to make an investment in physical hardware, organizations may effectively manage workloads and save costs by utilizing IaaS, which provides scalable and flexible computing resources. When combined, these cloud services improve the IT landscape’s scalability, agility, and affordability. In addition, all cloud computing services provide a cost-effective solution with minimal initial expenses, rapid deployment, customizable features as well as adaptability. These innovative environments bring additional benefits, including scalability, automatic updates, and enhanced collaboration capabilities. 

These enticing features make cloud services attractive to a diverse range of companies [3–5]. In particular, the low upfront costs associated with cloud services appeal to businesses, especially small and medium enterprises, as an alternative to constructing and managing their own IT infrastructure [6]. As reported in [7], cloud computing can result in cost savings of up to 40 times compared to operating in-house IT infrastructure for small and medium-sized businesses. During the COVID-19 pandemic in 2020 significantly accelerated global digital transformation, leading to a substantial increase in reliance on cloud computing applications and other related technologies [8, 9]. 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 5 of 21 

### **Literature review** 

Cloud computing stands out as a widely adopted technology, revered for its user-friendly features and economic benefits. By eliminating the need to construct and maintain IT infrastructure from scratch, its user base continues to expand exponentially. However, the pervasive threat of EDoS attacks poses significant security concerns, leading to financial losses for both providers as well as customers of cloud services. 

Researchers have diligently embarked on a journey to identify and prevent EDoS assaults since the early stages of their evolution. Initial attempts involved the application of various statistical and traditional methods for EDoS attack detection. Unfortunately, these methods proved inefficient and overly complex. The paradigm shift towards AI, with its monumental success in network traffic analysis, prompted researchers to explore its application in the detection of EDoS attacks. This section delves into a detailed examination of earlier works in EDoS attack detection, outlining their strengths and weaknesses. By understanding the evolution of detection methodologies, we aim to pave the way for more effective and sophisticated strategies in countering EDoS threats. 

S. Q. A. Shah et al. proposed the method EDOS-TSM that utilizes binomial probability of the TTL field value of IP packet headers and multi-TCP SYN requests to detect EDoS attacks, with a specific focus on single-user and spoofed IP based attacks [26]. The evaluation of their method was conducted in an experimental cloud setting, assessing its effectiveness against TCP-SYN-based flood attacks. This study concentrated solely on TCP-SYNbased flood EDoS attacks and does not consider other types of attacks, potentially limiting its applicability in real-world cloud implementations. Furthermore, the use of fixed thresholds and TTL values from IP headers may lack adaptability to diverse network and traffic patterns, posing a potential limitation in scenarios with varying conditions. 

Z. A. Baig et al. [27] introduced a novel and reactive approach employing a rate-limit technique with low overhead to detect and mitigate EDoS attacks against cloud-based services. Their proposed mitigation scheme comprises five components: virtual firewall (VF), VM investigator (VMI), load balancer (LB), database (DB), and the virtual machine (VM). The access permissions for cloud services are restricted for each user, determined by factors such as user trust factor (UTF), random check (RC), and concurrent requests per second (CRPS). However, this method did not address the issue of IP spoofing, which could be exploited by attackers to bypass the rate-limit technique and the Turing test. Additionally, the difficulty of the Turing test may potentially limit the rate of authentic users if they fail to pass it. 

The EDoS-ADS [21] technique proposed by A. Shawahna et al. incorporates threshold and duration parameters associated with typical cloud auto-scaling conditions for defending against EDoS attacks. The model assumed four operational modes for the cloud: normal, suspicion, flash overcrowd, and attack. The main components of EDoS-ADS include defense shell (DS), DB, and LB. The system utilized the port address of the client along with the IP address to differentiate between legitimate users and attackers, even though they stayed within the similar NAT-based network. However, the authors assume that the cloud provider offers URL redirection features, which may not be the case for all cloud services or platforms. 

EDOS-IDM model [28] utilized eight statistical features of ICMP traffic flows and exponential back-off functions to identify and counteract EDoS attacks that leverage ICMP flood. The exponential back-off algorithm employed operates by allowing packets from the same flow if the size of the ICMP packet is smaller compared to 64 KB for a specified time. After this period, the flow is blocked for another designated duration. However, a limitation of this study is the use of attack ICMP flows with a fixed interarrival time of 0.2 s, which may not accurately reflect the dynamic and random nature of real-world scenarios. Additionally, the study relies on static thresholds in their exponential back-off algorithms, which might not be optimal in diverse situations. Another limitation is that the study focuses solely on ICMP-based attacks, which are rarely observed in the real world due to their minimal resource usage. 

P. T. Dinh et al. have published a series of three consecutive papers, each employing distinct machine learning algorithms to detect EDoS attacks. Across these papers, the authors have demonstrated a successive improvement in their ability to detect and mitigate EDoS attacks, building upon the performance of their previous work. In their inaugural paper [24], they asserted the novelty of their work as the first machine learning-based EDoS attack detection system. Employing a long short-term memory (LSTM) model, they focused on detecting EDoS attacks in SDN-based clouds, utilizing the server machine dataset (SMD) provided by Ya Su et al. [29]. The LSTM model exhibited commendable performance, achieving an accuracy score of 89.86% and a detection rate of 91.40%. Even with these accomplishments, a drawback emerged in the form of a comparatively lower detection rate, accompanied by a worrisome high 9.75% false alarm rate. In their second publication, the authors adopted the MAD-GAN framework [30], a fusion of generative adversarial networks (GANs) and LSTM recurrent neural networks (LSTM-RNN). This framework was applied to detect attacks within an SDN-based cloud computing 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 6 of 21 

environment. Using the dynamic error threshold, the MAD-GAN architecture calculates a multivariate anomaly score and determines the ideal threshold for separating attack and benign traffic. When applying the MAD-GAN framework to the SMD dataset, they achieved a noteworthy accuracy score of 94.84%, accompanied by a relatively low false positive rate of 5.44%. This performance improvement compared to their previous work is commendable. However, it is important to note that, despite these advancements, the MAD-GAN method lags behind the existing one-class SVM model in terms of resource utilization and response time. In their third paper [31], the authors aimed to enhance their prior contributions. This time, they employed a gated recurrent neural network (GRNN) on the same dataset and within the same cloud architecture. The GRNN was initially trained on normal traffic to discern and learn benign traffic patterns. Subsequently, this acquired knowledge was leveraged to distinguish between normal and attack traffic using a soft threshold, a strategy implemented to refine and enhance their detection accuracy. The results of their efforts were notable, yielding an accuracy score of 94.33% and an impressive detection rate of 96.27%, accompanied by a reduced false alarm rate of 4.72%. These outcomes signify a substantial improvement over their earlier works. Although the model effectively detects three out of the five trained EDoS attack types, its efficacy diminishes for the remaining two types, rendering it ineffective against attacks utilizing these two types. 

S. B. R. Jones et al. introduced a system named EDoSDome for detecting EDoS attacks, integrating a deep learning approach utilizing regression coefficients deer hunting deep Elman neural network (RCDH-ENN) [32]. This system classifies user data into either a blacklist or whitelist based on predefined conditions and optimized weight values. Notably, they achieved impressive performance metrics, including an accuracy of 97.01%, precision of 97.05%, recall of 97.05%, and an F1 score of 97.05%. Despite these promising results, the authors omitted any comparisons with existing studies and neglected to provide details about their datasets. This lack of comparative analysis and dataset information hinders the evaluation of the method’s true effectiveness. 

In 2021, V. Q. Ta et al. introduced a multihead attention network (MANEDoS) [33] closely resembling the transformer model. However, their innovation lies in exclusively leveraging the encoder component of the autoencoder-decoder module from the transformer to compute attention scores. The final model was constructed using a total of eight attention heads. Through experimentation with the UNSWNB15 [34] dataset, they achieved remarkable performance metrics, including 98.00% accuracy, 98.90% precision, 98.30% recall, 

and 98.60% F1 score. Their model’s efficacy is demonstrated by these outcomes. It is important to note that, while the proposed model demonstrates significant efficacy, it relies on a complex transformer-like architecture that demands substantial computing resources for training. Additionally, the potential need for frequent model updates due to evolving attack patterns could impose further financial burdens. 

In their effort to defend against EDoS attacks, H. Abbasi et al. [35] proposed an EDoS attack detection approach reliant on two machine learning models constructed from an attack profile, utilizing a dataset derived by extracting 18 features from cloud traffic flows. They employed neural network (NN) and support vector machine (SVM) for attack detection. The implementation of their machine learning model was carried out using the WEKA tool, yielding an accuracy score of 97.07% and 100% for NN and SVM models, respectively. However, a notable limitation of their approach is its ability to only detect known attack patterns. The performance of their models decreases in the case of evolving attack patterns. 

In the study by T.H. Aldhyani et al. [13] utilized three machine learning models (SVM, KNN, RF) and two deep neural network models (CNN, LSTM) for the detection of EDoS attacks. The UNSW-NB15 dataset was utilized in their experiments, resulting in the highest recall score of 98%. However, it’s important to note that they only utilized a partial amount of the UNSW-NB15 dataset and did not assess their model’s performance with other publicly available datasets. This limitation raises questions about the generalizability and effectiveness of their model in scenarios involving different datasets. 

In the work presented by [36], the authors propose the SDPN, a multivariate time-series anomaly detection system. The SDPN initially learns precise representations of multivariate time sequences to replicate typical patterns. Subsequently, the reconstructed input data is compared to the original, and probabilities derived from this reconstruction process serve as a tool for detecting attacks. Notably, the authors incorporate a soft threshold for EDoS attack detection, deviating from a hard threshold. Despite achieving a sensitivity of 97.34% and an accuracy score of 96.89% on the UNSW-NB15 dataset, the performance scores do not surpass existing methods on the same dataset, indicating a need for further enhancement in the model’s effectiveness. Table 1 presents an organized summary of the reviewed studies, highlighting their main contributions, datasets utilized, techniques/models utilized, results, strengths, and limitations. 

Despite the promising advancements observed in the reviewed papers regarding both accuracy and efficiency in EDoS attack detection research, there remain some common limitations across various methodologies. 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 7 of 21 

|**Limitations**<br> <br>t-<br>Lower detection rate,<br>with a very high 4.24% false<br>alarm rate<br>ci-<br>s<br>Potential model instability,<br>requires further investiga-<br>tion on optimal subse-<br>quence length and latent<br>dimension<br> <br>k<br>Potential false positives<br>in cases of legitimate high<br>trafc<br>-<br> <br>Lack of comparisons<br>with existing studies,<br>and no detail of the dataset<br>is provided|
|---|
|**Strengths**<br>,<br>Efective in detect-<br>ing EDoS attacks, high<br>accuracy, low false alarm<br>rate, low overhead, adap<br>able to various network<br>systems<br>l<br> <br>Efective in detecting<br>anomalies in complex<br>multivariate time series<br>data, high recall and pre<br>sion, novel use of GAN<br>framework for time serie<br>data<br>,<br> <br>,<br>%<br>Low false alarm rates,<br>high detection accuracy,<br>efective in diverse attac<br>scenarios, low resource<br>consumption<br> <br>High accuracy and preci<br>sion, low response time,<br>cost-efcient, robust<br>against EDoS attacks|
|**Results**<br>e<br>,<br> <br> <br> <br>Detection rate of 95.03%<br>Accuracy of 95.38%,<br>and a False Alarm Rate<br>of 4.24%<br>-<br>SWaT dataset shows<br>a Precision of 99.98%,<br>Recall of 99.99%,<br>and F1-score of 77.00%.<br>On the WADI dataset,<br>Precision is 46.98%, Recal<br>99.99%, and F1-score<br>37.00%. For the KDD-<br>CUP99 dataset, Precision<br>is 94.92%, Recall 96.33%,<br>and F1-score 94.00%<br> <br>Detection rate of 96.27%<br>accuracy of 94.33%, false<br>alarm rate (FAR) of 4.72%<br>and an F1-score of 95.51<br>Achieved 97.01% accu-<br>racy, 97.05% precision,<br>97.05% recall, and 97.05%<br>F-measure in attack clas-<br>sifcation|
|**Dataset**<br>**Method/Model**<br>-<br> <br> <br>-<br>Server Machine Dataset<br>(SMD)<br>LSTM for multivariate tim<br>series anomaly detection<br>Dynamic Error Threshold,<br>Exponentially-Weighted<br>Average (EWMA) for gen-<br>erating smoothed errors,<br>SDN-based proactive<br>detection and mitigation<br> <br> <br>Secure Water Treatment<br>(SWaT) dataset, Water Dis-<br>tribution (WADI) dataset<br>and KDDCUP99 dataset<br>Generative Adver-<br>sarial Networks (GAN)<br>with LSTM-RNN as gen-<br>erator and discriminator,<br>Discrimination and Recon<br>struction Anomaly Score<br>(DR-Score)<br> <br>-<br>SMD dataset<br>Multivariate time series<br>anomaly detection, GRU,<br>variational autoencoder<br>(VAE), stochastic gradient<br>variational Bayes (SGVB),<br>planar normalizing fows<br> <br>Not specifed<br>Obfuscated IP spoofng,<br>CI-RDA load balancer,<br>RCDH-ENN for classifca-<br>tion|
|**Major Contribution**<br>Proposed a machine learn<br>ing-based approach using<br>Long Short-Term Memory<br>(LSTM) for multivariate<br>time series anomaly detec<br>tion with a dynamic error<br>threshold to detect EDoS<br>attacks in an SDN-based<br>cloud environment<br>Proposed MAD-GAN,<br>a GAN-based unsuper-<br>vised anomaly detection<br>method for multivariate<br>time series data using<br>LSTM-RNN as gen-<br>erator and discriminator,<br>and a novel anomaly score<br>combining discrimination<br>and reconstruction losses<br>Proposed R-EDoS, a robust<br>scheme for detecting<br>and mitigating EDoS<br>attacks using multivariate<br>time series anomaly detec<br>tion and gated recurrent<br>unit (GRU) to capture<br>complex temporal<br>dependencies<br>Proposed EDoS-DOME<br>system to mitigate EDoS<br>attacks using obfuscated<br>IP spoofng and regression<br>coefcients deer hunting-<br>deep Elman neural<br>network (RCDH-ENN)|
|**Reference**<br>Dinh and Park [24]<br>Li et al. [30]<br>Dinh and Park [31]<br>Ribin and Kumar [32]|



Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 8 of 21 

|**Limitations**<br>-<br>Complex architecture<br>requiring substantial com-<br>puting resources<br> <br>Not evaluated using bench-<br>marks dataset<br>Limited generalizability<br>and efectiveness on difer-<br>ent datasets<br> <br>Face challenges in detect-<br>ing YoYo and Slowloris<br>types attacks|
|---|
|**Strengths**<br>Efective attention mecha<br>nism<br>High detection accuracy,<br>ability to detect multiple<br>types of EDoS attacks, low<br>false positives and nega-<br>tives<br> <br>High accuracy, efective<br>in binary and multi-clas-<br>sifcation, low prediction<br>error, robust against vari-<br>ous EDoS attacks<br>High detection accuracy,<br>efective in detecting vari-<br>ous EDoS attacks|
|**Results**<br>al<br>Achieved 98% detection<br>accuracy and 60% faster<br>computational speed<br>compared to previous<br>techniques<br>),<br> <br>-<br>The framework achieved<br>accuracy of 97.06% using<br>NN and 100% using SVM<br>y<br>RF achieved 98% accuracy<br>with binary classifcation,<br>SVM achieved 97.54%<br>with multi-classifcation<br>i-<br>r<br>SDPN achieved sensitiv-<br>ity of 97.34%, specifcity<br>of 97.49%, accuracy<br>of 96.89%, and a kappa<br>index of 88|
|**Method/Model**<br>Multihead Attention<br>Network (MAN), position<br>encoding, feed-forward<br>neural network, softmax<br>for attention scores<br>Machine learning algo-<br>rithms (Support Vector<br>Machine, Neural Network<br>periodic trafc sampling,<br>resource usage patterns,<br>Exponential Moving Aver<br>age (EMA)<br>SVM, KNN, Random For-<br>est (RF), Convolutional<br>Neural Network (CNN),<br>Long Short-Term Memor<br>(LSTM), binary classifca-<br>tion, multi-classifcation<br>Stack Deep Polynomial<br>Network (SDPN), multivar<br>ate time series anomaly<br>detection, dynamic<br>threshold, Singular Vecto<br>Decomposition (SVD)|
|**Major Contribution**<br>**Dataset**<br>Proposed MAN-EDoS,<br>an attention-based<br>deep learning model<br>for efcient and accu-<br>rate detection of EDoS<br>attacks, utilizing multihead<br>attention mechanism<br>to enhance feature selec-<br>tion and reduce process-<br>ing time<br>UNSW-NB15, NSL-KDD<br>and CICIDS dataset<br>Proposed a novel machine<br>learning-based framework<br>using execution trace<br>analysis to detect EDoS<br>attacks, focusing on traf-<br>fc and resource usage<br>anomalies<br>Own dataset<br>Proposed multiple<br>machine learning<br>and deep learning<br>algorithms to detect<br>and mitigate EDoS attacks,<br>comparing performance<br>metrics like accuracy,<br>precision, recall, F1 score,<br>MSE, and RMSE<br>UNSW-NB15<br>Proposed SDPN technique<br>for detecting and mitigat-<br>ing EDoS attacks in SDN-<br>based cloud environments<br>using multivariate time<br>series anomaly detection<br>with dynamic thresholds<br>UNSW-NB15|
|**Reference**<br>Ta and Park [33]<br>Abbasi et al. [35]<br>Aldhyani and Alkahtani<br>[13]<br>Sugana et al. [36]|



Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 9 of 21 

Certain approaches utilize their generated datasets in developing and building ML algorithms, which may lack effectiveness when benchmarked against standard datasets. Another challenge is the data dependence observed in some techniques, where high performance on specific datasets contrasts with low performance on different datasets. Resource-intensive models, exemplified by complex architectures like transformers, may impose substantial computing demands for training and updates, potentially incurring financial burdens. The ever-changing characteristic of EDoS introduces significant challenges, as existing methods may struggle to detect novel or rapidly changing attack patterns, necessitating continuous adaptation and improvement for robust defense mechanisms. To overcome these limitations, we have proposed a novel data-driven approach for detecting EDoS attacks. Our study utilizes two different benchmark datasets to demonstrate its generality across different datasets. 

### **Proposed methodology** 

In this research, we have introduced a novel framework for detecting EDoS attacks in the cloud computing environment (CCE). The framework comprises two modules: the Integrated Model Prediction and Feature Selection (I-MPaFS) dataset generation unit and the EDoS attack detection unit. 

Our proposed I-MPaFS unit focuses on selecting the best ML model, whose predictions serve as features, and focuses on identifying optimal features from the dataset. This module produces two unique datasets: one containing predictions from selected ML models (base models) and another consisting of a subset of features selected by feature selection methods. These two datasets are integrated to create an I-MPaFS Dataset reproducing the original dataset. We assume that the reproduced dataset will produce better results than the original datasets when training and evaluating machine learning model. This assumption is based on the premise that the combined strengths of multiple models and the selection of optimal features enhance the dataset’s quality, leading to improved performance in detecting EDoS attacks. The attack detection model development unit in this study is an RF model trained using the I-MPaFS Dataset generated by the I-MPaFS unit. 

#### **Dataset description** 

A relevant dataset, appropriate to the context, plays a pivotal role in the development of ML and deep learning models. In this study, the UNSW-NB15 dataset [34], the 

CIC-CSC-IDS18 dataset [37] and the ISCX NSL-KDD dataset [38] are employed. All datasets were meticulously selected for their comprehensive nature and their ability to simulate real-world network conditions, which is crucial for the detection of EDoS attacks. These three datasets are widely acknowledged and regarded as benchmark datasets in the development of intrusion detection systems based on machine learning and deep learning [39]. The UNSW-NB15 dataset has been cited 3,170 times, the CIC-CSC-IDS18 dataset has been cited 3,648 times and the NSL-KDD dataset has been cited 5,497 times based on Google Scholar, a popular academic search engine that catalogs books, conference papers, theses, and scholarly articles. This extensive citation history highlights their reliability in this field. 

The raw network packets of the UNSW-NB15 dataset were generated by the IXIA PerfectStorm tool in the Cyber Range Lab of the University of New South Wales (UNSW), Canberra, Australia. This process aimed to create a hybrid dataset that incorporates both real-world normal activities and synthetic contemporary attack characteristics. Because of this, the UNSE-NB15 has been utilized by researchers in their recent work [13, 40, 41]. This dataset is an invaluable resource for developing and testing EDoS attack detection models because it offers a wide range of attack scenarios and network characteristics. 

The CSE-CIC-IDS2018 dataset was generated within a practical Amazon Web Services (AWS) cloud environment, as part of a joint initiative between the Canadian Institute for Cybersecurity (CIC) and the Communications Security Establishment (CSE). This dataset addresses the limitations of static and non-diverse intrusion data by employing dynamically generated user profiles that reflect real-world cloud attacks. The CSE-CIC-IDS2018 dataset creation AWS cloud environment was equipped with an attacking infrastructure comprising 50 machines and a victim organization consisting of 5 departments, including 420 machines and 30 servers. The dynamic user profiles in the CSE-CICIDS2018 dataset offer a realistic environment for testing EDoS attack detection methods in cloud computing, ensuring that the models are trained on varied and representative data. This dataset’s realistic setup and comprehensive attack scenarios make it ideal for evaluating the robustness of detection models in real-world cloud environments. 

The Information Security Centre of Excellence (ISCX) created the ISCX NSL-KDD dataset, which is based on the KDD’99 dataset, in response to complaints about the 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 10 of 21 

original dataset’s lack of difficulty variations and redundancy. This improved dataset gives machine learning models a more realistic and demanding environment by removing duplicate records and guaranteeing a balanced distribution of training and testing data. Furthermore, the NSL-KDD train and test sets have a sufficient number of records, so it is possible to conduct experiments on the entire set without having to choose a smaller subset at random. The diverse and realistic attack scenarios within the ISCX NSL-KDD dataset make it an invaluable resource for evaluating the effectiveness of EDoS detection methods in cloud computing environments, ensuring that models are trained on representative and varied data. 

The UNSW-NB15 dataset comprises 9 types of attacks and 42 features, the CSE-CIC-IDS-IDS18 dataset incorporates 7 types of attacks and 78 features, whereas the NSL-KDD dataset has 4 classes of attacks and 41 features. 

#### **Data preprocessing** 

The performance of any ML model relies significantly on the consistency of the training data. Hence, data preprocessing plays a crucial role in model development [42]. Initially, duplicate rows are removed, and any rows with missing or NaN values are eliminated due to their negligible count compared to the total dataset size. Label encoding techniques are employed to transform categorical data into numerical data. Another essential preprocessing step involves normalization. We have applied minmax normalization, which scales the dataset values between a specified range, typically 1 and 0. The min– max normalization formula is: 



Here, _X_ is the original value, _X_ min is the minimum value in the feature, and _X_ max is the maximum value in the feature. 

#### **Dataset distribution** 

To ensure rigorous training and evaluation, we have divided the dataset into two distinct partitions: 

#### **_Training set (80%)_** 

This set, referred to as both “fold data” and “feature selection data” served two crucial purposes: 

- _Base-model selection:_ It guides the identification of optimal base models for generating model predictions. 

- _Feature selection:_ It enables the determination of the most relevant feature subset, enhancing model efficiency and reducing noise. 

#### **_Testing set (20%)_** 

This set, entirely independent of the training process, provided an unbiased assessment of the model’s true performance, revealing its ability to generalize to unseen data. 

#### **I‑MPaFS dataset generation** 

Our study focuses on enhancing an existing dataset through the implementation of a novel framework. The proposed feature engineering framework comprises two modules. The first module generates a dataset that incorporates predictions from various machine learning models as its features. The second module generates a dataset that comprises the selected subset of the original feature set. This framework harnesses the collective capabilities of different ML models and a features selection technique to uncover hidden insights and improve model performance. 

The proposed framework accommodates any number and type of ML models for feature creation, along with the flexibility to apply different feature selection approaches. 

#### **_Model prediction dataset generation_** 

The initial module of the proposed data generation framework involves creating a dataset based on predictions from models. Several machine learning models are selected as candidate base learners for generating the model prediction dataset. Each of these candidate models undergoes training and evaluation using the preprocessed fold data. Subsequently, the evaluation score is compared to a threshold value to ascertain the qualification of the model prediction, which is then included as a feature in the model prediction dataset. If the evaluation score equals or exceeds the threshold value, we consider that model prediction as a feature in the model prediction dataset. Otherwise, the model prediction is not included in the dataset. The dataset generated by this module is named the model prediction dataset ( _D_ pred). Algorithm 1 outlines the working process of this unit. 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 11 of 21 

##### **Algorithm 1** Generating model prediction dataset 



#### **_Feature selection dataset generation_** 

The second module of our proposed I-MPaFS framework generates a subset of the original dataset that includes selected features determined by the feature selection algorithm. The proposed I-MPaFS framework is adaptable to any feature selection technique, enabling the selection of the most effective features from the original dataset to achieve optimal performance. The feature subset, obtained after selection with feature selection algorithms, is employed to train and evaluate various machine learning algorithms. 

This framework is also adaptable in enhancing feature selection performance until a satisfactory evaluation score is achieved by the selected feature subset from the original dataset. The dataset generated by the feature selection module is named the feature selection dataset ( _D_ subset). Algorithm 2 outlines the working process of this unit. After generating the model prediction dataset and the feature subset dataset using the model prediction and feature selection modules, we concatenate these two datasets to create the I-MPaFS dataset ( _D_ I-MPaFS). 

**Algorithm 2** Feature subset selection 





<!-- Start of picture text -->
Doriginat<br>Train-Test Split<br>‘Dirain Drest<br>|-MPaFS Framework<br>‘Di-mpaes -train ‘Di-mpars-test<br>&@<br>Model training<br>Trained Model 3 2)<br>Model Evaluation and Comparison<br><!-- End of picture text -->



<!-- Start of picture text -->
oO<br>=<br>& True Positive (TP) False Negative (FN)<br>2<br><<br>oO<br>2<br>Ey<br>S False Positive (FP) True Negative (TN)<br>a<br>Predicted Positive Predicted Negative<br><!-- End of picture text -->

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 13 of 21 

In this study, the Recursive Feature Elimination (RFE) technique with an RF as the core model is utilized for feature selection to identify and retain the most relevant features for creating the IMPaFS dataset. RFE operates by iteratively training the RF model, ranking features by their importance, and recursively removing the least important features. This elimination process continues until the optimal subset of features is reached, enhancing the core model’s performance by reducing dimensionality. The criteria for selecting features are based on their importance scores derived from the RF model, which assesses the contribution of each feature to the overall predictive power. By focusing on the most significant features, RFE helps eliminate irrelevant or redundant data, thereby streamlining the dataset. By concentrating on the most important features, the model performs better in terms of prediction since it can identify patterns and abnormalities more easily. 

### **EDoS attack detecting model** 

The EDoS attack-detecting module consists of the I-MPaFS framework and a ML-based model. The original dataset is initially divided into the training dataset ( _D_ train) and the test dataset ( _D_ test) to facilitate the effective development and evaluation of the EDoS attack detection model. Subsequently, both the training and test datasets are input into the I-MPaFS framework separately, generating the corresponding train dataset ( _D_ I-MPaFS-train) and test dataset ( _D_ I-MPaFS-test). The _D_ I-MPaFS-train dataset is utilized to train an ML model. Following the model training, the _D_ I-MPaFS-test dataset is used for model evaluation. After evaluation, the model’s performance is compared with the original dataset’s performance, as well as with the _D_ pred and _D_ subset dataset’s performance. The diagram depicted in Fig. 2 illustrates the developmental stages of the EDoS attack detection model. 

Scikit-Learn [43], an open-source toolkit based on the Python programming language, is used to implement all algorithms and models. The programs are executed on a system running Windows 11 OS, equipped with an Intel Core i5-1135G7 Processor @ 3.40 GHz and a total of 16 GB RAM. 

### **Performance evaluation metrics** 

Various performance metrics, including accuracy, recall, precision, F1-score, ROC, AUC, TPR, FPR, confusion matrix, and others, are utilized to evaluate the effectiveness of ML models. Each of these metrics holds unique significance, and its value provides insights into the specific capabilities of ML models. 

The confusion matrix is a tabular representation employed in classification to illustrate the performance 

of any ML model. It represents a summary of how many true positives (TP), true negatives (TN), false positives (FP), and false negatives (FN) a classification model made [44]. Figure 3 presents the distribution of TP, TN, FP, and FN in the confusion matrix. Other performance metrics of the machine learning model are assessed using this matrix as the foundation. In this study, we have assessed and presented 4 evaluation scores: accuracy, recall (sensitivity), precision, and F1-score. 

Accuracy is one widely used metric, which measures the ratio of correctly predicted instances to the total instances in the dataset. It is represented by the equation: 





Recall measures the model’s capacity to find all pertinent occurrences; it is sometimes called true positive rate or sensitivity. The recall formula is: 



F1-score is a balanced metric that combines precision and recall through a harmonic mean. It is computed as: 



### **Experimental performance analysis** 

In this research, to detect EDoS attacks, we have proposed a novel framework named I-MPaFS, which incorporates a feature engineering technique using model prediction and a feature selection technique. These two modules produce a modified rendition of the original dataset, known as the model prediction and feature selection dataset ( _D_ I-MPaFS). To produce the model prediction dataset, we have primarily selected Random Forest (RF), Decision Tree (DT), Light Gradient Boosting Machine (LGBM), Extreme Gradient Boosting (XGB), K-nearest neighbor (KNN), Support Vector Machine (SVM), Logistic Regression (LR), and Multi-Layer Perceptron (MLP) as model prediction dataset generators. After training and evaluating those models, their accuracy scores are compared with a threshold value to determine whether any candidate model would finally be qualified as contributing to making predictions and be included as a feature in the model prediction dataset ( _D_ pred). In this study, two 



<!-- Start of picture text -->
102<br>@@@ Original Om FS am MP tm I-MPaFS<br>101<br>o ite} ~ al<br>100 a 8-5-3bi gape Oa latesSt = Qase) onaa oex<br>> eT Pe er ee<br>EF gf 3 S-_ 8<br>£<br>8 98<br>7)<br>97<br>96<br>95<br>Accuracy Recall Precision Fl1-score<br><!-- End of picture text -->



<!-- Start of picture text -->
102<br>@@m@ Original ma FS m= MP @m I-MPaFS<br>101<br>g g 5 <<br>100 a B—5—g gol ~ Baul 4-593<br>= so 3 a a ~ 8 Foe<br>& 99 a S BO 93<br>g<br>8 98<br>77)<br>97<br>96<br>95<br>Accuracy Recall Precision F1-score<br><!-- End of picture text -->



<!-- Start of picture text -->
102<br>@@ Original Om FS Mm MP mm I-MPaFS<br>zy Re 8 ee 8 . Rk @ x R 8<br>wot a 8 8 & 9a $ $8 8 ¢§on) § 8 F §a F F SB<br>& 99<br>g<br>& 98<br>97<br>96<br>95<br>Accuracy Recall Precision Fl-score<br><!-- End of picture text -->



<!-- Start of picture text -->
Original dataset I-MPaFS dataset<br>30000<br>0 32543 346 0 32716 173 25000<br>3 Ss 20000<br>Q pot<br>&&<br>E3E3 15000<br>10000<br>1 268 18378 1 107 18539<br>5000<br>0 1 0 1<br>Predicted label Predicted label<br><!-- End of picture text -->



<!-- Start of picture text -->
Original dataset I-MPaFS dataset 16000<br>14000<br>0 15994 263 0 16075 182 12000<br>3 3 10000<br>QQ<br>&&<br>° o 8000<br>zz<br>BB 6000<br>1 711 13009 1 344 13376 4000<br>2000<br>0 1 0 1<br>Predicted label Predicted label<br><!-- End of picture text -->



<!-- Start of picture text -->
Original dataset I-MPaFS dataset<br>17500<br>15000<br>0 18478 117 0 18563 39<br>12500<br>Fg<br>&& 10000<br>ez<br>&& 7500<br>1 18448 1 29 18480 5000<br>2500<br>0 1 0 1<br>Predicted label Predicted label<br><!-- End of picture text -->



<!-- Start of picture text -->
-C0) : iH iH ¢ gor iH<br>& i ger<br>By OG rrrener rere erence<br>a7)~ HH o Pe HH iH<br>9 Ot i: Celie Cis iia i<br>Ee Lt<br>0.2 rae<br>— ROC curve (I-MPaFS dataset, area = 0.9945)<br>0.0 +E ROC curve (Original dataset, area = 0.9876) |<br>0.0 0.2 0.4 0.6 0.8 1.0<br>False Positive Rate<br><!-- End of picture text -->



<!-- Start of picture text -->
8 ao<br>ga<br>oa<br>— ROC curve (I-MPaFS dataset, area = 0.9819)<br>004-0 ROC curve (Original dataset, area = 0.9660) |<br>0.0 0.2 0.4 0.6 0.8 1.0<br>False Positive Rate<br><!-- End of picture text -->



<!-- Start of picture text -->
2 i “|<br>ga<br>©on<br>— ROC curve (I-MPaFS dataset, area = 0.9982)<br>004-0 ROC curve (Original dataset, area = 0.9950) _<br>0.0 0.2 0.4 0.6 0.8 1.0<br>False Positive Rate<br><!-- End of picture text -->

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 18 of 21 

**Table 3** Comparison with other state-of-art studies (UNSW-NB15 dataset) 

|**Model with Reference**|**Accuracy**<br>**(%)**|**Precision**<br>**(%)**|**Recall**<br>**(%)**|**F1‑Score**<br>**(%)**|
|---|---|---|---|---|
|DFS [50]|92.76|96.11|*|94.44|
|MAN-EDoS [33]|98.00|98.90|98.30|98.60|
|SDPN [36]|96.89|*|97.34|*|
|SVM and RF [13]|99.00|98.00|98.00|98.00|
|DT [51]|90.85|80.33|98.38|88.45|
|CNN and LSTM [52]|93.21|92.91|93.10|93.00|
|Transfer Learning [53]|99.21|99.00|100|99.00|
|LightGBM [41]|99.21|99.21|99.21|99.21|
|BG-based GB [45]|94.66|92.21|92.94|92.60|
|M-MultiSVM [54]|97.54|97.67|98.95|98.00|
|**Proposed Approach**|**99.46**|**99.37**|**99.45**|**99.41**|



*means not mentioned in the paper 

**Table 4** Comparison with other state-of-art studies (CSE-CICIDS18 dataset) 

|**Model with**<br>**Reference**|**Accuracy**<br>**(%)**|**Precision**<br>**(%)**|**Recall (%)**|**F1‑Score (%)**|
|---|---|---|---|---|
|CNN [46]|99.99|81.75|82.25|82.00|
|LSTM [49]|96.02|96.00|96.00|96.00|
|DDM and GM [48]|97.38|*|98.18|*|
|ML [47]|96.00|99.00|79.00|90.87|
|PTDAE [55]|95.79|95.38|95.79|95.11|
|TCN, BiGRU,<br>and TGA [56]|97.83|97.85|97.83|97.57|
|DNN [57]|97.98|98.12|97.98|97.98|
|DNN [58]|96.25|98.75|96.80|97.76|
|**Proposed**<br>**Approach**|**98.25**|**98.28**|**98.19**|**98.23**|



*means not mentioned in the paper 

**Table 5** Comparison with other state-of-art studies (NSL-KDD dataset) 

|**Model with Reference**|**Accuracy**<br>**(%)**|**Precision**<br>**(%)**|**Recall**<br>**(%)**|**F1‑Score**<br>**(%)**|
|---|---|---|---|---|
|G-CNN_AE [59]|90.30|91.95|90.35|90.30|
|RNN [60]|88.13|*|*|*|
|Fuzzy Numbers and Scor-<br>ing Methods based on CFS<br>[61]|96.89|*|97.40|97.50|
|SVM, LR, KNN [62]|98.24|97.99|97.91|98.00|
|**Proposed Approach**|99.82|99.82|99.82|99.82|



*means not mentioned in the paper 

Figure 7 depicts the confusion matrices for _D_ original and _D_ I-MPaFS of the UNSW-NB15 dataset, while Figs. 8 and 9 depicts the corresponding matrices for the CSE-CICIDS18 dataset and NSL-KDD dataset. Additionally, the 

Area Under the Receiver Operating Characteristic (ROC) curve for these datasets is represented in Fig. 10 for the UNSW-NB dataset, in Fig. 11 for the CSE-CIC-IDS18 dataset and in Fig. 12 for the NSL-KDD dataset. 

Table 3 provides a comprehensive comparison of our research results with recently published studies that used the UNSW-NB15 dataset for EDoS attack detection. According to this Table, SVM and RF [13] achieved the highest position with an accuracy score of 99.21%. MANEDoS [33] achieved the highest precision, and F1-score values of 99.21%, and 99.21%, respectively. However, the highest recall score is achieved by Louk et at. [45] with a score of 100%. Our proposed framework, using the RF model trained on _D_ I-MPaFS dataset, surpasses these results with an outstanding performance score of 99.46%, 99.37%, and 99.41% in accuracy, precision, and F1-score, respectively. Our recall score is 99.45% that is slightly lower than the highest recall score. 

Table 4 provides a comprehensive comparison of our research results with some other published studies that utilized the CSE-CIC-IDS18 dataset. According to this table, Kim et al. [46] achieved the highest accuracy score of 99.99%, but its recall, precision, and F1-score values are notably lower, around 80.00%. In terms of precision score, D’hooge et al. [47] achieved the highest position with a score of 99.00%, but its recall score is only 79.00%, indicating its incapability to identify EDoS attacks effectively. In terms of recall and F1-score, [48] and [49] achieved the highest positions with scores of 98.18% and 97.98%, respectively. This table also highlights the high fluctuation among score values of models developed in studies [46] and [47], which is not acceptable in the case of cloud security. Our proposed framework, using the RF model trained on _D_ I-MPaFS dataset, surpasses these results with a performance score of 98.25%, 98.19%, 98.28%, and 98.23% in accuracy, recall, precision, and F1score, respectively. Our model’s performance scores are also consistent with each other, implying the reliability of this approach in EDoS attack detection. 

Table 5 presents a detailed comparison between our research findings and several other published studies that utilized the NSL-KDD dataset. The table reveals that Vibhute et al. [62] outperforms other works with an accuracy of 98.24%, precision of 97.99%, recall of 97.91%, and F1-score of 98.00%. In contrast, the RF model we built using the _D_ I-MPaFS framework on the NSL-KDD dataset achieved a performance score of 98.82% across all four metrics. This demonstrates the superiority and effectiveness of the proposed I-MPaFS framework. 

### **Discussion and future work** 

The I-MPaFS framework proposed in this study demonstrates significant advancements in the detection of EDoS attacks in cloud computing environments. By 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 19 of 21 

leveraging the RF ensemble model and an enhanced dataset produced by the proposed I-MPaFS framework, this study has shown superior performance compared to existing techniques, achieving recall scores of 99.45% on the UNSW-NB15 dataset, 98.19% on the CSE-CIC-IDS18 dataset, and 99.82% on the NSL-KDD dataset. These outcomes demonstrate the framework’s resilience and effectiveness in detecting and preventing EDoS attacks, shielding cloud users from possible financial exploitation. 

The I-MPaFS framework can be integrated into CCE as part of the existing attack detection system or implemented independently. Incoming packets in the CCE must be feature-engineered according to the detection model used in the I-MPaFS framework. This framework is designed to handle the vast and dynamic nature of cloud computing’s incoming and outgoing data packets, ensuring scalability to meet the demands of various cloud settings. However, practical implementation may face challenges if the feature engineering module takes too long to generate features from the incoming packets. This can delay communication with legitimate users and attackers alike. To address this issue, the feature generation module needs to process packets in real time. This can be achieved by employing a hardwarebased implementation of the feature generation unit, which is significantly faster than a software-based one. Alternatively, a dedicated feature engineering unit optimized for this task can also be a solution. The RF model used in the I-MpaFS framework has a computational complexity of Ο( _N_ log( _N_ ) _d_ . _k_ ), where N is the number of the training samples, d is the dimension of the training data, k is the number of DTs used in RF. The run-time complexity/inference time of the RF model is Ο( _h_ . _k_ ), where h is the height of each tree. The space complexity of the RF is in the same order as of the run-time complexity. 

Despite promising results, this study has some limitations. The proposed I-MPaFS framework integrates the strengths of several ML models, enhancing detection rates and system robustness. However, this integration increases system resource usage and requires all models to be updated when changes are needed. Additionally, the financial and computational costs of integrating this framework into CCE are yet to be assessed. RF models used in the framework depend on the data used during training. If EDoS attack patterns change over time, the model may struggle to adapt without retraining. 

Future work will extend this research by reducing the number of ML models in the I-MPaFS framework while maintaining diversity, performance, and robustness. 

This can be achieved using game-theoretic approaches to select an optimal subset of models. Optimization techniques can also be used to determine the optimal number of ML models, replacing the current threshold methods. Furthermore, the integration cost of this framework will be assessed in terms of resource consumption and prediction time to evaluate its true benefits for cloud users. 

### **Conclusion** 

EDoS attacks exploit cloud computing’s auto-scaling and pay-per-use features, making them a serious security concern that can lead to significant financial losses for users. To address this challenge, we have employed a data-driven framework called I-MPaFS, leveraging ML techniques. The initial phase of the framework involves regenerating the original dataset by amalgamating predictions from multiple trained ML models and selecting a feature subset from the original dataset. Subsequently, a RF model is constructed using the regenerated dataset, serving as the ultimate detector for EDoS attacks. The RF model built using the regenerated dataset demonstrates superior performance compared to the model constructed using the original dataset and outperforms other existing methods of EDoS attack detection. The RF model achieved a recall score of 99.45% on the UNSW-NB-15 dataset, 98.19% on the CSE-CIC-IDS18 dataset, and 99.82% on the NSL-KDD dataset. All these results are higher than the recall scores found using the original datasets. The other performance scores are also higher on the regenerated dataset than those of the original dataset. These results highlight the effectiveness of the proposed framework in EDoS attack detection. 

##### **Abbreviations** 

_CC_ Cloud Computing _CCE_ Cloud Computing Environment _IT_ Information Technology _IDC_ International Data Corporation _EDoS_ Economic Denial of Sustainability _DoS_ Denial of Service _DDoS_ Distributed Denial of Service _VM_ Virtual Manager _AI_ Artificial Intelligence _ML_ Machine Learning _RF_ Random Forest _I-MPaFS_ Integrated Model Prediction and Feature Selection _NN_ Neural Network _ANN_ Artificial Neural Network _SVM_ Support Vector Machine _LSTM_ Long Short-Term Memory _CNN_ Convolutional Neural Network _KNN_ K-Nearest Neighbors _RFE_ Recursive Feature Elimination _IaaS_ Infrastructure as a Service _PaaS_ Platform as a Service _SaaS_ Software as a Service 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 20 of 21 

##### **Acknowledgements** 

We gratefully acknowledge the fellowship support of the Information and Communication Technology (ICT) Division of People’s Republic of Bangladesh, under grant number 56.00.0000.052.33.007.20-74. 

##### **Authors’ contributions** 

All authors contributed to design and development of the system as well as the manuscript. All authors have read and approved the final manuscript. 

##### **Funding** 

No funding was received by the authors for conducting this research. 

##### **Availability of data and materials** 

All datasets utilized in this study are publicly available, and the sources are explicitly mentioned in the corresponding citations. 

#### **Declarations** 

##### **Ethics approval and consent to participate** 

This article does not contain any studies with human participants performed by any of the authors. 

##### **Competing interests** 

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

##### Received: 21 May 2024   Accepted: 19 August 2024 



##### **References** 

1. P. M. Mell and T. Grance, “The NIST definition of cloud computing,” National Institute of Standards and Technology, Gaithersburg, MD, NIST SP 800–145, 2011. https:// doi. org/ 10. 6028/ NIST. SP. 800- 145 

2. Md. A. Hossain and Md. A. Al Hasan. Improving cloud data security through hybrid verification technique based on biometrics and encryption system. Int J Comput Appl. 44;(5):455-464, May 2022, https:// doi. org/ 10. 1080/ 12062 12X. 2020. 18091 77 

3. Haque MA, Almrezeq N, Haque S, El-Aziz AAA (2022) Device Access Control and Key Exchange (DACK) Protocol for Internet of Things. Int J Cloud Appl Comput 12(1):1–14. https:// doi. org/ 10. 4018/ IJCAC. 297103 

4. Hossain M. A, Ferdush J, Khatun M (2021) A study and implementation of large-scale log-determinant computation to cloud. Int J Comput Appl 43(10):1020–1028. https:// doi. org/ 10. 1080/ 12062 12X. 2019. 16486 32 

5. Vakili A, Al-Khafaji HM, Darbandi M, Heidari A, Jafari Navimipour N, Unal M (2024) A new service composition method in the cloud-based Internet of things environment using a grey wolf optimization algorithm and MapReduce framework. Concurr Comput Pract Exp 36(16):e8091. https:// doi. org/ 10. 1002/ cpe. 8091 

6. A. Heidari, N. J. Navimipour, and A. Otsuki, “Cloud-based non-destructive characterization,” in _Non-Destructive Material Characterization Methods_ , Elsevier, 2024, pp. 727–765. https:// doi. org/ 10. 1016/ B978-0- 323- 91150-4. 00006-9 

7. Bismah Nazim Killedar and Maaz Zahid Datey, “The Impact of Cloud Computing on Small and Medium-Sized Businesses,” May 2023, https:// doi. org/ 10. 5281/ ZENODO. 81334 55 

8. Z. Alashhab, M. Anbar, M. Mahinderjit Singh, Z. Al-Sai, and S. Abu Alhayjaa, “Impact of Coronavirus Pandemic Crisis on Technologies and Cloud Computing Applications,” _J. Electron. Sci. Technol._ , Nov. 2020, https:// doi. org/ 10. 1016/j. jnlest. 2020. 100059 

9. Department of Computer Science and Engineering, SDM College of Engineering and Technology, Dharwad, Karnataka-580002, India, R. Yadawad, U. P. Kulkarni, and J. A. Alzubi, “Auto-metric Graph Neural Network for Attack Detection on IoT-based Smart Environment and Secure Data Transmission using Advanced Wild Horse Standard Encryption Method,” _Int. J. Comput. Netw. Inf. Secur._ , vol. 16, no. 3, pp. 1–15, Jun. 2024, https:// doi. org/ 10. 5815/ ijcnis. 2024. 03. 01 

10. A. Verma and S. Kaushal, “Cloud Computing Security Issues and Challenges: A Survey,” in _Advances in Computing and Communications_ , vol. 193, A. Abraham, J. L. Mauri, J. F. Buford, J. Suzuki, and S. M. Thampi, Eds., in Communications in Computer and Information Science, vol. 193. , Berlin, Heidelberg: Springer Berlin Heidelberg, 2011, pp. 445–454. https:// doi. org/ 10. 1007/ 978-3- 642- 22726-4_ 46 

11. Sinjilawi YK, Al-Nabhan MQ, Abu-Shanab EA (2014) Addressing Security and Privacy Issues in Cloud Computing. J Emerg Technol Web Intell 6(2):192–199. https:// doi. org/ 10. 4304/ jetwi.6. 2. 192- 199 

12. Alouffi B, Hasnain M, Alharbi A, Alosaimi W, Alyami H, Ayaz M (2021) A Systematic Literature Review on Cloud Computing Security: Threats and Mitigation Strategies. IEEE Access 9:57792–57807. https:// doi. org/ 10. 1109/ ACCESS. 2021. 30732 03 

13. Aldhyani THH, Alkahtani H (2022) Artificial Intelligence Algorithm-Based Economic Denial of Sustainability Attack Detection Systems: Cloud Computing Environments. Sensors 22(13):4685. https:// doi. org/ 10. 3390/ s2213 4685 

14. El Kafhali S, El Mir I, Hanini M (2022) Security Threats, Defense Mechanisms, Challenges, and Future Directions in Cloud Computing. Arch Comput Methods Eng 29(1):223–246. https:// doi. org/ 10. 1007/ s11831- 021- 09573-y 

15. Jangjou M, Sohrabi MK (2022) A Comprehensive Survey on Security Challenges in Different Network Layers in Cloud Computing. Arch Comput Methods Eng 29(6):3587–3608. https:// doi. org/ 10. 1007/ s11831- 022- 09708-9 

16. Hossain MdA (2023) Enhanced Ensemble-Based Distributed Denial-ofService (DDoS) Attack Detection with Novel Feature Selection: A Robust Cybersecurity Approach. Artif Intell Evol 4(2):165–186. https:// doi. org/ 10. 37256/ aie. 42202 33337 

17. G. Somani, M. S. Gaur, D. Sanghi, M. Conti, and R. Buyya, “DDoS Attacks in Cloud Computing: Issues, Taxonomy, and Future Directions,” 2015, https:// doi. org/ 10. 48550/ ARXIV. 1512. 08187 

18. Idziorek J, Tannian M (2011) Exploiting Cloud Utility Models for Profit and Ruin,” in _2011 IEEE 4th International Conference on Cloud Computing_ . IEEE, Washington, DC, pp 33–40. https:// doi. org/ 10. 1109/ CLOUD. 2011. 45 

19. Al-Haidari F, Sqalli M, Salah K (2015) Evaluation of the Impact of EDoS Attacks Against Cloud Computing Services. Arab J Sci Eng 40(3):773–785. https:// doi. org/ 10. 1007/ s13369- 014- 1548-y 

20. F. Z. Chowdhury, L. B. M. Kiah, M. A. M. Ahsan, and M. Y. I. Bin Idris, “Economic denial of sustainability (EDoS) mitigation approaches in cloud: Analysis and open challenges,” in _2017 International Conference on Electrical Engineering and Computer Science (ICECOS)_ , Palembang: IEEE, Aug. 2017, pp. 206–211. https:// doi. org/ 10. 1109/ ICECOS. 2017. 81671 35 

21. A. Shawahna, M. Abu-Amara, A. Mahmoud, and Y. E. Osais, “EDoS-ADS: An Enhanced Mitigation Technique Against Economic Denial of Sustainability (EDoS) Attacks,” _IEEE Trans. Cloud Comput._ , pp. 1–1, 2018, https:// doi. org/ 10. 1109/ TCC. 2018. 28059 07 

22. Bhingarkar S, Shah D (2018) FLNL: Fuzzy entropy and lion neural learner for EDoS attack mitigation in cloud computing. Int J Model Simul Sci Comput 09(06):1850049. https:// doi. org/ 10. 1142/ S1793 96231 85004 96 

23. Monge M, Vidal J, Villalba L (2017) Entropy-Based Economic Denial of Sustainability Detection. Entropy 19(12):649. https:// doi. org/ 10. 3390/ e1912 0649 

24. P. T. Dinh and M. Park, “Dynamic Economic-Denial-of-Sustainability (EDoS) Detection in SDN-based Cloud,” in _2020 Fifth International Conference on Fog and Mobile Edge Computing (FMEC)_ , Paris, France: IEEE, Apr. 2020, pp. 62–69. https:// doi. org/ 10. 1109/ FMEC4 9853. 2020. 91449 72 

25. Alzubi JA, Alzubi OA, Qiqieh I, Singh A (2024) A Blended Deep Learning Intrusion Detection Framework for Consumable Edge-Centric IoMT Industry. IEEE Trans Consum Electron 70(1):2049–2057. https:// doi. org/ 10. 1109/ TCE. 2024. 33502 31 

26. Shah SQA, Khan FZ, Ahmad M (2022) Mitigating TCP SYN flooding based EDOS attack in cloud computing environment using binomial distribution in SDN. Comput Commun 182:198–211. https:// doi. org/ 10. 1016/j. comcom. 2021. 11. 008 

27. Baig ZA, Sait SM, Binbeshr F (2016) Controlled access to cloud resources for mitigating Economic Denial of Sustainability (EDoS) attacks. Comput Netw 97:31–47. https:// doi. org/ 10. 1016/j. comnet. 2016. 01. 002 

28. S. Q. Ali Shah, F. Zeeshan Khan, and M. Ahmad, “The impact and mitigation of ICMP based economic denial of sustainability attack in cloud computing environment using software defined network,” _Comput. Netw._ , 

Hossain _et al. Journal of Cloud Computing          (2024) 13:151_ 

Page 21 of 21 

vol. 187, p. 107825, Mar. 2021, https:// doi. org/ 10. 1016/j. comnet. 2021. 107825 

29. Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust Anomaly Detection for Multivariate Time Series through Stochastic Recurrent Neural Network,” in _Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining_ , Anchorage AK USA: ACM, Jul. 2019, pp. 2828–2837. https:// doi. org/ 10. 1145/ 32925 00. 33306 72 

30. D. Li, D. Chen, L. Shi, B. Jin, J. Goh, and S.-K. Ng, “MAD-GAN: Multivariate Anomaly Detection for Time Series Data with Generative Adversarial Networks,” 2019, _arXiv_ . https:// doi. org/ 10. 48550/ ARXIV. 1901. 04997 

31. Dinh PT, Park M (2021) R-EDoS: Robust Economic Denial of Sustainability Detection in an SDN-Based Cloud Through Stochastic Recurrent Neural Network. IEEE Access 9:35057–35074. https:// doi. org/ 10. 1109/ ACCESS. 2021. 30616 01 

32. S. B. Ribin Jones and N. Kumar, “An efficient EDoS-DOME system in cloud computing using obfuscated IP spoofing technique and RCDH-ENN detection technique,” _Appl. Nanosci._ , vol. 13, no. 2, pp. 1703–1715, Feb. 2023, https:// doi. org/ 10. 1007/ s13204- 021- 02153-3 

33. Ta VQ, Park M (2021) MAN-EDoS: A Multihead Attention Network for the Detection of Economic Denial of Sustainability Attacks. Electronics 10(20):2500. https:// doi. org/ 10. 3390/ elect ronic s1020 2500 

34. Moustafa N, Slay J, “UNSW-NB15: a comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set)”, in, (2015) Military Communications and Information Systems Conference (MilCIS). Canberra, Australia: IEEE, Nov 2015:1–6. https:// doi. org/ 10. 1109/ MilCIS. 2015. 73489 42 

35. Abbasi H, Ezzati-Jivan N, Bellaiche M, Talhi C, Dagenais MR (2019) Machine Learning-Based EDoS Attack Detection Technique Using Execution Trace Analysis. J Hardw Syst Secur 3(2):164–176. https:// doi. org/ 10. 1007/ s41635- 018- 0061-2 

36. S. M, M. M, S. J, M. Suresh, P. G. Banupriya, and L. Dhavamani, “Detection of EDoS attacks in SDN-based Cloud Model using Deep Learning based SDPN Technique,” in _2022 Third International Conference on Smart Technologies in Computing, Electrical and Electronics (ICSTCEE)_ , Bengaluru, India: IEEE, Dec. 2022, pp. 1–7. https:// doi. org/ 10. 1109/ ICSTC EE569 72. 2022. 10099 583 

37. I. Sharafaldin, A. Habibi Lashkari, and A. A. Ghorbani, “Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization:,” in _Proceedings of the 4th International Conference on Information Systems Security and Privacy_ , Funchal, Madeira, Portugal: SCITEPRESS - Science and Technology Publications, 2018, pp. 108–116. https:// doi. org/ 10. 5220/ 00066 39801 080116 

38. M. Tavallaee, E. Bagheri, W. Lu, A. A. Ghorbani, “A detailed analysis of the KDD CUP 99 data set”, in (2009) IEEE Symposium on Computational Intelligence for Security and Defense Applications. Ottawa, ON, Canada: IEEE, Jul 2009:1–6. https:// doi. org/ 10. 1109/ CISDA. 2009. 53565 28 

39. M. A. Hossain and M. S. Islam, “Ensuring network security with a robust intrusion detection system using ensemble-based machine learning,” _Array_ , p. 100306, Jul. 2023, https:// doi. org/ 10. 1016/j. array. 2023. 100306 

40. H. I. H. Alsaadi, M. K. Al-Anni, and F. E. K. Al-Khuzaie, “Deep Learning to Mitigate Economic Denial of Sustainability (EDoS) Attacks: Cloud Computing,” in _2023 3rd International Conference on Emerging Smart Technologies and Applications (eSmarTA)_ , Taiz, Yemen: IEEE, Oct. 2023, pp. 1–7. https:// doi. org/ 10. 1109/ eSmar TA593 49. 2023. 10293 405 

41. Md. S. Hossain and Md. S. Islam, “Economic Denial of Sustainability Attack Detection Using Machine Learning,” in _2023 26th International Conference on Computer and Information Technology (ICCIT)_ , Cox’s Bazar, Bangladesh: IEEE, Dec. 2023, pp. 1–6. https:// doi. org/ 10. 1109/ ICCIT 60459. 2023. 10441 045 

42. Hossain Md. A, Islam Md. (2024) Enhancing DDoS attack detection with hybrid feature selection and ensemble-based classifier: A promising solution for robust cybersecurity. Meas Sens 32:101037. https:// doi. org/ 10. 1016/j. measen. 2024. 101037 

43. F. Pedregosa et al., Scikit-learn: Machine Learning in Python. J Mach Learn Res2011;12(85) 

44. Hossain MdA, Islam MdS (2023) A novel hybrid feature selection and ensemble-based machine learning approach for botnet detection. Sci Rep 13(1):21207. https:// doi. org/ 10. 1038/ s41598- 023- 48230-1 

46. Kim J, Kim J, Kim H, Shim M, Choi E (2020) CNN-Based Network Intrusion Detection against Denial-of-Service Attacks. Electronics 9(6):916. https:// doi. org/ 10. 3390/ elect ronic s9060 916 

47. L. D’hooge, T. Wauters, B. Volckaert, and F. De Turck, “Inter-dataset generalization strength of supervised machine learning methods for intrusion detection,” _J. Inf. Secur. Appl._ , vol. 54, p. 102564, Oct. 2020, https:// doi. org/ 10. 1016/j. jisa. 2020. 102564 

48. Ferrag MA, Maglaras L, Moschoyiannis S, Janicke H (2020) Deep learning for cyber security intrusion detection: Approaches, datasets, and comparative study. J Inf Secur Appl 50:102419. https:// doi. org/ 10. 1016/j. jisa. 2019. 102419 

49. P. Lin, K. Ye, and C.-Z. Xu, “Dynamic Network Anomaly Detection System by Using Deep Learning Techniques,” in _Cloud Computing – CLOUD 2019_ , vol. 11513, D. Da Silva, Q. Wang, and L.-J. Zhang, Eds., in Lecture Notes in Computer Science, vol. 11513. , Cham: Springer International Publishing, 2019, pp. 161–176. https:// doi. org/ 10. 1007/ 978-3- 030- 23502-4_ 12 

50. Ahsan M, Gomes R, Chowdhury MdM, Nygard KE (2021) Enhancing Machine Learning Prediction in Cybersecurity Using Dynamic Feature Selector. J Cybersecurity Priv 1(1):199–218. https:// doi. org/ 10. 3390/ jcp10 10011 

51. Kasongo SM, Sun Y (2020) Performance Analysis of Intrusion Detection Systems Using a Feature Selection Method on the UNSW-NB15 Dataset. J Big Data 7(1):105. https:// doi. org/ 10. 1186/ s40537- 020- 00379-6 

52. Altunay HC, Albayrak Z (2023) A hybrid CNN+LSTM-based intrusion detection system for industrial IoT networks. Eng Sci Technol Int J 38:101322. https:// doi. org/ 10. 1016/j. jestch. 2022. 101322 

53. Ullah F, Ullah S, Srivastava G, Lin JC-W (2024) IDS-INT: Intrusion detection system using transformer-based transfer learning for imbalanced network traffic. Digit Commun Netw 10(1):190–204. https:// doi. org/ 10. 1016/j. dcan. 2023. 03. 008 

54. Turukmane AV, Devendiran R (2024) M-MultiSVM: An efficient feature selection assisted network intrusion detection system using machine learning. Comput Secur 137:103587. https:// doi. org/ 10. 1016/j. cose. 2023. 103587 

55. Kunang YN, Nurmaini S, Stiawan D, Suprapto BY (2021) Attack classification of an intrusion detection system using deep learning and hyperparameter optimization. J Inf Secur Appl 58:102804. https:// doi. org/ 10. 1016/j. jisa. 2021. 102804 

56. Song Y, Luktarhan N, Shi Z, Wu H (2023) TGA: A Novel Network Intrusion Detection Method Based on TCN, BiGRU and Attention Mechanism. Electronics 12(13):2849. https:// doi. org/ 10. 3390/ elect ronic s1213 2849 

57. Verma R, Jailia M, Kumar M, Kaliraman B (2024) Deep Neural Network Model for Improved DDoS Attack Detection in Cloud Environments, in _2024 5th International Conference for Emerging Technology (INCET)_ . IEEE, Belgaum, pp 1–6. https:// doi. org/ 10. 1109/ INCET 61516. 2024. 10593 561 

58. Alzughaibi S, El Khediri S (2023) A Cloud Intrusion Detection Systems Based on DNN Using Backpropagation and PSO on the CSE-CIC-IDS2018 Dataset. Appl Sci 13(4):2276. https:// doi. org/ 10. 3390/ app13 042276 

59. Park C, Lee J, Kim Y, Park J-G, Kim H, Hong D (2023) An Enhanced AI-Based Network Intrusion Detection System Using Generative Adversarial Networks. IEEE Internet Things J 10(3):2330–2345. https:// doi. org/ 10. 1109/ JIOT. 2022. 32113 46 

60. Kasongo SM (2023) A deep learning technique for intrusion detection system using a Recurrent Neural Networks based framework. Comput Commun 199:113–125. https:// doi. org/ 10. 1016/j. comcom. 2022. 12. 010 

61. Shiravani A, Sadreddini MH, Nahook HN (2023) Network intrusion detection using data dimensions reduction techniques. J Big Data 10(1):27. https:// doi. org/ 10. 1186/ s40537- 023- 00697-5 

62. Vibhute AD, Patil CH, Mane AV, Kale KV (2024) Towards Detection of Network Anomalies using Machine Learning Algorithms on the NSL-KDD Benchmark Datasets. Procedia Comput Sci 233:960–969. https:// doi. org/ 10. 1016/j. procs. 2024. 03. 285 

### **Publisher’s Note** 

Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations. 

45. Louk MHL, Tama BA (2023) Dual-IDS: A bagging-based gradient boosting decision tree model for network anomaly intrusion detection system. Expert Syst Appl 213:119030. https:// doi. org/ 10. 1016/j. eswa. 2022. 119030 

