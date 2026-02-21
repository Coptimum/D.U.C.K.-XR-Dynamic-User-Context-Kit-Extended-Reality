HELLO PEOPLE WHO ARE WATCHING!!! ENJOY!

Notes on use/Reminders:
Provide a response to the blurb for each step. Do not feel limited by the questions, though! You are welcome (and encouraged!) to include as information as necessary.
This proposal is your step by step guide through the project (ie. the more time you put in now, the easier the implementation will be)
Don't be afraid to ask board for ideas and resources if you are stuck on any part
Use the Wiki or lectures as a refresher on each topic, if necessary

Overview
The goal of this project is to investigate how real-time visualization of both personal and interpersonal physiological data, delivered through a mixed-reality headset, affects user behavior in social settings and everyday tasks. To accomplish this, we will develop a mixed-reality (MR) system that processes biomarker data collected from multiple sensors and cameras and streams it directly into the Meta Quest 3, which functions as both the central computing hub and our MR simulation platform. By integrating signals related to heart rate, posture, sweat, vocal characteristics, and facial expression, the system will enable users to monitor and interpret their physiological state in real time. Our aim is to deliver this information through an intuitive, minimally intrusive interface that enhances user awareness without disrupting their engagement with the real world.
We are currently searching for components that could best fulfill our goal for this project. As of now, one of the components we were looking for is a wrist watch that provides one or many of these biomarkers: sweat, heartrate, blood-oxygen level, or sleep. We are also interested in a watch that is open source and allows us to communicate this data directly to another program in real-time so that we may be able to process it with our program and send this information directly to the Meta Quest 3 headset. 

Literature Review
Source 1: Paper on HRV and BCI Applications
Quick overview: This paper examines the use of heart rate variability (HRV) in BCIs, with a focus on how HRV can be a reliable indicator of stress and cognitive workload.
Notes/Takeaways:
Useful for understanding how HRV can be used to assess stress levels.
Provides a detailed breakdown of electrode placements for HRV monitoring.
Recommended preprocessing steps for HRV analysis, such as bandpass filtering between 0.5-5 Hz
HRV metrics include RMSSD (root mean square of successive differences), SDNN (standard deviation of NN intervals), and frequency-domain measures (LF, HF, LF/HF ratio)
Higher HRV generally indicates better stress regulation and autonomic nervous system balance
Lower HRV is associated with increased stress, anxiety, and poor cardiovascular health
Electrode placement: typically uses ECG with electrodes on chest (standard 3-lead or 5-lead configuration) for accurate R-R interval detection
Requires clean signal acquisition with minimal motion artifacts for reliable HRV calculation.
Source 2: Posture Feedback Systems
Quick overview: This source reviews posture correction technologies and their applications, including wearable devices that monitor alignment and provide feedback.
Notes/Takeaways:
Posture sensors are essential for tracking body alignment; could help develop real-time feedback for users.
Provides guidelines for sensor placement on the body for maximum efficacy.
Focuses on the need for real-time feedback to ensure timely corrections in posture.
Common sensor types include flex sensors, IMUs (inertial measurement units), and pressure-sensitive resistors
Sensor placement locations: upper back (thoracic spine), lower back (lumbar spine), shoulders, and neck
Feedback mechanisms can include vibration alerts, audio cues, or visual displays when poor posture is detected
Real-time monitoring allows for immediate correction before chronic issues develop
Can be integrated with mobile apps for tracking posture patterns over time and generating reports
Source 3: Identification of Suitable Biomarkers for Stress and Emotion Detection for Future Personal Affective Wearable Sensors
Quick overview: Skin conductivity (sweat) is an important basis for many physiology-based emotion and stress detection systems. This paper reviews current human emotional stress biomarkers and proposes the major potential biomarkers for future wearable sensors in affective systems. Identifies antistress hormones and cortisol metabolites as the primary stress biomarkers that can be used in future sensors for wearable affective systems.
Notes/Takeaways:
Main purpose of sweating is to regulate the body's core temperature
But there's also emotional sweating, which occurs as a physical reaction against emotive stimuli such as stress
Emotional sweat is produced on the entire surface of the skin, but it is concentrated on the palms, soles, and underarms
^so underarms is our best bet if we want user to be wearing it all day
Antibody-based technique most common tool used to detect cortisol in sweat
Less commonly used techniques: aptamer, e-nose, MIP techniques
Cortisol metabolite detection requires sophisticated lab-based machines 
^ok so not helpful for us
CortiWatch - a cortisol wristband sensor using antibody technique
^link to paper for this: https://www.tandfonline.com/doi/full/10.2144/fsoa-2019-0061 (look at it later)
The combined response to stress of cortisol, its metabolites, and cortisone raises the idea of using multiparameters rather than only using cortisol, as all these markers are present in sweat within a measurable range

^eccrine glands mainly in palms of hands and soles of feet, apocrine glands mainly in the armpits

Source 4: Voice and Facial Expression Based Classification of Emotion Using Linear Support Vector Machine 
Quick overview: Collected facial expression and voice data from subject, used a linear SVM classifier to classify these features into different emotion classes. Recognition accuracy of emotion up to a level of 95%
Notes/Takeaways:
7 subjects, asked to say "what are you doing here" with emotions in both their voice and facial expression
Features extracted from voice samples:
Pitch
First 3 formants
Powers at first 3 formants
6 snapshots of facial expression while they utter the sentence
Features:
Mouth-opening
Eye-opening
Length of eyebrow-constriction
7 emotions: anger, disgust, fear, surprise, happiness, sadness, and neutral
Classification done with both facial and voice data is better than each of the data types alone
Compared only-face and only-voice, fall-off in percentage classification in only-voice is much steeper than only-face

Source 5: A learning framework of modified deep recurrent neural network for classification and recognition of voice mood 
Quick overview: They propose a framework for classifying emotions via voice data.
Notes/Takeaways:
Proposed technique - using "modified deep duck and traveler recurrent neural network" (MDDTRNN) 
Preprocessing: ELMS (enhanced least mean square) algorithm to remove noise in signal 
Feature extraction: MFCC (Mel frequency cepstral coefficients) implemented in the feature extraction process to evaluate efficient representation to recognize different emotions
Feature extraction: use adaptive African vultures optimization algorithm (AAVOA) b/c it reduces the computational complexity and run time in selecting optimal features
"The proposed method is implemented by using two datasets called IEMOCAP and EMODB. The main objective of the proposed MDDTRNN is to attain high classification accuracy over different emotions. The results of the proposed method have achieved the accuracy rate of (95.86%), precision as (93.79%), Specificity as (94.28%), error rate as (5.266%), sensitivity rate as (92.89%), and FPR as (1.01%). When compared with the other classifiers, the proposed method achieves a better result in terms of accuracy."


Source 6: Deep Facial Expression Recognition: A Survey
Quick overview: This paper surveys deep learning approaches for facial expression recognition (FER), covering CNN architectures, datasets, preprocessing techniques, and performance metrics for emotion classification from facial images.
Notes/Takeaways:
CNN architectures such as VGGNet, ResNet, and custom models are commonly used for facial feature extraction
Preprocessing steps include face detection, alignment, normalization, and data augmentation to improve model robustness
Common benchmark datasets: FER2013, CK+, JAFFE, AffectNet - each with varying numbers of emotion categories
Key facial features analyzed: eye shape, eyebrow position, mouth curvature, and overall facial muscle movements
Transfer learning from pre-trained models significantly improves accuracy, especially with limited training data
Real-time FER systems require optimization techniques for deployment on resource-constrained devices 
Source 7: Emotion Recognition from Physiological Signal Analysis: A Review - ScienceDirect
Quick overview: This review paper examines physiological signal-based emotion recognition, focusing on biosignals like EEG, ECG, GSR (galvanic skin response), EMG, and respiration patterns for detecting emotional states.
Notes/Takeaways:
Multiple physiological signals provide more robust emotion detection than single modality approaches
GSR (skin conductance) is highly responsive to emotional arousal and stress levels
Feature extraction techniques include time-domain, frequency-domain, and time-frequency analysis methods
Machine learning classifiers: SVM, Random Forest, and neural networks commonly achieve 70-90% accuracy
Challenges include inter-subject variability, context dependency, and need for sensor calibrationWearable implementation requires lightweight sensors with low power consumption for continuous monitoring 
Source 8: A Review of Emotion Recognition Using Physiological Signals - PMC
Quick overview: Similar to Source 7, this review analyzes emotion recognition using physiological signals including ECG, EEG, EMG, and GSR, with emphasis on signal processing pipelines and classification algorithms.
Notes/Takeaways:
Signal preprocessing is critical: noise filtering, baseline correction, and artifact removal improve accuracy
Fusion of multiple biosignals (multimodal approach) achieves higher accuracy than single-signal methods
Real-world applications include stress monitoring, mental health assessment, and affective computing systems
Personalized models that adapt to individual users show improved performance over generic models 
Source 9: Enhanced multimodal emotion recognition in healthcare analytics: A deep learning based model-level fusion approach
Quick overview: This paper proposes a deep learning-based model-level fusion approach for multimodal emotion recognition in healthcare, combining facial, vocal, and physiological signals for improved diagnostic accuracy.
Notes/Takeaways:
Model-level fusion: combines predictions from multiple trained models rather than early feature fusion
Healthcare applications: patient monitoring, telemedicine assessments, mental health diagnostics
Attention mechanisms help the model focus on most relevant modalities for each emotion type
Achieves state-of-the-art results on benchmark datasets by leveraging complementary information from multiple sourcesRobustness to missing modalities: system can still function if one sensor fails or data is unavailable 
Source 10: Multimodal Emotion Recognition in Conversations: A Survey of Methods, Trends, Challenges and Prospects
Quick overview: This survey examines multimodal emotion recognition in conversational contexts, covering methods for analyzing speech, text, facial expressions, and body language in dialogue scenarios.
Notes/Takeaways:
Conversational context adds temporal dynamics - emotions evolve through dialogue turns
Contextual modeling: understanding previous utterances improves current emotion prediction
Speaker-specific patterns: different individuals express emotions differently in conversations
Challenges: handling interruptions, overlapping speech, turn-taking dynamics, and multi-party interactions
Applications: virtual assistants, chatbots, customer service automation, and social robotics 
Source 11: Multimodal emotion recognition using deep learning architectures | IEEE Conference Publication
Quick overview: This IEEE conference paper presents deep learning architectures for multimodal emotion recognition, combining audio, visual, and text modalities using advanced neural network fusion techniques.
Notes/Takeaways:
Late fusion strategies allow each modality to be processed independently before combining predictions
Transformer-based architectures show superior performance for capturing cross-modal interactions
Ensemble methods combining multiple deep learning models improve overall system robustness
Attention weights reveal which modalities contribute most to each specific emotion classification
Real-time implementation considerations: model compression, quantization, and edge deployment strategies

Source 12: Affective computing in virtual reality: emotion recognition from brain and heartbeat dynamics using wearable sensors - PMC
^uses VR and EEG at the same time, not sure how they made it work

Source 13: Emotional Speech Recognition Using Deep Neural Networks - PMC


Other sources:
Source: EMG for Posture and Movement Analysis
Quick overview: Explores the use of electromyography (EMG) to monitor muscle activity, particularly for identifying signs of poor posture or repetitive strain injuries.
Notes/Takeaways:
EMG sensors could be used in conjunction with posture sensors to monitor muscle tension.
Real-time feedback via EMG could prevent conditions like carpal tunnel or muscle fatigue.
Offers advice on EMG system requirements and implementation.
Software
There exists multiple parts in software:
Meta Quest 3 environment that will house program
Will be using Unity to program the environment
Will be using  
Programming for sensors
Posture Sensor (PRIORITY)
Fitbit watch
Heart rate monitor (PRIORITY)
Sweat (might be part of watch, might be separate, TBD)
Blood-oxygen (TBD confirmed feature)
Sleep quality (TBD confirmed feature)
Microphone
Analyzing audio for other people to detect real-time changes in tonality, etc.
Programming for cameras 
Posture classification for other people
Facial analysis for emotion classification of other people
Overall program that collects raw data from sensors
Will take data from all components into one program that will decide 

Will be using Unity's environment to develop the MR program itself.
For the VR program itself we will using the Meta SDK
Use Meta's SDK (software development kit) (duck)(duckerburg) 
For pre-processing and classifying raw facial recognition data, and raw auditory data we will be using a combination of Convolutional Neural Network (CNN) + Recurrent Neural Network (RNN).
CNN is for facial recognition, RNN is for auditory.
Both are reliable, considering so many papers we have cited seem to rely on them. 

How will you interpret the data?
Outline and describe how you are going to preprocess your data.
What filters will you use?
Will you be performing feature extraction?
What kind of machine learning models will be used?
How will you integrate your model in real time?
Hardware
Confirmed Features to Implement
Heart rate sensor 
Could be part of fitbit watch 2-3 
Watch: Amazon.com: XIAOMI Smart Band 8 Pro Fitness Tracker, 1.74" AMOLED Display, Up to 20 Days Battery, 5ATM, Sleep and Heart Rate Monitoring, 150+ Training Modes, Pedometer, Black
Might potentially help with collecting data: Xiaomi - Gadgetbridge
Posture Sensor - 1 needed only 
Posture Awareness Sensor : 11 Steps - Instructables
Materials for Posture Sensor
Lilypad Arduino Board
LilyPad Vibe Board - SparkFun Electronics
LilyPad Button Board - SparkFun Electronics
Flex Sensor 2.2"
Resistor 10k Ohm 1/6th Watt PTH - SparkFun Electronics
Alligator Clip with Pigtail (4 Pack) - SparkFun Electronics
Conductive Thread
Potential items
Wire Strippers
Solder 
Soldering Iron
Sweat sensor 
At least 2 people
Place in armpit most likely (will need to aggregate with other features to tell difference between nervous sweating vs. exercise sweating)
*Meeting with grad student who does relevant work on wearables and sweat patches planned for Thurs, will acquire more info then
Auditory analysis to discern stress/emotion (pitch, inflection, tone, etc.)
2-3 microphones
Microphone
Emotion analysis using camera on the meta quest 3 to record other people's faces
Built-in camera in meta quest
Go to Ebay and buy sketchy stuff

Analyze correlations between the people/places the user interacts with and the user's physiological data

Data Collection
*This will be for testing purposes, so we're moving it to after software and hardware b/c we need to implement our device first before we can collect data on how well it works
Phase 1 Data Collection:
This phase is collecting data and doing any training of ML models as needed (overall goal is just to get each individual feature we want working)
Heart rate and sweat: measured by wristwatch, have user wear wristwatch, measure baseline, then measure across 45 minutes
To elevate heart rate and sweat, we could get the user to perform some kind of exercise, like walking back and forth, jogging, sprinting, etc. (estimate 15 minutes)
Let participant rest until their heart rate is back at baseline (however long this takes)
We also want to check for elevated heart rate and sweat in the case of nervousness and not physical activity
To do this, use a simpler version of the Trier Social Stress Test (~15 min):
Participant is taken into a room where a panel of 3 judges are waiting
3 phases:
1: anticipatory stress, participant is asked to prepare a 5 min presentation
Participant is allowed to use paper and pen in their prep, but the paper is unexpectedly taken away from them when it is time to begin the presentation
2: presentation phase, participant is asked to give the 5 min presentation
Judges observe without comment, if the participant stops and the 5 min isn't up, judges will ask them to continue
3: mental arithmetic component
Participant is asked to count backwards from 1,022 in increments of 13
*for ethical reasons, need to debrief the participant after the procedure, tell them the purpose was the tests was to create stress and that the results don't reflect their personal abilities in any way
Posture sensor: use as testing to determine accuracy of program 
Get participant to put on sensor and sit in different positions (some obviously not correct, others more subtle like your back being a little too slumped – different degrees of slouched posture)
See if our sensor gives the correct response (can it actually identify good posture vs. bad posture)
If we pull this off, see if we can get our program to provide advice on how to correct the bad posture 
Test in both sedentary environment and active environment  
Auditory analysis (will be RNN type neural network):
We will most likely pull a pre-trained model in identifying changes in tonality off the internet and just plug this into our overall model
We will edit to fit within our overall program
Facial analysis (will be CNN type neural network): 
We will most likely pull a pre-trained model in identifying facial expressions off the internet and just plug this into our overall model
We will edit to fit within our overall program
Phase 3 Data Collection 
User Preparation: The user will be equipped with a Meta Quest 3 headset, heart rate sensor, posture sensor, sweat sensor, and microphone.
Heart rate sensor (and potentially sweat sensor) attached via wristwatch
Wireless microphone attached via clip on shirt
Posture sensor (for user) attached to back of neck 
Sensor Calibration: Each sensor will be calibrated to establish baseline data. For example, the heart rate sensor will be used to monitor baseline heart rate variability, and posture sensors will track alignment.
Real-time Feedback: Data will be processed and displayed in real-time via mixed reality, offering the user instant insights into their physiological state (e.g., stress levels, posture alignment).
Data Collection in Social Settings: Users will be placed in controlled social scenarios (e.g., interacting with another person, walking through different environments). The sensors will track physiological data, including heart rate, posture, and sweat levels.
We will have a control group interaction where they will just interact with the other participants and we will observe 
Might have to create list of observations to take into note or consideration 
We will have one participant be the "user" or person with all gear i.e. the MR headset.
The user will interact with the other participants again. We will observe any changes in behavior
We will repeat this process 2-3 more times to observe how behavior is further impacted as the user gets acclimated to the new information they are being fed.
Note any noticeable changes 

BCI Pipeline
Provide a digital drawing (must be readable!) of your full pipeline include small visual for each step, label the arrows (what connectors will you be using), and describe what will be occurring in each step.
Note: No "new" information should be presented in this section; this is a means to organize the technical aspects outlined in previous steps.


Input Devices: Sensors (heart rate, posture, sweat, EMG) collect biometric data
Data Processing: The raw data is filtered and features are extracted
Machine Learning: A classification model processes the features to assess the user's physiological state
Output (MR Interface): The results are presented in real-time through the Meta Quest 3's mixed-reality interface, providing immediate feedback on posture, stress, and other health metrics
Record: Measure behavioral change of the user and impact on social and mental processes. Test with no features as control, individual features themselves, and together as well. Measure behavioral changes from this as well.

BCI Pipeline Drawing

Phases
Phase 1 - Implementation of all these features
Make sure each sensor is working properly on its own, hardware works, collecting the right data, etc.
Including developing our DIY version of a posture sensor for the user. 
Get features on our primary user working first (their heart rate, sweat, posture sensor, auditory analysis, etc.)
Then, get features on secondary people that the user is interacting with working
Analyzing their posture through camera
Their heart rate, sweat, other biomarkers measured through a wristband they'd be wearing
Auditory and facial behavior that indicates stress level and/or mood
Goal is for auditory analysis program to be able to record a conversation, automatically distinguish between 2 people's voices, and analyze the stress/mood of each of the two people

Phase 2 - Making the ecosystem of the entire project (e.g. the actual integration of MR and the biodata that we receive from these features) 
Integrate information for heart rate, sweat, facial, auditory to get a more accurate read of stress/mood
Each sensor on its own can tell us something about stress/emotion, but we need to analyze all their patterns together to get a more accurate read of stress/emotion
Integrate the facial and auditory analysis first
Then, integrate the results from that with heart rate and sweat and any other physiological data we might have
**The data from each sensor will get sent to a computer, which processes and analyzes the data, then the computer sends the information to the headset to be displayed to the user
The output from each of the individual features is integrated into the mixed-reality program to present a cohesive interface to the user
There should be one interface shown to the user with all the information
What their heart rate is
Whether they should shift their posture right now and how
What their heart rate + sweat (and any other metric we might collect) in this moment shows about their stress level and/or mood/emotion
The posture and stress/mood of the person they're currently interacting with

Phase 3 - analysis on impacts of these features (social experiment-esque study)
Give users access to the device, goal is to see how the information provided to users via features influences how they interact with others – does it result in small changes in day-to-day life
Ex: how does the emotional analysis impact the user's response to the person they are interacting with 
How does continued use of a device such as this continue to further impact behavior of the user

Identify key milestones that you want to achieve and how you can take your project further if you have additional time. Plan out your project in phases (how would you expand your project if you have time?) Think of this as a list of goals that you can achieve AFTER you finish phase one (getting your initial project up and running).
(Optional) Itemized Cost for Later Phases
Prioritize free services/materials. Do not feel obligated to fill out this section. This is solely a way to keep costs organized should your team deem it necessary. Provide cost breakdown of additional costs with the items Projects could possibly fund.
Any cost in the future will most likely come in the form of additional sensors that we might buy to improve on our project. For example, a better fitbit watch that provides improved real time data on heart rate, sleep, etc.
(Optional) Additional Considerations
Is there anything that is important to the project that did not fit in any other section? Include it here. If you have clearly outlined every aspect already, do not feel obligated to provide information here.
User Experience: The interface must be intuitive and provide easy-to-understand feedback without overwhelming the user
Ethical Considerations: The project raises potential privacy concerns about collecting sensitive health data. User consent and data anonymization will be critical

Potential Name: URHealth - User Reality Health

