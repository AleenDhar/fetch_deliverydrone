from flask import Flask
from flask_cors import CORS
from uagents.query import query
from uagents import Model
import json
 
# Define Request Data Model classes for interacting with different agents
class DeliveryReq(Model):
    gps_loc: str


# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enables CORS for all domains on all routes
 
# Define agent addresses
news_agent_address = "agent1q2e9kfdrxfa5dxn6zeyw47287ca36cdur9xevhmdzzfmf4cwlmahv73dadasv"



@app.route('/')
def home():
    return "Welcome to the Drone !"
 
# Define an asynchronous endpoint to get news for a given company
@app.route('/api/news/<string:gps_loc>', methods=['GET'])
async def get_news(gps_loc):
    print(gps_loc)
    response = await query(destination=news_agent_address, message=DeliveryReq(gps_loc=gps_loc), timeout=15.0)
    data = json.loads(response.decode_payload())
    print(data)
    return data["drone_res"]
 
 

 
# Start the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)