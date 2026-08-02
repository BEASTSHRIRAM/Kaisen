# **Preemptive Intrusion Detection: Theoretical Framework and Real-World Measurements** 

Phuong Cao, Eric Badger, Zbigniew Kalbarczyk, Ravishankar Iyer Coordinated Science Laboratory University of Illinois at Urbana Champaign {pcao3,badger1,kalbarcz,iyer}@illinois.edu 

Adam Slagell National Center for Supercomputing Applications University of Illinois at Urbana Champaign {slagell}@illinois.edu 

## **ABSTRACT** 

This paper presents a Factor Graph based framework called AttackTagger for highly accurate and preemptive detection of attacks, i.e., before the system misuse. We use security logs on real incidents that occurred over a six-year period at the National Center for Supercomputing Applications (NCSA) to evaluate AttackTagger. Our data consist of security incidents that led to compromise of the target system, i.e., the attacks in the incidents were only identified after the fact by security analysts. AttackTagger detected 74 percent of attacks, and the majority them were detected before the system misuse. Finally, AttackTagger uncovered six hidden attacks that were not detected by intrusion detection systems during the incidents or by security analysts in post-incident forensic analysis. 

## **1. INTRODUCTION** 

Cyber-systems are enticing attack targets, since they host mission-critical services and valuable data. Cyber-attacks are often tied to leaked credentials. Millions of credentials can be bought on black markets at low cost [20]. Using stolen credentials, attackers impersonate as legitimate users, effectively bypassing traditional defenses, e.g., network firewalls. Such attacks are often discovered only in their final stages when attack payloads are delivered, e.g., authentication services are contaminated to harvest more credentials or computing infrastructure are utilized to build botnets [18]. 

Detecting such cyber-attacks in their early stages presents several challenges. Attackers leave no discernible trace, as they infiltrate a target system as legitimate users using stolen credentials. Only a partial knowledge of the attacks is available at the early stages. As a user has just logged in at the beginning of a user session, only a few attributes of the user profile are available for examination, e.g., user role or physical location of the user login. The user activities remain to be seen on the target system. Examining an individual user activity is not a sufficient basis for drawing an accurate conclusion about the user’s intention. Logging in from a remote 

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. To copy otherwise, to republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee. _HotSoS_ ’15 Urbana, IL USA Copyright 2015 ACM 978-1-4503-3376-4/15/04 http://dx.doi.org/10.1145/2746194.2746199 ...$15.00. 

location can indicate either a _legitimate_ user is logging in from outside of the regular infrastructure, or an _illegitimate_ user is logging in using stolen credentials. A framework is considered to reason about the user’s activities collectively. 

We propose the AttackTagger framework, which is built upon _Factor Graph_ , a type of probabilistic graphical model consisting of random variables and factor functions [8]. A random variable quantifies an observed user behavior or a hidden state (e.g., the user intention: benign, suspicious, or malicious). Relationships among variables are defined by discrete factor functions. A factor function _imply_ ( _A, B_ ) means _B_ is often followed by _A_ . For example, in the context of masquerade attacks, an attacker impersonates a legitimate user, e.g., by logging into the target system from the attacker’s computer using stolen credentials. In that case, the factor function means _When a user logs in from an unregistered computer (A), the user is likely to be suspicious (B)_ . Each factor does not necessarily capture entire user behaviors leading to an attack: rather, a factor only captures a part of the attack and can influence other factors. For example, _When a user is suspicious (B) and the user is downloading an executable file from an unknown remote server (C), then the user is likely to be malicious (D)_ . 

While traditional signature-based detection methods identify a specific signature of an attack, our AttackTagger framework uses factor functions to reason about stages of an attack collectively. The factor function _imply_ (B,C,D) can use the existing result of the previous factor _imply_ (A,B) to determine that a user is malicious. An entire sequence of hidden user states is jointly inferred as a whole, based on observed user behaviors and defined factors. This design allows AttackTagger to detect attacks relatively early and uncover the attacks that were undetected by security analysts. 

As a case study, our experiment uses incident data of 116 security incidents over a six-year period (2008-2013) at the National Center for Supercomputing Applications (NCSA). Each incident includes data from a number of sources: an incident report in free text format, raw logs (e.g., network flows, syslogs, and security alerts), and user profiles (e.g., a user role or user’s registered physical location). Using Factor Graph as a framework allows AttackTagger to integrate user behaviors from a variety of data sources. As a result, AttackTagger can identify most malicious users relatively early (from minutes to hours before the system is misused). All the NCSA incidents used in this study were in reality detected after the fact, i.e., after the attacker misused the system. In addition, AttackTagger identified hidden malicious users that were missed by NCSA security analysts. 

The main contributions are: 

- A novel application of Factor Graphs that integrates user behaviors from a heterogeneous data sources for preemptive intrusion detection, i.e., before the system misuse. 

- Design, implementation, and experimental evaluation on a variety of security incidents collected over a sixyear period (2008-2013). 

- Detection of six hidden malicious users that were missed by security analysts. 

## **2. A CREDENTIAL-STEALING INCIDENT** 

In this section, we describe a credential-stealing incident that occurred at NCSA and analyze the challenges of detecting such an incident promptly. 

**A credential-stealing incident (2008).** In May 2008, a sophisticated credential-stealing incident occurred at NCSA. Using a compromised user account credential (e.g., a pair of a username and a password), attackers logged into a gateway node at NCSA and injected credential-collecting code into the secure shell daemon (SSHd)<sup>1</sup> of the node. NCSA computing infrastructures were shared among hundreds of users, and many of them logged in to NCSA using the compromised gateway node. Thus, the attackers were able to collect new credentials of subsequent user logins. 

An excerpt from the raw logs of the incident is listed in Table 1. First, the attackers used the compromised credential to log into the gateway node from a remote host, i.e., a host located outside of NCSA’s computing infrastructure in the event _e_<sup>0</sup> . Second, the attackers downloaded a source code file (vm.c) with a sensitive extension (.c) in the event _e_<sup>1</sup> . A sensitive extension indicates either a source code file (e.g., .c, .sh) or an executable file (e.g., .exe). A sophisticated attacker can change the file extension to a harmless one (e.g., .jpg). But our netflow monitor can identify a mismatch between a file extension and its content by analyzing the file header (e.g., a Windows executable file always begins with the _MZP_ string because of its Portable Executable file format specification). The attackers then compiled, and escalated privilege to the root by exploiting a kernel bug (CVE-2008-0600) on the compromised node . Those actions were not captured by the monitoring systems at runtime; they were only revealed in the forensic analysis process after the incident. Thus, they were not shown in the raw logs. To harvest credentials of users logging into the compromised node, after the attackers escalated to _root_ , the attackers injected credential-collecting code into the original SSHd, forcing it to restart (which resulted in the _SIGHUP_ signal in the event _e_<sup>2</sup> ). Each raw log entry was automatically mapped to an event identifier using regular expression scripts. 

In this incident, the attackers were identified after the fact by security analysts. The collateral effect of the incident was: leaking credentials of subsequent users who logged into the compromised node and potential usage of the leaked credentials for subsequent attacks. 

**Characteristics of multi-staged attacks.** The discussed incident is an example of a multi-staged attack, in which an attack i) spans an extended amount of time, and ii) involves several steps, such as stealing or brute-force guessing of credentials, remote login, download and execution of 

1 a widely deployed authentication service of UNIX systems. 

|_Raw _|_log_|_Eve_|_nt_|
|---|---|---|---|
|`sshd:`|`Accepted <user> from <remote>`|_e_<sup>0</sup>`:`|`remote login`|
|`HTTP `|`GET vm.c (<bad-domain>.com)`|_e_<sup>1</sup>`:`<br>|`download sensitive`|
|`sshd:`|`Received SIGHUP; restarting.`|_e_<sup>2</sup>`:`|`restart sys service`|



Table 1: Example raw logs and events of an incident 

privilege escalation exploits, installation of backdoors, and periods of dormancy. On the other hand, single-staged attacks (which typically are remote exploits, such as SQL injection or exploitation of VNC servers) are usually accomplished in a single execution step in a short amount of time (in terms of minutes) to launch the attack payload (e.g., reading hashed passwords from a database). 

**Challenges of detecting multi-staged attacks.** Detecting a multi-staged attack requires identification of the states of the involved users throughout the attack. A user state can be _benign_ (when a legitimate user logs in from the remote location as a part of his/her normal activity), _suspicious_ (when an illegitimate user uses stolen credentials to log in from the remote location), or _malicious_ (when a user violates a security policy). Each observed user event can be tagged with a _user state_ . 

In the above example, the single _remote login_ event provides insufficient information to tag the corresponding user state as _malicious_ . By itself, that event does not indicate a security violation, although other single events could do so, such as modification of a system service by someone who is not a system administrator. Based solely on this event, it is more reasonable to tag its state as either _benign_ or _suspicious_ . In order to be more conclusive about how to tag the event, we need further information. For example, the existing context of the system, the user profile, and we need information from subsequent events. Therefore, the usual approach of using _per-event classifiers_ is not effective in detecting multi-staged attacks. 

To detect single-staged attacks, existing IDSes often employ _per-event classifiers_ , which use rules or signatures to identify malicious users. In our example, given the event _e_<sup>2</sup> ( _restart system service_ in Table 1), a possible tag _s_<sup>2</sup> = _benign_ could mean that the event corresponds to a maintenance activity of a benign user, e.g., the user is upgrading the SSHd to a newer version. The tag _s_<sup>2</sup> = _benign_ is plausible, because an upgrade of the SSHd often requires restarting of the current SSHd in order to load the updated binaries. 

However, _per-event classifiers_ consider each event individually and do not take advantage of knowledge of an event sequence. For example, when it is known that the previous observed event was tagged as _suspicious_ , the current event _e_<sup>2</sup> can be tagged differently in light of this knowledge. In such a case, a more likely tag _s_<sup>2</sup> = _malicious_ could indicate that the event _e_<sup>2</sup> corresponds to an unauthorized activity of an already suspicious user, who is attempting to inject malicious code into the SSHd, thus forcing it to restart. A framework is needed to reason on the user events collectively. 

## **3. PROBABILISTIC GRAPHICAL MODELS** 

In this section, we provide an overview of _Probabilistic graphical models_ (PGMs), graph-based representations of dependencies among random variables, in modeling security incidents. PGMs such as Bayesian Networks (BNs), Markov Random Fields (MRFs), and Factor Graphs (FGs) can compactly represent complex joint distributions of random variables over a high-dimensional space [8]. While BNs and MRFs have been successfully employed in a variety of do- 



<!-- Start of picture text -->
e 1 e 2 e 1 e 2 e ` 1 e 2 e 1 e 2<br>Bayesian<br>Network<br>s 1 s 2 s s 1 s 2 s 1 s 2<br>(a1) Simple Bayesian Network (SBN) (a2) Naive Bayesian Network (NBN) (a3) Complex Bayesian Network (CBN) (c3-1) Complex FG of the CBN<br>e 1 e 2 e 1 e 2 e 1 e 2 e 1 f 2 e 2<br>Markov<br>Random  f 1 f 3<br>Field<br>s 1 s 2 s s 1 s 2 s 1 s 2<br>(b1) Simple MRF (SMRF) (b2) Naive MRF (NMRF) (b3) Complex MRF (CMRF) (c3-2) Complex FG of the CMRF<br>(f1) (f2) (f3)<br>x f 1( x ) e 0 e 0 e 1 e 0 e 1 e 2<br>e 1 e 2 e 1 e 2 e 1 e 2 f 2( x, y ) f 1 f 2 f 1 f 2 f 1 f 2 f 1 f 2 f 1 f 2 f 1 f 2<br>Factor y<br>Graph f 3 f 3 f 3<br>f 3( y, z ) s 0 s 0 s 1 s 0 s 1 s 2<br>s 1 s 2 s s z<br>benign suspicious malicious<br>(c1) Simple FG (c2-2) Naive FG of the NBN (c2-1) Naive FG of the NBN (d) An example Factor Graph (f) Evolution of a factor graph and the inferred user states<br><!-- End of picture text -->

Figure 1: Illustrations of use of Bayesian Network, Markov Random Field, and Factor Graph to model security incidents. 

mains, such as medical condition diagnosis or entity extraction from text [12, 10], the use of FGs in security domains has not been explored. We found that FG is more suitable than the others for modeling security incidents, since FG can subsume both BN and MRF [8]. 

When PGMs are used to model security incidents, the random variables consist of _observed user events_ (derived from incident reports and raw logs) and _hidden user states_ associated with the events. Specifically, in the credential-stealing incident example (Table 1), we consider the sequence of the observed events _E_ = _{e_<sup>1</sup> = _download sensitive_ , _e_<sup>2</sup> = _restart system service}_ , and the sequence of the corresponding user states is _S_ = _{s_<sup>1</sup> _, s_<sup>2</sup> _}_ . Based on the observed user events, PGMs are defined to capture the dependencies among the random variables. We compare the use of BN, MRF, and FG to model the example incident as follows. 

**Bayesian Networks.** A BN is a type of probabilistic graphical model that uses a directed acyclic graphs _G_ = ( _V, E_ ) to represent causal dependencies among random variables. Each vertex _v ∈ V_ corresponds to a random variable; each directed edge _e ∈ E_ represents a causal relation between two variables, e.g., X _→_ Y means X causes Y. A simple Bayesian Network (SBN) models the dependencies of the observed events _E_ and the user states _S_ in Figure 1-a1. This model assumes that the observed events _E_ are independent and that event-state dependencies are causal relations: an event _e_<sup>_i_</sup> depends only on its user state variable _s_<sup>_i_</sup> ( _s_<sup>1</sup> _→ e_<sup>1</sup> , and _s_<sup>2</sup> _→ e_<sup>2</sup> ). Because of the independent assumption, the SBN cannot capture the dependencies of a sequence of events and the corresponding sequence of user states. An example of such dependencies is, an event _e_<sup>_i_</sup> that is not only caused by its corresponding user state _s_<sup>_i_</sup> , but also caused by a previous user state _s_<sup>_i−_1</sup> . 

In Figure 1-a2, a Naive Bayesian Network (NBN) models the dependencies of all the observed events _E_ and a single user state _s_ . NBN assumes an event is independent of others. Thus, the causal dependencies are simplified: each event _e_<sup>_i_</sup> depends only on the single user state variable _s_ (e.g., _s → e_<sup>1</sup> _, s → e_<sup>2</sup> ). NBN is not suitable for early detection of attacks, since it operates on a complete sequence of the observed events _E_ to infer the user state. To detect attacks in real-time, a detection system should determine the user state after the arrival of each new observed event (i.e., based on an incomplete set of the observed events). 

In Figure 1-a3, a more complex BN (CBN) models the sequential dependencies among a group of random variables. Consider the user states _s_<sup>1</sup> _, s_<sup>2</sup> and the observed event _e_<sup>2</sup> ; to model dependencies among the three variables, the CBN must make an assumption of the pairwise causal dependencies among the random variables ( _s_<sup>1</sup> _→ e_<sup>2</sup> _, s_<sup>1</sup> _→ s_<sup>2</sup> _, s_<sup>2</sup> _→ e_<sup>2</sup> ). The disadvantages of this CBN are as follows. Although CBN is relatively simple in this example incident, the number of pairwise dependencies among a group of variables in a CBN can grow quickly as the number of variables in the group increases. When a group involves _n_ variables, a CBN may have to define up to _n_ ( _n−_ 1) _/_ 2 pairwise dependencies in the group, making the CBN much more complex. Moreover, in some domains (e.g., natural language processing), a causal relation between a pair of variables cannot be claimed; only a non-causal relation can be assumed. That non-causal relation is discussed in more detail in the part-of-speech tagging example in the MRFs sub-section. 

The discussed BN models allow explicit representation of causal dependencies among variables, however, they become more complex as the number of variables grows. 

**Markov Random Fields.** A MRF is a type of probabilistic graphical model that uses an undirected graph _G_ = ( _V, E_ ) to represent relations among random variables. Each vertex _v ∈ V_ corresponds to a random variable; each edge _e ∈ E_ represents a relation between two variables. 

The simple Markov Random Field (SMRF) depicted in Figure 1-b1 is equivalent to the simple Bayesian Network (SBN) in Figure 1-a1. In the SMRF, the dependency between _e_<sup>1</sup> and _s_<sup>1</sup> is represented by a function _φ_ ( _e_<sup>1</sup> _, s_<sup>1</sup> ). The function _φ_ ( _e_<sup>1</sup> _, s_<sup>1</sup> ) is defined as a conditional probability function _p_ ( _e_<sup>1</sup> _|s_<sup>1</sup> ). 

Characteristics of an MRF are as follows. Let _n_ ( _v_ ) be the set of _v_ ’s neighbors, i.e., the vertices that are directly connected to _v_ by a single edge. Variables in a MRF are grouped into cliques, in which all variables within each clique must be pairwise connected. A clique is a maximal clique if it cannot be extended by addition of an adjacent variable. 

A complex joint probability function (pdf) of variables in an MRF can be factorized into a product of simpler local functions, defined on the set of maximal cliques in the MRF. Each local function corresponds to a clique and describes relations of its variables. The factorization simplifies representation and computation of MRFs. 

MRFs are used in domains where variable relations are non-causal, e.g., it is natural to indicate that X correlates with Y, rather than say X causes Y [10]. For example, in part of speech (POS) tagging, a word (an observed variable) is often tagged with a part of speech (a hidden variable), e.g., noun or verb, based on the word itself and its context. Depending on the context ( _my research_ or _I research_ ), the word _research_ can be correlated with different parts of speech. In this example, the relation between the observed word (research) and its part of speech is non-causal. 

When the variable dependencies are simple, e.g., dependencies among a group of two or three variables, an MRF can be used as an alternative to a BN. Figure 1-b1 and Figure 1-b2 depict an MRF model’s equivalent to the BN models in Figures 1-a1,a2, where the directed edges in the BNs have been replaced with the undirected edges. An MRF does not make any assumptions on the causal relation among the variables. An arbitrary function can be used to define the relation among the variables. 

In our example, an event (an observed variable) and a user state (a hidden variable) can have a non-causal relation. For example, when a user logs in remotely, it is usually that the user is traveling (i.e., the user state is benign), not because an attacker is impersonating the user with a stolen user credential (i.e., the user state is malicious). 

An MRF model (Figure 1-b3) illustrates non-causal dependencies among the events and the user states. Consider a group of variables _s_<sup>1</sup> _, s_<sup>2</sup> _, e_<sup>2</sup> , they can have the following cliques: the two-variable cliques _e_<sup>2</sup> _, s_<sup>2</sup> (represented by a dotted line), and the three-variable clique _e_<sup>2</sup> _, s_<sup>1</sup> _, s_<sup>2</sup> . In the cliques, one can define either the local functions of an event and the corresponding user state (e.g., _φ_ ( _e_ 2 _, s_ 2)), or the local functions of an event, the corresponding user state, and the previous user state (e.g., _φ_ ( _e_ 2 _, s_ 1 _, s_ 2)). 

In the example MRF, the function of a clique simplifies the representation of the MRF compared to the equivalent representation in a BN. For example, the clique _e_ 2 _, s_ 1 _, s_ 2 in the MRF (Figure 1-b3) simply uses one local function to describe the relation among the three variables in the clique, instead of using three local functions (i.e., conditional probability distribution function) to describe the three pair-wise causal dependencies in the equivalent BN model (Figure 1- a3). Despite the simpler representation in MRFs, a practitioner can still model complex dependencies by factorizing a local function into a product of smaller functions, e.g., the _φ_ ( _e_ 2 _, s_ 1 _, s_ 2) can be factorized into the three functions representing the pairwise causal dependencies between the variables in the clique. 

The advantages and disadvantages of using MRFs are as follows. In MRFs, the use of one local function per clique avoids the need to make explicit assumptions about causal dependencies among variables, as necessary in BNs. However, there is an overlap between the three-variable clique _s_<sup>1</sup> _, s_<sup>2</sup> _, e_<sup>2</sup> and the two-variable clique _s_<sup>2</sup> _, e_<sup>2</sup> that cannot be naturally expressed using MRFs, because a MRF is built upon maximal cliques. 

The above analysis suggests a common representation of both BNs and MRFs, which is Factor Graphs. 

**Factor Graphs.** A Factor Graph is a type of probabilistic graphical model that can describe complex dependencies among random variables using an undirected graph representation, specifically a bipartite graph. The bipartite graph representation consists of variable nodes represent- 

ing random variables, factor nodes representing local functions (or factor functions), and edges connecting the two types of nodes. Variable dependencies in a Factor Graph are expressed using a global function, which is factored into a product of local functions. 

Suppose a global function _g_ ( _x, y, z_ ) of the three variables _x, y, z_ can be factored as a product of the local functions _f_ 1 _, f_ 2 _, f_ 3 as follows: _g_ ( _x, y, z_ ) = _f_ 1( _x_ ) _f_ 2( _x, y_ ) _f_ 3( _y, z_ ). In this example, the variable nodes are _x, y, z_ ; the factor nodes are _f_ 1 _, f_ 2 _, f_ 3; and the edges are shown in Figure 1-d. 

Factor Graphs are simpler and more expressive than BNs and MRFs. In a Factor Graph, factor functions explicitly identify functional relations among variables, including causal relations (BNs) and non-causal relations (MRFs). Moreover, complex dependencies in BNs and MRFs can be subsumed using Factor Graphs [8]. A factor function can be used to represent multiple causal relations or non-causal relations. The use of factor functions can simplify a complex BN or a complex MRF by reducing the number of functional relations that have to be defined. Equivalent FG representations of BNs and MRFs are shown in Figures 1- _{_ c1, c2-1, c2-2, c3-1, and c3-2 _}_ . A detailed discussion of conversions among FGs, BNs, and MRFs can be found in [8]. FGs has led to development of effective inference algorithms (e.g., Gibbs sampling or belief propagation) [16, 8]. Since FGs offer the same representation for both BNs and MRFs, those algorithms can be used for existing BNs and MRFs when they are converted to FGs. 

In our security domain, Factor Graphs are more flexible to define different types of relations among the events to the user state compared to BNs and MRFs. Specifically, FGs can integrate sequential relation among events and external knowledge (e.g., expert knowledge or knowledge of a user profile) to their models. 

## **4. FRAMEWORK OVERVIEW** 

In this section, we provide an overview of using Factor Graphs in our framework to model the example incident described Section 2. We briefly overview steps of our framework in Figure 2. 

**Step 1: Extract user events.** User events can be extracted automatically from raw logs (using regular expression scripts) or manually from incident reports. In the example incident, the sequence of observed events was _E_ = _{e_<sup>0</sup> = _login remotely_ , _e_<sup>1</sup> = _download sensitive_ , _e_<sup>2</sup> = _restart system service}_ . The event sequence is associated with a sequence of hidden user states _S_ = _{s_<sup>0</sup> _, s_<sup>1</sup> _, s_<sup>2</sup> _}_ . 

**Step 2: Define factor functions.** A factor function defines the relations among variables. Each factor function is a discrete function that takes random variables, e.g., observed user events or hidden user states as the input, and outputs a discrete value indicating relations among the inputs. 

For example, a _Type-1_ factor function _f_ ( _e, s_ ) can be de- 

|Extract user events<br>Defne factor functions<br>Construct per-user factor graph|Extract events from raw logs (automatically)<br>or from incident reports (manually)<br>Defne functional relations among variables<br>(e.g., events, user states) using factor functions<br>Construct per-user factor graph based on user<br>events and factor functions|
|---|---|
|Infer hidden user states<br>Identify malicious users|Perform inference on per-user factor graphs to<br>determine the most probable values of the<br>sequence of user states<br>Conclude the user as malicious when the user<br>state at the time of examination is malicious|



Figure 2: Process of modeling using Factor Graphs. 

fined to imply the relation: _if e happens then s_ . Suppose we have the relation: _if a user downloads a file with a sensitive extension, then the user is suspicious_ . Here we have two variables: one event _e_ = _download sensitive_ and a state _s_ = _suspicious_ . The function _f_ ( _e, s_ ) returns 1 if _e_ = _download sensitive_ and _s_ = _suspicious_ ; it returns 0 otherwise. For example, the function _f_ 1 in Figure 1-f is defined as follows. 



Similarly, a factor function can capture the case when a system administrator restarts an SSHd, which is likely a maintenance activity. The function _f_ 2 in the Figure 1-f is as follow. 



The function _f_ 2 returns 1 when the user event is restarting a system service (i.e., SSHd in our example) and the user state is _benign_ . It returns 0 otherwise. 

To identify a user state based on the context of an event, a more complex function can involve more variables, e.g., the previous user state or the previous event. A _Type-2_ factor function _f_ ( _e_<sup>_t_</sup> _, e_<sup>_t−_1</sup> _, s_<sup>_t_</sup> _, s_<sup>_t−_1</sup> ) defines the relation among a user state _s_<sup>_t_</sup> , its previous user state _s_<sup>_t−_1</sup> , and observed events _e_<sup>_t−_1</sup> _, e_<sup>_t_</sup> . For example, the function _f_ 3 in Figure 1-f is as follows. 



The function _f_ 3 returns 1 when an already _suspicious_ user restarts a system service and the current user state is _malicious_ . Given the event _restart system service_ , it identifies the current user state in the context that the previous user state is _suspicious_ . It returns 0 otherwise. 

In this illustration, we consider only two types of factors: Type-1 factors and Type-2 factors. More factor functions can be manually defined to capture user state in the context of events and user profiles, and to integrate expert knowledge into Factor Graphs. A more formal definition and discussion of Type-1 and Type-2 factors are provided in Section 5. 

**Step 3: Construct per-user Factor Graphs.** Given a sequence of user events _E_ and a defined set of factor functions _F_ , a Factor Graph is automatically constructed for the user, namely _per-user factor graph_ . Each factor connect its corresponding user events and user states. 

Figure 1-f illustrates the _evolution_ of a per-user Factor Graph as new events are observed. When only one event is observed, the Factor Graph contains only two Type-1 factors ( _f_ 1 _, f_ 2) for the event _e_<sup>0</sup> and its corresponding state _s_<sup>0</sup> . When two events are observed, the two Type-1 factors are used to connect the new event _e_<sup>1</sup> and its corresponding state _s_<sup>1</sup> . In addition, the Factor Graph has a Type-2 factor ( _f_ 3) connecting both the events and their states: _e_<sup>0</sup> _, s_<sup>0</sup> _, e_<sup>1</sup> _, s_<sup>1</sup> . As more events are observed, the same set of defined factors ( _f_ 1 _, f_ 2 _, f_ 3) is used to connect the new events. 

**Step 4: Infer hidden user states.** Given a per-user Factor Graph (Figure 1-f), a possible sequence of user states _S_ is automatically evaluated through a summation of the weighted factor functions _F_ , _score_ ( _S|E_ ) =<sup>�</sup> _f ∈F_<sup>_wff_(</sup><sup>_cf_),</sup> where _wf_ is the weight of the factor function _f_ , and _cf_ is the set of inputs to the factor function _f_ . The sequence of user 

states that has the highest score represents the most probable sequence corresponding to the event sequence observed until that point. 

A naive approach is to iterate over possible values of the user states in the constructed Factor Graph and select the sequence of values that results in a highest score. The most probable sequence of values is _S_ = _{benign, suspicious, malicious}_ , as shown in Figure 1-f. In our model, we compute the probabilities of the user state sequences using more efficient methods (Section 5). 

**Step 5: Conclude that users are malicious.** The compromised user is automatically identified when the user state at a time of observation is _malicious_ . 

Most steps in our framework are automated, except Step-2 (defining of factor functions), which requires expert knowledge. Using our framework, security analysts can quickly examine user states to identify the transition of a user from benign to suspicious and malicious, without having to manually examine a large amount of raw logs. As a result, security analysts have more time to respond to security incidents or to increase additional monitoring of suspicious users to uncover potentially unauthorized activities. 

## **5. ATTACKTAGGER MODEL** 

In this section, we provide a generic formulation of the Factor Graph model for incident modeling and detection. **Preliminaries.** Consider a _user u_ of a target system. The user is characterized by a _user profile U_ , which is a vector of _user attributes_ . Examples of the user attributes are shown in Table 3. _U_ does not change during usage of the target system. In order to capture the user activities in the target system, monitors are deployed at various system and network levels to collect raw logs. At runtime, each log entry is automatically converted to a discrete _event e_ . An _event e_<sup>_t_</sup> indicates an important activity in the target system (e.g., restart of a system service), or an alert on a suspicious activity (e.g., download of a file with a sensitive extension). The set of events E (Table 3) is system-specific and is predefined based on: the capabilities of the monitoring tools (e.g., IDS alerts) and expert knowledge of the target system. 

A _user session_ is a sequence of _user events E_<sup>_t_</sup> = _{e_<sup>1</sup> _. . . e_<sup>_t_</sup> _}_ from the time when user started using the target system until the observation time _t_ . 

A _user state s_<sup>_t_</sup> _∈_ S = _{_ benign, suspicious, malicious _}_ is a hidden variable whose value determines the suspiciousness of the user. The initial user state is determined based on the user profile. A user is _benign_ when no security event (e.g., a policy-violation event or an alert) has been observed for the user and the user profile is clean of suspicions. For example, the initial user state is _benign_ if the user has just logged in and the user account has not been compromised in the past. As the user proceeds, each user state _s_<sup>_i_</sup> is associated with the arriving event _e_<sup>_i_</sup> of the user. A user is _suspicious_ when more than one security events has been observed for the user; however, further information is needed to make a conclusion. A user is _malicious_ when the user is determined to violate a security policy or there is enough information to conclude that the user has malicious intentions. More fine-grained user states can be defined. 

The notation and the meaning of the variables of an attack in the model are given in Table 2. 

**Characterization of factor functions.** A factor func- 



<!-- Start of picture text -->
… e t− 1 e t …<br>fe t− 1 fe t<br>fs t<br>s t− 1 s t<br>fu t− 1 fu t<br>U<br><!-- End of picture text -->

Figure 3: A snapshot of the Factor Graph model of an attack at a time _t_ . 

tion can capture i) the relation between a user state and an event, ii) the relation among a user state and the earlier events/states observed during the progression of the incident, and iii) the relation between a user state and a user profile. Defining such factor functions can assert a user state with a higher degree of confidence. Factor functions can be categorized into the three main types of relations: Type-1 (event-state), Type-2 (state-state), and Type-3 (user-state). _Type-1._ A factor node _fe_<sup>_t_(</sup><sup>_e, s_)capturestherelationbe-</sup> tween the event _e_ and the hidden state variables _s_ . _Type-2._ A factor node _fs_<sup>_t_(</sup><sup>_et−_1</sup><sup>_, et, st−_1</sup><sup>_, st_)capturesthe</sup> relation among the hidden states _s_<sup>_t−_1</sup> , _s_<sup>_t_</sup> , events _e_<sup>_t−_1</sup> , and _e_<sup>_t_</sup> . 

_Type-3._ A factor node _fu_<sup>_t−_1</sup> ( _U, e_<sup>_t−_1</sup> _, s_<sup>_t−_1</sup> ) captures the relation among a user profile _U_ , an event _e_<sup>_t−_1</sup> , and a hidden state _s_<sup>_t−_1</sup> . 

A factor function has a discrete value output of 0 or 1. Each factor _f_ ( _x_ ) is defined by an _indicator function IA_ ( _x_ ) : _X →{_ 0 _,_ 1 _}_ that returns 1 if an input _x ∈ X_ is a match with _A_ and 0 otherwise, where _A_ is a tuple of values and _x_ is a tuple of variables. A match between _x_ and _A_ (i.e., _x_ = _A_ ) means that the values of variables in _x_ are the same as those of _A_ , element-wise. 



For example, in Section 3, we defined a factor function _f_ 3 for capturing the user state associated with the event _restart system service_ , given that the previous observed event was labeled as _suspicious_ . The factor function belongs to the Type-2 category and can be defined using indicator function as follows. Let _A_ be a tuple of ( _e_<sup>_t−_1</sup> = _e_<sup>_∗_</sup> , _e_<sup>_t_</sup> = restart system service, _s_<sup>_t−_1</sup> = _suspicious_ , _s_<sup>_t_</sup> = _malicious_ ). The notation _e_<sup>_∗_</sup> for the event _e_<sup>_t−_1</sup> means that the event _e_<sup>_t−_1</sup> can be any of the events in the event set E. Using our definition, the factor function is defined as _fs_<sup>_t_(</sup><sup>_et−_1</sup><sup>_, et, st−_1</sup><sup>_, st_) =</sup> _IA_ ( _e_<sup>_t−_1</sup> _, e_<sup>_t_</sup> _, s_<sup>_t−_1</sup> _, s_<sup>_t_</sup> ). We illustrate real factor functions, derived from our real-world incidents dataset, in Section 6. 

Higher-order and complex factor functions relating multiple events can be defined, however, they construct more complex Factor Graphs. 

**A generic Factor Graph.** Figure 3 shows a generic Factor Graph model of an attack. Variable nodes correspond to either observed variables _U, E_<sup>_t_</sup> or hidden variables ( _S_<sup>_t_</sup> ). Factor nodes represent factor functions describing functional relations among the observed variables and hidden variables. 

For the purpose of illustration, Figure 3 shows a part of the 

|_Symbol_|_Description_|
|---|---|
|_e,_E_, E_|Event, event set, sequence of events|
|_u, U_|User, user profle|
|_f, F_|Factor function, set of factor functions|
|_su,_S|User state, user state set|



Table 2: Notations of variables used in our model. 

complete Factor Graph at the time _t_ . Five factor functions are illustrated: _fe_<sup>_t−_1</sup> _, fe_<sup>_t_(Type-1),</sup><sup>_f_</sup> _s_<sup>_t_(Type-2),and</sup><sup>_f_</sup> _u_<sup>_t−_1</sup> _, fu_<sup>_t_</sup> (Type-3). In our model, the factor functions are defined for the sequence of events _E_<sup>_t_</sup> from _e_<sup>1</sup> (when a user begins using the system) to _e_<sup>_t_</sup> (at an observation time _t_ ). 

**Inference of hidden user states.** To identify malicious users, AttackTagger infers the most probable values of the user state in the sequence _S_<sup>_t_</sup> using the constructed factor graph. Specifically, if the user state _s_<sup>_t_</sup> = _suspicious_ , then the user is allowed to operate in the target system under close monitoring (e.g., logging network traffic of the user or logging user commands); if the user state _s_<sup>_t_</sup> = _malicious_ , the user is identified as an attacker and actions are taken to disconnect the user from the target system (e.g., terminating the user’s active network connections or disabling the user account). Our inference is based on the joint probability distribution on the Factor Graph. 

_Joint probability distribution function (pdf)._ Let _F_ = _{Fe, Fs, Fu}_ be the set of factor functions of Type-1, Type2, and Type-3, respectively. Let _f_ ( _cf_ ) be a factor function _f ∈ F_ where _cf_ is the set of its inputs that can be observed and hidden state variables. The joint probability distribution _P_ ( _U, E_<sup>_t_</sup> _, S_<sup>_t_</sup> ) of the observed variables and hidden state variables can be factorized using factor functions _F_ : _P_ ( _U, E_<sup>_t_</sup> _, S_<sup>_t_</sup> ) = _Z_<sup><u>1</u></sup> � _f ∈F_<sup>_f_(</sup><sup>_cf_).Inthejointpdf,weuse</sup><sup>_Z_as</sup> the normalization factor to make sure that the joint pdf is a proper distribution, instead of computing the _score_ of _S_<sup>_t_</sup> as seen in Section 4. The normalization factor _Z_ can be computed by summing values of _f_ over all possible combinations of the variables _{U, E_<sup>_t_</sup> _, S_<sup>_t_</sup> _}_ . 

_Inference._ The most probable values of the user states in the sequence _S_<sup>_t_</sup> can be inferred by enumerating all possible values of the user states in the sequence and returning the values that maximize _P_ ( _U, E_<sup>_t_</sup> _, S_<sup>_t_</sup> ). 



Although the brute-force approach can give an exact result for the most probable hidden state variables _S_<sup>_t_</sup> , its naive enumeration of all possible values of the user states in the sequence is costly. Since each state variable _s_<sup>_t_</sup> has a discrete value, approximation methods such as Gibbs sampling, which have been successfully utilized in computer vision and natural language processing, can be used for inference [16]. 

_Gibbs sampling on Factor Graphs._ Given a constructed Factor Graph of a user session, the user state sequence can be approximated using Gibbs sampling, a popular inference algorithm on Factor Graphs [5]. In a real-world detection system that requires inference in near real-time, Gibbs sampling can produce an approximate result within a predefined bounded time (e.g., the algorithm stops after 100 iterations). Performance and ease of use are the main reasons for using Gibbs sampling rather than using exact inference (for which the complexity is exponential to the length of the sequence). We briefly describe how a Gibbs sampler works. 

A Gibbs sampler runs over _N_ iterations. It starts with a 

||Registered physical location (categorical)|
|---|---|
|_User_<br>_attributes_|Number of days since the last login (integer)<br>Has been compromised previously (boolean)|
||Login remotely (using secure shell)|
|_Event_|Download sensitive fle (.exe, .c)<br>Restart system service (secure shell server)|
||Large number of incorrect login attempts|
||Large number of open network connections|



Table 3: Examples of user attributes and events. 



<!-- Start of picture text -->
(a1) Define factor functions using Construction Set (b1) For each user in the Testing Set, automatically construct a<br>manual factor graph based on the event sequences and the defined<br>raw logs definition factor functions (obtained from the Construction Set)<br>Factor<br>Construction functions<br>Exact inference<br>2008-2009 incident  manual events or Gibbs sampling<br>51 incidents reports definition Re-used<br>for all users<br>factor<br>Prediction<br>auto script<br>raw logs extraction user state benign suspicious malicious<br>User (b1) Construct factor graph (b2) Infer user states User u1 is  malicious<br>Testing events User u2 is  benign<br>incident  manual Represented …<br>2010-2013 reports extraction as .timeline files<br>65 incidents<br>(a2) Extract event sequences in Testing Set (b2) Infer the user state sequence based on the observed user events. (c) Output predictions<br><!-- End of picture text -->



<!-- Start of picture text -->
Construction<br><!-- End of picture text -->



<!-- Start of picture text -->
Testing<br><!-- End of picture text -->

Figure 4: Experiment flow with input is incident report or raw logs, and output is prediction of malicious users. 

random user state sequence at iteration 0. At iteration 1, it samples a new user state, starting at a user state _s_<sup>0</sup> . That sampling process is conditioned on the value of the previous user state sequence and the Factor Graph. In the next step, this sampling process is repeated for the next user state _s_<sup>_i_</sup> and so forth, until it reaches the last user state _s_<sup>_n_</sup> . That concludes the sampling process for a user state sequence at iteration 1. The Gibbs sampler repeats the iteration process and stops when it reaches one of the two termination conditions: i) _N_ iterations, or ii) the user state sequence converges (i.e., the user state sequence does not change from iteration _k_ to iteration _k_ + 1). 

## **6. EVALUATION OF ATTACKTAGGER** 

This section describes the incident dataset, generation of the factor functions, construction of Factor Graphs, and evaluation of AttackTagger. 

## **6.1 Threat model** 

We consider networked computers in an enterprise environment (NCSA) where adversaries come from outside the enterprise perimeter. We assume that the monitoring infrastructure at NCSA was implemented to capture events leading to attacks [18]. 

## **6.2 Dataset** 

We use data on 116 real-world security incidents observed at NCSA during a six-year (2008-2013) period. The incidents contain sophisticated attacks, such as tampering with system services (e.g., SSHd) to steal credentials, misuse of computing infrastructure (to build botnets, send spam emails, or launch denial of service attacks), or remote exploitation of Virtual Network Computing servers to get a system shell. 

**Incident data.** The incident data include incident reports and raw logs. For each incident in our dataset, we obtained its _incident report_ , manually created by NCSA security analysts in free format text. Each incident report contains a detailed post-mortem analysis of the incident, including alerts generated by NCSA security monitoring tools. An incident report often includes snippets of _raw logs_ (e.g., syslogs, network flows, and Bro IDS logs) associated with malicious activities. Incident reports may also contain extra information about the incident, such as records of emails exchanged among security analysts during the incident. 

Most incidents considered in our dataset are related to multi-staged attacks, in which an attack spanned a duration 

of 24 to 72 hours. Thus, for a subset of security incidents we also gathered the _raw logs_ for a period of 24 to 72 hours before and after the NCSA security team detected a given incident. That duration of time is sufficiently long to cover most of the traces of attacks in our dataset. Since the data retention policy changed during 6 years when incident data were being collected, the raw logs were only available for a subset of incidents (Table 4). The raw logs are valuable because they captured activities of both benign and malicious users during the incidents. 

**Construction Set and Testing Set.** The data on 116 incidents have been partitioned into two disjoint sets: (i) a Construction Set of 51 incidents collected during the 20082009 period, and (ii) a Testing Set of 65 incidents collected during the 2010-2013 period. We used the incident data from the Construction Set to extract the set of events observed during the incidents and to define the factor functions. We use the Testing Set incident data to construct the Factor Graph for each user and to evaluate the detection capabilities of the constructed Factor Graphs. 

The partition was based on the following. In the 20082009 period, a subset of the incidents were credential stealing incidents. Our conjecture is that, in many incidents observed during the 2010-2013 period, the attackers used the stolen credentials, exploited weak user passwords, or used similar attack patterns (e.g., remote login, download sensitive file, and escalate privilege) to infiltrate the NCSA infrastructure. As a result, our model has been constructed using the Construction Set and evaluated using the Testing Set. Table 4 summarizes the two disjoint sets. 

**Ground truth.** The benign and malicious users provided by incident data are considered the _ground truth_ in our evaluation. The 51 incident reports and 18 incident raw logs in the Construction Set identified 46 malicious users, 5 benign users misclassified as malicious by NCSA security analysts, and 2,612 benign users who were involved in the incidents. Based on post-incident analysis, the 65 incident reports and 5 incident raw logs for the Testing Set identified 62 malicious users, 3 benign users misclassified as malicious users by the NCSA security analysts, and 1,253 benign users who 

|DataSet|Available Data||
|---|---|---|
||Incident reports|Raw logs|
|Construction Set (51)|51|18|
|Testing Set (65)|65|5|



Table 4: Summary of the incident dataset 



<!-- Start of picture text -->
Incident report Events Raw logs Events<br>The security team started receiving some  ssh  ANOMALOUS_HOST<br>suspicious alerts from the machine <machine> for the user <user>. There were also some Bro  HTTP_HOTCLUSTER_CONN sshd: Accepted <user> from <host> LOGIN<br>HTTP_HotClusterConn alerts from the machine<br><machine> as well. From the Bro sshd logs the user<br>ran the following commands GET_HOST_INFO HTTP GET vm.c (bad-domain.com) SENSITIVE_URL<br>uname -a GET_LOGGEDIN_USERS<br>.. HTTP GET vm64.c (bad-domain.com) SENSITIVE_URL<br>w DISABLE_HISTORY<br>..unset HISTFILE.. SENSITIVE_URL sshd: Received SIGHUP; restarting. RESTART_SYS_SRV<br>wget <xx.yy.zz.tt>/abs.c -O a.c;gcc a.c -o a; COMPILE<br>a1) Manual conversion from incident report to events a2) Automatic conversion from raw logs to events<br><!-- End of picture text -->



<!-- Start of picture text -->
a2) Automatic conversion from raw logs to events<br><!-- End of picture text -->

Figure 5: Manual and automatic conversion of incident reports and raw logs to events. 

were involved in the incidents. In total, nearly four thousand users logged into the target system during the six year (2008-2013) period. When counting the number of users, the same user _u_ observed in separated incidents is considered as separated users. There could be hidden malicious users who were not indicated in the incident reports by the NCSA security analysts. Our model detected six hidden malicious users (Section 6.5). 

## **6.3 Extraction of events and definition of factor functions** 

Given the data for an incident, we extracted _user sessions_ from the incident report and the raw logs. Usually there were several hundred user sessions in an incident. 

**Extraction of events.** A sequence of events was extracted from each user session. In the case of a raw log snippet listed in the written incident report, we used regular expression scripts to automatically extract the corresponding events. In the case of a textual description of a user activity, we manually extracted a list of events in an order that matched the textual description (to the best of our knowledge). The textual descriptions often do not include an accurate timestamp associated with each event, but rather were arranged in an order that we inferred from the incident reports. To illustrate our manual extraction process, an excerpt of a written report and the extracted events are given in Figure 5-a1. 

When the raw logs corresponding to a user session were available, regular expressions scripts were used to convert them to a sequence of events. Each log entry in the raw logs was mapped to a unique event identifier and event metadata, including epoch timestamp and the user identifier who triggered the event. Order of events happenned in the raw logs are inferred from the timestamps. Examples of a log entry and the corresponding event are illustrated in Figure 5-a2. For incidents for which we have both the incident report and the raw logs, we combined the events extracted from the written report and the raw logs. 

Preprocessing of incident data resulted in a list of _.timeline_ files for each incident in the Testing Set. Each file contains a sequence of events for a user and the ground truth information, indicating whether the user is malicious or not. There were 1,315 users and 65,389 events for the incidents in the Testing Set. 

**Definition of factor functions.** The factor functions were defined manually using incident data from the Construction Set and experts’ knowledge of the system. In the following, we illustrate the three types of factor functions derived from real incidents in the Construction Set. 

A Type-1 factor function can directly associate an _event_ with a _malicious user state_ when the event is an obvious 

violation of a security policy, e.g., a simple factor function could capture the following relation: _the user downloads a known exploit/malware file_ (the observed event) implies _the user is malicious_ (the assigned user state). A Type-1 factor can also capture a less obvious policy violation, e.g., _the user logs in from a remote location_ (the observed event) implies the user is _suspicious_ (the assigned user state). The accuracy of the established association between the _event_ and the _user state_ depends on the representativeness of the data on the past incidents and the confidence of the expert. 

More advanced factor functions, i.e., Type-2 and Type-3, take into account the knowledge of the user state, as determined based on the earlier events observed during the progression of the incident. As a result, Type-2 and Type3 factor functions can assert the user state with a higher degree of confidence. For example, a Type-2 factor function could assert the following relation: _the user downloads a file with a sensitive extension_ (the most recent event) and _the user state is suspicious_ (determined based on an earlier event) imply _the user state is malicious_ . Type-3 factor functions are **_extensions_** of the Type-2 factor functions, in which the user profile is taken into account because of the flexibility of Factor Graphs. For example, a Type-3 factor function could assert the following relation: _a user has been previously compromised_ (established based on the user profile) and _the user state is suspicious_ (determined based on an earlier event) and _the user restarts a system service_ (the most recent event) imply _the user state is malicious_ . 

Following our illustrated definitions, practitioners can construct their own factor functions based on their events and expert knowledge of their target systems. We defined a total of 65 factors, in which there are 29 Type-1 factors, 34 Type2 factors, and 2 Type-3 factors. Due to space limitation, a complete list of factor functions is available online<sup>2</sup> . 

## **6.4 Construction and inference on Factor Graph** 

Given the defined factor functions, we constructed a Factor Graph for each user session ( _per-user Factor Graph_ ) and performed inference on the constructed Factor Graphs. 

**Construction of Factor Graphs.** Each per-user Factor Graph was used to re-evaluate the user state (benign, suspicious, or malicious) on arrival of a new event. The resulting Factor Graphs were dense with many edges, since the entire defined factor functions have to link all of the events in the user event sequence. For a sequence of _n_ user events, a Type-1 factor function links each event _e_<sup>_i_</sup> with the user state _s_<sup>_i_</sup> ( _i_ = 1 _..n_ ). The process is repeated for the Type-2 and Type-3 factor functions with their corresponding events and user states. Figure 5 shows the experimental flow, including the process of constructing a Factor Graph for each user. 

2http://bit.ly/preemptive-intrusion-detection 

|Detection timeliness|Detected by<br>security analysts<br>Preemption timeliness|
|---|---|
|_t_0|<br>_ts_<br>_tn_<br>_tm_|
|The frst event|Detected by<br>AttackTagger<br>The last event|



Figure 6: An attack timeline: the first event is observed at _t_ 0; AttackTagger detects the attack at _tm_ ; the attack finishes at _tn_ ; security analysts detect the attack at _ts_ . Each square dot is an event related to the attack. 

In our experiments, the weights for the factor functions were assumed to be equal (i.e., the weight was 1). No training was performed to obtain the weights. The main difficulty in determining weight was the required human supervision for labeling each event with a user state. A value of a user state must be assigned for each observed event (i.e., whether the corresponding user state of the event is benign, suspicious, or malicious), and that is an arduous manual process taking into account about 300,000 observed events (20082013). Despite the use of equal factor weights, our model still achieves a good detection performance compared with detection by security analysts (Section 6.5). 

**Inference of user states on Factor Graphs.** In Figure 5-b2, given a constructed Factor Graph of a user session, the user state sequence was approximated using Gibbs sampling [5] in the OpenGM library [2]. Runtime performance of our model was evaluated on a desktop running Ubuntu 12.04 on Intel i5-2320 CPU at 3.00 GHz with 6 GB of RAM. 

## **6.5 Empirical results** 

Our model was able to detect most of the malicious users (74.2%) relatively early (i.e., before system misuse). More importantly, our model uncovered a set of six hidden malicious users, which had not been discovered by NCSA security analysts. In this section, we describe how we analyzed the detection timeliness and detection accuracy of our model using the Testing Set. 

### _6.5.1 Timestamps and ordering of events_ 

We used _Lamport timestamp_ (or logical clock) to establish the relative order of events [11]. The Lamport timestamp was used because _absolute timestamps_ of events were not available for most of the incidents in our dataset. 

Each event in a user session was assigned a Lamport timestamp (specifying the order of events) or an absolute timestamp. For example, when a user session had a single event _a_ , its Lamport timestamp was C( _a_ ) = 1. As more events were observed, the events were assigned increasing values of the Lamport timestamp, such that if an event _a_ happened before _b_ , then C( _a_ ) _<_ C( _b_ ). For incidents for which raw logs were available, each event was assigned an _absolute timestamp_ in addition to its Lamport timestamp. 

Figure 6 illustrates an event timeline of a malicious user. In the following, we refer to a timestamp as either a Lamport timestamp or an absolute timestamp, depending on the context. Consider a sequence of events _t_ 0 is the timestamp of the first observed event, _tm_ is the timestamp when AttackTagger concludes the user is malicious, _tn_ is the timestamp of the last observed event, and _ts_ is the timestamp when the malicious user is detected by a security analyst. We define the _attack duration ta_ of the malicious user to be given by _ta_ = _tn − t_ 0. A _Lamport attack duration_ or an _absolute attack duration_ can be derived from that formula. In practice, a larger Lamport attack duration (expressed in the 



<!-- Start of picture text -->
45<br>40<br>35<br>30<br>25<br>20<br>15<br>10<br>5<br>0<br>0 . 0 0 . 2 0 . 4 0 . 6 0 . 8 1 . 0<br>incident time<br>incident id<br><!-- End of picture text -->

Figure 7: The x axis is the Lamport attack duration (incident time) of the malicious users normalized to the range [0-1]. Each row (incident id) in the y axis is a malicious user detected by AttackTagger in an incident. The dot in a row represents the time when the malicious user was detected by AttackTagger. 

number of events) corresponds to a larger number of events during the attack and indirectly corresponds to an absolute attack duration (expressed in seconds, minutes, or hours). To measure the absolute attack duration, we need an absolute timestamp to be associated with each event. 

All reported incidents were discovered by NCSA security analysts after system misuse, when attack payloads had already been executed; that means _ts ≥ tn_ . Our objective is to improve the detection time of the incidents, i.e., to detect a progressing attack as early as possible. 

_6.5.2 Detection timeliness and preemption timeliness_ We use two metrics to characterize the detection capabilities of our approach. 

**Detection timeliness** characterizes the responsiveness of an intrusion detection system to an attack. The detection timeliness is measured by _td_ = _tm − t_ 0. A _Lamport detection timeliness_ (LDT) was computed using Lamport timestamps associated with each event. An LDT corresponds to the number of events observed from the start of a user session until the determination that the user was malicious. 

In addition, for incidents for which raw logs were available, we computed their _absolute detection timeliness_ (ADT) using the absolute timestamp associated with each event. ADT provides the absolute time duration from the start of the user session until the determination that the user was malicious. Shorter detection timeliness is better. 

**Preemption timeliness** characterizes the amount of time that a human or an automated system had to respond to an attack, from the time when a user was identified as malicious until the time of the last observed user event. The preemption timeliness is measured by _tp_ = _ta − tm_ . Preemption timeliness was measured only for incidents for which a ground truth on when the attack was stopped was available. 

In our experiment, a _Lamport preemption timeliness_ (LPT) was computed using the Lamport timestamp associated with each event. In addition, for incidents for which raw logs were available, we computed their _absolute preemption timeliness_ (APT) using the absolute timestamp associated with each event. Longer preemption timeliness is better. 

**Detection and preemption timeliness.** The Lamport detection timeliness and the Lamport preemption timeliness are presented by detection points in Figure 7. For example, malicious user 15 was detected by AttackTagger when the malicious user had progressed 24% of the total attack duration represented by the number of observed events. 

Certain insights can be drawn from timeliness measurements. In total, our approach detected 46 of 62 (74.2%) the malicious users. Of the detected malicious users, 41 of 62 (66.1%) were detected before the attackers delivered their attack payloads. We considered only 62 of 65 incidents when computing detection performance, since we excluded the three incident reports that misclassified three benign users as malicious. 5 of the 62 (8.1%) malicious users were detected at the last stage of the attacks. 12 of the 46 identified malicious users were identified at the first observed event, at which they violated an obvious security policy (e.g., downloaded known malware or logged in using an expired account). 

|**Event**|**Description**|**UserState**|
|---|---|---|
|INCORRECT<br>PASSWORD<br>(5 times)|A user supplies an incorrect<br>credential at login. Repeated<br>alerts indicate password guessing<br>or bruteforcing.|benign|
|LOGIN|A user logs into the target system.|_suspicious_|
|HIGHRISK<br>DOMAIN|A user connects to a high-risk<br>domain, such as one hosted<br>using dynamic DNS<br>(e.g., .dyndns, .noip) or a site<br>providing ready-to-use exploits<br>(e.g., milw0rm.com).<br>The dynamic DNS domains can be<br>registered free and are easy to set up.<br>Attackers often use such domains<br>to host malicious webpages.|_suspicious_|
|SENSITIVE<br>URL|A user downloads a fle with<br>a sensitive extension<br>.<br>Such fles may contain shell<br>code or malicious executables.|**_malicious_**|
|CONNECT<br>IRC|A user connects to an Internet<br>Relay Chat server. IRC are often<br>used to host botnet Control servers.|**_malicious_**|
|SUSPICIOUS<br>URL|A user requests a URL containing<br>known suspicious strings,<br>e.g., leet-style strings<br>such as expl0it or r00t,<br>or popular PHP-based<br>backdoors such as c99 or r57.|**_malicious_**|



Table 5: Observed events during incident 2010-05-13. 

#### **Detection timeliness of an example incident.** 

In incident 2010-05-13, the following sequence of events was observed (Table 5), as determined from the incident report. After infiltrating the target system, the attackers started delivering the payloads by connecting to a highrisk domain (milw0rm.com, which provides ready-to-use exploits), downloading a sensitive file (xploit.tgz), and then placing a backdoor that connected to an external IRC server (irc2. _<_ bad-domain _>_ .fi). Our approach identified the user as suspicious after repeated incorrect login attempts (event INCORREC ~~T P~~ ASSWORD, LOGIN and 

HIGHRIS ~~K D~~ OMAIN ). Most importantly, our Factor Graph based approach identified the user as malicious immediately when attack payloads began to be delivered (events SENSITIV ~~E U~~ RL, CONNEC ~~T I~~ RC, and SUSPICIOU ~~S U~~ RL). 

For the 5 incidents for which we did not detect the malicious user until the end of the attacks, the main reason was a limited number of events generated by the monitoring system during these incidents. For example, in incident 2010-10-29, only two events were observed: ANOMALOU ~~S L~~ OGIN and DISABL ~~E B~~ AS ~~H L~~ OGGING. A better monitoring infrastructure would improve the detection timeliness. For a discussion of the 16 incidents for which we did not detect the malicious users, refer to the False negatives 

paragraph in the next section. 

**Measuring both LDT and LPT.** To get a summary of detection timeliness for a set of incidents, we used a new metric to measure both LDT and LPT, called the _area under the Lamport timeliness curve_ (AULTC). An AULTC value of 1 means that all malicious users were identified from the first observed event (in theory), which is ideal. An AULTC value of 0 means that all malicious users were identified after the fact (in reality, by the NCSA security team). Using a Lamport timeliness curve formed by connecting the detection points in Figure 7, we obtained an AULTC of 62.5% normalized for 46 detection points. Compared to human detections, which often happen after system misuse (AULTC = 0), our model is relatively good at early detection. 

_Absolute Detection Timeliness._ For a subset of 5 incidents in the Testing Set, we had the raw logs. For those incidents, we computed the ADT values over the attack duration (in seconds): 1.97/1.97, 59.00/3,601.00, 1,787.00/1,787.00, 3,600.00/3,600.00, and 10,897.00/21,913.00. The best result was detection of a malicious user at the very first minute (59th second) of an hour-long attack (3,601 seconds). In that case, the aggressive attacker caused a burst of security events and/or alerts. The attacker logged in using a stolen credential from a remote location, and then immediately collected system information (using the command _uname - a_ ), and downloaded privilege escalation exploits stored in .c files; that gave our model enough evidence to conclude that the user was malicious. Our detection timeliness is better than that of human detection, which only detects attacks after system misuse. 

### _6.5.3 Detection performance_ 

Detection performance was evaluated using standard performance metrics for machine learning classifiers. The true positive rate (TP), i.e., the _detection rate_ , is the percentage of malicious users who are correctly identified as malicious. The false positive rate (FP) is the percentage of benign users who are incorrectly identified as malicious. The true negative rate (TN) is the percentage of benign users who are correctly identified as benign. The false negative rate (FN) is the percentage of malicious users who are incorrectly identified as benign. 

**True positives.** AttackTagger detected 46 of 62 (74.2%) malicious users relatively early. Most of the attacks were detected before the attack payloads were launched. Our model detected attacks as early as within the first minute of observing events related to the attack. 

**False negatives.** AttackTagger did not detect 16 out of 62 (25.8%) malicious users. The major reasons for misdetection were: a lack of events (very few events were observed), new event types (i.e., events that were not observed in the incidents included in the Construction Set), and generation of only one type of events. 

Specifically, for seven of the false negatives, input to our model included only 1 to 2 events, which made it difficult even for security analysts to reach a conclusion. That suggests a need for comprehensive monitoring infrastructure across a system and network stacks (e.g., at the kernel or the hypervisor level) to capture attacker behavior. For three of the false negatives, the malicious users performed one activity repeatedly (e.g., using an incorrect credential), which were seen as merely suspicious by AttackTagger. That phenomenon can be addressed by refining the factor functions. Similarly, for the remaining six false negatives, new event 

|Incident|Activity|
|---|---|
|20100416|Illegal activities|
|20100513|Incorrect credentials (multiple times); Sending spam emails|
|20100513|Logging in from multiple IP addresses; Illegal activities|
|20101029|Logging in using expired passwords; Illegal activities|
|20101029|Illegal activities|
|20101029|Illegal activities|



Table 6: Six hidden malicious users uncovered. 

types were observed (e.g., misconfiguration of a web proxy, logging in using an incorrect version of SSH, or downloading of adult content) that had not been captured in our factor functions derived based on the Construction Set. The fix is to update the factor functions continuously (which requires human intervention) when system infrastructure changes or when a new event of interest is observed. 

**False positives.** AttackTagger identified 19 of 1,253 benign users as malicious (1.52%), although these users were not recorded as malicious in the incident reports. We analyzed the false positives for those incidents when raw logs of the incident were available and discussed our analysis with NCSA. Six of the 19 users were confirmed to have behaved maliciously and should be investigated further. Table 6 summarizes those users<sup>3</sup> . Although we misidentified the remaining 13 users, the discovery of the six malicious users suggests that our method can uncover hidden attacks that have been missed by NCSA security analysts. 

### _6.5.4 Performance comparison_ 

Using the Test Set, we compared our approach with other types of binary classifiers. A primitive type of classifier (baseline) is based on rules to detect attackers. More sophisticated classifiers are learning-based such as Decision Trees or Support Vector Machines. 

The main difference between our approach and the others is that our approach works with progressing attacks (i.e., using an incomplete sequence of events). The other binary classifiers often rely on a complete sequence of events to classify a user, so usually can be used only after attacks have reached their final stage. 

In the following, we compare the detection performance of the selected techniques. 

_AttackTagger (AT)_ , our approach, tags each observed event with a user state using Type-1, Type-2, and Type-3 factors. _Rule Classifier (RC)_ is a baseline rule-based classification model. We implemented it to identify attacks based on the most frequently observed alert in the Construction Set, namely a log in from an anomalous host. 

_Decision Trees (DT)_ are rule-based classification model that groups decisions into a tree. They learn the rules from previous attacks. We used the _C_ 45 decision tree implementation in the scikit-learn machine learning library [14]. 

_Support Vector Machines (SVM)_ are frequently used classifier that uses a hyperplane and margins to classify classes. We used _classifier_ =Support Vector Classification, with kernel= _linear_ using the scikit-learn implementation [14]. 

**Implementation parameters.** Parameters of the aformentioned techniques ,except AT, were optimized based on the Construction Set. In our AT model, we constructed only the factor functions from the Construction Set and considered all the weights of factor functions to be equal. The training-free approach makes our approach less dependable 

3Examples of illegal activities include download of a file with sensitive extensions or execution of anomalous commands (w, uname -a). 

|_Name_|_TP_|_TN_|_FP_|_FN_|
|---|---|---|---|---|
|AttackTagger|_74.2_|_98.5_|_1.5_|_25.8_|
|Rule Classifer|9.8|96.0|4.0|90.2|
|Decision Tree|21.0|100.00|0.00|79.0|
|Support Vector Machine|27.4|100.00|0.00|72.6|



Table 7: Detection performance of the techniques 

on a training set, i.e., there is less overfit. 

**Performance analysis.** We compared our detection performance and that of other techniques (Table 7). 

The rule-based techniques (RC) performed poorly compared to AttackTagger. The Rule Classifier (RC) has a true positive rate of 9.8% since it identifies malicious users based solely on the most frequent alert in the Construction Set: a log in from an anomalous host. In the Testing Set, that alert was not observed in many of the incidents. 

The other techniques (DT and SVM) seem to have an overfit problem, such that they only learn patterns of existing attacks in the Construction Set; the true negative is 100.0% for both, which means these models are conservative in classifying a user as malicious. As a result, they do not generalize well in the Testing Set; their true positive are 21.0% and 27.4% respectively. 

**Comparing detection performance.** In this experiment, AT had the best detection rate among the techniques (74.2% vs. 27.4% for the next-best technique SVM). We performed a hypothesis test to show that the true positive rate for AttackTagger is significantly better than the true positive rate for the SVM approach. Our null hypothesis _H_ 0 is that AT and SVM have the same detection performance. The alternative hypothesis _H_ 1 is that AT and SVM have significant different detection performance. We tested our hypothesis using the McNemar test, a popular drug treatments statistical test [19]. 

We measured differences in detection of AT and SVM. For example, _AT_<sup>+</sup> _SV M_<sup>+</sup> means that for a user, both AT and SVM determined that the user was malicious. Similarly, we measured the number of differences and agreements between the two techniques by four metrics: a = _AT_<sup>+</sup> _SV M_<sup>+</sup> , b = _AT_<sup>+</sup> _SV M_<sup>_−_</sup> , c = _AT_<sup>_−_</sup> _SV M_<sup>+</sup> , and d = _AT_<sup>_−_</sup> _SV M_<sup>_−_</sup> . 

The McNemar test statistic is based on the number of discordant pairs (identified by b and c) between the two methods. The test statistic is computed by _χ_<sup>2</sup> = ( _b_ + _c_ )<sup>2</sup> _/_ ( _b− c_ ). In our case, a=17, b=48, c=0, and d=1,250; the test statistic is _χ_<sup>2</sup> = 48. A p-value can be inferred according to the _χ_<sup>2</sup> value. The inferred p-value is _<_ 0.00001 (i.e., the result is significant). 

According to the test, we can safely reject the null hypothesis _H_ 0. It means that the detection performance of AT is significantly different from that of the next-best (SVM); in our case it has a better detection rate (74.2% vs. 27.4%). 

### _6.5.5 Runtime performance_ 

A detection model must come up with a decision in a reasonable amount of time; otherwise, it misses the attack. AttackTagger was able to tag user states with events within seconds. Since we use Gibbs sampling for approximate inference instead of exact inference, the time it takes to infer the user states depends on sampling iterations and is linear to the length of the event sequence. On average, it took AttackTagger 530 ms to tag an event. The minimum tagging time was 328ms, the maximum tagging time was 644ms, and the standard deviation was 0.1 for 65,389 events. The number of events can be limited by a fixed time-window or by importance sampling of interesting events. 

## **7. RELATED WORK** 

Intrusion detection systems have been investigated ever since the Anderson report was published over thirty years ago [1]. Most of the work has focused on signature-based or anomaly-based techniques. Signature-based techniques often identify only a stage of an attack that uses known patterns [3]. Anomaly-based methods use profiles, statistical measurements, or distance measurements to capture abnormal behaviors of potential novel attacks at the cost of overwhelming number of false alarms [6]. 

As IDSes have been widely deployed, dynamic infrastructure (e.g., a variety of constantly changing hosts and network devices) presents new challenges [13]. IDS alerts are generated from monitoring across system stacks and network interfaces, e.g., network packet captures, authentication logs (SSH or Kerberos), and access logs (HTTP requests). Such diverse and numerous alerts challenge automated systems to correlate alerts (i.e., normalization, aggregation, correlation, and analysis of alerts) with an attack and to identify users involved in the attack [17]. Given the correlated alerts, security analysts still have to spend a significant amount of time investigating false or insignificant alerts [13]. 

Probabilistic graphical models have been employed to model uncertainty in multi-staged attacks. In attack scenario modeling, BNs can model causal relations among high-level attack stages [15]. A BN and its parameters can be derived based on domain knowledge of the target system and known attacks. The network allows inference on a potential attack stage. The main challenge of BN is the assumption of the model structure and its parameters, which have high uncertainty in a constantly changing infrastructure. In attack sequence modeling, Markov models such as MRFs define an attack as a sequence of actions that causes a transition in the underlying system state [9]. Previous sequence modeling techniques (such as variable length markov models or matrix-based recommendation systems) built models based on observed events [7]. Those techniques do not integrate external knowledge of users or the target system (e.g., the user profile in our model) to improve accuracy of inference. 

To address the limitations of previous efforts, we use Factor Graphs, a type of probabilistic graphical model that unifies BNs and MRFs [8, 4]. Unlike signature and anomaly techniques, Factor Graphs do not rely on a single rule or an anomaly measure. Instead, using factor functions, a Factor Graph collectively identifies attacks using rules, anomaly measures, and sequential measures among observed events. In our model, Type-1 factors represent rules and Type-2 factors represent sequential dependency among events and user states. Moreover, Type-3 factors can incorporate user profile and expert knowledge into our model. 

Our technique does not mean to replace existing IDSes, instead, our technique operates on top of monitoring data provided by IDSes and system/network monitors. By combining strengths of individual techniques, AttackTagger can identify progressing attacks using only a partial observation of events leading to the attacks. 

## **8. CONCLUSION** 

In this paper, we evaluated the effectiveness of using Factor Graphs to detect progressing attacks at early stages. Incident data for 116 real-world security incidents were used in our evaluation. Our approach i) detected 74% of the at- 

tacks as early as minutes to hours before the system misuse (whereas human detection always occurred after misuse) and ii) uncovered six hidden malicious users from 65 incidents in our Testing Set. In the future, we plan to investigate the effectiveness of individual or groups of factor functions in our detection performance. 

## **Acknowledgements** 

We would like to acknowledge the NCSA security team for providing incident data and ground truth; DEPEND group members, Dr. Charles Kamhoua, Dr. Shuo Chen, and anonymous reviewers for providing valuable feedbacks; and Ms. Jenny Applequist for proofreading. This work was supported in part by the National Science Foundation under Grant No. CNS 10-185303 CISE, by the Army Research Office under Award No. W911NF-12-1-0086, by the National Security Agency under Award No. H98230-14-C-0141, by the Air Force Research Laboratory, and by the Air Force Office of Scientific Research under agreement No. FA8750-11-20084. The opinions, findings, and conclusions stated herein are those of the authors and do not necessarily reflect those of the sponsors. 

## **9. REFERENCES** 

- [1] Anderson, J. P. Computer security threat monitoring and surveillance. Tech. rep., 1980. 

- [2] Andres, B. e. a. An empirical comparison of inference algorithms for graphical models with higher order factors using opengm. In _Pattern Recognition_ . Springer, 2010, pp. 353–362. 

- [3] Bro. Bro intrusion detection system. www.bro-ids.org. 

- [4] Cao, P., Chung, K.-w., Kalbarczyk, Z., Iyer, R., and Slagell, A. J. Preemptive intrusion detection. In _Proceedings of the 2014 Symposium and Bootcamp on the Science of Security_ (2014), ACM, p. 21. 

- [5] Carter, C. K., and Kohn, R. On gibbs sampling for state space models. _Biometrika 81_ , 3 (1994), 541–553. 

- [6] Denning, D. E. An intrusion-detection model. _IEEE Transactions on Software Engineering_ , 2 (1987), 222–232. 

- [7] Fava, D. S. e. a. Projecting cyberattacks through variable-length markov models. _Information Forensics and Security, IEEE Trans. on_ (2008). 

- [8] Frey, B. J., Kschischang, F. R., Loeliger, H.-A., and Wiberg, N. Factor graphs and algorithms. In _Proceedings of the Annual Allerton Conference on Communication Control and Computing_ (1997), pp. 666–680. 

- [9] Hu, J., Yu, X., Qiu, D., and Chen, H.-H. A simple and efficient hidden markov model scheme for host-based anomaly intrusion detection. _Network, IEEE 23_ , 1 (January 2009), 42–47. 

- [10] Lafferty, J., McCallum, A., and Pereira, F. C. Conditional random fields: Probabilistic models for segmenting and labeling sequence data. 

- [11] Lamport, L. Time, clocks, and the ordering of events in a distributed system. _Communications of the ACM 21_ (1978). 

- [12] Nikovski, D. Constructing bayesian networks for medical diagnosis from incomplete and partially correct statistics. _Knowledge and Data Engineering, IEEE Transactions on 12_ , 4 (2000), 509–516. 

- [13] Pecchia, A., Sharma, A., Kalbarczyk, Z., Cotroneo, D., and Iyer, R. K. Identifying compromised users in shared computing infrastructures: a data-driven bayesian network approach. In _Proc. of Reliable Distributed Systems (SRDS)_ (2011), IEEE. 

- [14] Pedregosa, F. e. a. Scikit-learn: Machine learning in python. _JMLR 12_ (2011). 

- [15] Qin, X., and Lee, W. Attack plan recognition and prediction using causal networks. In _Computer Security Applications Conference, 2004. 20th Annual_ (2004), IEEE, pp. 370–379. 

- [16] Robert, C. P., and Casella, G. _Monte Carlo Statistical Methods (Springer Texts in Statistics)_ . Springer-Verlag New York, Inc., Secaucus, NJ, USA, 2005. 

- [17] Sadoddin, R., and Ghorbani, A. Alert correlation survey: framework and techniques. In _Proc. of Intl. Conference on Privacy, Security and Trust_ (2006), ACM. 

- [18] Sharma, A., Kalbarczyk, Z., Barlow, J., and Iyer, R. Analysis of security data from a large computing organization. In _Dependable Systems & Networks (DSN)_ (2011), IEEE. 

- [19] Sheskin, D. J. _Handbook of parametric and nonparametric statistical procedures_ . crc Press, 2003. 

- [20] Shulman, A. The underground credentials market. _Computer Fraud & Security 2010_ , 3 (2010), 5–8. 

