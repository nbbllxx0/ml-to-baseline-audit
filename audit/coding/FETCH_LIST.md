# Papers to fetch (optional): records in the decision order the coding agents could not read

**Why.** G1 walks the decision order (`audit/screening/pilot_final_order.csv`). The pre-registered rule skips a record whose full text the coders cannot read, which biases the pilot toward papers that automated agents can reach. Supplying a PDF makes the record count.

**How to supply a paper.**
1. Save the PDF outside the project (third-party PDFs are never stored in the project; PROTOCOL §7.4), for example in a private folder next to it named `ml-to-baseline-audit-private`, as `<pid>.pdf`.
2. Add a row to `audit/coding/user_supplied_fulltext.csv` with columns `pid,file,date` (create the file with that header if it does not exist).
3. Tell me; the supplied records get coded and re-enter the G1 walk at their positions.

Positions up to 161 (the span coded so far). Earlier positions matter most.

## A. Free to read in a browser, but blocked for automated agents (18)

| Order | pid | Title | Link |
|---|---|---|---|
| 14 | P01268 | Application of a Machine Learning-Based Topology Optimization Method on an Automotive B-Pillar for Crashworthy Lightweig | https://doi.org/10.1051/matecconf/202642203010 |
| 24 | P00918 | Accelerating cell topology optimisation by leveraging similarity in the parametric input space | https://doi.org/10.1016/j.cma.2025.118044 |
| 26 | P00610 | Effective thermal conductivity estimation using a convolutional neural network and its application in topology optimizat | https://doi.org/10.1016/j.egyai.2023.100310 |
| 29 | P01870 | Exploring VAE-driven implicit parametric unit cells for multiscale topology optimization | https://doi.org/10.1016/j.matdes.2024.113087 |
| 35 | P00875 | Learning topology optimization process via convolutional long‐short‐term memory autoencoder‐decoder | https://doi.org/10.1002/nme.7221 |
| 40 | P00550 | Machine learning for topology optimization: Physics-based learning through an independent training strategy | https://doi.org/10.1016/j.cma.2022.115116 |
| 42 | P00983 | A function online learning and prediction method for accelerating structural topology optimization and its application t | https://doi.org/10.1016/j.tws.2025.112942 |
| 43 | P00605 | Fast topology optimization of phononic crystal‐based metastructures for vibration isolation by deep learning | https://doi.org/10.1111/mice.13100 |
| 44 | P01151 | Two-scale topology optimization of multiscale structures and materials via deep neural networks for local and global buc | https://doi.org/10.1016/j.cma.2026.119038 |
| 45 | P00808 | A Geometric-Enhanced Neural Network Method for Scalable and High-Resolution Topology Optimization | https://doi.org/10.3390/sym18030537 |
| 68 | P00893 | Deep learning-aided topology design of metasurfaces for Rayleigh waves | https://doi.org/10.1093/jcde/qwae037 |
| 69 | P00860 | AI-Based Topology Optimization of Freehand Sketches | https://doi.org/10.1016/j.procir.2021.11.221 |
| 73 | P01994 | Practical topology optimization with deep reinforcement learning | https://doi.org/10.13140/rg.2.2.16548.95369 |
| 82 | P00842 | Topology Optimization via Frequency Tuning of Neural Design Representations | https://doi.org/10.1145/3485114.3485124 |
| 89 | P02084 | Hierarchical thermal design for battery packs using phase change materials | https://doi.org/10.1016/j.ijheatmasstransfer.2026.129081 |
| 91 | P01827 | TPMS-Optimized Cement Geometries for Carbon-Efficient Structural Performance | https://doi.org/10.70671/dq9am588 |
| 95 | P00533 | A complete Physics-Informed Neural Network-based framework for structural topology optimization | https://doi.org/10.1016/j.cma.2023.116401 |
| 99 | P01016 | Designing Porous Structure with Optimized Topology using Machine Learning | https://doi.org/10.1016/j.procir.2024.08.033 |

## B. Paywalled per OpenAlex (73)

| Order | pid | Title | DOI |
|---|---|---|---|
| 2 | P00557 | Machine learning-combined topology optimization for functionary graded composite structure design | https://doi.org/10.1016/j.cma.2021.114158 |
| 3 | P00751 | A robust-weighted hybrid nonlinear regression for reliability based topology optimization with multi-source uncertaintie | https://doi.org/10.1016/j.cma.2025.118360 |
| 6 | P00616 | A level-set-oriented and problem-independent robust topology optimization strategy based on convolutional neural network | https://doi.org/10.1016/j.cma.2026.118894 |
| 7 | P00607 | Machine learning powered sketch aided design via topology optimization | https://doi.org/10.1016/j.cma.2023.116651 |
| 9 | P00627 | Topology optimization based on deep representation learning (DRL) for compliance and stress-constrained design | https://doi.org/10.1007/s00466-020-01859-5 |
| 12 | P00754 | Machine-learning driven differentiable concurrent multiscale topology optimization framework for truss structures | https://doi.org/10.1016/j.cma.2026.119135 |
| 13 | P00732 | Machine learning-based multiscale topology optimization framework for nonlinear materials | https://doi.org/10.1016/j.ijmecsci.2026.111380 |
| 16 | P00979 | Machine‐Learning‐Powered, Rapid, Accurate, and Multi‐Target Mechanical Metamaterials Inverse Design | https://doi.org/10.1002/smll.202500634 |
| 17 | P02179 | Data-Driven-Design ( D 3 ) of multi-material systems: A novel framework and its application to viscoelastic metamaterial | https://doi.org/10.1016/j.ijsolstr.2026.113844 |
| 20 | P00767 | DEEP LEARNING FOR TOPOLOGY OPTIMIZATION OF TRIPLY PERIODIC MINIMAL SURFACE BASED GYROID-LIKE STRUCTURES | https://doi.org/10.12783/asc36/35824 |
| 21 | P01429 | Highly Efficient Multi-resolution Topology Optimization Based on the Kriging-Interpolation Network | https://doi.org/10.1007/978-3-031-49791-9_9 |
| 23 | P01132 | Optimization of Electric-Bike’s Frame Using Topology Optimization, Back Propagation Neural Network and Genetic Algorithm | https://doi.org/10.1007/978-981-97-8197-3_10 |
| 25 | P01258 | Generative design and optimization of lightweight mechanical structures based on physics-constrained neural networks | https://doi.org/10.1049/icp.2025.4682 |
| 27 | P00804 | Data-driven robust topology optimization using surrogate modeling, model reduction, and machine learning | https://doi.org/10.1016/j.engappai.2025.113136 |
| 28 | P00874 | Artificial neural network reinforced topological optimization for bionics-based tridimensional stereoscopic hydrogen sen | https://doi.org/10.1016/j.ijhydene.2023.11.325 |
| 32 | P01873 | Efficient Topology Optimization Design for Three-Dimensional Heat Transfer Structure Based on ResUNet-Involved Generativ | https://doi.org/10.1007/s10338-025-00587-8 |
| 33 | P00576 | Multiscale topology optimisation with nonparametric microstructures using three-dimensional convolutional neural network | https://doi.org/10.1080/17452759.2021.1913783 |
| 36 | P00915 | Topology optimization of smart structures to enhance the performances of vibration control and energy harvesting | https://doi.org/10.1088/1361-665x/ad69ea |
| 37 | P01859 | Structural topology optimization based on diffusion generative adversarial networks | https://doi.org/10.1016/j.engappai.2024.109444 |
| 39 | P00548 | Improving connectivity and accelerating multiscale topology optimization using deep neural network techniques | https://doi.org/10.1007/s00158-022-03223-y |
| 41 | P01500 | Super-Resolution Based Topology Optimization for Rapid Generation of Low Mass Structural Designs | https://doi.org/10.1109/aero58975.2024.10521001 |
| 48 | P01605 | Design-Aware Optimization of 2D Skeletal Structures Using conditional Generative Adversarial Networks (cGANs) | https://doi.org/10.1109/mercon67903.2025.11217036 |
| 50 | P01928 | A Two-Stage Integrated Approach for Accelerating Structural Topology Optimization Using VAE and SIMP | https://doi.org/10.1007/978-981-95-1723-7_11 |
| 52 | P00858 | Deep learning-driven topology optimization using principal stress information based on assumed source point | https://doi.org/10.1016/j.engstruct.2025.121203 |
| 53 | P00544 | A Parametric Level Set Method for Topology Optimization Based on Deep Neural Network | https://doi.org/10.1115/1.4050105 |
| 54 | P00833 | Comparative study on manifold learning approaches for parametric topology optimization problem via unsupervised deep lea | https://doi.org/10.1007/s11081-023-09806-y |
| 55 | P00719 | Deep learning accelerated topology optimization with inherent control of image quality | https://doi.org/10.1007/s00158-022-03433-4 |
| 56 | P02398 | Conditional diffusion models for the inverse design of lattice structures | https://doi.org/10.1007/s00158-025-03984-2 |
| 57 | P01101 | Topology optimization of piezoelectric structures based on multi-modal input neural network | https://doi.org/10.1016/j.engappai.2026.115159 |
| 59 | P01729 | Building Structure Optimization: A Framework Based on Multi-Agent Reinforcement Learning | https://doi.org/10.1109/icaace69793.2026.11508877 |
| 60 | P02490 | Deep Reinforcement Learning for Digital Materials Design | https://doi.org/10.1021/acsmaterialslett.1c00390 |
| 62 | P02524 | Kriging-assisted topology optimization of crash structures | https://doi.org/10.1016/j.cma.2019.02.002 |
| 63 | P00687 | Problem-independent machine learning-enhanced structural topology optimization of complex design domains based on isopar | https://doi.org/10.1016/j.eml.2024.102237 |
| 65 | P00553 | Problem-independent machine learning (PIML)-based topology optimization—A universal approach | https://doi.org/10.1016/j.eml.2022.101887 |
| 66 | P01855 | Generative Adversarial Networks With Synthetic Training Data for Enforcing Manufacturing Constraints on Topology Optimiz | https://doi.org/10.1115/detc2020-22399 |
| 67 | P00934 | Theory of Machine Learning Assisted Structural Optimization Algorithm and Its Application | https://doi.org/10.2514/1.j062195 |
| 70 | P00615 | Supervised deep learning for the moving morphable components topology optimization framework | https://doi.org/10.1016/j.engappai.2023.106436 |
| 71 | P00613 | Reliability-based optimization of structural topologies using artificial neural networks | https://doi.org/10.1016/j.probengmech.2022.103356 |
| 72 | P01457 | CNN-driven Approximate Algorithm of Topology Optimization Based on Initial Stress Learning | https://doi.org/10.26226/morressier.612f6735bc98103724100785 |
| 75 | P00650 | Enhancing topology optimization with adaptive deep learning | https://doi.org/10.1016/j.compstruc.2024.107527 |
| 77 | P00545 | Convolution Hierarchical Deep-Learning Neural Network Tensor Decomposition (C-HiDeNN-TD) for high-resolution topology op | https://doi.org/10.1007/s00466-023-02333-8 |
| 78 | P01100 | Topology Optimization Through Deep Neural Network for Different Mechanical and Thermomechanical Problems | https://doi.org/10.1115/imece2022-94604 |
| 79 | P00817 | DL4TO : A Deep Learning Library for Sample-Efficient Topology Optimization | https://doi.org/10.1007/978-3-031-38271-0_54 |
| 80 | P01856 | Intelligent design of key joints in aerial building machine using topology optimization and generative adversarial netwo | https://doi.org/10.1016/j.autcon.2024.105747 |
| 86 | P00690 | A machine learning-assisted structural optimization scheme for fast-tracking topology optimization | https://doi.org/10.1007/s00158-022-03181-5 |
| 87 | P02135 | Large language model agent as a mechanical designer | https://doi.org/10.1080/09544828.2026.2624356 |
| 90 | P00889 | Implicit geometry representation via neural operators on Riemannian manifolds for topology optimisation | https://doi.org/10.1016/j.cirp.2025.04.068 |
| 93 | P01398 | CoPR-DTO: collaboratively driven and periodically recalibrated dynamic topology optimization | https://doi.org/10.1117/12.3111177 |
| 94 | P00922 | Physics-guided deep learning for generative design of large-diameter tunnels under existing metro lines | https://doi.org/10.1016/j.autcon.2024.105901 |
| 101 | P01133 | A new level set structual topology optimization framework enhanced by nested physical informed neural network | https://doi.org/10.1007/s10409-025-25750-x |
| 103 | P00543 | Machine Learning-Driven Real-Time Topology Optimization Under Moving Morphable Component-Based Framework | https://doi.org/10.1115/1.4041319 |
| 107 | P00797 | SVR-TO-APMA: Hybrid efficient modelling and topology framework for stable topology optimization with accelerated perform | https://doi.org/10.1016/j.cma.2022.115762 |
| 115 | P01279 | A novel approach for topology optimization mirroring human intention: Introducing a pattern-embedded filter built by mac | https://doi.org/10.1016/j.cma.2026.118882 |
| 116 | P01382 | Variable-Resolution Topology Optimization Based on Dynamic Vision Transformer | https://doi.org/10.1115/1.4072316 |
| 117 | P02240 | A force neural network framework for structural optimization | https://doi.org/10.1016/j.engappai.2024.109991 |
| 118 | P00938 | Graph convolutional networks-driven multiscale topology optimization base on polygonal coarse-grid elements | https://doi.org/10.1016/j.ijmecsci.2025.110500 |
| 122 | P02336 | Inverse design of composite materials with desired mechanical behaviors based on conditional diffusion model | https://doi.org/10.1016/j.engstruct.2025.121417 |
| 125 | P01277 | A high-performance parallel algorithm based on problem independent machine learning (PIML) for large-scale topology opti | https://doi.org/10.1007/s10409-025-25942-x |
| 126 | P02399 | Integrating large models with topology optimization for conceptual design realization | https://doi.org/10.1016/j.aei.2025.103524 |
| 128 | P00957 | Data-Driven AI for Topology Optimization: A Comparative Study of CNN and Self-Attention Enhanced Architectures in Data-C | https://doi.org/10.1109/aihcir65563.2024.00048 |
| 129 | P00536 | A deep convolutional neural network for topology optimization with perceptible generalization ability | https://doi.org/10.1080/0305215x.2021.1902998 |
| 132 | P02292 | Heterogeneous Metamaterials Design Via Multiscale Neural Implicit Representation | https://doi.org/10.1115/1.4071438 |
| 133 | P01887 | Intelligent generative design of novel aluminum joints connecting wood members using generative adversarial networks | https://doi.org/10.1016/j.istruc.2026.111755 |
| 140 | P00774 | A multi-point synergistic gradient evolution method for topology optimization leveraging neural network with application | https://doi.org/10.1007/s00466-023-02358-z |
| 142 | P00551 | Deep super-resolution neural network for structural topology optimization | https://doi.org/10.1080/0305215x.2020.1846031 |
| 144 | P00902 | Data-driven enhanced multi-scale topology optimization of lattice structures | https://doi.org/10.1016/j.engstruct.2026.122097 |
| 145 | P00748 | Initial Design of Trusses using Topology Optimization in a Deep Learning Environment | https://doi.org/10.1109/fiti52050.2020.9424894 |
| 146 | P02006 | Continuous action reinforcement learning for topology optimization via capped-simplex projection | https://doi.org/10.1016/j.cma.2026.119446 |
| 148 | P01033 | Topologically optimal design and failure prediction using conditional generative adversarial networks | https://doi.org/10.1002/nme.6814 |
| 149 | P00781 | Machine learning-driven hotspot thermal management in chip heat sinks through topology optimization | https://doi.org/10.1016/j.icheatmasstransfer.2026.110632 |
| 150 | P00598 | Machine Learning to Aid Tuning of Numerical Parameters in Topology Optimization | https://doi.org/10.1115/1.4044228 |
| 153 | P02227 | Finite Operator Learning: Bridging neural operators and numerical methods for efficient parametric solution and optimiza | https://doi.org/10.1016/j.finel.2025.104506 |
| 160 | P01436 | Latent Space Diffusion Models With Auxiliary Losses for Structural Topology Optimization | https://doi.org/10.1115/imece2025-166864 |
