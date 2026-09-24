# Author: Mohammad Tejabwala
# Using: Human brain

- Process the voice mp3 files into text (using OpenAI Whisper in Google Colab (GPU))

Why? Because the model is free better than DeepSeek and does not involve a tedious registration process. Why didn't I use the agents directly, well in order to scale this project in the future, 
building a thorough deployment process is a good practice, because agents might not handle large volumes of mp3 files

Kept in a new directory, "dataset_processed" with the file name "audio_to_text.txt"
Hmm, might have kept it easy to parse if it was json. Done. "audio_to_text.json"

- Process the images to text files now

Using PyTesseract as it was the only reliable open source model I could find except directly
using the LLMs.
Hmm it failed spectacularly, too less text was rendered
Let us use LLMs for that

- Seperate group admins

After checking the initial messages in the sample CSV, I noticed that the admin messages in the group are trusted and sometimes can be time sensitive, so we can increase the weight of trust worthiness for them

- Made the rules initially, then I refined them using Gemini

- Now comes the important part, how do we categorize the messages into the Action: 
-- notify: interrupt the user now
-- digest: safe but low priority; show later
-- mute: repetitive, unwanted, low-value, suspicious, scam-like, or unsafe for this user

Also we would need to specify the message_type:

personal
urgent
event
payment
business_update
promotion
greeting
forward
spam
scam
unknown

With a reason, which can be generated from an LLM
Confidence, would be just a probablity
evidence_message_ids: important for scording, basically checking the previous user behavior

So what I wanna do is two stage evaluation, stage 1: text classification model or something
stage 2: a good LLM evaluation based on the rules and the stage 1 results
