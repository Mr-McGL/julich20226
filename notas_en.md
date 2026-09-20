This is the presentation I am preparing for the research group in which I am currently doing a stay. I would like you to take my notes and translate them into English.

# Introduction
* First, I would like to thank the Boris for the opportunity to present my work and to thank Sandra and Boris for inviting me to visit the center during the next two months.
* Although I believe our groups have been collaborating actively over the past few years, this is the first time I have seen that I agree with the majority of you.
* For this reason, I wanted not only to present my work but also to introduce my institution and my research group.

## URJC
* As Boris mentioned, my name is Marcos García, and I am an assistant professor at the Universidad Rey Juan Carlos.
* In Madrid, there are six public universities. The Universidad Rey Juan Carlos is the youngest public university in Madrid, founded in 1996, but it is the second-largest by student population.
* I belong to the Department of Computer Science and Statistics and we are located on the Móstoles campus.
* The university currently has more than 40,000 students and 2,500 faculty members. It has four campuses, and my research group is located on the Móstoles campus, in the southwest of Madrid.

## My current work
* In collaboration with the Experimental and Computational Electrophysiology Group (https://cajal.csic.es/en/experimental-and-computational-electrophysiology/), which belongs to the Cajal Neuroscience Center at the Spanish National Research Council (CSIC).
* They are interested in brain activity using intracranial EEG recordings.
* The signals captured by electrodes are known as local field potentials (LFPs).
* These signals are composed of the sum of neuronal activity from different regions.
* This group has been working for years on the development of blind source separation techniques to isolate activity from different brain regions.
* Several methods exist, but they work with a customized version of Independent Component Analysis (ICA).
* This technique is not free from limitations.

## The cocktail party problem

## Problems
* It depends on the number N of sources selected. Several approaches exist to estimate the number of sources.
* Basic techniques cannot recover the original signal amplitudes.
* Signals cannot be correlated.
    * We must remove synchronous activity from our analysis.
    * We can only work with baseline activity.

## Objective
* Although most of our recordings contain baseline activity.
* This activity is highly complex and apparently random.
* Our objective is to determine whether we are able to identify patterns in baseline activity that allow us to distinguish brain regions.
* And whether these patterns are consistent across subjects.

## Methodology
* We have worked on training ML models based on handcrafted features and DL models operating on raw signals to determine whether there are patterns in baseline activity that allow us to identify brain regions.
* Methods based on handcrafted features usually offer better interpretability, but they are less powerful than DL models.
* Our secondary objective is to assess whether DL methods identify patterns beyond the handcrafted features we have extracted.
* We compare models with different levels of complexity to determine whether the relationships among handcrafted features that support generator identification can be captured by linear models or require more flexible nonlinear functions.

## Results
The results on the test set are quite clear: both feature-based methods and DL models are capable of identifying brain regions from baseline activity.

DL models significantly outperform feature-based models.

To assess the extent to which DL models were learning patterns beyond the handcrafted features:
* First, we verified that the transformer model was aligned with the output probability.
* We then analyzed the cases in which the feature-based models failed.
* We found that the DL model classified with high confidence in cases where the feature-based models failed.

## Future lines of work
* In recent years, significant effort has been devoted to the study of DL interpretability:
    * Explainable AI (XAI)
    * Mechanistic interpretability
* This is certainly easier with images and text, but it is worth trying.
* Once we have shown that baseline activity contains patterns that allow us to identify brain regions, we want to determine whether we can distinguish healthy regions from regions with pathological activity.
* In the context of epilepsy, seizures are sometimes provoked to identify regions. Being able to detect a region with pathological activity using baseline activity would be a major advance.

We also verified the alignment between the transformer model and the output probabilities.

"mixed-effects models"
