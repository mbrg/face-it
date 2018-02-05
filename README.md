# Face-It

First runner-up at Facebook Hackathon, Tel Aviv, 2017.

## Intro

What is the minimal set of elements which makes a person distinct?

We present our attempt to approach this question, conceived and implemented in a 24-hour hackathon at Facebook, 2017.

Our project combines a model which generates painting videos from still images, and a fun game which allows you to challenge your friends in a fast recognition competition!

## The Game

After logging into our Facebook account, we can choose a friend to challenge:

<!---![Alt text](/demo/pick.png?raw=true "Welcome, pick a friend")-->

<img src="/demo/pick.png" alt="Welcome & Pick a friend" width="600" height="600" />

A random mutual friend is selected, and his profile picture runs through our model to generate a painting video. Our goal is to recognize the person in the photo as fast as possible!

<img src="/demo/or.png" alt="Wrong choice" width="300" height="400" /> <img src="/demo/guy.png" alt="Correct!" width="300" height="400" /> 

Now I can challenge my friend to try and recognize our mutual friend faster!

## The Model

We start by applying a facial recognition model, which crops and resizes the picture to focus on a face.

Our model has two main components:

- A Markov Random Field (MRF) on a grid-graph, where each pixel is a vertex, connected to its direct neighbors (left, right, up, down).
All vertices are initiated at an *unobserved* state.
- A Saliency prediction model, which attempt to find the areas in the image that contain the most information.

To generate the painting video, we use the following steps iteratively:
- We find the vertex (pixel) with the highest saliency, and set it as a starting point.
- The MRF is used to generate a continues path along the graph's *unobserved* vertices. The path starts at the starting point, and probabilistically traverses a low gradient path along the graph (i.e, a path with similar pixel values). Once a path has traveled through a vertex, the vertex is considered *observed*.
- The saliency map is updated according to reflect only unobserved parts of the image. For intuition, consider the following question - once the eyebrows have been painted, will you be surprised by the location of the eyes, once they're painted?
- A video frame is generated, which corresponds to the observed part of the image at that time.

The results resembles the all-familiar videos of paint-artists, creating amazing images with MS-paint:

![Alt text](/web-service/static/vid/guy_vid.gif?raw=true "Result")

## Implications

Once the user successfully recognized the person in the video, we induce that enough information about the image has been unveiled, and the image's subject is now clear. Hence, we can generate a dataset of images, and their minimal-information versions, which is still recognizable by a human.

Such a dataset can help to develop and evaluate computer vision models, in hope to acquire (at least) human-level performance at the intuitive task of identifying subject in sub-optimal vision conditions.
