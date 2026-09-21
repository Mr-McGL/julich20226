# Presenter Notes

## 1. Inside VG-LAB: Selected Research Areas

* First, I would like to thank Boris for the opportunity to present my work  
* and to thank Sandra for inviting me to visit the center during the next two months.

<br>

* Although our groups have been collaborating over the past few years,

* I haven't been involved in those collaborations.



* For this reason, **first**, I wanted to frame my work in the context of my group.

## 2. URJC – Rey Juan Carlos University

* I belong to the Rey Juan Carlos University

* In Madrid, there are 6 public universities and URJC is the youngest one.

* However, we are the second largest by number of students.

## 3. ETSII

* I'm a member of the Computer Science School.

* We are 200 faculty members and we offer 8 bachelor's degree programs.

* Which is a lot of lecturing for a school of this size.

## 4. VG-LAB

* The VG-Lab is my research group.

* VG-Lab stands for Graphics and Visualization Lab.

* We are a fairly small group of only 5 faculty members.

## 5. VG-LAB

* In the early years, our group focused on computer graphics and high-performance computing.

* I never worked on HPC myself.

* I was focused on computer graphics and medical simulation.

* With the beginning of the Blue Brain Project and then the Human Brain Project,  
our main focus shifted from computer graphics to visualization;

* And in my particular case, to the application of machine learning and deep learning to the biomedical field.

## 6. Computer Graphics and Medical Simulation

* I didn't have too much time to prepare this presentation  
* I think it is too long; I want to focus on my recent work.  
* Therefore, I'm going to move fast through the next slides.

* I just want to highlight this project because it was carried out in cooperation with RWTH Aachen; with Professor Dr. Torsten Kuhlen,

* In the RASIMAS project, we worked on an ultrasound-guided regional anesthesia simulator.

## 7. Computer Graphics and Medical Simulation

* This is our projection radiography simulator.

* I just mention it because it was one of our latest medical simulators.

* It lets the physicians train with different patient models, and  
* it simulates the full procedure in real time.

* This includes patient positioning and machine settings.

## 8. Enhancing Simulated X-Ray Images

Enhancing simulated X-ray images:  
* Monte Carlo methods accurately simulate how photons interact with different materials in the scene.

However, producing high-quality images takes a lot of computing time.  
The top-left image was simulated using one billion photons.  
It took about 70 hours on a server running 20 threads in parallel.  
The center image was simulated in less than one second on a desktop PC.  
However, this deterministic simulation only accounts for the energy absorbed by tissues.  
It does not include scattering.  
We aim to use deep learning to add scattering effects to the final image.

## 9. VG-LAB in the Human Brain Project

* Our group was first involved in the Blue Brain Project.  
* In this project, many of our group members started a visualization and exploratory analysis research line.

* This research line was consolidated first in the Human Brain Project,  
and now in EBRAINS 2.0 and the Virtual Brain Twin project.

## 10. VG-LAB in EBRAINS

EBRAINS is a European project.  
Here are our contributions to EBRAINS 2.0 and the Virtual Brain Twin project.

## 11. Visualization Ecosystem

* Probably, most of you have seen this slide before.

* It is not my work.

* It shows the philosophy behind the visualization tools being developed in EBRAINS.

* Basically, the idea is to develop independent tools that allow us to visualize  
structural, topological, and activity data from the brain at different scales

* And provide them with communication mechanisms so they can work together.

## 12. MeLVin

* During the HBP, I worked a little bit on visualization,

* But going in the opposite direction,

* I worked on a framework to integrate web-based visualization technologies and data analysis tools.


MeLVin: https://vg-lab.es/melvin/  
MeLVin is a web-based meta-framework for building visualization applications.  
It is especially useful for rapid prototyping and interactive exploratory analysis.  
It connects visualizations and data analysis tools built with different technologies, so they can work together.  
It can be extended and adapted to different research areas.  
Users can define the data analysis process with simple flowcharts.  
Most flowchart-based data mining tools use visualizations only to show the final results.  
MeLVin also lets users include visualizations and interactions between them as part of the analysis process.

## 13. VG-LAB in the Human Brain Project

* During the HBP, I started working with neuroanatomists from the Cajal Institute.

* They were interested in developing algorithms to automate the segmentation of their data.

* And this is how we started working on deep learning.

* In the remaining time that I have, I would like to show my  
first and latest work in this line of research.

## 14. DeepSpineNet

* Our first work was DeepSpineNet, a deep learning tool for automatic dendritic spine segmentation from confocal microscopy images.

* The system works pretty well, but it is not perfect.  
So we had to develop a set of human-supervised correction algorithms.


----

Challenges:  
Scientific datasets are often small, and their labels are incomplete or imprecise.  
We propose three approaches:  
- Automatic algorithms to improve the quality of the training data.  
- Training techniques to reduce overfitting caused by poor-quality data.  
- Correction algorithms to further improve the ground-truth labels.

## 15. DeepSpineNet

As most of you already know, deep learning models work well for many segmentation and classification tasks.  
However, applying them to biomedical images can be difficult.

First, we work with 3D image stacks.  
Many state-of-the-art models mainly work with 2D images.  
Processing 3D images requires more complex models, often with many parameters.

These models need large training datasets.  
Labeling dendritic spines is difficult and takes a lot of time.  
This makes it hard to obtain enough labeled data to train reliable models.

Finally, the labels in many datasets are incomplete.  
Researchers are often interested in only one dendritic branch in the image stack.  
As a result, other parts of the image remain unlabeled.

## 17. DeepSpineNet

Our approach has three components:  
- A preprocessing module to prepare the data.  
- A deep learning model designed for this task.  
- A postprocessing module that lets users correct the model's errors.

## 18. DeepSpineNet

Our approach has three components:  
- A preprocessing module to prepare the data.  
- A deep learning model designed for this task.  
- A postprocessing module that lets users correct the model's errors.

## 19. DeepSpineNet

Our approach has three components:  
- A preprocessing module to prepare the data.  
- A deep learning model designed for this task.  
- A postprocessing module that lets users correct the model's errors.

## 20. DeepSpineNet

Our approach has three components:  
- A preprocessing module to prepare the data.  
- A deep learning model designed for this task.  
- A postprocessing module that lets users correct the model's errors.

## 21. DeepSpineNet

The main goal of the preprocessing module is to create the training set  
and automatically reconstruct the necks of disconnected dendritic spines.

This figure shows the model's performance with and without the preprocessing module.

## 23. Analyzing LFPs

* I would like to finish my presentation by showing my most recent work.  
* I have been working in this line of research for the last year and we have some preliminary results.

<br>

* In this work, we are working with the Experimental and Computational Electrophysiology Group from the Cajal Institute.

* They work with intracranial EEG recordings.

* The signals captured by electrodes are known as local field potentials (LFPs).

* Those signals are a mixture of the activity of different brain regions.

* They use blind source separation techniques to recover the activity of different brain regions.

* I have always wanted to show visually how ICA works, and  
* yesterday I asked ChatGPT for a video.  
* It was not exactly what I wanted. But I think it is good enough.


* However, I think I'm going to skip it to go directly to our work.

## 26. ICA Limitations

The main limitation that we have to face with ICA is that the source signals cannot be correlated.

Therefore, we are forced to remove synchronous activity from our analysis  
and we can only work with baseline activity;

And just keep basal activity, which is highly complex and apparently random.

## 28. ICA Limitations

Here we have a picture with the activity types, basal and synchronous.

## 29. LFP Generators

This is what we have after the blind source separation.

At the top, we have the reconstructed signals, which are the activity of different brain regions.

The bottom row shows how the activity is distributed across the electrodes.

## 30. Motivation

* Most of the recordings contain baseline activity, which is highly complex and apparently random.

* Our goal is to see if there are patterns in baseline activity that allow us to identify brain regions;

* And whether these patterns are consistent across subjects.

* We also want to see whether DL methods identify patterns beyond our handcrafted features.

## 31. Methodology

* We have trained ML models based on handcrafted features;  
* and DL models operating on raw signals  
to determine whether there are patterns in baseline activity that allow us to identify brain regions.

* We compare models with different levels of complexity  
to see whether linear models can identify the generators,  
or whether we need more flexible nonlinear models.

## 32. Results

* Both types of models can identify brain regions from baseline activity in the test set.

* The deep learning models perform significantly better than the models based on handcrafted features.

## 33. Results

* Next, we asked whether deep learning finds patterns beyond our handcrafted features.

* We looked at the transformer's predictions and their probabilities.

* We focused on cases where the models based on handcrafted features made mistakes.

* In these cases, the deep learning model made predictions with high confidence.

## 34. Future lines of work

* We now want to understand which patterns the deep learning models use.

* We plan to explore explainable AI and mechanistic interpretability.

* These approaches may be easier to apply to images and text, but we want to try them with our signals.

* We also want to distinguish healthy regions from regions with pathological activity.

* The aim is to do this using baseline activity.

* This could help identify regions involved in epilepsy without provoking a seizure.
