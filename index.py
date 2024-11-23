from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os
import json
import time
import threading



# loading our open ai api key 
load_dotenv()
client = OpenAI( api_key = os.getenv('API_KEY') )


# loading our firebase keys
Firebase_KEY = credentials.Certificate(os.getenv('FIREBASE_KEY'))
firebase_admin.initialize_app(
    Firebase_KEY,{
 "databaseURL": os.getenv('DATABASE_URL')
})


app = Flask(__name__)
CORS(app)


# Shared storage for data between /medicalTalk and /response routes
shared_data = {"response": None}

# Lock to synchronize access to shared_data
data_lock = threading.Lock()


# open ai route
@app.route("/medicalTalk", methods=["POST"])
def openAi():
    try:
        # getting user text and user expectation 
        req = request.get_json()

        data = req.get("data", "")
        opinion = req.get("opinion", "0")
        uid = req.get("user", "anonymose")
        backend = req.get("backend", "")

        print(data)
        
        prompt = Prompt(data)

        res = ""

        # Handeling if we are going to call the openAi servers, or our LLM
        if(backend == "HeReFaNmi LLM"):

            # connecting to RAG server
            RAGrequest(data)     

            # waiting for the response from the LLM server to be stored in shared_data
            res = wait_for_response()

            # terminate the connection and make a simple response so the app don't crash 
            if res == None : 

                res = """{
                        "medical": "True",
                        "news": "False",
                        "label": "Doubtful",
                        "reasoning": "We can't respond to your statment due to the waiting timeout for the LLM to respond, PLEASE TRY LATER!",
                        "sources": []
                }"""
            
        else :

            # connecting to openAi server
            res = backendHandler(backend, prompt)
        
        print(res)

        # getting the fields from the json
        res_dict = json.loads(res)
        medical_value = res_dict.get("medical", "True")
        response_value = res_dict.get("reasoning", "")
        label = res_dict.get("label", "Doubtful")
        sources = res_dict.get("sources",[])
        news = res_dict.get("news", "False")

        #c learing the source list from the links that don't work before returning it 
        sources = ClearSources(sources)

        # means that the data is not related to the medical field
        if medical_value == "False" :
            # saving data in firebase
            reference = firebaseSave(uid, opinion, data, medical_value, news, response_value, label)
            return jsonify(data = "Please try to ask something related to to medical field... !",
                            key = reference), 200
        
        # saving data in firebase
        reference = firebaseSave(uid, opinion, data, medical_value, news, response_value, label)
        return jsonify(data = response_value, news = news, label = label, source = sources, key = reference), 200
    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500   


# Waiting timeout for the LLM response
def wait_for_response(timeout=30):

    # Wait for the external server to respond, with a timeout.
    start_time = time.time()

    while time.time() - start_time < timeout:
        with data_lock:
            if shared_data["response"] is not None:

                # Retrieve and clear the shared response we got from the /response route
                response = shared_data["response"]
                shared_data["response"] = None
                return response

        # Wait a short time before checking again
        time.sleep(0.5)

    # Return None if no response within the timeout period
    return None


# Sending prompt to the RAG server
def RAGrequest(prompt):

    # Connecting to walid's backend to send him the user prompt 
    url = "http://127.0.1:5000/find_similar_chunks"

    # Prompt to send in the POST request
    payload = {
        "prompt": prompt,
        "top_n": 3
    }

    try:
        # Make a POST request to oualid's RAG server
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Prompt sent successfully!")
            
        else:
            print("Failed to send the prompt to oualid's RAG server. Status code:", response.status_code)

    except Exception as e:
        print("Error during request:", e)


# getting the response from Hamdi's LLM server    
@app.route("/response", methods=["POST"]) 
def LLMResponse():
    try:

        # getting the response from the LLM
        data = request.get_json()
        res = data.get("response", "")

        print("################################")
        print("dataaa from the server", res)
        print("#################################")

        # Store the LLM server response in shared_data
        with data_lock:
            shared_data["response"] = res

        return "SUCCESS", 200

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500 


def ClearSources(sources):
    working_links = []
    for link in sources:
        try:
            response = requests.head(link)
            # Check if the response status code indicates success (2xx)
            if response.status_code // 100 == 2:
                working_links.append(link)
        except requests.RequestException:
            # If there's an exception (e.g., connection error), consider the link not working
            working_links.append("{Web page is not working}")
            pass
    return working_links       


def Prompt(data) : 

    return '''  
    <SYSTEM>
    You  are the most knowledgeable medical professional in history, you can effectively and accurately classify medical news articles as 'Trustworthy', 'Doubtful', or 'Fake'.
    You can also provide reasoning and resources to back up your decision.  Please include relevant details such as publication date, author, and any notable bias associated with the sources. Ensure a comprehensive analysis to assist  in determining the credibility of the news report.
    Here are some Examples for you to learn how you can response to my prompt :
    --------------------------------------------------------------------
    [
    {
    "input": "Groundbreaking Research Confirms New Treatment for Common Illness",
    "output": {
    "medical" : "True",
    "news" : "True",
    "reasoning": "A recent scientific study has discovered a revolutionary treatment for [common illness]. The research involved a large sample size and rigorous testing, providing hope for millions of patients worldwide.",
    "label": "Trustworthy",
    "sources": ["link from the internet to the reference that confirms it's trustworthy"]
    }
    },
    {
    "input": "Unverified Sources Claim Extra-terrestrial Contact in Remote Area",
    "output": {
    "medical" : "False",
    "news" : "True",
    "reasoning": "Reports from unidentified sources suggest that extra-terrestrial beings have made contact in a remote area. The lack of credible evidence and reliance on unverified testimonials makes this information highly doubtful.",
    "label": "Doubtful",
    "sources": [link from the internet for the reference that confirms it's doubtful]
    }
    },
    {
    "input": "World Leaders Announce Global Collaboration for Sustainable Energy",
    "output": {
    "medical" : "False",
    "news" : "True",
    "reasoning": "In a historic move, world leaders have come together to announce a comprehensive global collaboration aimed at achieving sustainable and clean energy solutions. The news is corroborated by official statements from multiple government representatives.",
    "label": "Trustworthy",
    "sources": ["https://official-government-statements.com"]
    }
    },
    {
    "input": "Giant Prehistoric Lizard Discovered in Urban Area",
    "output": {
    "medical" : "False",
    "news" : "True",
    "reasoning": "A team of archaeologists claims to have discovered a giant prehistoric lizard in the heart of a major city. The lack of credible sources, scientific backing, and the sensational nature of the news make it likely to be fake.",
    "label": "Fake",
    "sources": ["link from the internet to the reference that confirms it's fake"]
    }
    },
    {
    "input": "What is cancer?",
    "output": {
    "medical" : "True",
    "news" : "False",
    "reasoning": "Cancer is a group of diseases involving abnormal cell growth with the potential to invade or spread to other parts of the body.  ",
    "label": "trustworthy",
    "sources": ["https://official-health-statements.com"]
    }
    },
    ]
    --------------------------------------------------------------------
    Instructions:
    <instructions>
    A - The response should always be only the output part of the JSON.
    B - Responde by JSON contains the fields:
    <json>
        1 - "medical" : "True"  (if the input has a relation with the medical field), or "False" (if the input doen't have a relation to the medical field).
        2-  "news" : "True"  (if the input presents  news, declarations, or information), or "Fake" (if the input presents a question, or is asking to provide information).
        3 - "label" :  "Fake" ( if the input is fake and presents false informations, unverified treatment , or information not aligned with medical research or regulated clinical practices), "Doubtful" (if the input presents trustworthy information contaminated by  some fake information,  or if the information presented is still experimental and is not completely validated by  medical research and clinical practice ), or "Trustworthy"(  if the input presents valid information verified by peer reviewed medical research and common clinical practice).
        4 - "reasoning" : ( contains an explanation to the reason you chose the label ).
        5 - "sources" : contains a list of web sites links, and research papers that have the reference to back up your decision for the label.
    </json>
    C - Don't add any other text besides the JSON response.
    D - Respond to every following prompt by  strictly adhering to the instruction provided above.
    </instructions>
    </SYSTEM>

    <query>
    Strictly following the information and direction provided to you as a system, evaluate this query :
    <input>''' , data , ''' </input>
    </query>" '''


# Choosing which openAi model we want to work with 
def backendHandler(type, prompt):

    Model = ""

    # gpt 4 turbo ai request
    if (type == "GPT4") : 
        Model = "gpt-4" 
        print("Working wih gpt 4 in the open ai ")
    else :
        Model = "gpt-3.5-turbo" 
        print("Working wih gpt 3 turbo in the open ai ")    

    # calling the openAi api
    chat_completion = client.chat.completions.create(
    messages=[
    {
        "role": "user",
        "content": str(prompt), 
    }
    ],
    model= Model,)

    # getting response from open ai
    res = chat_completion.choices[0].message.content
    return res    


# saving the user rating route    
@app.route("/save", methods=["POST"]) 
def saveRating():
    try:
        # getting reference and rating
        data = request.get_json()
        ref = data.get("reference", "")
        rating = data.get('rating', "")
        uid = data.get('user', "anonymose")

        ratingSaveReference(uid, ref, rating)
        return "SUCCESS", 200

    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500 


# saving the user expectation, user prompt + the open ai response in the firebase
def firebaseSave(uid, opinion, data, med, news, res, label):
    # puting user data in firebase
    ref = db.reference(uid).push()
    ref.set({
        "Question": data,
        "Opinion": opinion,
        "Medical": med,
        "News": news,
        "label": label,
        "Response": res,
        "Rating" : "0"
    })
    # returning the key so we can use it to save the rating after
    return str(ref.key)


# save rating in the firebase with the passed reference from the user
def ratingSaveReference(uid, reference, rating):
    # puting user data in firebase
    db.reference(uid).child(reference).child("Rating").set(rating)


# save the user first signup points in the firebase 
@app.route("/pointsave", methods=["POST"]) 
def savePoints():
    try:
        # getting the user id from the request
        data = request.get_json()
        user = data.get("user", "") 
        points = data.get("points", "")  

        db.reference("users").child(user).child("points").set(points)
        return "SUCCESS", 200

    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
    

# check if this is the user's first signup 
@app.route("/pointcheck", methods=["POST"]) 
def checkPoints():
    try:
        # getting the user id from the request
        data = request.get_json()
        user = data.get("user", "")

        points = db.reference("users").child(user).get("points")

        # Extracting points from the tuple
        if (points[0] != None):
            points = points[0].get('points', 1)
            print("Your point are ", points)
            if points is not None:
                # means that this user is not a new user
                return jsonify(points = points), 200
        
        # means this is a new user account 
        return jsonify(points = -1), 200
    
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500 
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
    # app.run(port=4000)