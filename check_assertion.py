from random import random
from random import randint
import pip
import copy
import os
import sys

#Attempt to import pydot. Failing to import pydot will not result in program failure. It will only result in an inferior visualization.
try:
	import pydot
except ImportError as e:
	pip.main(['install', '--no-python-version-warning', '--force-reinstall', '--upgrade', 'pydot'])

visualization_import_success = False
try:
	import pydot
	#It is apparently possible to successfully import pydot, but not have access to the libraries. The following ensures access.
	(test_graph,) = pydot.graph_from_dot_data('Graph name {A -> B}')
	test_graph.create_png()
	visualization_import_success = True
except:
	visualization_import_success = False

def check_assertion(G: list[list], W: list[list], init: int):
	'''
	check_assertions checks if the system satisfies the assertion.
	Parameter: G is an n-by-n array: G[i,j] = 1 iff there's a transition from state i to state j.
	Parameter: W is an n-by-2 array: W[i,0] = 1 iff gnt = 1 in state i, and W[i,1] = 1 iff req = 1 in state i.
	Paramater: init is an integer indicating the initial state.
	n is the number of states of the system.

	Returns a satisfying trace.
	'''
	#Go through all states in W.
	for i in range(len(W)):
		#Check if gnt is true for the state in question.
		if W[i][0] == 1:
			#Go through all transitions.
			for j in range(len(G)):    # check all the transition from state i to j
				#Check if req is false for the connected state.
				if G[i][j] and not W[j][1]:
					#Return the failed trace.
					return [i, j]
	return []

def find_trace(G, init, final):
	'''
	Graph search the shortest route between init and final.
	Parameter: G - Adjacency matrix.
	Parameter: init - the starting node.
	Parameter: final - the start of the interesting trace.
	Returns: route to get from init to final. If they are the same it is an empty list.
	'''
	trace = []
	distance_list = [[] for i in range(len(G))]

	#Done if we're already there.
	if init != final:
		starting_points = [init]
		have_visited = []

		found_end = False
		while not found_end and starting_points:
			#Breadth first search.
			init_point = starting_points.pop(0)

			for transitions_index in range(len(G)):
				#Add connections to the starting point list.
				if G[init_point][transitions_index] and transitions_index != init_point and not transitions_index in have_visited:
					starting_points.append(transitions_index)
					have_visited.append(transitions_index)

				#If there is a better path, make that the new path.
				if G[init_point][transitions_index] and (len(distance_list[transitions_index]) == 0 or len(distance_list[init_point]) + 1 < len(distance_list[transitions_index])) and transitions_index != init_point:
					distance_list[transitions_index] = copy.deepcopy(distance_list[init_point])
					distance_list[transitions_index].append(init_point)
				
				#If there is a connection to the end, we've found the magic trace.
				if transitions_index == final and G[init_point][transitions_index]:
					found_end = True
					trace = distance_list[transitions_index]
					break

	return trace

def main():
	'''
	The place where all the code happens.
	'''
	global graph_number
	graph_number = 0

	if visualization_import_success:
		results_path = get_new_result_folder_name()
		os.mkdir(results_path)

	#The graph sizes.
	sizes = [5, 10, 15]
	for i in range(len(sizes)):
		#Find a graph that passes the assertion and fails the assertion (so there are graphs of interest).
		fsm_tracker = {'have_failed': False, 'have_passed': False}
		while not fsm_tracker['have_failed'] or not fsm_tracker['have_passed']:
			G, W, init = gen_random_fsm(sizes[i])
			fsm_trace = check_assertion(G, W, init)
			#If the fsm_trace is empty, there was no failing trace.

			should_display = False

			if not fsm_tracker['have_failed'] and fsm_trace:
				fsm_tracker['have_failed'] = True
				should_display = True
			elif not fsm_tracker['have_passed'] and not fsm_trace:
				fsm_tracker['have_passed'] = True
				should_display = True

			if should_display:
				#If the visualization libaries imported successfully, use fancy visualization of the graph and the trace. Otherwise use terminal display.
				graph_number += 1

				if fsm_trace:
					shortest_trace = find_trace(G, init, fsm_trace[0])
					shortest_trace.extend(fsm_trace)

					fsm_trace = copy.deepcopy(shortest_trace)

				title = f'Graph {graph_number} ({sizes[i]} states - '
				if len(fsm_trace) > 0:
					title += 'Fails Assertion'
				else:
					title += 'Passes Assertion'

				if visualization_import_success:
					title = os.path.join(results_path, title)

					create_graph_visualization(G, {state_number: W[state_number] for state_number in range(len(W))}, init, title + ').png')
					if len(fsm_trace) > 0:
						create_graph_visualization(fsm_trace, {state_number: W[state_number] for state_number in list(set(fsm_trace))}, init, title + f' Trace {fsm_trace}).png')
				else:
					terminal_display_matrix(G, W, init, title + ')')
					if len(fsm_trace) > 0:
						print('Failure trace:\n' + ' -> '.join([str(state) for state in fsm_trace]) + '\n')
						print('Satisfying trace:\n' + ' -> '.join([str(state) for state in fsm_trace[-2:]]) + '\n')

def gen_random_fsm(state_count=randint(2, 10)):
	'''
	Create a completely randomized finite state machine with a given state count.
	Returns an adjacency matrix, a state_response_grid, and init.
	'''
	#Random initial state.
	init_state = randint(0, state_count-1)

	#Make randomized adjacency matrix.
	#Ensure it is traversable.
	transition_map = []
	found_connected_map = False
	while not found_connected_map:
		transition_map = []
		for state in range(state_count):
			transition_map.append(get_random_array(0, state_count, distribution=randfloat(.25, .4)))

		found_connected_map = True

		for state in range(len(transition_map)):
			if state != init_state and not find_trace(transition_map, init_state, state):
				found_connected_map = False

	#Create a randomized response grid.
	#	The grid has a higher req/gnt density the more states there are (to promote successfull assertion graphs).
	state_response_grid = []
	for i in range(state_count):
		top = state_count/15
		if top > .9:
			top = .9
		if top < .7:
			top = .7
		
		bottom = state_count/20
		if bottom > .8:
			bottom = .8
		if bottom < .5:
			bottom = .5

		state_response_grid.append(get_random_array(0, 2, distribution=randfloat(bottom, top)))

	return transition_map, state_response_grid, init_state

def get_random_array(beg: int, length: int, distribution: float = .5):
	'''
	Make an array with a distribution.
	Parameter: beg - where to start from.
	Parameter: length - the length of the array.
	Paramater: distribution - a number correlated with the randomized distribution (better than coin flip).
	Returns: a randomized list.
	'''
	return [int(random() <= distribution and i >= beg) for i in range(length)]

def randfloat(low: int, high: int):
	'''
	Return a bounded float.
	Parameter: low - the lower bound (inclussive).
	Parameter: high - the upper bound (inclussive).
	'''
	return random() % (high-low) + low

def terminal_display_matrix(matrix, state_responses, start_state=0, title=''):
	'''
	Display the matrix in the terminal.
	Parameter: matrix - an adjacency matrix to display.
	Parameter: state_responses - a state wise map where [0] represents gnt and [1] represents req.
	Parameter: start_state - the starting state of the graph.
	Paramater: title - something to differentiate the display.
	'''

	output_str = ''

	#Only add a title if there is one to add.
	if len(title):
		output_str += title + f', Starting State - S{start_state}\n'

	#Add labels to the top.
	output_str += '\t'.join(['-' if i < 2 else (str(i-2) if i-2 != start_state else f'*{i-2}') for i in range(len(matrix)+2)]) + '\n'
	output_str += '\t'.join(['_' for i in range(len(matrix)+2)]) + '\n'

	#Go through the adjacency matrix.
	for x in range(len(matrix)):
		#If the current state is the start state, put a * infront.
		if x == start_state:
			output_str += '*'
		
		#Put the incoming state on the left.
		output_str += f'{x}\t|\t'
		#Iterate through matrix.
		for y in range(len(matrix)):
			#1 for transition existing, 0 for no transition.
			output_str += str(matrix[x][y])

			#Place a tab between each value.
			if y < len(matrix) - 1:
				output_str += ' \t'
		
		output_str += '\n'
	
	#Display the conditionals.
	output_str += '\nConditionals:\n'
	output_str += '-\t-\tgnt\treq\n'
	output_str += '\t'.join(['__' for i in range(len(state_responses[0]) + 2)]) + '\n'

	for state_index in range(len(state_responses)):
		if state_index == start_state:
			output_str += '*'
		
		output_str += f'{state_index}\t|\t'

		output_str += '\t'.join([str(i) for i in state_responses[state_index]])
	
		output_str += '\n'

	print(output_str)

def create_graph_visualization(matrix, state_responses, start_state=0, title='test.png'):
	'''
	Use dot notation to represent the bidirectional matrix.
	Parameter: matrix - an adjacency matrix.
	Parameter: state_responses - a state wise map where [0] represents gnt and [1] represents req.
	Parameter: start_state - the starting state of the graph.
	Paramater: title - something to differentiate the display.
	'''
	dot_str = f'DIGRAPH graph_name ' + '{\n'
	#Make starting node blue.
	dot_str += f'S{start_state} [color=blue fontcolor=white style=filled]\n'

	if 'list' in str(type(matrix[0])):
		#Make any transition bidirectional (without needing to be intelligent about it).
		dot_str += 'concentrate=true\n'
	
	for state_index in state_responses:
		attr = ''

		#Add the state response in each state bubble.
		if state_responses[state_index][0] and state_responses[state_index][1]:
			attr = f'S{state_index} [label="S{state_index}\ngnt\nreq"]'
		elif state_responses[state_index][0] and not state_responses[state_index][1]:
			attr = f'S{state_index} [label="S{state_index}\ngnt"]'
		elif not state_responses[state_index][0] and state_responses[state_index][1]:
			attr = f'S{state_index} [label="S{state_index}\nreq"]'
	
		dot_str += attr + '\n'

	if 'list' in str(type(matrix[0])):
		for x in range(len(matrix)):
			#Make a color for the transitions leaving a node.
			color = color_list[randint(0, len(color_list)-1)]
			for y in range(len(matrix)):
				if matrix[x][y]:
					#Add the transition and set it to be a color.
					dot_str += f'S{x} -> S{y} [color={color} style=bold]\n'
	else:
		#If the matrix is not a list of lists, then it must be a trace, in which case we only need to show state to state (list of sequential states).
		for x in range(len(matrix)-1):
			dot_str += f'S{matrix[x]} -> S{matrix[x+1]} [label={x+1}{"color=brown style=bold" if x == len(matrix)-2 else ""}]\n'

	dot_str += '}'

	#Make a png.
	(graph,) = pydot.graph_from_dot_data(dot_str)
	graph.write_png(title)

color_names = '''
aliceblue	aqua	aquamarine	aquamarine1	aquamarine2
aquamarine3	aquamarine4	azure	azure1	azure2
azure3	azure4	beige	bisque	bisque1
bisque2	bisque3	bisque4	black	blanchedalmond
blue	blue1	blue2	blue3	blue4
blueviolet	brown	brown1	brown2	brown3
brown4	burlywood	burlywood1	burlywood2	burlywood3
burlywood4	cadetblue	cadetblue1	cadetblue2	cadetblue3
cadetblue4	chartreuse	chartreuse1	chartreuse2	chartreuse3
chartreuse4	chocolate	chocolate1	chocolate2	chocolate3
chocolate4	coral	coral1	coral2	coral3
coral4	cornflowerblue	cornsilk	cornsilk1	cornsilk2
cornsilk3	cornsilk4	crimson	cyan	cyan1
cyan2	cyan3	cyan4	darkblue	darkcyan
darkgoldenrod	darkgoldenrod1	darkgoldenrod2	darkgoldenrod3	darkgoldenrod4
darkgray	darkgreen	darkgrey	darkkhaki	darkmagenta
darkolivegreen	darkolivegreen1	darkolivegreen2	darkolivegreen3	darkolivegreen4
darkorange	darkorange1	darkorange2	darkorange3	darkorange4
darkorchid	darkorchid1	darkorchid2	darkorchid3	darkorchid4
darkred	darksalmon	darkseagreen	darkseagreen1	darkseagreen2
darkseagreen3	darkseagreen4	darkslateblue	darkslategray	darkslategray1
darkslategray2	darkslategray3	darkslategray4	darkslategrey	darkturquoise
darkviolet	deeppink	deeppink1	deeppink2	deeppink3
deeppink4	deepskyblue	deepskyblue1	deepskyblue2	deepskyblue3
deepskyblue4	dimgray	dimgrey	dodgerblue	dodgerblue1
dodgerblue2	dodgerblue3	dodgerblue4	firebrick	firebrick1
firebrick2	firebrick3	firebrick4	forestgreen
fuchsia	gainsboro	gold	gold1
gold2	gold3	gold4	goldenrod	goldenrod1
goldenrod2	goldenrod3	goldenrod4
green	green1	green2	green3	green4
greenyellow	honeydew	honeydew1
honeydew2	honeydew3	honeydew4	hotpink	hotpink1
hotpink2	hotpink3	hotpink4	indianred	indianred1
indianred2	indianred3	indianred4	indigo	invis
ivory	ivory1	ivory2	ivory3	ivory4
khaki	khaki1	khaki2	khaki3	khaki4
lavender	lavenderblush	lavenderblush1	lavenderblush2	lavenderblush3
lavenderblush4	lawngreen	lemonchiffon	lemonchiffon1	lemonchiffon2
lemonchiffon3	lemonchiffon4	lightblue	lightblue1	lightblue2
lightblue3	lightblue4	lightcoral	lightcyan	lightcyan1
lightcyan2	lightcyan3	lightcyan4	lightgoldenrod	lightgoldenrod1
lightgoldenrod2	lightgoldenrod3	lightgoldenrod4	lightgoldenrodyellow	lightgray
lightgreen	lightgrey	lightpink	lightpink1	lightpink2
lightpink3	lightpink4	lightsalmon	lightsalmon1	lightsalmon2
lightsalmon3	lightsalmon4	lightseagreen	lightskyblue	lightskyblue1
lightskyblue2	lightskyblue3	lightskyblue4	lightslateblue	lightslategray
lightslategrey	lightsteelblue	lightsteelblue1	lightsteelblue2	lightsteelblue3
lightsteelblue4	lightyellow	lightyellow1	lightyellow2	lightyellow3
lightyellow4	lime	limegreen	linen	magenta
magenta1	magenta2	magenta3	magenta4	maroon
maroon1	maroon2	maroon3	maroon4	mediumaquamarine
mediumblue	mediumorchid	mediumorchid1	mediumorchid2	mediumorchid3
mediumorchid4	mediumpurple	mediumpurple1	mediumpurple2	mediumpurple3
mediumpurple4	mediumseagreen	mediumslateblue	mediumspringgreen	mediumturquoise
mediumvioletred	midnightblue	mintcream	mistyrose	mistyrose1
mistyrose2	mistyrose3	mistyrose4	moccasin	navy
navyblue	none	oldlace	olive	olivedrab
olivedrab1	olivedrab2	olivedrab3	olivedrab4	orange
orange1	orange2	orange3	orange4	orangered
orangered1	orangered2	orangered3	orangered4	orchid
orchid1	orchid2	orchid3	orchid4	palegoldenrod
palegreen	palegreen1	palegreen2	palegreen3	palegreen4
paleturquoise	paleturquoise1	paleturquoise2	paleturquoise3	paleturquoise4
palevioletred	palevioletred1	palevioletred2	palevioletred3	palevioletred4
papayawhip	peachpuff	peachpuff1	peachpuff2	peachpuff3
peachpuff4	peru	pink	pink1	pink2
pink3	pink4	plum	plum1	plum2
plum3	plum4	powderblue	purple	purple1
purple2	purple3	purple4	rebeccapurple	red
red1	red2	red3	red4	rosybrown
rosybrown1	rosybrown2	rosybrown3	rosybrown4	royalblue
royalblue1	royalblue2	royalblue3	royalblue4	saddlebrown
salmon	salmon1	salmon2	salmon3	salmon4
sandybrown	seagreen	seagreen1	seagreen2	seagreen3
seagreen4	seashell	seashell1	seashell2	seashell3
seashell4	sienna	sienna1	sienna2	sienna3
sienna4	silver	skyblue	skyblue1	skyblue2
skyblue3	skyblue4	slateblue	slateblue1	slateblue2
slateblue3	slateblue4	slategray	slategray1	slategray2
slategray3	slategray4	slategrey	snow	snow1
snow2	snow3	snow4	springgreen	springgreen1
springgreen2	springgreen3	springgreen4	steelblue	steelblue1
steelblue2	steelblue3	steelblue4	tan	tan1
tan2	tan3	tan4	teal	thistle
thistle1	thistle2	thistle3	thistle4	tomato
tomato1	tomato2	tomato3	tomato4	transparent
turquoise	turquoise1	turquoise2	turquoise3	turquoise4
violet	violetred	violetred1	violetred2	violetred3
violetred4	webgray	webgreen	webgrey	webmaroon
webpurple	wheat	wheat1	wheat2	wheat3
wheat4	x11gray	x11green
x11grey	x11maroon	x11purple	yellow	yellow1
yellow2	yellow3	yellow4	yellowgreen
aliceblue	aqua	aquamarine	azure
beige	bisque	black	blanchedalmond	blue
blueviolet	brown	burlywood	cadetblue	chartreuse
chocolate	coral	cornflowerblue	cornsilk	crimson
cyan	darkblue	darkcyan	darkgoldenrod	darkgray
darkgreen	darkgrey	darkkhaki	darkmagenta	darkolivegreen
darkorange	darkorchid	darkred	darksalmon	darkseagreen
darkslateblue	darkslategray	darkslategrey	darkturquoise	darkviolet
deeppink	deepskyblue	dimgray	dimgrey	dodgerblue
firebrick	forestgreen	fuchsia	gainsboro
gold	goldenrod	gray	grey
green	greenyellow	honeydew	hotpink	indianred
indigo	ivory	khaki	lavender	lavenderblush
lawngreen	lemonchiffon	lightblue	lightcoral	lightcyan
lightgoldenrodyellow	lightgray	lightgreen	lightgrey	lightpink
lightsalmon	lightseagreen	lightskyblue	lightslategray	lightslategrey
lightsteelblue	lightyellow	lime	limegreen	linen
magenta	maroon	mediumaquamarine	mediumblue	mediumorchid
mediumpurple	mediumseagreen	mediumslateblue	mediumspringgreen	mediumturquoise
mediumvioletred	midnightblue	mintcream	mistyrose	moccasin
navy	oldlace	olive	olivedrab
orange	orangered	orchid	palegoldenrod	palegreen
paleturquoise	palevioletred	papayawhip	peachpuff	peru
pink	plum	powderblue	purple	red
rosybrown	royalblue	saddlebrown	salmon	sandybrown
seagreen	seashell	sienna	silver	skyblue
slateblue	slategray	slategrey	snow	springgreen
steelblue	tan	teal	thistle	tomato
turquoise	violet	wheat
yellow	yellowgreen
'''
'''
All colors available in dot notation. I couldn't figure out how to use hex in a dot file.
'''

color_list = color_names.replace('\n\n', '').replace('\n', '\t').split('\t')
color_list = color_list[1:-1]
'''Turn the website text into a list of colors.'''

def get_new_result_folder_name():
	base_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
	list_of_directory_items = os.listdir(base_directory)
	list_of_folders = []
	for directory_item in list_of_directory_items:
		if 'Results' in directory_item:
			list_of_folders.append(directory_item)
	
	folder_numbers = [0 if len(folder.replace('Results', '')) == 0 else int(folder.replace('Results', '')) for folder in list_of_folders]

	return os.path.join(base_directory, 'Results' + str(max(folder_numbers) + 1))

if __name__ == "__main__":
	main()

	#Let the user know about a better alternative.
	if not visualization_import_success:
		print('\nTo see advanced visualization. Run this program on flip. Trust us, it will be worth it.')