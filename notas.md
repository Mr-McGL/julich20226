Esta es la presentación que estoy perparando para el grupo de investigación en el que estoy haciendo una estancia actualmente. Quiero que tomes mis notas y las traduzcas al inglés



# Introducción
* Lo primero aegradecer la presentación y agrader a Sandra y Boris que me hayan invitado vistar el centro durnate los proximos dos meses. 
* Aunque creo que nuestros grupos han estado colaborando activamente los ultimos años. Creo que es la primera vez que veo que coincido con la moyoria de vosotro.
* Así no solo quería presentar mi trabajo sino tambien dar a conocer un poco a mi institución y a mi grupo de investigación.


## URJC
* Como ha comentado Boris, mi nombre es Marcos García, y soy assistan professor En la Universidad Rey Juan Carlos.

* En madrid tenemos 6 universidades publicas. La Universidad Rey Juan Carlos es la Universidad pública más joven de Madrid, fundada en 1996, pero la sengunda por numero de alumnos. 

* Yo pertenezo al Departamento de Informatica y Estadistica (Camputer Science and Statistics) y estamos situados en el campus de Móstoles. 


* Es u
, el siguiente paso es ver si estos patrones son consistentes entre sujetos.


Actualmente cuenta con más de 40.000 estudiantes y 2.500 profesores. La universidad tiene 4 campus, y mi grupo de investigación se encuentra en el campus de Móstoles, al suroeste de Madrid.

## Mi trabajo actual

* En coperación con el EXPERIMENTAL AND COMPUTATIONAL ELECTROPHYSIOLOGY GROUP (<https://cajal.csic.es/en/experimental-and-computational-electrophysiology/>) who belong to the Cajal Neurscience Center at the Spanish National Research Council (CSIC).

* The are interested in the brain activity using intracranel EEG recordings.

* The signals captured by electrodes are called local field potentials (LFPs). 

* Estas señales estan compuestas por la suma de la actividad de neuronas de difrentes regiones. 

* Este grupo lleva años trabajando en el desarrollo de técnicas de separación ciega de funtes para separar la actividad de diferentes regiones cerebrales. 

* Existen distintas técnicas pero ellos trabajan con una version custumizada Independent Component Analysis (ICA).

* Esta técnica no esta libre de problemas. 


## The Cocktail problem


## Problemas:

* Dependes del numero N de fuentes que escojas. Existen téncias para estimar el numero de fuentes.
* Las técnicas básicas no pueden recuperar la intesidad original del las señales.
* Las señales no pueden estar correlacionads. 
    * Debemos quitar de nuestro análisis la actividad sincrona
    * Solo podemos trabjar con actividad basal.
    

## Objetivo

* Si bien la mayor parte de nuestras señales contiene actividad basal.
* Es una actividad muy compleja y aparentemente aleatoria. 
* Nuestro objetivo es ver si somos capaces encontar patrones en la actividad basal que nos permitan identificar regiones cerebrales.
* Y si estos patrones son consistentes entre sujetos

## Metodologia

* Hemos trabajado entrenado modelos ML basados en features y modelos DL <que trabajan sobre la señal crudo -- usa el vocabulario técnico adecuado>,
para ver si existen patrones en la actividad basal que nos permitan identificar regiones cerebrales.

* Los metodos basados en features suele tener mejor interpretabilidad, pero son menos potentes que los modelos DL.

* Nuestro objetivo secundario es ver los metodos DL encuentra patrones que van mas allas de las features que hemos extraido. 

* We compare models with
different levels of complexity to determine whether the re-
lationships among handcrafted features that support gen-
erator identification can be captured by linear models or
require more flexible nonlinear functions.

## Resultados

Los resultado en el conjunto de test son bastante claros, tanto las técnicas basadas en features como los modelos DL son capaces de identificar regiones cerebrales a partir de la actividad basal.

Los modelos DL superan a los modelos basados en features, de mandera significativa. 


Para comprobar hasta que punto los modelos DL estaban aprendiendo patrones mas alla de las features. 
* Primero comprobamos que el modelo tranformes estuviese alineado con la probabilidad de salida.
* Despues analiamos los casos donde los modelos basados en features fallaban.
* Comprobamos que el modelo DL clasifica con niveles de certidumbre altos, casos en el que los modelos basados en features fallaban.


## Lineas de trabajo futuro

* En los últimos años se estan dedicando muchos esfuerzoas en al estudio la interpretabilidad de modelos DL:
    * Explainable AI (XAI)
    * Intepretabilidad mecanicista.

* Es cierto que es más fácil con  imagenes y texto, pero belive is worht tring.

* Un vez que probado que la actividad basal cotiene patrones que permiten identificar regiones cerebrales, queremos ver si somos capaces de identificar regines normales de regiones con actividad patologica.

* En el contexto de la epilepsia, a veces se probacan ataque para identificar reigiones, poder idetificar una region con actividad patologica, mediante el analisis de la actividad basal, seria un gran avance.




Tambien comprobamos el alineamiento de modelo transforme con la probabilidades de salidad. 


"mixed-effects models"




