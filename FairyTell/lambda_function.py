#####           Read Story Text from S3 Bucket          #####

# read story text from S3 bucket
def tell_story(story_name):
    import boto3
    s3 = boto3.client('s3')
    filename = story_name + ".txt"

    # get story text
    data = s3.get_object(Bucket="fairytell", Key=filename)
    story_text = data['Body'].read()

    # narration for speech output
    speech_text = "Reading the story of " + story_name + ". " + story_text
    return(speech_text)

# pick a random story to tell
def tell_random_story():
    # get available stories from S3 'fairytell' bucket
    import boto3
    s3 = boto3.client('s3')

    story_list = []
    list_output = s3.list_objects_v2(Bucket="fairytell")
    for item in list_output['Contents']:
        story_list.append(item['Key'])

    # pick a random story to read
    import random
    filename = random.sample(story_list, 1)[0]

    # remove the file extension
    import re
    story_name = re.sub(r".txt", '', filename)
        
    data = s3.get_object(Bucket="fairytell", Key=filename)
    story_text = data['Body'].read()
        
    # narration for speech output
    speech_text = "Reading the story of " + story_name + ". " + story_text
    return(story_name, speech_text)


#####       Helper Functions to Create Speech and Card Output          #####

# creates display card with a given title and image
def build_SimpleCard(story_name, image_url):
    card = { 'type' : 'Standard', 'title' : story_name, 'image' : {'smallImageUrl' : image_url} }
    return card

# produces speech output
def build_PlainSpeech(speech_text):
    speech = { 'type' : 'PlainText', 'text' : speech_text }
    return speech

# builds response
def build_response(message):
    response = {}
    response['response'] = message
    return response

# produces speech and text output
# text is displayed as a card
# while speech is played aloud on speakers
def statement(story_name, speech_text, image_url):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(speech_text)
    speechlet['card'] = build_SimpleCard(story_name, image_url)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)

#####            Intent Handler              #####

# handling the tell_story intent
def intent_handler(event, context):
    # get intent name
    intent_name = event['request']['intent']['name']
    if intent_name == "tell_story":

        # check if the story name is specified in the intent
        if event['request']['intent']['slots']['story'].has_key('value'):
            story_name_raw = event['request']['intent']['slots']['story']['value']

            # format story-name string to match the filename in S3 bucket
            words = story_name_raw.split()
            story_name = ""
            for w in words:
                if story_name == "":
                    story_name = w.capitalize()
                else:
                    story_name = story_name + "-" + w.capitalize()
            speech_text = tell_story(story_name)

        # if no story name is mentioned, pick a random story in S3 bucket
        else:
            (story_name, speech_text) = tell_random_story()
            
        image_url = "https://s3.amazonaws.com/fairytell/Images/" + story_name + ".jpg"
        return statement(story_name, speech_text, image_url)
    else:
        return statement("Sorry", "Sorry, I couldn't understand. Please try again..", "")


#####               Main Function for Event Handling        #####

# main event handler
def lambda_handler(event, context):
    if event['request']['type'] == "IntentRequest":
        return intent_handler(event, context)
