#####           Read Horoscopes from S3 Bucket          #####

# returns horoscope reading for a given zodiac sign
def read_horoscope(sun_sign):
    import boto3
    s3 = boto3.client('s3')
    filename = sun_sign + ".txt"

    # get reading
    data = s3.get_object(Bucket="horoscopica", Key=filename)
    reading = data['Body'].read()

    # narration for speech output
    speech_text = "Reading the horoscope for " + sun_sign + ". " + reading
    return(speech_text)


#####       Helper Functions to Create Speech and Card Output          #####

# creates display card with a given title and image
def build_SimpleCard(sun_sign, image_url):
    card = { 'type' : 'Standard', 'title' : sun_sign, 'image' : {'smallImageUrl' : image_url}}
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

# creates speech and text output
def compile_speechlet(sun_sign, speech_text, image_url):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(speech_text)
    speechlet['card'] = build_SimpleCard(sun_sign, image_url)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)

#####            Intent Handler              #####

# handling the check_horoscope intent
def intent_handler(event, context):
    # get intent name
    intent_name = event['request']['intent']['name']
    if intent_name == "check_horoscope":

        # check if the sunsign is specified in the intent
        if event['request']['intent']['slots']['sunsign'].has_key('value'):
            sun_sign_raw = event['request']['intent']['slots']['sunsign']['value']
            sun_sign = sun_sign_raw.lower()
            speech_text = read_horoscope(sun_sign)

        # if no sun sign is mentioned
        else:
            sun_sign = "zodiac"
            speech_text = "No sun sign mentioned"
        image_url = "https://s3.amazonaws.com/horoscopica/Images/" + sun_sign + ".png"
        return compile_speechlet(sun_sign, speech_text, image_url)

    # intent not recognized
    else:
        return compile_speechlet("Sorry", "Sorry, I couldn't understand. Please try again..", "")


#####               Main Function for Event Handling        #####

# main event handler
def lambda_handler(event, context):
    if event['request']['type'] == "IntentRequest":
        return intent_handler(event, context)
