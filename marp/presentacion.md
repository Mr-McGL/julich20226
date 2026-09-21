---
marp: true
theme: vg-lab
size: 4:3
paginate: false
title: 'Inside VG-LAB: My Role and Selected Research Areas'
author: 'Marcos García Lorenzo'
---

<!-- _class: cover -->

# Inside VG-LAB: <br>*Selected Research Areas*

*Marcos García Lorenzo*
marcos.garcía@urjc.es


<!--
* First, I would like to thank Boris for the opportunity to present my work.

* I would also like to thank Sandra for inviting me to spend the next two months at the center.

* Our groups have been collaborating over the past few years.

* I haven't been involved in those collaborations.

* So I would like to start by putting my work in the context of my group.
-->

---

<!-- _class: split -->

# URJC – Rey Juan Carlos University

* Founded in 1996
* Sixth public university established in the Community of Madrid
* 5 campuses: Madrid, Móstoles, Alcorcón, Fuenlabrada, and Aranjuez
* More than 40,000 students
* Second in the Community of Madrid and seventh in Spain by student enrollment

![Image 4](assets/images/image5.png)

<!--
* I work at Rey Juan Carlos University.

* Madrid has six public universities, and URJC is the youngest.

* However, we are the second largest by number of students.
-->

---

<!-- _class: split -->

# ETSII

<div class="box" style="--x: 132.24px; --y: 309px; --w: 367.77px; --h: 268.83px; --z: 4; --fill: white">

* School of Computer Science
* Around 200 faculty members
* 8 bachelor's degree programs
* 9 double bachelor's degree programs
* 6 master's degree programs
* 1 PhD program in IT


</div>

<div class="media" style="--x: 498.96px; --y: 311.57px; --w: 337.79px; --h: 184.95px; --z: 2; --outline: 2.66px solid rgba(0,0,0,1.0000); --outline-offset: -1.33px">

![image8.png](assets/images/image7.png)

</div>

<div class="media" style="--x: 132.24px; --y: 173.06px; --w: 704.50px; --h: 116.40px; --z: 3; --outline: 2.66px solid rgba(0,0,0,1.0000); --outline-offset: -1.33px; --image-left: -3.02531%; --image-top: -257.36380%; --image-width: 257.25458%; --image-height: 502.13407%">

![Image 5](assets/images/image8.jpg)

</div>

<div class="media" style="--x: 508.83px; --y: 525.00px; --w: 282.29px; --h: 176.72px; --z: 5; --outline: 24.00px solid rgba(0,0,0,1.0000); --outline-offset: -12.00px">

![image10.jpeg](assets/images/image9.jpg)

</div>

<div class="caption" style="--x: 708.48px; --y: 660.08px; --w: 152.12px; --h: 41.63px; --z: 6; --fill: rgba(255,255,255,1.0000)">

MÓSTOLES

</div>

<!--
* I'm a member of the School of Computer Science.

* We have around 200 faculty members and offer eight bachelor's degree programs.

* That is a lot of teaching for a school of this size.
-->

---

<!-- _class: figure -->

# VG-LAB

<div class="media" style="--x: 794.69px; --y: 548.07px; --w: 117.30px; --h: 117.30px; --z: 2">

![image4](assets/images/image4.png)

</div>

<div class="media" style="--x: 27.01px; --y: 277.36px; --w: 905.96px; --h: 228.92px; --z: 3">

![image10](assets/images/image10.png)

</div>

<!--
* VG-LAB is my research group.

* VG-LAB stands for Graphics and Visualization Lab.

* We are a fairly small group, with only five faculty members.
-->

---

<!-- _class: text -->

# VG-LAB

**Early research areas:**

* **Computer graphics:** Virtual reality, haptic interaction, medical training simulators, simulation, rendering
* **High-performance computing:** Distributed computing, GPGPU, load balancing

**Current research areas:**

* **Visualization:** Scientific visualization, information visualization, and exploratory analysis
* **Machine learning and deep learning**


<!--
* In the early years, our group focused on computer graphics and high-performance computing.

* I never worked on high-performance computing myself.

* I focused on computer graphics and medical simulation.

* With the Blue Brain Project and then the Human Brain Project, our main focus shifted to visualization.

* In my case, I started applying machine learning and deep learning to biomedical research.
-->

---

<!-- _class: figure -->

# Computer Graphics and Medical Simulation

<div class="media" style="--x: 77.47px; --y: 198.03px; --w: 331.04px; --h: 166.78px; --z: 2">

![image11](assets/images/image11.jpg)

</div>

<div class="media" style="--x: 56.66px; --y: 401.68px; --w: 372.66px; --h: 256.00px; --z: 3">

![Picture 2](assets/images/image12.jpg)

</div>

<div class="media" style="--x: 480.00px; --y: 245.41px; --w: 442.78px; --h: 362.28px; --z: 5">

![image13](assets/images/image13.png)

</div>

<div class="media" style="--x: 569.72px; --y: 266.53px; --w: 171.85px; --h: 158.13px; --z: 6">

![image14](assets/images/image14.jpg)

</div>

<!--
* I didn't have much time to prepare this presentation.

* I think it is too long, and I want to focus on my recent work.

* So I will go through the next few slides quickly.

* I want to highlight this project because we worked with RWTH Aachen and Professor Torsten Kuhlen.

* In the RASIMAS project, we worked on a simulator for ultrasound-guided regional anesthesia.
-->

---

<!-- _class: sidebar -->

# Computer Graphics and Medical Simulation 

***Projectional Radiography Simulator***: An interactive learning environment for diagnostic radiography that helps educators connect theory and practice

[https://vg-lab.es/xraysim/](https://vg-lab.es/xraysim/)

<video controls preload="none" playsinline poster="assets/images/image18.png" src="assets/videos/1.mp4" aria-label="videoplayback"></video>

![Picture 4](assets/images/image16.png)

![Picture 6](assets/images/image17.png)

![Picture 2](assets/images/image15.png)

<!--
* I will go through this radiography simulator quickly.

* I mention it because it was one of our most recent medical simulators.

* It lets users train with different patient models.

* It simulates the full procedure in real time.

* This includes patient positioning and machine settings.
-->

---

<!-- _class: sidebar -->

# Enhancing Simulated X-Ray Images

**Deterministic simulation** +  
**Deep learning**  
to mimic high-quality Monte Carlo simulations with a high computational cost

<div class="media" style="--x: 349.86px; --y: 199.62px; --w: 576.12px; --h: 246.30px; --z: 4">

![Image 18](assets/images/image19.png)

</div>

<div class="media" style="--x: 386.14px; --y: 445.27px; --w: 107.09px; --h: 236.87px; --z: 5">

![Image 20](assets/images/image20.png)

</div>

<div class="media" style="--x: 586.98px; --y: 458.48px; --w: 288.09px; --h: 214.66px; --z: 6; --image-left: -31.31065%; --image-top: -35.65964%; --image-width: 169.64104%; --image-height: 170.75920%">

![Image 22](assets/images/image21.png)

</div>

<!--
* Monte Carlo methods accurately simulate how photons interact with different materials.

* However, producing high-quality images takes a lot of computing time.

* The top-left image was simulated using one billion photons.

* It took about 70 hours on a server running 20 threads in parallel.

* The center image was simulated in less than one second on a desktop PC.

* However, this deterministic simulation only accounts for the energy absorbed by tissues.

* It does not include scattering.

* We aim to use deep learning to add scattering effects to the final image.
-->

---

<!-- _class: text -->

# VG-LAB in the Human Brain Project


**Ramp-Up**  
> T7.3.2 – Neuroscience-specific visualization

**SGA1**  
> T1.4.2 – Visual analysis tools for microanatomical data  
>T7.3.2 – Neuroscience-specific visualization

**SGA2**  
>T1.4.4 – Towards an integrated framework for the acquisition and early analysis of microanatomical data  
>T7.3.8 – In-situ visual analysis of simulation data  
>T7.3.9 – Low-level visualisation backend

**SGA3**  
> T5.7 – Visualisation framework (SC3)

<!--
* Our group first took part in the Blue Brain Project.

* In this project, many group members started working on visualization and exploratory analysis.

* This work continued in the Human Brain Project.

* It now continues in EBRAINS 2.0 and the Virtual Brain Twin project.
-->

---

<!-- _class: split -->

# VG-LAB in EBRAINS

<!--
* EBRAINS is a European project.

* Here are our contributions to EBRAINS 2.0 and the Virtual Brain Twin project.
-->

**Virtual Brain Twin Project (HORIZON-HLTH-2023-TOOL-05-03)**  
> Developing a GUI for integrative workflows

**EBRAINS 2.0 Project (HORIZON-INFRA-2022-SERV-B-01)**
> Developing SimVisSuite, a visualization framework for neuroscience data

![EBRAINS 2.0](assets/images/EBRAINS.png)

---

<!-- _class: figure -->

# Visualization Ecosystem


<div class="media" style="--x: 155.78px; --y: 172.00px; --w: 675.26px; --h: 505.61px; --z: 3">

![Content placeholder 4](assets/images/image22.png)

</div>

<!--
* Most of you have probably seen this slide before.

* This is not my own work.

* It shows the idea behind the visualization tools being developed in EBRAINS.

* The idea is to develop separate tools to visualize brain data at different scales.

* These tools cover brain structure, connections, and activity.

* They also have ways to communicate, so they can work together.
-->

---


<!-- _class: sidebar -->

# MeLVin

A graphical meta-framework for prototyping data visualization and exploratory analysis

<video controls preload="none" playsinline poster="assets/images/image26.png" src="assets/videos/2.mp4" aria-label="SnapSave.io-MeLVin(360p)"></video>

![Picture 2](assets/images/image23.png)

![Picture 6](assets/images/image24.png)

![Picture 4](assets/images/image25.png)


<!--
* During the Human Brain Project, I also did some work on visualization.

* I took a different approach.

* I worked on a framework to bring together web-based visualization and data analysis tools.

* MeLVin is a web-based framework for building visualization applications.

* It is especially useful for rapid prototyping and interactive exploratory analysis.

* It connects visualizations and analysis tools built with different technologies.

* It can be extended and adapted to different research areas.

* Users can define the analysis process with simple flowcharts.

* Most data mining tools based on flowcharts use visualizations only to show the final results.

* MeLVin also includes visualizations and interactions between them in the analysis process.

MeLVin: https://vg-lab.es/melvin/
-->

---

# VG-LAB in the Human Brain Project

**Ramp-Up**  
> T7.3.2 – Neuroscience-specific visualization

**SGA1**  
> **T1.4.2 – Visual analysis tools for microanatomical data**  
> T7.3.2 – Neuroscience-specific visualization

**SGA2**  
> **T1.4.4 – Towards an integrated framework for the acquisition and early analysis of microanatomical data** 
> T7.3.8 – In-situ visual analysis of simulation data  
>T7.3.9 – Low-level visualisation backend

**SGA3**  
>  T5.7 – Visualisation framework (SC3)

<!--
* During the Human Brain Project, I started working with neuroanatomists from the Cajal Institute.

* They wanted algorithms to automate the segmentation of their data.

* This is how we started working on deep learning.

* In the time I have left, I would like to show our first and most recent work in this area.
-->

---

<!-- _class: sidebar -->

# DeepSpineNet

**Automatic dendritic spine segmentation using deep learning** +  
user-supervised correction algorithms

[https://vg-lab.es/deepspinenet/](https://vg-lab.es/deepspinenet/)



<video controls preload="none" playsinline poster="assets/images/image28.png" src="assets/videos/3.mp4" aria-label="DSNet2"></video>

![Picture 2](assets/images/image30.png)

<video controls preload="none" playsinline poster="assets/images/image29.png" src="assets/videos/4.mp4" aria-label="DSNet3"></video>

![Picture 4](assets/images/image27.png)

<!--
* Our first project was DeepSpineNet.

* It uses deep learning to automatically segment dendritic spines in confocal microscopy images.

* The system works quite well, but it is not perfect.

* So we developed a set of correction algorithms guided by the user.

* Scientific datasets are often small, and their labels are incomplete or imprecise.

* We propose three approaches to address these problems.

* First, automatic algorithms to improve the quality of the training data.

* Second, training techniques to reduce overfitting caused by poor-quality data.

* Third, correction algorithms to further improve the reference labels.
-->

---

<!-- _class: text -->

# DeepSpineNet

**Challenges**:
Several challenges make these techniques difficult to apply in biomedical research:

* **Image stacks:**  Many state-of-the-art models work with 2D images.  
3D image stacks require complex models.

* **Limited training data:**  Limited data is available for training.  
Complex problems require complex models.  
Complex models require large datasets for training.

* **Weakly labeled datasets:** Incomplete segmentations.  
For instance, scientists are generally not interested in segmenting the entire image.

<!--
* As most of you know, deep learning works well for many segmentation and classification tasks.

* However, applying it to biomedical images can be difficult.

* First, we work with 3D image stacks.

* Many state-of-the-art models mainly work with 2D images.

* Processing 3D images requires more complex models, often with many parameters.

* These models need large training datasets.

* Labeling dendritic spines is difficult and takes a lot of time.

* This makes it hard to get enough labeled data to train reliable models.

* Finally, the labels in many datasets are incomplete.

* Researchers are often interested in only one dendritic branch in the image stack.

* Other parts of the image remain unlabeled.
-->
---

<!-- _class: figure -->
# DeepSpineNet

![problems](assets/images/img1.png)

<!--
* Here are some examples of the segmentation challenges.

* The top row shows the microscopy images.

* The bottom row shows the segmentations.

* The marked areas highlight some of the problems.
-->

---

<!-- _class: figure -->

# DeepSpineNet

<div class="diagram" style="--diagram-ratio: 1084 / 935">

![Picture 2](assets/images/image36.jpg)

</div>

<!--
* Our approach has three components.

* A preprocessing module to prepare the data.

* A deep learning model designed for this task.

* A postprocessing module that lets users correct the model's errors.
-->

---

<!-- _class: figure -->

# DeepSpineNet

<div class="diagram" style="--diagram-ratio: 1084 / 935">

![Picture 2](assets/images/image36.jpg)

<div class="diagram-highlight" role="img" aria-label="Preprocessing highlighted area" style="--x: 14.2066%; --y: 3.6364%; --w: 59.5018%; --h: 24.0642%"></div>

</div>

<div class="figure-caption">

**Preprocessing**

</div>

<!--
* First, the preprocessing module prepares the data for training.
-->

---

<!-- _class: figure -->


# DeepSpineNet

<div class="diagram" style="--diagram-ratio: 1084 / 935">

![Picture 2](assets/images/image36.jpg)

<div class="diagram-highlight" role="img" aria-label="Training the DL model highlighted area" style="--x: 0.5535%; --y: 27.8075%; --w: 98.8930%; --h: 21.6043%"></div>

<div class="diagram-highlight" role="img" aria-label="DL model highlighted area" style="--x: 13.3764%; --y: 58.3957%; --w: 7.3801%; --h: 6.4171%"></div>

</div>

<div class="figure-caption">

**Training the DL model** · **DL model**

</div>

<!--
* Next, we train the deep learning model.

* We then use it to segment the images.
-->

---

<!-- _class: figure -->

# DeepSpineNet

<div class="diagram" style="--diagram-ratio: 1084 / 935">

![Picture 2](assets/images/image36.jpg)

<div class="diagram-highlight" role="img" aria-label="Postprocessing highlighted area" style="--x: 36.0701%; --y: 53.5829%; --w: 63.2841%; --h: 45.2406%"></div>

</div>

<div class="figure-caption">

**Postprocessing**

</div>

<!--
* Finally, the postprocessing module lets users correct the model's errors.
-->

---

<!-- _class: figure -->

# DeepSpineNet

![Picture 6](assets/images/image37.jpg)

<!--
* The preprocessing module creates the training set.

* It also automatically reconstructs the necks of disconnected dendritic spines.

* This figure compares the model's performance with and without preprocessing.
-->

---

<!-- _class: figure -->

# EspINA

<div class="media" style="--x: 224.69px; --y: 187.30px; --w: 509.15px; --h: 509.15px; --z: 3">

<video controls preload="none" playsinline poster="assets/images/image38.png" src="assets/videos/5.mp4"></video>

</div>

<!--
* This video shows EspINA.

[Play the video.]
-->

---

<!-- _class: text -->

# Analyzing LFPs

* In collaboration with the Experimental and Computational Electrophysiology Group (https://cajal.csic.es/en/experimental-and-computational-electrophysiology/), which belongs to the Cajal Neuroscience Center at the Spanish National Research Council (CSIC).

<br>

* They study brain activity using intracranial EEG recordings.
* The signals captured by electrodes are known as local field potentials (LFPs).
* These signals are a mixture of neuronal activity from different regions.
* This group has been working for years on the development of blind source separation techniques to isolate activity from different brain regions.
* Several methods exist, but they work with a customized version of Independent Component Analysis (ICA).
* This technique has several limitations.


<!--
* I would like to finish by showing my most recent work.

* I have been working in this area for the past year, and we have some preliminary results.

* We work with the Experimental and Computational Electrophysiology Group from the Cajal Institute.

* They study brain activity using intracranial EEG recordings.

* The signals recorded by the electrodes are called local field potentials, or LFPs.

* These signals mix activity from different brain regions.

* The group uses blind source separation to recover the activity of each region.

* They use a customized version of independent component analysis, or ICA.

* I have always wanted to show visually how ICA works.

* Yesterday, I asked ChatGPT for a video.

* It was not exactly what I wanted, but I think it is good enough.

* However, I think I will skip it and go straight to our work.
-->

---

<!-- _class: figure -->
 
# The Cocktail Party Problem

<div class="media" style="--x: 224.69px; --y: 187.30px; --w: 509.15px; --h: 509.15px; --z: 3">

<video controls preload="none" playsinline src="assets/videos/v1.mp4"></video>

</div>

<!--
[Play the video if time allows.]
-->

---

<!-- _class: figure -->

# The Cocktail Party Problem

<div class="media" style="--x: 224.69px; --y: 187.30px; --w: 509.15px; --h: 509.15px; --z: 3">

<video controls preload="none" playsinline src="assets/videos/v2.mp4"></video>

</div>

<!--
[Play the video if time allows.]
-->

---

<!-- _class: text -->

# ICA Limitations


* The results depend on the selected number of sources, N. Several approaches exist to estimate this number.
<br>

* Basic techniques cannot recover the original signal amplitudes.
<br>

* Source signals cannot be correlated.

    * We must remove synchronous activity from our analysis.
    * We can only work with baseline activity.

<br><br><br><br><br><br><br><br>


<!--
* ICA has several limitations.

* We need to choose the number of sources.

* Basic methods cannot recover the original signal amplitudes.

* For us, the main limitation is that the source signals cannot be correlated.

* So we remove synchronous activity from our analysis.

* We only keep baseline activity.

* This activity is highly complex and seems random.
-->

---



<!-- _class: figure -->

# The Cocktail Party Problem

<div class="media" style="--x: 224.69px; --y: 187.30px; --w: 509.15px; --h: 509.15px; --z: 3">

<video controls preload="none" playsinline src="assets/videos/v3.mp4"></video>

</div>

<!--
[Play the video if time allows.]
-->

---

<!-- _class: figure -->

# ICA Limitations

![](assets/images/theta2.png)

<!--
* This figure shows two types of activity: baseline and synchronous.
-->

---

<!-- _class: figure -->

# LFP Generators

![](assets/images/LFPG.png)

<!--
* This is what we get after blind source separation.

* At the top, we have the reconstructed signals from different brain regions.

* The bottom row shows how the activity is distributed across the electrodes.
-->

---

# Motivation

* Most of our recordings contain baseline activity.
* This activity is highly complex and apparently random.
<br>

**Our objective**:
* To determine whether we can identify patterns in baseline activity that allow us to distinguish brain regions.
* To determine whether these patterns are consistent across subjects.

> Methods based on handcrafted features usually offer better interpretability, but they are less powerful than DL models.
* Our secondary objective is to assess whether DL methods identify patterns beyond the handcrafted features we have extracted.

<br><br><br><br>

<!--
* Most of our recordings contain baseline activity.

* This activity is very complex and seems random.

* We want to find patterns that help us identify brain regions.

* We also want to see if these patterns are consistent across subjects.

* Models based on handcrafted features are usually easier to interpret.

* We want to know whether deep learning can find patterns that these features miss.
-->

---

# Methodology

* We have trained ML models based on handcrafted features and DL models operating on raw signals to determine whether there are patterns in baseline activity that allow us to identify brain regions.

* We compare models with different levels of complexity to determine whether the relationships among handcrafted features that support generator identification can be captured by linear models or require more flexible nonlinear functions.

<br><br><br><br><br><br>

<!--
* We trained two types of models to identify brain regions.

* The first uses handcrafted features extracted from the signals.

* The second uses deep learning on the raw signals.

* We also compare simpler and more complex models.

* This helps us see whether linear models are enough to identify the generators.

* Or whether we need more flexible, nonlinear models.
-->
---

<!-- _class: results -->

# Results

* Both feature-based and deep learning models identify brain regions from baseline activity in the test set.

* Deep learning models perform significantly better than feature-based models.

![Picture 2](assets/images/r1.png)

<!--
* Both types of models can identify brain regions from baseline activity in the test set.

* The deep learning models perform significantly better than the models based on handcrafted features.
-->

---

<!-- _class: results -->

# Results

Does deep learning capture patterns beyond our handcrafted features?

* We first examined the transformer's predictions and output probabilities.
* We then focused on cases misclassified by the feature-based models.
* In these cases, the deep learning model made predictions with high confidence.

![Picture 2](assets/images/r2.png)

<!--
* Next, we asked whether deep learning finds patterns beyond our handcrafted features.

* We looked at the transformer's predictions and their probabilities.

* We focused on cases where the models based on handcrafted features made mistakes.

* In these cases, the deep learning model made predictions with high confidence.
-->

---
# Future Work
* In recent years, significant effort has been devoted to the study of DL interpretability:
    * Explainable AI (XAI)
    * Mechanistic interpretability
  > This may be easier with images and text, but it is worth trying.
* Once we have shown that baseline activity contains patterns that allow us to identify brain regions, we want to determine whether we can distinguish healthy regions from regions with pathological activity.
  > In the context of epilepsy, seizures are sometimes provoked to identify regions. Being able to detect a region with pathological activity using baseline activity would be a major advance.

<!--
* We now want to understand which patterns the deep learning models use.

* We plan to explore explainable AI and mechanistic interpretability.

* These approaches may be easier to apply to images and text, but we want to try them with our signals.

* We also want to distinguish healthy regions from regions with pathological activity.

* The aim is to do this using baseline activity.

* This could help identify regions involved in epilepsy without provoking a seizure.
-->

