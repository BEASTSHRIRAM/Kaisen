

_Grenze International Journal of Engineering and Technology, Jan Issue_ 

# A Survey on Intrusion Detection Systems using Deep Reinforcement Learning 

Arsalan Anwar<sup>1</sup> and Dr. D.G. Jyothi<sup>2</sup> 

1Data Scientist, West Pharmaceutical Services, Bangalore, India Email: arsalan.anwar@westpharma.com 2Professor and Head, Department of AI & ML Bangalore Institute of Technology, Bangalore, India Email: dgjyothi@bit-bangalore.edu.in 

**_Abstract_ —The significant increase in cyber-attacks particularly during the COVID-19 pandemic, calls for efficient cyber security systems which help organizations detect and mitigate cyber threats. Several traditional cyber defense systems such as Intrusion Detection Systems (IDS) are in place, but the ever evolving and complex novel attacks demand advanced and selflearning systems that can adapt to detect such threats. Such autonomous systems have been implemented using modern reinforcement learning (RL) techniques. This paper presents a survey on various IDSs implemented using Deep RL methods. We cover numerous architectures and present ways by which different authors address the common issues in IDSs such as the tradeoff between accuracy and the false positive rate (FPR), high computational requirements, etc. We expect that this comprehensive survey provides the foundations for and facilitates future studies on exploring the potential of implementing robust and advanced IDSs using DRL by addressing some of the common limitations like low accuracy, high FPR & high computational requirements.** 

**_Index Terms_ — Deep Reinforcement Learning, Intrusion Detection System, Q-Learning, Deep Q Networks, Cybersecurity, NSL-KDD, AWID, CIC-IDS17, UNSW-NB15.** 

## I. INTRODUCTION 

Since the onset of the COVID-19 pandemic, when the global economy transitioned into the work from home (WFH) culture, a significant increase in cyber-attacks has been observed. These cyber-attacks are said to be caused by various internal and external factors such as negligent and incautious user actions, failures in systems & technology, and evolving cyber-attacks. While the enterprises are trying to address the internal factors by providing appropriate training to their employees, the external factors are uncontrollable. Enterprises that are aware of the quantum of damage that these attacks can have on them, understand the importance of having robust cyber security systems, especially Intrusion Detection and Prevention Systems so that they can identify the threats & mitigate the risks immediately. However, these cyberattacks & threats are constantly evolving, with 360,000 new malware signatures detected every day which calls for advanced cyber security systems in place [1]. 

Traditional intrusion prevention methods such as encryption and access control firewalls do not fully prevent the systems  from  advanced attacks [2] and it is observed that these attacks have now become dynamic which means 

> _© Grenze Scientific Society, 2023_ 

_Grenze ID: 01.GIJET.9.1.95_ 

the attacks circumvent the cyber security systems that are in place at each level of the organization. This dynamism in the attacks calls for dynamic and responsive Intrusion Detection Systems which can quickly alert unforeseen events and help organizations reduce the impact of a cyber-attack [3]. 

This dynamism can be achieved using RL. RL is a branch of machine learning where an agent learns to make decisions through trial and error. Unlike the other two branches of machine learning namely supervised and unsupervised learning, reinforcement learning uses the feedback obtained from its actions to learn from its mistakes. This feedback mechanism helps the agent to provide dynamic and sequential responses to the everevolving cyber threats. 

Through this survey, we first understand the importance of having robust and dynamic cyber security systems. We then cover IDS and its types in Section II. After that, in Section III, we understand deep reinforcement learning and the Markov Decision Process (MDP) which represents the RL problem at hand. Following that, we cover the Agent-Environment interaction and types of DRL. In section IV, we cover the various implementations of IDSs using DRL and understand various architectures used, the underlying DRL models along with their advantages and disadvantages. 

## II. INTRUSION DETECTION SYSTEM 

## _A. What is IDS?_ 

Intrusion detection elucidates identifying unauthorized use, misuse, and abuse of computer systems by both internal users and external intruders. The main function of an Intrusion Detection System (IDS) is to secure a computer system or computer network by detecting malicious attacks on a network system or host device by monitoring inbound network traffic to uncover any anomalous and abnormal behaviour [4]. These intrusions can prove to be very costly and hence Intrusion Detection Systems play an important role in early detection of intrusions, reducing the damage to the network structure or the data exchanged across the network. 

## _B. Types of IDS_ 

There are many ways to classify types of IDS in a production network. These classifications are not mutually exclusive; for instance, a network-based IDS may be using the signature-based approach to detection [4][5]. The widely classified types of IDS are: 

1) _Host-Based IDS:_ A host-based IDS (HIDS) is an IDS that generally operates within a computer, node, or device. Its main function is internal monitoring. This was the first type of intrusion detection software to have been designed, with the original target system being the mainframe computer where outside interaction was infrequent. A HIDS monitors and collects the characteristics of hosts containing sensitive information, servers running public services, and suspicious activities. For example, it can detect a malicious/ hostile program that accesses a system’s resources in a suspicious manner or discover that a program has modified the registry in a harmful way. 

2) _Network-Based IDS_ : A network-based IDS (NIDS) is usually placed along a LAN wire which differs from HIDS. NIDS attempts to discover unauthorized and malicious access to a LAN by analyzing traffic that traverses the wire to multiple hosts. There are many algorithms for detecting malicious traffic, but they generally read inbound and outgoing packets and search for any suspicious patterns. Any alert generated by a NIDS allows it to notify administrators or take active actions such as blocking the source IP address. 

3) _Anomaly-based IDS:_ Anomaly-based IDS (AIDS) works by identifying patterns from users or groups of users already defined. The detection system utilizes machine learning to recognize a normalized baseline which represents how the system normally behaves, and then all network activity is compared to that baseline. Then anomaly-based IDS simply identifies any abnormal behavior to trigger alerts. 

4) _Signature-based IDS:_ Signature-based IDS (SIDS) is typically best used for identifying known threats. It operates by using a pre-programmed list of known threats and their indicators of compromise (IOCs). An IOC might be a specific behavior or signature that generally precedes a malicious network attack, known byte sequences, file hashes, malicious domains, etc. SIDS monitors the packets traversing the network and compares these packets to the database of known IOCs or attack signatures to flag any suspicious behavior 

## III. DEEP REINFORCEMENT LEARNING 

## _A. What is Deep Reinforcement Learning?_ 

Deep reinforcement learning (DRL) combines Reinforcement Learning (RL) with Deep Learning to utilize the benefits of the latter such as its capability to handle complex, high dimensional data with minimal manual 

2322 



<!-- Start of picture text -->
Agent<br>state action<br>reward a<br>s t r, ' ‘<br>met+l<br>Environment<br><!-- End of picture text -->



<!-- Start of picture text -->
Reinforcement Learning<br>Algorithms<br>Model Based RL Model-Free RL<br>Policy Based Value Based<br><!-- End of picture text -->



<!-- Start of picture text -->
Q Table<br>‘State-Action Value<br>State st<br>Action > | >| Qvalue<br>Q-Learning<br>ON, >|i@ value Action 1<br>State DEKE >| Q value Action 2<br>~~ Ce x KER¥ * :<br>Ye -——>| Q value Action n<br>Deep Q-Learning<br><!-- End of picture text -->



<!-- Start of picture text -->
oe i CDS<br>i i newend Action<br>4 J Agent<br>i:%, HostsCd Cl :Network} Information(State)tratfic<br><!-- End of picture text -->



<!-- Start of picture text -->
1 (eS<br>acre<br>les<br><!-- End of picture text -->

- [11] J. Schulman, S. Levine, P. Abbeel, M. Jordan and P. Moritz, “Trust Region Policy Optimization,” _International Conference on Machine Learning,_ 2015, vol. 37, pp. 1889-1897 

- [12] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, “Proximal policy optimization algorithms,” _arXiv preprint_ , arXiv:1707.06347, 2017. 

- [13] C. Wu, A. Rajeswaran, Y. Duan, V. Kumar, A. M. Bayen, S. Kakade, ... and P. Abbeel, “Variance reduction for policy gradient with action dependent factorized baselines,” _arXiv preprint,_ arXiv:1803.07246, 2018 

- [14] T. P. Lillicrap, J. J. Hunt, A. Pritzel, N. Heess, T. Erez, Y. Tassa, ... and D. Wierstra, “Continuous control with deep reinforcement learning,” _arXiv preprint,_ arXiv:1509.02971, 2015. 

- [15] G. Barth-Maron, M. W. Hoffman, D. Budden, W. Dabney, D. Horgan, A. Muldal, ... and T. Lillicrap, “Distributed distributional deterministic policy gradients,” _arXiv preprint,_ arXiv:1804.08617, 2018. 

- [16] V. Mnih, A. P. Badia, M. Mirza, A. Graves, T. Lillicrap, T. Harley, ... and K. Kavukcuoglu, “Asynchronous methods for deep reinforcement learning,” in International Conference on Machine Learning, 2016, pp. 1928-1937. 

- [17] M. Jaderberg, V. Mnih, W. M. Czarnecki, T. Schaul, J. Z. Leibo, D. Silver, and K. Kavukcuoglu, “Reinforcement learning with unsupervised auxiliary tasks,” _arXiv preprint,_ arXiv:1611.05397, 2016. 

- [18] Nsl-Kdd dataset, https://www.unb.ca/cic/datasets/nsl.html, (accessed Feb. 25, 2022) 

- [19] T. T. Nguyen and V. J. Reddi, “Deep reinforcement learning for cyber security,” in _IEEE Transactions on Neural Networks and Learning Systems_ , 2021 

- [20] M. Lopez-Martin, B. Carro and A. Sanchez-Esguevillas, “Application of deep reinforcement learning to intrusion detection for supervised problems,” _Expert Systems with Applications_ , Volume 141, 2020 

- [21] Awid dataset—wireless security datasets project, http://icsdweb. aegean.gr/awid/. (accessed Mar. 22, 2022) 

- [22] K. Sethi, Y. V. Madhav, R. Kumar, P. Bera, “Attention based multi-agent intrusion detection systems using reinforcement learning,” _Journal of Information Security and Applications_ , Volume 61, 2021 

- [23] Intrusion detection evaluation dataset (Cic-Ids2017), https://www.unb.ca/cic/datasets/ids-2017.html (accessed Mar. 10, 2022) 

- [24] K. Sethi, E. S. Rupesh, R. Kumar, P. Bera and Y. V. Madhav, “A context-aware robust intrusion detection system: a reinforcement learning-based approach,” _Int. J. Inf. Secur._ 19, pp. 657–678 

- [25] The unsw-nb15 dataset description, https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFANB15Datasets/. (accessed Mar. 10, 2022) 

- [26] K. Sethi, R. Kumar, N. Prajapati and P. Bera, “Deep reinforcement learning based intrusion detection system for cloud infrastructure,” _2020 International Conference on COMmunication Systems & NETworkS (COMSNETS)_ , 2020, pp. 1-6 

- [27] V. Mnih, K. Kavukcuoglu, D. Silver, A. Graves, I. Antonoglou et. al, “Playing atari with deep reinforcement learning,” _arXiv_ , arXiv:1312.5602 

- [28] R. Blanco, J. J. Cilla, S. Briongos, P. Malagon and J. M. Moya, “Applying cost-sensitive classifiers with reinforcement learning to IDS,” _Intelligent Data Engineering and Automated Learning – IDEAL 2018_ , vol 11314, Springer 

- [29] M. Bachl, F. Meghdouri, J. Fabini and T. Zseby, “SparseIDS: learning packet sampling with reinforcement learning,” _2020 IEEE Conference on Communications and Network Security (CNS)_ , 2020, pp. 1-9. 

2328 

