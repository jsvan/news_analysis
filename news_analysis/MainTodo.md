
### TODO
- Get dataset (pontentially automate this)

- Write HOWTO doc.
    - Record video with me going through examples
    - Write script

    - Start getting samples ourselves to iron out philosophy

- Grab the url for samples -- then we can get a "neutral" dataset that doesnt overfit on our pos/neg samples.

- Change advertisement of this app to be a way to challenge yourself to consider how sentences in your news implicitly give you a good or bad impression of somebody.
    - "By helping us make this dataset, you will learn to process what youre reading at a deeper level."

- Train aspect model:
    - Input and output wordcounts are the same, but we only care about NE's getting correct sentiment label.
    - Only count NE's labels when calculating loss, ignore filler words.

- Visualize raw sentiment data vs deviation from average at that time.

- Get simple clustering

- Get website

- Get translated newspapers
- Aspect based Sentiment Analysis might not work well on translated stuff. 
  See if instead of translating everything to english, if making sentiment-models for every language with an auto-translated
  dataset is better-er.

- Get talk radio speech2text

- Get network news speech2text

- Add emotion recognition

- make shell script to run run.py with correct input params
   
