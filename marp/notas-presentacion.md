# Presenter Notes

## 1. Inside VG-LAB: Selected Research Areas

* First, I would like to thank Boris for the opportunity to present my work.

* I would also like to thank Sandra for inviting me to spend the next two months at the center.

* Our groups have been collaborating over the past few years.

* I haven't been involved in those collaborations.

* So I would like to start by putting my work in the context of my group.

## 2. URJC – Rey Juan Carlos University

* I work at Rey Juan Carlos University.

* Madrid has six public universities, and URJC is the youngest.

* However, we are the second largest by number of students.

## 3. ETSII

* I'm a member of the School of Computer Science.

* We have around 200 faculty members and offer eight bachelor's degree programs.

* That is a lot of teaching for a school of this size.

## 4. VG-LAB

* VG-LAB is my research group.

* VG-LAB stands for Graphics and Visualization Lab.

* We are a fairly small group, with only five faculty members.

## 5. VG-LAB

* In the early years, our group focused on computer graphics and high-performance computing.

* I never worked on high-performance computing myself.

* I focused on computer graphics and medical simulation.

* With the Blue Brain Project and then the Human Brain Project, our main focus shifted to visualization.

* In my case, I started applying machine learning and deep learning to biomedical research.

## 6. Computer Graphics and Medical Simulation

* I didn't have much time to prepare this presentation.

* I think it is too long, and I want to focus on my recent work.

* So I will go through the next few slides quickly.

* I want to highlight this project because we worked with RWTH Aachen and Professor Torsten Kuhlen.

* In the RASIMAS project, we worked on a simulator for ultrasound-guided regional anesthesia.

## 7. Computer Graphics and Medical Simulation

* I will go through this radiography simulator quickly.

* I mention it because it was one of our most recent medical simulators.

* It lets users train with different patient models.

* It simulates the full procedure in real time.

* This includes patient positioning and machine settings.

## 8. Enhancing Simulated X-Ray Images

* Monte Carlo methods accurately simulate how photons interact with different materials.

* However, producing high-quality images takes a lot of computing time.

* The top-left image was simulated using one billion photons.

* It took about 70 hours on a server running 20 threads in parallel.

* The center image was simulated in less than one second on a desktop PC.

* However, this deterministic simulation only accounts for the energy absorbed by tissues.

* It does not include scattering.

* We aim to use deep learning to add scattering effects to the final image.

## 9. VG-LAB in the Human Brain Project

* Our group first took part in the Blue Brain Project.

* In this project, many group members started working on visualization and exploratory analysis.

* This work continued in the Human Brain Project.

* It now continues in EBRAINS 2.0 and the Virtual Brain Twin project.

## 10. VG-LAB in EBRAINS

* EBRAINS is a European project.

* Here are our contributions to EBRAINS 2.0 and the Virtual Brain Twin project.

## 11. Visualization Ecosystem

* Most of you have probably seen this slide before.

* This is not my own work.

* It shows the idea behind the visualization tools being developed in EBRAINS.

* The idea is to develop separate tools to visualize brain data at different scales.

* These tools cover brain structure, connections, and activity.

* They also have ways to communicate, so they can work together.

## 12. MeLVin

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

## 13. VG-LAB in the Human Brain Project

* During the Human Brain Project, I started working with neuroanatomists from the Cajal Institute.

* They wanted algorithms to automate the segmentation of their data.

* This is how we started working on deep learning.

* In the time I have left, I would like to show our first and most recent work in this area.

## 14. DeepSpineNet

* Our first project was DeepSpineNet.

* It uses deep learning to automatically segment dendritic spines in confocal microscopy images.

* The system works quite well, but it is not perfect.

* So we developed a set of correction algorithms guided by the user.

* Scientific datasets are often small, and their labels are incomplete or imprecise.

* We propose three approaches to address these problems.

* First, automatic algorithms to improve the quality of the training data.

* Second, training techniques to reduce overfitting caused by poor-quality data.

* Third, correction algorithms to further improve the reference labels.

## 15. DeepSpineNet

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

## 16. DeepSpineNet

* Here are some examples of the segmentation challenges.

* The top row shows the microscopy images.

* The bottom row shows the segmentations.

* The marked areas highlight some of the problems.

## 17. DeepSpineNet

* Our approach has three components.

* A preprocessing module to prepare the data.

* A deep learning model designed for this task.

* A postprocessing module that lets users correct the model's errors.

## 18. DeepSpineNet

* First, the preprocessing module prepares the data for training.

## 19. DeepSpineNet

* Next, we train the deep learning model.

* We then use it to segment the images.

## 20. DeepSpineNet

* Finally, the postprocessing module lets users correct the model's errors.

## 21. DeepSpineNet

* The preprocessing module creates the training set.

* It also automatically reconstructs the necks of disconnected dendritic spines.

* This figure compares the model's performance with and without preprocessing.

## 22. EspINA

* This video shows EspINA.

[Play the video.]

## 23. Analyzing LFPs

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

## 24. The Cocktail Party Problem

[Play the video if time allows.]

## 25. The Cocktail Party Problem

[Play the video if time allows.]

## 26. ICA Limitations

* ICA has several limitations.

* We need to choose the number of sources.

* Basic methods cannot recover the original signal amplitudes.

* For us, the main limitation is that the source signals cannot be correlated.

* So we remove synchronous activity from our analysis.

* We only keep baseline activity.

* This activity is highly complex and seems random.

## 27. The Cocktail Party Problem

[Play the video if time allows.]

## 28. ICA Limitations

* This figure shows two types of activity: baseline and synchronous.

## 29. LFP Generators

* This is what we get after blind source separation.

* At the top, we have the reconstructed signals from different brain regions.

* The bottom row shows how the activity is distributed across the electrodes.

## 30. Motivation

* Most of our recordings contain baseline activity.

* This activity is very complex and seems random.

* We want to find patterns that help us identify brain regions.

* We also want to see if these patterns are consistent across subjects.

* Models based on handcrafted features are usually easier to interpret.

* We want to know whether deep learning can find patterns that these features miss.

## 31. Methodology

* We trained two types of models to identify brain regions.

* The first uses handcrafted features extracted from the signals.

* The second uses deep learning on the raw signals.

* We also compare simpler and more complex models.

* This helps us see whether linear models are enough to identify the generators.

* Or whether we need more flexible, nonlinear models.

## 32. Results

* Both types of models can identify brain regions from baseline activity in the test set.

* The deep learning models perform significantly better than the models based on handcrafted features.

## 33. Results

* Next, we asked whether deep learning finds patterns beyond our handcrafted features.

* We looked at the transformer's predictions and their probabilities.

* We focused on cases where the models based on handcrafted features made mistakes.

* In these cases, the deep learning model made predictions with high confidence.

## 34. Future Work

* We now want to understand which patterns the deep learning models use.

* We plan to explore explainable AI and mechanistic interpretability.

* These approaches may be easier to apply to images and text, but we want to try them with our signals.

* We also want to distinguish healthy regions from regions with pathological activity.

* The aim is to do this using baseline activity.

* This could help identify regions involved in epilepsy without provoking a seizure.
