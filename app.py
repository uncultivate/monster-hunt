from flask import Flask, jsonify, request
from flask_cors import CORS
from simulation import GameState, GRID_WIDTH, GRID_HEIGHT, NUM_ENGINEERS, ENGINEER_EMOJIS, ENGINEER_NAMES

app = Flask(__name__)
CORS(app)

game_state = GameState()

@app.route('/update', methods=['GET'])
def update_game():
    update_occurred = game_state.update()
    return jsonify({"update_occurred": update_occurred, **game_state.to_dict()})



# Add a new /reset route
@app.route('/reset', methods=['POST'])
def reset():
    global game_state
    game_state = GameState()
    return jsonify(game_state.to_dict())

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(game_state.to_dict())

if __name__ == '__main__':
    app.run(debug=True)

# This is for testing the simulation
# if __name__ == '__main__':
#     game = GameState()
#     for _ in range(100):

#         game.update()
#         print(game.to_dict())