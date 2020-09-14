# [Stratego](https://jacklove5.herokuapp.com)
Play Stratego online

This project started out as an Assignment for an AI class. The original project was written completely in Python and ran from the command line.

For the web version, I kept most of the original Python code intact, but I made a few design changes to faciliate websockets and PvP gameplay. I also added a frontend written in HTML/CSS/JS and used Flask to handle routing.

## Accomplishments
* First time attempting OO Design in Python
* First nontrivial application written in Python
* First web application
* First time trying front end development

## Challenges / Areas for Improvement
Currently the AI is a bit too defensive. In fact, it is deliberately programmed to never attack a piece unless it knows it will win in combat. If the player never moves a particular piece, the AI will literally assume the piece is a bomb and will never attack it. This ultimately makes the AI very weak against aggressive players / most human players in general. I plan to research how to write good utility functions and improve the AI's gameplay. Also, the AI can only look 2-3 moves ahead due to time constraints. I could drastically reduce the runtime of the search by eliminating the deep copy that takes place at each step of the search.

Regarding the website itself, one of the biggest weaknesses I'm aware of is that games are not persistent. If a player disconnects while playing, they'll have no way of recovering their game. I think an approach to solving this would be to somehow store the game's state in a database and generate a random id for each player at the start of the game. This id could be included in a url query to rejoin the game in case of a disconnect. Maybe it could also be stored in the form of a cookie on the user's browser? I plan to research methods of authentication more in the future.

Another issue is that the "join" urls in PvP mode can only be used once. This means if the first player accidently visits the join link before the second player, they'll have to start a new game to get a new join url. This can be fixed by waiting to remove the join url until a user submits a starting piece configuration at which point the user's id can become "locked in."
