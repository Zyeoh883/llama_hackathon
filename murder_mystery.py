import os
import random
from crewai.agent import Agent
from crewai.task import Task
from crewai.crew import Crew
from crewai.process import Process
from langchain_openai import ChatOpenAI

api_key = input("Enter your openai-api key: ")

os.environ["OPENAI_API_BASE"] = 'https://api.groq.com/openai/v1'
os.environ["OPENAI_API_KEY"] = api_key

is_verbose = False

chat_model = ChatOpenAI(model_name="llama3-8b-8192", temperature=0.7)

game_master = Agent(
    role="game master",
    goal="Provide the events last night for each of the ducks and the killer",
    backstory="You are the Game Master",
    verbose=is_verbose,
    allow_delegation=False,
    llm=chat_model)

check_death = Agent(role="Check for death",
              goal="Just output only the name of the character who died or was killed if any",
              backstory="You are displaying the death of a character if any",
              verbose=is_verbose,
              allow_delegation=False,
              llm=chat_model)

# murderer = Agent(
#     role="murderer suspect",
#     goal="display input given",
#     backstory="You are displaying the information input by the user",
#     verbose=is_verbose,
#     allow_delegation=False,
#     llm=chat_model)

Intro_str = """**Objective:**
As the Sheriff, your goal is to identify the murderer among the ducks and bring them to justice.

**Gameplay:**

1. **duck Selection:** The game begins with the selection of 6-8 ducks (players) who will participate in the game. Each duck has a unique character, occupation, and motive.
2. **Murder:** The game master (me) will announce the murder of one of the ducks. The victim's character, occupation, and motive will be revealed.
3. **Investigation:** The Sheriff (you) will begin the investigation by asking questions to the ducks, trying to gather information about the murder. Each duck will respond with a statement, providing clues or misleading information.
4. **Clue Cards:** Throughout the game, the Sheriff will receive Clue Cards containing vital information about the murder. These cards can be used to cross-examine ducks, uncover alibis, or reveal motives.
5. **Accusations:** The Sheriff can accuse a duck of being the murderer at any time. If correct, the game ends, and the Sheriff wins. If incorrect, the game continues, and the Sheriff must continue investigating.
6. **duck Elimination:** As the game progresses, ducks can be eliminated from the game by the Sheriff if they are deemed to be innocent. The Sheriff must use their Clue Cards wisely to eliminate suspects and narrow down the list of potential murderers.
7. **Game End:** The game ends when the Sheriff correctly accuses the murderer or all ducks have been eliminated. If the Sheriff correctly identifies the murderer, they win the game. If all ducks have been eliminated, the game master reveals the true murderer, and the game ends with no winner.

**Additional Rules:**

* All ducks are assumed to be innocent until proven guilty.
* The Sheriff cannot ask duplicate questions to the same duck.
* Clue Cards can be used strategically to gain an advantage or distract from a suspect.
* The game master has the final say in all matters, including the interpretation of Clue Cards and the outcome of the game.

**Are you ready to begin the investigation?**
"""

# Class/ Struct for Agent and alive state
class Player:
	def __init__(self, role="innocent suspect", alive=True):
		self.name = ""
		self.alive = alive
		self.agent = Agent(
			role=role,
			goal="Answer the input by the user only within 3 sentences and prove you are innocent, share only your experiences",
			backstory="You are an innocent duck in Duckville Town",
			verbose=is_verbose,
			allow_delegation=False,
			llm=chat_model
		)

# Global Declarations
names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry", 
         "Ivy", "Jack"]
history = []
# ducks = []
DEAD = 0
ALIVE = 1


def yes_no(question):
	while (True):
		ans = (input(question + (" (y/n): ")))
		if ans == "y":
			return (1)
		elif ans == "n":
			return (0)
		print("Please enter a 'y' or 'n'")

def init_ducks(num_of_ducks): # ! Fix random names, aka dont let Alice be killer lmao
  # First duck is the Killer
	name_list = names[:num_of_ducks]
	random.shuffle(name_list)
	ducks = []
	ducks.append(Player(role="murder suspect"))
	ducks[0].agent = Agent(
		role="murder suspect",
		goal="Answer the input by the user only within 3 sentences, share only your experiences",
		backstory="You are the killer in Duckville Town",
		verbose=is_verbose,
		allow_delegation=False,
		llm=chat_model
	)

	# Setting all other ducks as innocents
	for n in range(1, num_of_ducks):
		ducks.append(Player())
	for n in range(0, num_of_ducks):
		ducks[n].name = name_list[n]
		# print(ducks[n])
		# print(ducks[n].name)
	return ducks


# Logs output in [name] and then message on newline
def add_to_history(name, message):
  history.append('[' + name + ']' + message + '\n')


# Output Game Objective and input num of ducks
def setup():
#   Intro_str = "Welcome to the village setup!"
  print(Intro_str)

  while True:
    try:
      num_of_ducks = int(input("Number of ducks: "))
      if 3 <= num_of_ducks <= 10:
        return (num_of_ducks)
      else:
        print("Number of ducks should be between 3 to 10.")
    except ValueError:
      print("Please enter a valid integer.")



def give_statement(num_of_ducks, ducks):

	# current_task
	random.shuffle(ducks)
	for duck in ducks:
		if duck.agent.role == "murder suspect":
			current_task = (Task(
				description=
				f"""You are {duck.name}. Describe what you did in only 2 sentences but lie if it hints that you are
				the killer, the nights are based on the string starting with [GM] in history [{history}], but say nothing from the history.'""",
				agent=duck.agent,
				expected_output="I'm sure I did this",
			))
		elif duck.alive == True:
			current_task = (Task(
				description=
				f"""You are {duck.name}. Describe what you did in only 2 sentences, it should be inline with the nights based on the string starting with [GM] in history [{history}], but say nothing from history.""",
				agent=duck.agent,
				expected_output="",
			))
		else:
			output = ": dead"
			add_to_history(duck.name, output)
			print(duck.name)
			print(output)
			continue

		crew = Crew(agents=[duck.agent],
					tasks=[current_task],
					verbose=0,
					process=Process.sequential)

		output = crew.kickoff()
		add_to_history(duck.name, output)
		print(duck.name)
		print(output)
			
	return (output)


def create_scenario(num_of_ducks, ducks):

	for duck in ducks:
		if duck.agent.role == "murder suspect":
			killer_name = duck.name

	chance = random.randint(0, 2)
	name_list = names[:num_of_ducks]
	dead = ""
	if chance == 0:
		while True:
			random.shuffle(name_list)
			for temp in ducks:
				if temp.name == name_list[0]:
					duck = temp
			if duck.agent.role != "murder suspect" and duck.alive:
				dead = duck.name + "died"
				duck.alive = False
				break


	name_list = names[:num_of_ducks]
	for n, duck in enumerate(ducks):
		if duck.alive == False:
			name_list[n] = ""

	task = Task(
		description=f"{dead}. Provide what the ducks [{names[:num_of_ducks]}] did last night and how killer [{killer_name}] killed any ducks if anyone died recently. Keep in line with the history ['{history}'] that starts with [GM], add more to the story short.",
		agent=game_master,
		expected_output= "What each duck did and what did the killer do"
	)
	crew = Crew(agents=[game_master],
            tasks=[task],
    		verbose=0,
    		process=Process.sequential
        )
	output = crew.kickoff()
	# print("[GM]" + output)
	add_to_history("GM", output)
	# print(history)
	task = Task(
		description=f"the last sentences in ['{history}'] that starts with [GM], output only name of the most recent death if any",
		agent=game_master,
		expected_output= "Alice"
	)
	crew = Crew(agents=[check_death],
            tasks=[task],
    		verbose=0,
    		process=Process.sequential
        )
	output = crew.kickoff()
	for duck in ducks:
		if output == duck.name:
			duck.alive = False
 

def investigate_duck(duck):

	print("3 Questions can be asked")
	for n in range(1, 4):

		question = input(f"Question {n} {duck.name}: ")

		respond_to_question = Task(
			description=f"You are {duck.name}. Respond to the question [{question}], inline with the history [{history}] starting with [GM]. If you're the murderer, lie if it hints that you are the killer.",
			agent=duck.agent,
			expected_output="",
		)

		crew = Crew(
			agents=[duck.agent], 
			tasks=[respond_to_question],
			verbose=0,
			process=Process.sequential
		)

		# output = ""
		output = crew.kickoff()
		print(output)
		add_to_history(duck.name, output)

def open_investigation(ducks):
  # Investigate one duck
	print("Opening investigation")
	while (True):
		duck_choice = input("Who do you want to investigate ? (Enter Name) ")
		for duck in ducks:
				if duck.name.lower() == duck_choice.lower():
					investigate_duck(duck)
					return
		print("You need to choose an existing duck")

def win(ducks):
	print("You caught the Killer!!!")
	print("\n\nYOU WIN!!!!\n\n")
	score = 0
	total = -1
	for duck in ducks:
		total += 1
		if (duck.alive == True):
			score += 1
	print("====== SCORE ======")
	print(f"       {score} / {total}        ")

def loss(ducks):
	print("Killer Won!!!")
	print("\n\nYOU LOST!!!!\n\n")
	total = -1
	for duck in ducks:
		total += 1
	print("====== SCORE ======")
	print(f"       0 / {total}        ")

def check_winloss(ducks):
	innocent = -1
	for duck in ducks:
		if duck.agent.role == "murder suspect" and duck.alive == False:
			win(ducks)
			return (0)
		if duck.alive == True:
			innocent += 1
	if innocent == 0:
		loss(ducks)
		return (0)
	return 1

def voting_system(ducks):
	print("Opening voting system")
	while (True):
		vote_choice = input("Who do you want to vote out (Enter name)? ")
		for duck in ducks:
			if vote_choice == duck.name and duck.alive == True:
				duck.alive = False
				return

def main():
	while (True):
		history.clear()
		num_of_ducks = setup()
		ducks = init_ducks(num_of_ducks)
		### print out name of all agents

		while (check_winloss(ducks)):
			create_scenario(num_of_ducks, ducks)
			give_statement(num_of_ducks, ducks)
			if (check_winloss == 0):
				break
			if (yes_no("Do you want to investigate someone?")):
				open_investigation(ducks)
			if yes_no("Do you want to vote someone out?"):
				voting_system(ducks)
		if (yes_no("Do you want to play again?") == 0):
			exit()


if __name__ == '__main__':
  main()
