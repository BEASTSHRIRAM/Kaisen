



<!-- Start of picture text -->
3<br><!-- End of picture text -->



<!-- Start of picture text -->
3<br><!-- End of picture text -->

<mark>International Journal of Machine Learning Research in Cybersecurity and Artificial Intelligence</mark> 

Volume: 5    Issue no: 01    (2014) Available Online: https://ijmlrcai.com/index.php/Journal/index 



as **Random Forest, SVM, XGBoost, and Deep Learning (LSTM, CNN)** in terms of **detection accuracy, false positive rate (FPR), precision, recall, and real-time adaptability** . 

# **1. Performance Evaluation** 

The proposed GCSF was tested using multiple evaluation metrics: 

|**Model**|**Accuracy**<br>**(%)**|**Precision**<br>**(%)**|**Recall**<br>**(%)**|**F1-**<br>**Score**<br>**(%)**|**False**<br>**Positive**<br>**Rate (%)**|**Detection**<br>**Time (ms)**|
|---|---|---|---|---|---|---|
|**Random Forest**|84.7|82.1|80.5|81.3|15.2|9.4|
|**SVM**|80.3|78.4|77.1|77.7|17.5|12.1|
|**XGBoost**|87.6|85.3|84.9|85.1|12.7|8.2|
|**LSTM**|89.2|87.5|88.3|87.9|10.3|7.6|
|**CNN**|90.8|88.7|89.4|89.0|9.5|7.1|
|**Proposed GCSF**<br>**(GNN+KG)**|**95.4**|**93.8**|**94.1**|**94.0**|**6.1**|**4.8**|



From the table, the **Graph-Based Cybersecurity Framework (GCSF)** significantly outperforms 

traditional models in terms of **accuracy, precision, recall, and false positive reduction** . The **False Positive Rate (FPR) was reduced to 6.1%** , compared to **9.5% in CNN-based IDS and 15.2% in Random Forest** . The detection time was also significantly lower (4.8ms), demonstrating the real-time feasibility of graph-based IDS. 

# **2. Graph-Based Threat Intelligence Analysis** 

Unlike conventional ML-based IDS, which analyze **isolated network packets** , the **graph-based approach captures relationships between network entities** , allowing for improved **attack correlation and anomaly detection** . The knowledge graph **maps network nodes, IP addresses,** 

**Page | 39** 

<mark>International Journal of Machine Learning Research in Cybersecurity and Artificial Intelligence</mark> 

Volume: 5    Issue no: 01    (2014) Available Online: https://ijmlrcai.com/index.php/Journal/index 



**user behavior, and past attack patterns** , enhancing the system’s ability to **detect zero-day attacks and advanced persistent threats (APTs)** . 

The graph-based IDS demonstrated the following advantages: 

- **Early Threat Detection:** By analyzing network structures and edge relationships, the GCSF model detected attacks **30% faster** than traditional ML-based IDS. 

- **Improved Detection of Complex Attacks:** The model efficiently identified **lateral movement, botnet behavior, and zero-day exploits** that were often missed by signaturebased systems. 

- **Reduction in False Positives:** By utilizing **graph embeddings and node connectivity metrics** , the model significantly reduced **false alarms** , leading to **more efficient security operations** . 

# **3. Comparative Analysis of Detection of Specific Cyber Threats** 

The effectiveness of the GCSF model in detecting different types of attacks was analyzed. The results indicate superior performance in identifying **DoS, botnets, and APTs** , where traditional ML models often fail. 

|**Attack Type**|**Random**<br>**Forest**|**XGBoost CNN**|**LSTM**|**Proposed**<br>**GCSF**|
|---|---|---|---|---|
|DoS (Denial of Service)|81.3%|86.7%<br>91.2%|89.4%|**96.5%**|
|Botnet Detection|79.5%|84.3%<br>88.6%|86.8%|**94.7%**|
|Advanced Persistent Threats<br>(APT)|75.1%|80.6%<br>85.9%|84.2%|**92.8%**|
|Ransomware Detection|77.4%|82.9%<br>87.5%|85.1%|**94.2%**|
|Phishing Attack Detection|80.9%|85.1%<br>89.1%|88.3%|**95.1%**|



**Page | 40** 



<!-- Start of picture text -->
3<br><!-- End of picture text -->



<!-- Start of picture text -->
3<br><!-- End of picture text -->



<!-- Start of picture text -->
3<br><!-- End of picture text -->

