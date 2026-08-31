**International Journal of Applied Mathematics** 

**Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

# **INTRUSION DETECTION IN CYBERSECURITY: A STUDY ON EXPLAINABLE GRAPHIC REINFORCEMENT LEARNING** 

# **Arun Kumar B S**<sup>**1***</sup> **, Rathnakar Achary**<sup>**2**</sup> 

1Research Scholar, Department of Computer Science and Engineering, Alliance School of Advanced Computing, Alliance University, Bangalore, Karnataka- 562106 India 

*Corresponding Email Id: karunphd23@ced.alliance.edu.in 

2Professor, Department of Computer Science and Engineering, Alliance School of Advanced Computing, Alliance University, Bangalore, Karnataka- 562106 India 

Email Id: rathnakar.achary@alliance.edu.in 

# **Abstract** 

Intrusion Detections Systems (IDS), which are consequently vital for safeguarding digital infrastructure, counter evolving cyber threats. Often, conventional IDS systems including signature-based and anomaly-based battle dynamic attack patterns and high false warning rates. Artificial intelligence (AI) driven solutions, especially reinforcement learning (RL) and graphbased models—have grown more popular in reaction to their capacity to adapt and identify sophisticated threats. As a result, the lack of transparency that is associated with AI-driven intrusion detection systems provides a significant challenge for decision-makers in the field of cybersecurity. Growing confidence and interpretability in AI-based intrusion detection have been greatly influenced by explainable artificial intelligence (XAI). Emphasizing their efficacy in modeling network traffic, enhancing detection accuracy, and guaranteeing decision transparency, this paper seeks to investigate the incorporation of explainability in graph-based reinforcement learning models for IDS. Using secondary data gathering from online databases covering the years 2018 to 2025, a qualitative research approach is employed. The study methodically surveys research on explainability methods in AI-driven IDS, graph-based intrusion detection, and reinforcement learning applications in cybersecurity. Though explainability systems increase interpretability with minimal accuracy loss, the results show that graph-based RL improves intrusion detection and network traffic analysis by utilizing structural links. Nevertheless, problems including adversarial assaults, computation costs, and the trade-off between openness and performance remain. The research shows that using explainable artificial intelligence in graph-based RL IDS can significantly increase detection capabilities and user confidence, hence promoting more efficient and responsible cybersecurity solutions, future studies should concentrate on increasing the scalability, durability, and realtime applicability of explainable graph-based RL models in the field of cyber security. 

**_Keywords:_** _Explainable Artificial Intelligence; Intrusion Detection Systems (IDS); Artificial Intelligence (AI); Reinforcement Learning (RL); Cybersecurity; Explainable Graph_ 

Received: August 02, 2025 

1161 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

# **Introduction** 

As cyber-attacks have grown in complexity and frequency, cyber security has emerged as a major concern in the modern digital landscape. Often inadequate against advanced persistent threats (APTs), polymorphic malware and zero-day vulnerabilities [1, 2], conventional security measures like firewalls and antivirus software fall short. By way of network traffic monitoring, identification of hostile activities, and alerting of security staff of potential hazards, IDS are a vital defensive tool. Notable disadvantages of conventional IDS techniques, including signature-based and anomaly-based detection, exist [2, 3]. While anomaly-based Intrusion Detection Systems generate higher false positive rates because of their reliance on deviations from normal traffic patterns, Signature-based Intrusion Detection Systems rely on established attack patterns, hence rendering them worthless against new threats [3, 4]. Attacks' complexity drives the need for sophisticated detection techniques able to dynamically adapt to new threats while maintaining accuracy and efficiency [4]. Without rule sets, RL is a potent cybersecurity tool since it can learn and adjust to fresh attack patterns. Reinforcement learning-based intrusion detection systems can identify and mitigate threats by treating network security as a sequential decision-making problem [5, 6]. Graphical models of network traffic can clarify structural relationships between nodes and identify uncommon interactions faster than flatfeature models [7, 8]. Combining graph neural networks (GNNs) with RL increases attack detection by leveraging network data spatial and temporal correlations. Though they have promise, artificial intelligence-driven intrusion detection systems lack transparency. Many deep learning-based security systems run as "black boxes," which makes it challenging for cybersecurity experts to know, assess, and depend on their choices [9]. By providing humaninterpretable insights into IDS decisions, XAI helps to close this gap by increasing confidence and supporting regulatory compliance. The figure 1 illustrates the trade-off in AI/XAI-based cybersecurity between three key aspects. 

This review article aims to investigate the integration of explainable artificial intelligence into graph-based reinforcement learning models for intrusion detection, hence assessing their effectiveness in modelling network traffic, improving detection accuracy, and guaranteeing decision transparency. The paper is structured as follows: Beginning with a presentation of conventional Intrusion Detection Systems (IDS) and their related problems, the paper then thoroughly examines graph-based learning and reinforcement learning in the framework of cybersecurity. Then, it evaluates performance and trust elements and studies explainability techniques in AI-driven Intrusion Detection Systems. The report points out research gaps and offers next paths to enhance the usability of explainable graph-based reinforcement learning models in cybersecurity. 

Received: August 02, 2025 

1162 



<!-- Start of picture text -->
Trustworthiness Intelligence<br>(HumanInteroperableCyberDecision) AUXAIWade-OnbasedDecision-makingExtractedbasedInsights) on<br>cyber<br>Security<br>Automation<br>(Reducing Manuat Efforts<br>with Setf-learning<br><!-- End of picture text -->



<!-- Start of picture text -->
Preprocessing GNN Embedding Detection& Training<br>Graph construction Nodelodge embedding projection Malicioushost detection<br>eanmae toa 4 * " » 8 tating.<br>eee ” é iain hy s 5<br>Meta-paths ” o-’ i= te 4. ¥<br>MP) a oa Ay ve<br>«Proce + fork -+ Procome nm) shite, 5<br>MD,: Process -+ rund -+ File -+ read! -+ Proce a ane J hpey) Se,<br>Node/edge-level preprocessing @% n *ee ; -— * Pynknyaonre)<br>® ° @ re ee<br>di o Training<br>be A lees naa Unepervanteee tnesliibandaniadlw= heats: fyWarrenrecmneructenertyenon0eereyoperater<br><!-- End of picture text -->



<!-- Start of picture text -->
Intrusion detection Agent training<br>Agent (agent) module<br><a Reinforcement<br>Preprocessing |__| Learning ><br>Module Module<br><!-- End of picture text -->

**International Journal of Applied Mathematics** 

**Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

By choosing actions depending on the existing network sate St (represented by the graph embedding), the RL agent is charged with dynamically identifying threats. To maximize long -term rewards, the agent discovers an optimal strategy, π^* (a|S_t ). Which is 

π<sup>∗</sup> (a|St) to maximize the long -term rewards. Where: 

"π<sup>∗</sup> (a|St) = argπ max E [Rt|St, π]" ------------------------------------- Eq (2) 

Furthermore, reinforcement learning-driven adaptive defensive mechanisms improve intrusion detection system effectiveness by dynamically modifying detection thresholds, revising security policies, and implementing countermeasures according to the intensity of an assault. Nonetheless, implementing reinforcement learning in cybersecurity entails problems like training complexity, processing demands, exploration-exploitation dilemmas, and adversary interference [15]. Despite these difficulties, RL-based IDS can improve real-time threat mitigation, network resilience, and security concerns in modern cybersecurity systems. 

# **Explainability in Ai-Driven Intrusion Detection** 

AI-driven intrusion detection must be explainable to improve cybersecurity decision-making transparency, reliability, and interpretability. Cybersecurity specialists struggle to understand warning triggers as AI-driven intrusion detection systems (IDS) get more complex. Their decision-making procedures typically resemble black-box models. Insufficient interpretability can lead to false positives, missed threats, and regulatory compliance issues [16]. Explainability helps security analysts validate threat classes, investigate warnings, and develop detection models to improve network security by revealing model behaviour. 

Two primary techniques for explainability are post-hoc and intrinsic. Post-hoc explainability techniques such as SHAP and LIME retrospectively assess model forecasts. While LIME approximates complex models with simpler, understandable models to clarify local decisionmaking, SHAP assigns relevance scores to input features highlighting their impact on categorization. Moreover, deep learning model attention mechanisms highlight important input areas affecting an IDS choice, thereby improving analyst interpretation [16, 17]. These approaches allow specialists in cybersecurity to verify, diagnose, and improve AI-driven Intrusion Detection Systems, hence ensuring that the responses are clear and accurate. 

The increasing fascination in Explainable artificial intelligence (XAI) arises from the need to render machine learning models more open. XAI techniques like LIME (Local Interpretable Model-agnostic Explanations) and SHAP (SHapley Additive exPlanations) provide ways to understand the forecasts of black-box models. XAI can enable security analysts to know why a particular action was taken in the framework of RL-based IDS, hence fostering confidence in the system. SHAP uses the Shapley value defined as: 



Received: August 02, 2025 

1166 

**International Journal of Applied Mathematics** 

**Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

Where, 

∅i(f) – It is the Shapley value for feature i, 

S – It is a subset of the features excluding i, 

N - It is the set of all features, 

Techniques like SHAP are included in XAI to clarify the choices of the RL agent. For every choice, the algorithm calculates feature importance ratings indicating which elements—such network characteristics—most influenced the identification of harmful activity. 



On the other hand, models especially in graph-based and RL-driven IDS include natural intrinsic explainability. Presenting a natural framework for intrusion detection, GNNs capture relational interdependence across network nodes and edges and provide understandable insights on connection strength and node relevance. RL models can also be designed with explained reward functions, boosting the transparency of their decision-making processes [17]. Still, often explainability means sacrificing precision and economy. While very accurate deep learning models lack openness, more understandable models could sacrifice performance. The evolution of AI-driven Intrusion Detections Systems that are both successful and responsible in cybersecurity defense depends on finding balance among detection accuracy”, computation efficiency, and interpretability. 

# **Integration of Graph-Based Learning with Reinforcement Learning for ids:** 

Combining graph-based learning with RL for IDS creates a novel approach for adaptive threat mitigation and real-time attack identification. With nodes signifying devices, edges expressing connections, and relational dependencies showing behavioural patterns, GNNs shine at describing complex network topologies. The result is a more dynamic and context-sensitive intrusion detection system competent of proactively reducing incursions when combined with reinforcement learning, which continuously learns and adapts to new threats. Using GNNs to produce sophisticated graph representations of network traffic and including these representations into RL-based decision models allows IDS to dynamically change detection rules, forecast hostile behaviours, and improve countermeasures in real time. GNNs' messagepassing mechanism modifies node characteristics depending on their neighbours: 



Where, 

(k) th hv – It is the feature vector of node v adter k interation (or layer), 

W<sup>(k)</sup> – It is the weight matrix for layer k, 

N(v) – It represents the neigbbours of node v, 

Received: August 02, 2025 

1167 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

hk−1u −It is the feature vector of neighbor u from the previous layer, 

σ  -It is the activation funciton (e.g., ReLU) 

b<sup>(k)</sup> - It is the bias term for layer k, 

As defined by, the GNN updates node features depending on nearby node information by means of message passing between nodes. 



Where, 

- (k) 

- hv – It is the updated feature vector of node v layer k 

W<sup>(k)</sup> and b<sup>(k)</sup> - They are the trainable weight and bias matrices 

N(v  It represents the neighbors of node v 

Graph-based RL enables intelligent network traffic monitoring and adaptive threat mitigation by means of the  conceptualizing of intrusion detection as a sequential decision-making problem. Using relational data, the IDS agent monitors the network graph, finds anomalies, and computes suitable countermeasures by means of trial and error learning. Reinforcement learning methods, especially deep Q-networks (DQNs) and policy-gradient approaches, may enhance defence measures by means of network state transition analysis. Ensuring that security rules can change in reaction to new threats helps to achieve this. Graph embedding's use in reinforcement learning improves the generalization ability of the model, which thus allows intrusion detection systems to identify new attacks more efficiently than is feasible with conventional signature-based approaches [18]. Though it offers certain benefits, the combination of GNNs with RL raises several issues. The notable computational complexity is a major issue since both graph-based learning and reinforcement learning need a great deal of resources for training and inference. 

Moreover, keeping large networks made up of millions of nodes and edges causes scale problems that render real-time analysis a resource-consuming task. Reward engineering—the design of an acceptable reward function for intrusion detection—is a major difficulty. This function has to balance system performance, false positive rates, and detection accuracy [18]. Finally, adversarial assaults on graph topologies and reinforcement learning rules create a security concern and call for strong defenses to prevent model exploitation. Facing these obstacles is essential to completely exploit the possibilities of graph-based reinforcement learning for the creation of solutions for next-generation intrusion detection systems. 

# **METHODOLOGY AND COMPARATIVE ANALYSIS OF VARIOUS STUDIES** 

This table now offers exact accuracy rates as cited in the study, so enabling a more obvious comparison of the effectiveness of several approaches. **Table 1.** Comparative Analysis 

Received: August 02, 2025 

1168 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

|**References**|**Methodology**|**Findings**|**Limitations**|
|---|---|---|---|
||||Limited<br>to<br>WiFi|
|Thang<br>&<br>Pashchenko<br>(2019)|Multistage<br>ML-<br>based<br>IDS<br>for<br>WiFi networks|Achieved**98.9% detection**<br>**accuracy**<br>for<br>WiFi<br>intrusions|networks;<br>lacks<br>adaptability<br>to<br>emerging<br>attack<br>patterns|
|Palmer,<br>Rogers<br>&<br>Mcfly (2020)|Graph-based<br>study of industrial<br>control<br>system<br>(ICS)<br>network<br>traffic|Detected<br>**88.2%**<br>of<br>anomalous behaviours in<br>ICS networks|Lacks<br>real-time<br>detection capabilities|
|Abou Daya et<br>al.,  (2020)|ML-based graph-<br>based<br>bot<br>detection<br>(BotChase)|Identified botnet (Botchase)<br>activities<br>with<br>**99%**<br>**accuracy**|Large-scale networks'<br>high<br>computational<br>cost|
|Neupane et al.,<br>(2022)|Survey<br>on<br>explainable<br>IDS<br>(X-IDS)|Provided<br>a<br>comparative<br>analysis of existing XAI<br>methods; noted that most<br>models<br>maintain<br>explainability at the cost of<br>**5-10% accuracy drop**|No<br>empirical<br>validation of proposed<br>methodologies|
|Baahmed et al.<br>(2023)|GNN for intrusion<br>detection method<br>and<br>the<br>explanation|GNN-based IDS achieved<br>**99.54%**<br>**accuracy**<br>with<br>improved interpretability|Model interpretability<br>and<br>explainability<br>trade-offs<br>remain<br>a<br>challenge|
|Lo (2023)|Graph<br>representation<br>learning<br>for<br>cyberattack<br>detection|Enhanced forensic analysis<br>and<br>attack<br>attribution;<br>increased detection rate to<br>**99.54%**|Requires large datasets<br>for effective learning|
|Kaya et al.<br>(2024)|X-CBA:<br>Explainability-<br>aided<br>CatBoost<br>model for IDS|Achieved**99.47% detection**<br>**accuracy**,<br>improving<br>interpretability in decision-<br>making|Explainability<br>performance<br>in<br>complex cyberattacks<br>not fully assessed|
|Adhikari<br>&<br>Thapaliya<br>(2024)|Explainable<br>AI<br>(XAI) models for<br>malware<br>and|XAI-based<br>models<br>improved<br>interpretability|Focuses on theoretical<br>concepts rather than<br>real-world deployment|



Received: August 02, 2025 

1169 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

||intrusion<br>detection|while<br>maintaining<br>**80%**<br>**accuracy**||
|---|---|---|---|
|Farrukh et al.<br>(2024)|Xg-NID:<br>Heterogeneous<br>graph<br>neural<br>network<br>with<br>LLM for IDS|Demonstrated<br>**97.2%**<br>**detection**<br>**accuracy**<br>by<br>integrating multimodal data|High<br>computational<br>complexity for large-<br>scale deployment|
|Shokouhinejad<br>et al. (2025)|Graph<br>learning<br>and<br>XAI<br>for<br>malware<br>detection|Combined graph learning<br>and<br>explainability,<br>achieving<br>around<br>**94%**<br>**classification**<br>**accuracy.**<br>Graph<br>reduction<br>and<br>embedding techniques have<br>tackled<br>issues<br>with<br>scalability and efficiency,<br>whilst<br>explainability has<br>connected high detection<br>accuracy with actionable<br>insights.|Trade-off<br>between<br>detection performance<br>and explainability|
|Kalutharage et<br>al. (2025)|The combination<br>of neurosymbolic<br>learning<br>and<br>domain<br>knowledge-<br>driven<br>explainable<br>artificial<br>intelligence<br>for<br>Internet of Things<br>attack<br>detection<br>and response|Achieved**97.1% detection**<br>**accuracy**,<br>improving<br>interpretability and response<br>efficiency in IoT networks|Increased<br>computational<br>complexity<br>and<br>dependency on high-<br>quality<br>domain<br>knowledge<br>for<br>effective reasoning|
|Ahanger et al.<br>(2025)|Graph Attention<br>Networks (GAT)<br>for IoT intrusion<br>detection|Achieved**99% accuracy**in<br>detecting<br>IoT-based<br>intrusions|High<br>memory<br>consumption<br>and<br>computational<br>overhead in large-scale<br>IoT environments|
|Ahmed et al.,<br>(2025)|Signature-based<br>intrusion<br>detection system|Improved<br>precision<br>and<br>recall for attack detection,|Due to the reliance on<br>signature-based<br>approaches, there is|



Received: August 02, 2025 

1170 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

||that makes use of<br>machine learning,<br>deep learning, and<br>fuzzy clustering|with<br>**96.5%**<br>**detection**<br>**accuracy**|limited generalization<br>to attacks that have not<br>yet been seen.|
|---|---|---|---|
|Kumar et al.,<br>(2025)|Modified Graph<br>Neural<br>Network<br>(GNN)<br>with<br>Explainable<br>AI<br>(XAI) for multi-<br>class<br>malware<br>detection|Enhanced<br>classification<br>accuracy<br>to<br>improving<br>malware categorization and<br>explainability|Model complexity may<br>hinder<br>real-time<br>detection capabilities|
|Wazid et al.<br>(2025)|Explainable deep<br>learning for IoT-<br>enabled<br>Intelligent<br>Transportation<br>Systems<br>(ITS)<br>malware<br>detection|Achieved**99.7% detection**<br>**accuracy**, improving threat<br>detection<br>in<br>smart<br>transportation|Model<br>robustness<br>against<br>adversarial<br>attacks<br>remains<br>a<br>challenge|



A varied range of machine algorithms can be used for analysis and their applications for vulnerability analysis and threat identification is performed and their performance are evaluated based on the parameters shown in the table (2). 

**Table 2.** Matrix for Performance Analysis 

|**Metric**|**Description**|
|---|---|
|**Accuracy**|Percentage of correctly identified intrusion vs. benign traffic.|
|**Precision**|Proportion of actual intrusions among those predicted as intrusions.<br>Reduces false positives.|
|**Recall**<br>**(Sensitivity)**|Proportion of actual intrusions that were correctly identified. Reduces false<br>negatives.|
|**F1-Score**|Harmonic mean of precision and recall, balancing both for imbalanced<br>datasets.|
|**Detection**<br>**Time**|Average time in milliseconds taken to detect an intrusion event.|
|**Explainability**<br>**Score**|A subjective or model-derived score (e.g., SHAP values, rule extraction<br>quality) on how well the model decisions can be understood by humans.|



Received: August 02, 2025 

1171 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

The different algorithms used are CNN, RNN, XGBoost, GNN, and EGL, their characterise such as, Local Reputation Field, Conventional Layers, Layer Stacking, Pooling Layers, Activation Functions, Fully Connected Layer and End-to-End Learning for the detection of security vulnerabilities is presented in the table (3). 

**Table 3.** Matrix for Performance Analysis 

|**Mo**<br>**del**|**Local**<br>**Reputati**<br>**on field**|**Conventiona**<br>**l Layers**|**Layer**<br>**Stacking**|**Pooling**<br>**Layer**|**Activ**<br>**ation**<br>**Func**<br>**tions**|**Fully**<br>**Connec**<br>**ted**<br>**Layer**|**End-to-**<br>**End**<br>**Learning**|
|---|---|---|---|---|---|---|---|
|**CN**<br>**N**|Capture<br>spatial<br>patterns<br>and<br>minimize<br>computed<br>cost<br>and<br>over<br>fitting<br>ya,b<br>= ∑∑w<br>k=1<br>j=0<br>k=1<br>i=0<br>xa+ i. b<br>+ j<br>Detection<br>of<br>port<br>scanning,<br>DDOS, or<br>brute<br>force<br>attacks|<br>Multiple<br>learnable<br>filters in each<br>layer<br>Conv(k)<br>= F × k + b<br>Detect SYN<br>flood pattern|Hierarchi<br>cal<br>representa<br>tion able<br>to capture<br>simple<br>and<br>abstract<br>h<sup>l+1</sup><br>= σ(w<sup>(l)</sup><br>× h<sup>(l)</sup><br>+b<sup>(l)</sup><br>Able<br>to<br>detect<br>advanced<br>attacks<br>such<br>as<br>APTs|Minimize<br>sthe spatial<br>dimension<br>which<br>reduces the<br>number of<br>parameters<br>hi,j<br>= max {xm,n<br>m, n<br>∈window(i<br>Make the<br>IDS robust<br>to<br>noise<br>and<br>temporal<br>shift|Learn<br>comp<br>lex<br>patter<br>ns<br>using<br>non-<br>linear<br>activa<br>tion<br>functi<br>on.<br>ReL<br>U,<br>Leak<br>y<br>ReL<br>U,<br>ELU.<br>σ(x)<br>= max<br>In<br>anom<br>aly<br>detect<br>ion|Toward<br>s<br>the<br>end<br>a<br>fully<br>connect<br>ed layer<br>helps<br>better<br>predicti<br>on<br>y<br>= σ(Wx<br>+ b)<br>Intrusio<br>n<br>detectio<br>n|Gradient<br>descent<br>and<br>back<br>propagatio<br>n<br>and<br>minimize<br>the<br>loss<br>function.<br>L =<br>−∑yilog (<br>N<br>i=1<br>Detection<br>of<br>any<br>evolving<br>threats|
|**RN**<br>**N**|Each<br>RNN unit|Provide<br>recent|Use<br>of<br>multi-|Focus<br>on<br>most|Funct<br>ions|Maps<br>hidden|Entire<br>model|



Received: August 02, 2025 

1172 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

||processes<br>input<br>at<br>time<br>t<br>with<br>hidden<br>state.<br>ht<br>= f(ht−1, xt)<br>It is able<br>to detect<br>the login<br>failures or<br>burst<br>or<br>increased<br>traffic|features with<br>RNN, LSTM,<br>GRU<br>zt<br>= Conv1D(xt)<br>HTTP based<br>attacks, brute<br>force|layer<br>RNN<br>ht<br>(l)<br>= f(ht−1<br>(l) , hf<br>l<br>Detect<br>complex<br>attack<br>challenge<br>s such as<br>APT|relevant<br>time steps.<br>hpool<br>=<br>(ht)<br>t<br>max<br>Privilege<br>escalation<br>attack|such<br>as<br>tanh,<br>ReL<br>U or<br>sigm<br>oid at<br>each<br>stage<br>tanh(k<br>=<sup>ex −</sup><br>e<sup>x </sup>+<br>ReLU<br>= max<br>σ(x)<br>=<br>1<br>1 +<br>Ano<br>maly<br>detect<br>ion|e<br>state to<br>find<br>predicti<br>on<br>output<br>y<br>= softma<br>+ b)<br>Classifi<br>es input<br>sequenc<br>e<br>as<br>malicio<br>us<br>or<br>benign.|<br>trained<br>using<br>BPTT<br>on<br>labelled<br>sequence<br>data.<br>L<br>= −∑yilo<br>N<br>i=1<br>Detection<br>of new or<br>evolving<br>threats|
|---|---|---|---|---|---|---|---|
|**X**<br>**GB**<br>**oos**<br>**t**|Decision<br>trees learn<br>splits<br>on<br>local<br>features<br>selection<br>Feature Im<br>= ∑∑<br>splitϵt<br>T<br>t=1<br>∆Lossis<br>the<br>reductio<br>in loss due|A group of<br>decision tree<br>series|Sequentia<br>l boosting<br>yj<br>= ∑ft(xi)<br>T<br>t=1<br>Where F<br>space<br>regression<br>trees|Aggregatio<br>n via tree<br>ensemble|Step-<br>wise<br>outpu<br>t<br>at<br>leave,<br>no<br>expli<br>cit<br>activa<br>tion<br>like<br>ReL<br>U/tan<br>h|Final<br>output<br>for<br>labeling|Gradient<br>boosting<br>on<br>structured<br>loss<br>L∅<br>= ∑l(yi, yi<br>n<br>i=1<br>+ ∑Ω(ft)<br>T<br>t=1|



Received: August 02, 2025 

1173 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

||to<br>that||||f(x)||Learning|
|---|---|---|---|---|---|---|---|
||split<br>Detect the<br>login<br>attempt<br>threshold|Capture nulti-<br>feature attack<br>patter|Privilege<br>escalation|Anomaly<br>detection|= ∑<br>J<br>j=1<br>Decid<br>e<br>input<br>featur<br>es are<br>malic<br>ious<br>or<br>benig<br>n.|W<br>Intrusio<br>n<br>detectio<br>n:<br>normal<br>or DoS|from<br>log<br>data|
|**G**<br>**NN**|Neighbor<br>hood<br>aggregati<br>on within<br>k-map<br>hv<br>(k)<br>= AGG(N(v<br>Detect<br>localized<br>attack<br>behaviour|<br>Message<br>passing<br>account,<br>graph edges.<br>H<sup>(l+1)</sup><br>= σ(AH<sup>(l)</sup>W<sup>(l)</sup><br>Learning<br>from<br>structured<br>dependencies<br>such as attack<br>trees.|Stacked<br>layers for<br>multi-hop<br>dependen<br>cy<br>learning<br>hv<br>(k)<br>= GNNLaye<br>{hu<br>(k−1)|uϵN<br>Detect<br>multistage<br>or stealthy<br>attacks<br>across<br>layers|<br><br>Graph<br>level<br>readout or<br>node<br>subsampli<br>ng<br>hG<br>= <sup>1</sup><br>|v|<br>∑hv<br>vϵv|Non-<br>linear<br>ity<br>each<br>layer<br>σ(x)<br>= ReL<br>Com<br>plex<br>mode<br>of<br>threat<br>activi<br>ties|U<br>Maps<br>graph/n<br>ode<br>embedd<br>ing<br>to<br>outputs.<br>y<br>= softma<br>+ bf)<br>Classifi<br>es each<br>node/gr<br>aph<br>as<br>benign<br>or<br>malicio<br>us.|<br>Learn<br>graph<br>feature via<br>back<br>propagatio<br>n<br>∑<br>Cross<br>vϵvtrain<br>Detection<br>of intrusion<br>form<br>topology|
|**EG**<br>**L**|Graph<br>convoluti<br>on layers<br>cumulativ<br>e<br>characteri<br>stics from<br>neighbour|Graph<br>convolution<br>layers<br>cumulative<br>characteristic<br>s<br>from<br>neighbours in<br>the<br>graph,|Stacking<br>multiple<br>GNN<br>layers<br>allows<br>learning<br>from<br>multi-hop|Graph<br>pooling<br>reduces the<br>graph size<br>by<br>summarizi<br>ng<br>node<br>informatio|Non-<br>linear<br>transf<br>ormat<br>ions<br>appli<br>ed<br>after|After<br>graph<br>embedd<br>ing, FC<br>layers<br>are used<br>for<br>classific|All<br>component<br>s<br>are<br>trained<br>together<br>using<br>a|



Received: August 02, 2025 

1174 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 



<!-- Start of picture text -->
s in the  similar  to  neighbour n, akin to  each  ation or  unified loss<br>graph,  how  CNNs  hoods.  max/avg  graph  regressi function.<br>similar to how  convolve over  image  hlv pooling in CNNs.  layer.  on tasks.  L =<br>= GNNLaye σ(x) LPred +λ<br>CNNs  patches.<br>S (l) = ReLUŷ  Lexpl<br>convolve<br>over  h(k)v = softmax(G = softma LPred<br>+ b)<br>image  = σ( = Prediction<br>∑soft<br>patches.  uϵN(v) L<br>expl<br>h(k)v = = Explanati<br>Final<br>σ(∑uϵN(v) α λ<br>Enabl<br>classific<br>)  =Regulariz<br>es  ation<br>ation<br>Detects<br>Captures  comp<br>(attack<br>Graph- weight<br>local  contextual  lex<br>Models  level  type,<br>anomalies node  multi-hop  intrusion  patter anomal<br>,  peer  behaviours  n<br>attack  y score)  Improves<br>summary<br>behaviour  discri<br>behaviour accuracy<br>minat<br>s  and<br>ion<br>explainabil<br>ity  of<br>detections<br><!-- End of picture text -->

The performance comparison using a test dataset from the public source is shown in the table (4) with their plot in the form of radar chart and graphical representation as in figure (4) and figure (5). 

**Table 4.** Performance Comparison of EGRL with Other Models in Intrusion Detection 

|Model|Accuracy<br>(%)|Precision<br>(%)|Recall<br>(%)|F1-Score<br>(%)|Detection<br>Time (ms)|Explainability<br>Score|
|---|---|---|---|---|---|---|
|EGL|96.9|95.7|97.4|97.1|120|9.1/10|
|CNN|94.1|92.3|91.9|92.0|160|3.4/10|
|RNN|91.9|90.0|90.7|90.3|180|2.8/10|
|XGBoost|94.6|94.5|94.8|94.5|140|4.7/10|
|GNN|95.6|93.7|96.1|94.9|130|5.2/10|



Received: August 02, 2025 

1175 



<!-- Start of picture text -->
Performance Analysis RadarAccuracyChart: EGRL10vs Other Models ———— FGRLModelMose!ModelBac<br>FLScd > ‘sion<br>Recall<br><!-- End of picture text -->



<!-- Start of picture text -->
= Performance Comparison of Models for Intrusion Detection<br>eo Accuracy<br>=e Precision<br>98 me+ RecallFi Score<br>96<br>94<br>z<br>§<br>a 2<br>90<br>88<br>86<br>EGRE CNN RNN XGBoost GNN<br><!-- End of picture text -->

**International Journal of Applied Mathematics** 

**Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

research gaps will necessitate the development of novel graph-learning frameworks, upgrades to reinforcement learning, and improved interpretability methodologies for the purpose of enhancing user trust and system usability. 

# **Future Scope** 

Future study ought to concentrate on enhancing graph-based network traffic monitoring through the development of scalable and real-time graph processing methodologies to manage extensive, dynamic environments. Improving dynamic learning and adaptation by selflearning, continually developing IDS models will enhance detection accuracy for emerging threats. Incorporating explainability techniques like SHAP, LIME, and attention mechanisms into graph-based learning would improve transparency, assisting cybersecurity professionals in comprehending AI-generated conclusions. Moreover, standardized evaluation frameworks must be established to systematically evaluate the trade-off between IDS performance and explainability, hence providing trustworthy benchmarking. Ultimately, cultivating trust and usability necessitates human-in-the-loop methodologies, wherein cybersecurity specialists engage with AI-driven Intrusion Detection Systems to authenticate warnings, enhance detection models, and augment reliability. By focusing on these aspects, future Intrusion Detection Systems will enhance adaptability, interpretability, and user-friendliness, hence assuring resilient real-time cybersecurity protections within intricate network infrastructures. 

# **Acknowledgement** 

The authors extend the gratitude to Cyber Security Centre of excellence at Alliance University for supporting the completion of the research work. 

# **References** 

1. Thapa, S., & Mailewa, A. (2020, April). The role of intrusion detection/prevention systems in modern computer networks: A review. In Conference: Midwest Instruction and Computing Symposium (MICS) (Vol. 53, pp. 1-14). 

2. Khraisat, A., Gondal, I., Vamplew, P., & Kamruzzaman, J. (2019). Survey of intrusion detection systems: techniques, datasets and challenges. Cybersecurity, 2(1), 1-22. 

3. Mallick, M. A. I., & Nath, R. (2024). Navigating the cyber security landscape: A comprehensive review of cyber-attacks, emerging trends, and recent developments. World Scientific News, 190(1), 1-69. 

4. Mehta, G., Jayaram, V., Maruthavanan, D., Jayabalan, D., Parthi, A. G., Bidkar, D. M., ... & Veerapaneni, P. K. (2024). Emerging Cybersecurity Architectures and Methodologies for Modern Threat Landscapes. Journal ID, 9471, 1297. 

5. Nie, M., Chen, D., & Wang, D. (2023). Reinforcement learning on graphs: A survey. IEEE Transactions on Emerging Topics in Computational Intelligence, 7(4), 1065-1082. 

6. Devailly, F. X., Larocque, D., & Charlin, L. (2021). IG-RL: Inductive graph reinforcement learning for massive-scale traffic signal control. IEEE Transactions on Intelligent Transportation Systems, 23(7), 7496-7507. 

Received: August 02, 2025 

1177 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

7. Alwasel, B., Aldribi, A., Alreshoodi, M., Alsukayti, I. S., & Alsuhaibani, M. (2023). Leveraging graph-based representations to enhance machine learning performance in IIoT network security and attack detection. Applied Sciences, 13(13), 7774. 

8. Ren, K., Zeng, Y., Zhong, Y., Sheng, B., & Zhang, Y. (2023). MAFSIDS: a reinforcement learning-based intrusion detection model for multi-agent feature selection networks. Journal of Big Data, 10(1), 137. 

9. Sarker, I. H., Janicke, H., Mohsin, A., Gill, A., & Maglaras, L. (2024). Explainable AI for cybersecurity automation, intelligence and trustworthiness in digital twin: Methods, taxonomy, challenges and prospects. ICT Express. 

10. Sayyed, T., Kodwani, S., Dodake, K., Adhayage, M., Solanki, R. K., & Bhaladhare, P. R. B. (2023). Intrusion Detection System. Int. J. of Aquatic Science, 14(1), 288-298. 

11. Elrawy, M. F., Awad, A. I., & Hamed, H. F. (2018). Intrusion detection systems for IoT-based smart environments: a survey. Journal of Cloud Computing, 7(1), 1-20. 

12. Kheddar, H. (2024). Transformers and large language models for efficient intrusion detection systems: A comprehensive survey. arXiv preprint arXiv:2408.07583. 

13. Islam, R., Devnath, M. K., Samad, M. D., & Al Kadry, S. M. J. (2022). GGNB: Graph-based Gaussian naive Bayes intrusion detection system for CAN bus. Vehicular Communications, 33, 100442. 

14. Caville, E., Lo, W. W., Layeghy, S., & Portmann, M. (2022). Anomal-E: A self-supervised network intrusion detection system based on graph neural networks. Knowledge-based systems, 258, 110030. 

15. Dos Santos, R. R., Viegas, E. K., Santin, A. O., & Cogo, V. V. (2022). Reinforcement learning for intrusion detection: More model longness and fewer updates. IEEE Transactions on Network and Service Management, 20(2), 2040-2055. 

16. Keshk, M., Koroniotis, N., Pham, N., Moustafa, N., Turnbull, B., & Zomaya, A. Y. (2023). An explainable deep learning-enabled intrusion detection framework in IoT networks. Information Sciences, 639, 119000. 

17. Le, T. T. H., Prihatno, A. T., Oktian, Y. E., Kang, H., & Kim, H. (2023). Exploring local explanation of practical industrial AI applications: A systematic literature review. Applied Sciences, 13(9), 5809. 

18. Zhong, M., Lin, M., Zhang, C., & Xu, Z. (2024). A survey on graph neural networks for intrusion detection systems: methods, trends and challenges. Computers & Security, 103821. 

19. Thang, V. V., & Pashchenko, F. F. (2019). Multistage System‐Based Machine Learning Techniques for Intrusion Detection in WiFi Network. Journal of Computer Networks and Communications, 2019(1), 4708201. 

20. Palmer, I., Rogers, E., & Mcfly, S. (2020). A Graph-Based Analysis of Industrial Control Systems Network Traffic. 

21. Abou Daya, A., Salahuddin, M. A., Limam, N., & Boutaba, R. (2020). BotChase: Graph-based bot detection using machine learning. IEEE Transactions on Network and Service Management, 17(1), 15-29. 

Received: August 02, 2025 

1178 

**International Journal of Applied Mathematics** 

## **Volume 38 No. 4s, 2025** 

ISSN: 1311-1728 (printed version); ISSN: 1314-8060 (on-line version) 

22. Neupane, S., Ables, J., Anderson, W., Mittal, S., Rahimi, S., Banicescu, I., & Seale, M. (2022). Explainable intrusion detection systems (x-ids): A survey of current methods, challenges, and opportunities. IEEE Access, 10, 112392-112415. 

23. Baahmed, A. R. E. M., Andresini, G., Robardet, C., & Appice, A. (2023, September). Using graph neural networks for the detection and explanation of network intrusions. In Joint European Conference on Machine Learning and Knowledge Discovery in Databases (pp. 201216). Cham: Springer Nature Switzerland. 

24. Lo, W. W. (2023). Graph representation learning for cyberattack detection and forensics. 

25. Kaya, K., Ak, E., Bas, S., Canberk, B., & Oguducu, S. G. (2024, June). X-CBA: Explainability Aided CatBoosted Anomal-E for Intrusion Detection System. In ICC 2024-IEEE International Conference on Communications (pp. 2288-2293). IEEE. 

26. Adhikari, D., & Thapaliya, S. (2024). Explainable AI for Cyber Security: Interpretable Models for Malware Analysis and Network Intrusion Detection. NPRC Journal of Multidisciplinary Research, 1(9), 170-179. 

27. Farrukh, Y. A., Wali, S., Khan, I., & Bastian, N. D. (2024). Xg-nid: Dual-modality network intrusion detection using a heterogeneous graph neural network and large language model. arXiv preprint arXiv:2408.16021. 

28. Shokouhinejad, H., Razavi-Far, R., Mohammadian, H., Rabbani, M., Ansong, S., Higgins, G., & Ghorbani, A. A. (2025). Recent Advances in Malware Detection: Graph Learning and Explainability. arXiv preprint arXiv:2502.10556. 

29. Kalutharage, C. S., Liu, X., & Chrysoulas, C. (2025). Neurosymbolic learning and domain knowledge-driven explainable AI for enhanced IoT network attack detection and response. Computers & Security, 151, 104318. 

30. Ahanger, A. S., Khan, S. M., Masoodi, F., & Salau, A. O. (2025). Advanced intrusion detection in internet of things using graph attention networks. Scientific Reports, 15(1), 9831. 

31. Ahmed, U., Nazir, M., Sarwar, A., Ali, T., Aggoune, E. H. M., Shahzad, T., & Khan, M. A. (2025). Signature-based intrusion detection using machine learning and deep learning approaches empowered with fuzzy clustering. Scientific Reports, 15(1), 1726. 

32. Kumar, S., Khot, V., Bhat, S., Ghare, A., & Kapadi, R. (2025). Multi-class Malware Detection using Modified GNN and Explainable AI. Frontiers of Innovation, 126. 

33. Wazid, M., Singh, J., Pandey, C., Sherratt, R. S., Das, A. K., Giri, D., & Park, Y. (2025). Explainable Deep Learning-Enabled Malware Attack Detection for IoT-Enabled Intelligent Transportation Systems. IEEE Transactions on Intelligent Transportation Systems. 

Received: August 02, 2025 

1179 

