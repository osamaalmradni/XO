import tkinter as tk
from tkinter import messagebox
import json
import os

class Player:
    """Represents a player with a name, symbol (X or O), and score."""
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.score = 0

class Board:
    """Represents the game board with 9 cells."""
    def __init__(self):
        self.cells = [""] * 9

    def reset(self):
        """Resets the board to its initial empty state."""
        self.cells = [""] * 9

    def update_cell(self, index, symbol):
        """
        Updates a cell if it's empty, returns True if successful.
        
        Args:
            index (int): The index of the cell to update (0-8)
            symbol (str): The symbol to place in the cell ('X' or 'O')
        
        Returns:
            bool: True if the cell was updated, False if it was already occupied
        """
        if self.cells[index] == "":
            self.cells[index] = symbol
            return True
        return False

    def check_win(self):
        """
        Checks if there's a winning combination on the board.
        
        Returns:
            bool: True if there's a winning combination, False otherwise
        """
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        for combo in win_combinations:
            if self.cells[combo[0]] == self.cells[combo[1]] == self.cells[combo[2]] != "":
                return True
        return False

    def check_draw(self):
        """
        Checks if the board is full and it's a draw.
        
        Returns:
            bool: True if the board is full (draw), False otherwise
        """
        return all(cell != "" for cell in self.cells)

class GameModel:
    """Manages game state, player turns, and interactions with the UI."""
    def __init__(self, controller):
        self.players = [Player("", ""), Player("", "")]
        self.board = Board()
        self.current_player_index = 0
        self.controller = controller
        self.load_scores()

    def setup_players(self, player1_name, player1_symbol, player2_name, player2_symbol):
        """
        Sets player names and symbols, then starts the game.
        
        Args:
            player1_name (str): Name of the first player
            player1_symbol (str): Symbol for the first player ('X' or 'O')
            player2_name (str): Name of the second player
            player2_symbol (str): Symbol for the second player ('X' or 'O')
        """
        self.players[0] = Player(player1_name, player1_symbol)
        self.players[1] = Player(player2_name, player2_symbol)
        self.load_player_scores()
        self.controller.show_game_board()

    def make_move(self, index):
        """
        Handles a player's move, checks for win/draw, and updates the UI.
        
        Args:
            index (int): The index of the cell where the move is made (0-8)
        
        Returns:
            bool: True if the move was successful, False otherwise
        """
        player = self.players[self.current_player_index]
        if self.board.update_cell(index, player.symbol):
            self.controller.update_button_text(index, player.symbol)
            if self.board.check_win():
                player.score += 1
                self.save_scores()
                self.end_game(f"Congratulations {player.name}, you win!")
            elif self.board.check_draw():
                self.end_game("It's a draw!")
            else:
                self.switch_player()
                self.controller.update_status(self.players[self.current_player_index])
            return True
        return False

    def switch_player(self):
        """Switches to the other player."""
        self.current_player_index = 1 - self.current_player_index

    def end_game(self, message):
        """
        Ends the game, displays the message, and prompts to restart.
        
        Args:
            message (str): The message to display at the end of the game
        """
        if messagebox.askyesno("Game Over", f"{message}\nCurrent Scores:\n{self.players[0].name}: {self.players[0].score}\n{self.players[1].name}: {self.players[1].score}\nDo you want to play again?"):
            self.reset_game()
        else:
            self.controller.quit_game()

    def reset_game(self):
        """Resets the game to the initial state."""
        self.board.reset()
        self.current_player_index = 0
        self.controller.reset_buttons()
        self.controller.update_status(self.players[self.current_player_index])

    def load_scores(self):
        """Loads the scores from a JSON file."""
        try:
            with open("scores.json", "r") as file:
                self.scores = json.load(file)
        except FileNotFoundError:
            self.scores = {}

    def save_scores(self):
        """Saves the current scores to a JSON file."""
        for player in self.players:
            self.scores[player.name] = player.score
        with open("scores.json", "w") as file:
            json.dump(self.scores, file)

    def load_player_scores(self):
        """Loads individual player scores from the saved scores."""
        for player in self.players:
            player.score = self.scores.get(player.name, 0)

class GameView:
    """Represents the main window and user interface for the game."""
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe Game")
        self.window.geometry("400x350")
        self.create_main_menu()
        self.window.protocol("WM_DELETE_WINDOW", self.quit_game)

    def create_main_menu(self):
        """Creates the main menu with options to start or quit the game."""
        self.frame = tk.Frame(self.window, bg="#f0f0f0")
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.frame, text="Welcome to Tic-Tac-Toe game!", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333333")
        self.label.pack(pady=20)

        self.start_button = tk.Button(self.frame, text="Start the game", command=self.controller.start_game, font=("Arial", 16), bg="#4CAF50", fg="white", activebackground="#45a049")
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(self.frame, text="Quit the game", command=self.quit_game, font=("Arial", 16), bg="#f44336", fg="white", activebackground="#d32f2f")
        self.quit_button.pack(pady=10)

    def setup_players(self):
        """Creates the setup interface for player names and symbols."""
        self.frame.destroy()
        self.setup_frame = tk.Frame(self.window, bg="#f0f0f0")
        self.setup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        labels = ["Player 1 Name:", "Player 1 Symbol:", "Player 2 Name:", "Player 2 Symbol:"]
        self.entries = []

        for i, text in enumerate(labels):
            label = tk.Label(self.setup_frame, text=text, font=("Arial", 12), bg="#f0f0f0", fg="#333333")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(self.setup_frame, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

        self.submit_button = tk.Button(self.setup_frame, text="Submit", command=self.submit_players, font=("Arial", 14), bg="#2196F3", fg="white", activebackground="#1976D2")
        self.submit_button.grid(row=4, columnspan=2, pady=20)

    def submit_players(self):
        """Validates input and starts the game with the provided player info."""
        player1_name, player1_symbol, player2_name, player2_symbol = [entry.get() for entry in self.entries]
        player1_symbol = player1_symbol.upper()
        player2_symbol = player2_symbol.upper()

        if all(name.isalpha() for name in [player1_name, player2_name]) and \
           all(len(symbol) == 1 and symbol.isalpha() for symbol in [player1_symbol, player2_symbol]) and \
           player1_symbol != player2_symbol:
            self.setup_frame.destroy()
            self.controller.setup_players(player1_name, player1_symbol, player2_name, player2_symbol)
        else:
            messagebox.showerror("Invalid input", "Please enter valid names (letters only) and symbols (different single letters).")

    def show_game_board(self):
        """Creates and displays the game board with buttons for each cell."""
        self.game_frame = tk.Frame(self.window, bg="#e0e0e0")
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.cells = []
        for i in range(9):
            button = tk.Button(self.game_frame, text="", width=5, height=2, 
                               command=lambda i=i: self.controller.on_button_click(i), 
                               font=("Arial", 20, "bold"), bg="white", activebackground="#f0f0f0")
            button.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=tk.NSEW)
            self.cells.append(button)

        for i in range(3):
            self.game_frame.grid_columnconfigure(i, weight=1)
            self.game_frame.grid_rowconfigure(i, weight=1)

        self.score_label = tk.Label(self.game_frame, text="", font=("Arial", 12), bg="#e0e0e0")
        self.score_label.grid(row=3, columnspan=3, pady=10)

        self.update_status(self.controller.game.players[self.controller.game.current_player_index])
        self.update_score_display()

    def update_button_text(self, index, symbol):
        """Updates the button text at a given index with the player's symbol."""
        color = "#FF4081" if symbol == self.controller.game.players[0].symbol else "#2196F3"
        self.cells[index].config(text=symbol, fg=color)

    def update_status(self, player):
        """Updates the window title with the current player's turn."""
        self.window.title(f"{player.name}'s turn ({player.symbol})")

    def reset_buttons(self):
        """Resets all the buttons on the game board."""
        for button in self.cells:
            button.config(text="", fg="black")

    def update_score_display(self):
        """Updates the score display label."""
        score_text = f"{self.controller.game.players[0].name}: {self.controller.game.players[0].score}  |  {self.controller.game.players[1].name}: {self.controller.game.players[1].score}"
        self.score_label.config(text=score_text)

    def quit_game(self):
        """Handles quitting the game and deleting scores."""
        self.controller.delete_scores()
        self.window.quit()

class GameController:
    """Controller to manage the interactions between the model and the view."""
    def __init__(self):
        self.view = GameView(self)
        self.game = GameModel(self)

    def start_game(self):
        """Starts the game by setting up players."""
        self.view.setup_players()

    def setup_players(self, player1_name, player1_symbol, player2_name, player2_symbol):
        """Sets up players and initializes the game."""
        self.game.setup_players(player1_name, player1_symbol, player2_name, player2_symbol)

    def show_game_board(self):
        """Displays the game board."""
        self.view.show_game_board()

    def on_button_click(self, index):
        """Handles button clicks on the game board."""
        if self.game.make_move(index):
            self.view.update_score_display()

    def update_button_text(self, index, symbol):
        """Updates the button text at a given index with the player's symbol."""
        self.view.update_button_text(index, symbol)

    def update_status(self, player):
        """Updates the window title with the current player's turn."""
        self.view.update_status(player)

    def reset_buttons(self):
        """Resets all the buttons on the game board."""
        self.view.reset_buttons()

    def delete_scores(self):
        """Deletes the scores JSON file."""
        if os.path.exists("scores.json"):
            os.remove("scores.json")

    def quit_game(self):
        """Quits the game."""
        self.view.quit_game()

if __name__ == "__main__":
    controller = GameController()
    controller.view.window.mainloop()