# equitable-dialogue-ACL2023
This is the code repo. for "Learning to Generate Equitable Text in Dialogue from Biased Training Data" published in ACL 2023.

The project is an extension and mostly uses the code/algorithms implemented [LEATHER](https://github.com/anthonysicilia/LEATHER-AACL2022) (linked repo.).

The two new scripts needed are provided in this repository:
1. ```evaluation.py```, which is used to conduct the automated bias/equity evaluation shown in the paper.
2. ```train.py```, which is a replacement for ```train/CL/train.py``` in the original [LEATHER repo](https://github.com/anthonysicilia/LEATHER-AACL2022). This new version adds/implements a ```fair``` flag in the script arguments to train the DS baseline in "Learning to Generate...".

Besides these scripts all dependencies/procedures are identical to those listed in the [LEATHER](https://github.com/anthonysicilia/LEATHER-AACL2022) README. Please reach out if you have any questions, and if you are interested in our other works on learning theory and dialogue, please see below:
 - [The Change that Matters in Discourse Parsing: Estimating the Impact of Domain Shift on Parser Error](https://arxiv.org/abs/2203.11317)
 - [PAC-Bayesian Domain Adaptation Bounds for Multiclass Learners](https://openreview.net/forum?id=S0lx6I8j9xq)
 - [Modeling Non-Cooperative Dialogue: Theoretical and Empirical Insights](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00507/113020/Modeling-Non-Cooperative-Dialogue-Theoretical-and)








