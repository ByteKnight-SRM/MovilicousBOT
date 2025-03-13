from flask import Flask, request, jsonify
import requests
import json
import config
from db_handler import save_movie_details
from send_email import send_movie_email

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)

    # Debugging: Print incoming request
    #print("Received JSON:", data)  

    # Ensure 'queryResult' and 'parameters' exist
    if not data or 'queryResult' not in data or 'parameters' not in data['queryResult']:
        return jsonify({"fulfillmentText": "Sorry, I didn't understand. Please try again with a movie name."})

    # Extract the intent from the request
    intent = data['queryResult']['intent']['displayName']

    # Extract movie parameter safely
    movie = data['queryResult']['parameters'].get('movie', [])
    # If movie is not present in the current intent, check the context for the previous movie
    if not movie and 'outputContexts' in data['queryResult']:
        for context in data['queryResult']['outputContexts']:
            if 'movie' in context['parameters']:
                movie = [context['parameters']['movie']]
                break

    if isinstance(movie, str):  # If it's a string, convert it to a list
        movie = [movie]

    # Check if movie is empty or incorrectly formatted
    if not movie or not isinstance(movie, list) or len(movie) == 0:
        return jsonify({"fulfillmentText": "Please provide a valid movie name."})

    # Extract first movie name and format it for OMDb
    movie_name = movie[0].replace(" ", "_")
    print("\n\nMovie:", movie_name)

    # Fetch movie details from OMDb API
    movie_detail = requests.get(f'http://www.omdbapi.com/?t={movie_name}&apikey={config.OMDB_API}').json()  # Convert response to dictionary
    metascore = movie_detail.get('Metascore', 'N/A')
    # Print OMDb response for debugging
    # print("OMDb API Response:", movie_detail)

    # Handle movie not found case
    if 'Title' not in movie_detail:
        return jsonify({"fulfillmentText": "Sorry, I couldn't find that movie. Try another one!"})

    save_movie_details(movie_detail)

    # Prepare response for movie details
    
    response_text = f"""
    🎬 TITLE: {movie_detail['Title']}
    📅 RELEASED: {movie_detail['Released']}
    👥 ACTORS: {movie_detail['Actors']}
    🎭 PLOT: {movie_detail['Plot']}
    """
    
    
    # Check if the intent is to get the movie detail
    if intent == 'get_movie-detail':
        response_text += "\n\nWould you like to know the metascore for this movie?"

    # Check if the intent is to get the metascore
    elif intent == 'get_movie-detail - yes':
          # Get metascore or 'N/A' if not available
        metascore = movie_detail.get('Metascore', 'N/A')
        #print(movie_detail['Title'])
        #response_text = f"The Metascore for {movie_detail['Title']} is {metascore}."

        if metascore != 'N/A':
            metascore = int(metascore)  # Convert metascore to integer for comparison
            if metascore >= 80:
                response_text = f"The Metascore for '{movie_detail['Title']}' is {metascore}. Seems like an awesome movie! Definitely worth watching!"
            elif metascore >= 60:
                response_text = f"The Metascore for '{movie_detail['Title']}' is {metascore}. Looks pretty good! Might be a fun watch."
            else:
                response_text = f"The Metascore for '{movie_detail['Title']}' is {metascore}. Eeh... give it a shot if you're feeling adventurous."
        else:
            response_text = "Sorry, I couldn't find the Metascore for that movie."
    # Send the response to Dialogflow
    #return jsonify({"fulfillmentText": response_text})

    elif intent == 'get_email':
        user_email = data['queryResult']['parameters'].get('email', [])
        print(user_email)
        if not user_email:
            return jsonify({"fulfillmentText": "Please provide a valid email address."})

        # Send email with movie details
        email_sent = send_movie_email(user_email, movie_detail['Title'])

        if email_sent:
            response_text = f"✅ Movie details have been sent to {user_email}!"
        else:
            response_text = "❌ Failed to send email. Please try again later."

    return jsonify({"fulfillmentText": response_text})

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5001)
