from objects import *
from utils import *
import gc
import random
class Algorithm(object):
	def __init__(self, assembly_line, algo_type = 'Greedy', station_based = True):
		self.al = AssemblyLine

	def run_greedy(self):
		#ASIGNA_INI
		al.open_WS(ordreTasques[0])
		del ordreTasques[0]

		while ordreTasques != []:
		
			#STATION BASED ALGORITHM
			if self.station_based:
				open_ws = True
				task_open_ws = 0

				for task in ordreTasques:
					if al.check(task, al.stations_AL[-1]):
						al.add_task(task, al.stations_AL[-1])
						open_ws = False
						ordreTasques.remove(task)
						break
					elif (task_open_ws == 0) and al.check_precedences(task, al.stations_AL[-1]):
						task_open_ws = task
				if open_ws:
					al.open_WS(task_open_ws)
					ordreTasques.remove(task_open_ws)
					break
		
			#TASK BASED ALGORITHM
			else:
				for task in ordreTasques:
					open_ws = True
					for ws in al.stations_AL:
						if al.check(task, ws):
							al.add_task(task, ws)
							open_ws = False
							ordreTasques.remove(task)
							break
					if open_ws and al.check_precedences(task, al.stations_AL[-1]):
						al.open_WS(task)
						ordreTasques.remove(task)
						break

		al.NES_workers = al.substitution_workers()
		al = OL(al)
		return al			


def algoritme1(raw_data):
	"""
	Algoritmo Greedy basado en Tareas - Estático
	"""
	al = AssemblyLine(raw_data)
	sorted_tasks = [x for (y,x) in sorted(zip(al.data['successors_time'], [x+1 for x in range(al.data['N'])]), reverse=True)]

	while sorted_tasks != []:
		if len(al.stations_AL) > 0:
			for task in sorted_tasks:
				open_ws = True
				for ws in al.stations_AL:
					if al.check(task, ws):
						al.add_task(task, ws)
						open_ws = False
						sorted_tasks.remove(task)
						break
				if open_ws and al.check_precedences(task, al.stations_AL[-1]): #No haría falta porque ninguna precedencia puede tener un tsucesiones mas pequeño que una sucesora
					al.open_WS(task)
					sorted_tasks.remove(task)
					break
		
		else:
			al.open_WS(sorted_tasks[0])
			sorted_tasks.remove(sorted_tasks[0])		

	al.NES_workers = al.substitution_workers()
	al = OL(al)
	return al

def algoritme2(raw_data, alfa):
	"""
	Algoritmo Greedy basado en Estaciones - Estático
	"""
	al = AssemblyLine(raw_data)
	indicator_list = [al.data['successors_time'][task] + alfa * al.data['numSucc'][task] for task in range(al.data['N'])]
	sorted_tasks = [x for (y,x) in sorted(zip(indicator_list, [x+1 for x in range(al.data['N'])]), reverse=True)]

	while sorted_tasks != []:
		if len(al.stations_AL) > 0:
			open_ws = True
			task_open_ws = 0
			for task in sorted_tasks:
				if al.check(task, al.stations_AL[-1]):
					al.add_task(task, al.stations_AL[-1])
					open_ws = False
					sorted_tasks.remove(task)
					break
				elif (task_open_ws == 0) and al.check_precedences(task, al.stations_AL[-1]):
					task_open_ws = task
			if open_ws:
				al.open_WS(task_open_ws)
				sorted_tasks.remove(task_open_ws)

		else:
			al.open_WS(sorted_tasks[0])
			sorted_tasks.remove(sorted_tasks[0])

	al.NES_workers = al.substitution_workers()
	al = OL(al)
	return al


def algoritme3 (raw_data, alfa, beta, gamma):
	'''
	Algoritmo Greedy basado en estaciones - Dinámico
	'''
	al = AssemblyLine(raw_data)

	to_do_tasks = [task for task in range(1, al.data['N'] + 1)]
	fixed_ind = [al.data['successors_time'][task - 1] + alfa * al.data['numSucc'][task - 1] for task in to_do_tasks]
	open_ws_cost = al.cost_to_open_ws_by_task()
	ended_tasks = []

	while to_do_tasks != []:

		indicator_list = [fixed_ind[task - 1] + beta * open_ws_cost[task - 1] - gamma * al.delta_cost_AL(task) for task in to_do_tasks]
		sorted_tasks = [x for (y,x) in sorted(zip(indicator_list, to_do_tasks), reverse=True)]
		if len(al.stations_AL) > 0:
			open_ws = True
			task_open_ws_candidates = list()
			for task in sorted_tasks:
				if al.check(task, al.stations_AL[-1]):
					al.add_task(task, al.stations_AL[-1])
					open_ws = False
					to_do_tasks.remove(task)
					break
				elif al.check_precedences(task, al.stations_AL[-1]):
						task_open_ws_candidates.append(task)

			if open_ws:
				indicator_list_open = [fixed_ind[task - 1] for task in task_open_ws_candidates] #+ beta_open * open_ws_cost[task - 1] - gamma_open * al.delta_cost_AL(task) == 0
				task_open_ws = [x for (y,x) in sorted(zip(indicator_list_open, task_open_ws_candidates), reverse=True)][0]
				al.open_WS(task_open_ws)
				to_do_tasks.remove(task_open_ws)
		
		else:
			first_candidate = [task for task in sorted_tasks if task in al.task_candidates([])][0]
			al.open_WS(first_candidate)
			to_do_tasks.remove(first_candidate)			


	al.NES_workers = al.substitution_workers()
	al = OL(al, verbose = True)
	return al


def algoritmet2(raw_data, alfa = 2, cand_ = 3):
	"""
	Algoritmo Greedy Metaheurística basado en Estaciones - Estático
	"""
	al = AssemblyLine(raw_data)
	indicator_list = [al.data['successors_time'][task] + alfa * al.data['numSucc'][task] for task in range(al.data['N'])]
	sorted_tasks = [x for (y,x) in sorted(zip(indicator_list, [x+1 for x in range(al.data['N'])]), reverse=True)]

	while sorted_tasks != []:
		if len(al.stations_AL) > 0:
			task_candidates = [task for task in sorted_tasks if al.check(task, al.stations_AL[-1])][ : cand_]
			if len(task_candidates) > 0:
				task = random.choices(task_candidates, weights = [indicator_list[task - 1] for task in task_candidates], k = 1)[0]
				al.add_task(task, al.stations_AL[-1])
				sorted_tasks.remove(task)
			else:
				task_candidates_op = [task for task in sorted_tasks if al.check_precedences(task, al.stations_AL[-1])][ : cand_]
				task = random.choices(task_candidates_op, weights = [indicator_list[task - 1] for task in task_candidates_op], k = 1)[0]
				al.open_WS(task)
				sorted_tasks.remove(task)

		else:
			task_candidates_op = [task for task in sorted_tasks if task in al.task_candidates([])][ : cand_]
			task = random.choices(task_candidates_op, weights = [indicator_list[task - 1] for task in task_candidates_op], k = 1)[0]
			al.open_WS(task)
			sorted_tasks.remove(task)

	al.NES_workers = al.substitution_workers()
	al = OL(al)
	return al

def algoritmet3 (raw_data, alfa, beta, gamma, cand_ = 3):
	'''
	Algoritmo Greedy Metaheurística basado en estaciones - Dinámico
	'''
	al = AssemblyLine(raw_data)

	to_do_tasks = [task for task in range(1, al.data['N'] + 1)]
	fixed_ind = [al.data['successors_time'][task - 1] + alfa * al.data['numSucc'][task - 1] for task in to_do_tasks]
	ordered_task_open_ws = [x for (y,x) in sorted(zip(fixed_ind, to_do_tasks), reverse=True)]
	open_ws_cost = al.cost_to_open_ws_by_task()
	ended_tasks = []

	while to_do_tasks != []:

		if len(al.stations_AL) > 0:
			task_candidates = [task for task in to_do_tasks if al.check(task, al.stations_AL[-1])][ : cand_]
			if len(task_candidates) > 0:
					indicator_list = [fixed_ind[task - 1] + beta * open_ws_cost[task - 1] - gamma * al.delta_cost_AL(task) for task in task_candidates]
					indicator_list = [y for (y,x) in sorted(zip(indicator_list, task_candidates), reverse=True)][:cand_]
					ordreTasques = [x for (y,x) in sorted(zip(indicator_list, task_candidates), reverse=True)][:cand_]
					task = random.choices(ordreTasques, weights = indicator_list, k = 1)[0]
					al.add_task(task, al.stations_AL[-1])
					to_do_tasks.remove(task)
			else:
				task_candidates_open = [task for task in ordered_task_open_ws if (task in to_do_tasks) and al.check_precedences(task, al.stations_AL[-1])][: cand_]
				task_open_ws = random.choices(task_candidates_open, weights = [fixed_ind[task - 1] for task in task_candidates_open], k = 1)[0]
				al.open_WS(task_open_ws)
				to_do_tasks.remove(task_open_ws)
		
		else:
			task_candidates_open = [task for task in ordered_task_open_ws if (task in to_do_tasks) and task in al.task_candidates([])][: cand_]
			first_candidate = random.choices(task_candidates_open, weights = [fixed_ind[task - 1] for task in task_candidates_open], k = 1)[0]
			al.open_WS(first_candidate)
			to_do_tasks.remove(first_candidate)			


	al.NES_workers = al.substitution_workers()
	al = OL(al, verbose = True)
	return al


def OL(al, verbose = False):
	def seek_for_movements(al_n, task, ws):
		for ws_tgt in recombine_list(al_n.stations_AL, ws.idx - 1):
			if (ws_tgt.idx > ws.idx) and (al_n.check_backward(task, ws, ws_tgt)):
				al_n.move_task_backward(task, ws, ws_tgt)
				break
				
			elif (ws_tgt.idx < ws.idx) and (al_n.check_forward(task, ws_tgt)):
				al_n.move_task_forward(task, ws, ws_tgt)
				break

	al_0 = copy.deepcopy(al)
	idx = 0
	while idx < len(al_0.stations_AL):
		ws = al_0.stations_AL[idx]
		if len(ws.tasks) <= 2:
			cost_0 = al_0.cost_AL()
			state_orig = al_0.save_state()
			for task in ws.tasks[::-1]:
				seek_for_movements(al_0, task, ws)

			if (cost_0 > al_0.cost_AL()) and ws.tasks == []:
				al_0.close_WS(ws)
				idx -= 1
			else:
				al_0.load_state(state_orig)
		idx += 1

	al_0.NES_workers = al_0.substitution_workers(end = True)
	al.NES_workers = al.substitution_workers(end = True)

	if al_0.cost_AL() < al.cost_AL():
		return al_0
	else: 
		return al