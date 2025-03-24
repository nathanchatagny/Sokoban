# Sokoban Game Improvement: Level Progression & Scoring System

Overview
In this improvement of the Sokoban game, I have added two key features to enhance the gameplay experience:

Level Progression: The game now advances to the next level upon completing the current level. Each level is followed by a transition that shows the player’s progress.

Scoring System: The game includes a points system, where each move subtracts points from a base score of 10,000. The player can see their remaining points as they play, creating a challenge to complete levels in fewer moves. At the end of the game, the final score is displayed on a congratulatory page.

Features Added
Level Progression: After completing a level, the game automatically loads the next level. If all levels are completed, a congratulatory message is displayed, including the player’s final score.

Scoring System: Each move in the game deducts 10 points from the starting score of 10,000. This encourages players to complete levels efficiently. The score is updated in real time, visible on the screen.

Completion Screen: Once all levels are completed, the game displays a final screen congratulating the player and showing their score.

Approach and Design
Level Progression:

At the end of each level, the game checks if there are more levels. If there are, the game transitions to the next level automatically. If the player has completed all levels, a congratulatory message is shown.

Scoring System:

The game starts with a score of 10,000. Each time the player makes a move, 10 points are subtracted from the score. The score is displayed on the screen, and the player can see how efficient they are in solving the levels.

The score is updated every time the player makes a move, and it is displayed in real-time.

End-of-Game Message:

Once the player finishes all the levels, a page displays a message of congratulations along with the total score achieved. This offers a sense of accomplishment.

