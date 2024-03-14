import numpy as np
from random import random
from random import randint
import pip

try:
	import pydot
except ImportError as e:
	pip.main(['install', 'pydot'])

visualization_import_success = False
try:
	import pydot
	visualization_import_success = True
except ImportError as e:
	visualization_import_success = False

def check_assertion(G: list[list], W: list[list], init: int):
	'''
	check_assertions checks if the system satisfies the assertion.
	G is an n-by-n array: G[i,j] = 1 iff there's a transition from state i to state j.
	W is an n-by-2 array: W[i,0] = 1 iff gnt = 1 in state i, and W[i,1] = 1 iff req = 1 in state i.
	init is an integer indicating the initial state.
	n is the number of states of the system.
	'''
	print("Check assertion is not implemented yet.")

def main():
	for i in range(3):
		G, W, init = gen_random_fsm()

		if visualization_import_success:
			create_graph_visualization(G, W, init, f'Graph {i+1}.png')
		else:
			terminal_display_matrix(G, init, f'Graph {i+1}')

		check_assertion(G, W, init)

def gen_random_fsm():
	state_count = randint(2, 10)
	transition_map = []
	for i in range(state_count):
		transition_map.append(get_random_array(0, state_count, distribution=randfloat(.25, .75)))

	#Prevent transitionless state.
	for state_num, transition_for_state in enumerate(transition_map):
		while sum(transition_for_state) < (2 if len(transition_for_state) > 2 else len(transition_for_state) - 1):
			rand_index = randint(0, len(transition_for_state)-1)
			while rand_index == state_num:
				rand_index = randint(0, len(transition_for_state)-1)
			
			transition_map[state_num][rand_index] = 1

	state_response_grid = []
	for i in range(state_count):
		state_response_grid.append(get_random_array(0, 2, distribution=randfloat(.6, .8)))
	
	init_state = randint(0, state_count-1)

	return transition_map, state_response_grid, init_state

def get_random_array(beg: int, length: int, distribution: float = .5):
	return [int(random() <= distribution and i >= beg) for i in range(length)]

def randfloat(low: int, high: int):
	return random() % (high-low) + low

def terminal_display_matrix(matrix, start_state=0, title=''):
	output_str = ''

	if len(title):
		output_str = title + f', Starting State - S{start_state}\n'

	for x in range(len(matrix)):
		for y in range(len(matrix)):
			output_str += str(matrix[y][x])

			if y < len(matrix) - 1:
				output_str += '  '
		
		output_str += '\n'
	print(output_str)

def create_graph_visualization(matrix, state_responses, start_state=0, title='test.png'):
	dot_str = f'DIGRAPH graph_name ' + '{\n'
	dot_str += f'S{start_state} [fontcolor=blue]'
	dot_str += 'concentrate=true\n'

	for state_index in range(len(state_responses)):
		attr = ''
		if state_responses[state_index][0] and state_responses[state_index][1]:
			attr = f'S{state_index} [label="S{state_index}\ngnt\nreq"]'
		elif state_responses[state_index][0] and not state_responses[state_index][1]:
			attr = f'S{state_index} [label="S{state_index}\ngnt"]'
		elif not state_responses[state_index][0] and state_responses[state_index][1]:
			attr = f'S{state_index} [label="S{state_index}\nreq"]'

		dot_str += attr + '\n'

	for x in range(len(matrix)):
		for y in range(len(matrix)):
			if matrix[x][y]:
				dot_str += f'S{x} -> S{y}\n'

	dot_str += '}'

	graphs = pydot.graph_from_dot_data(dot_str)
	graphs[0].write_png(title)

if __name__ == "__main__":
	main()