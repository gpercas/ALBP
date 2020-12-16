import time
import random
import copy
from utils import list_included
	
class RawData(object):
	def __init__(self, filename):

		self.filename = filename
		self.read_data()
	
	def read_data(self, filename = None):
		self.data = dict()
		with open(self.filename, 'r') as f:

			self.data['TCM'] = float(f.readline())
			self.data['N'] = int(f.readline())
			self.data['durations'] = [float(x) for x in f.readline().split('*')]
			preced_tuples = f.readline().split('*')
			self.data['NP'] = int(preced_tuples.pop(0))
			self.data['precedences'], self.data['successors'] = self.precedencies_successors(preced_tuples, self.data['N'])
			self.data['H'] = int(f.readline())
			tools = []
			for i in range(self.data['N']):
			    tool = [int(x) for x in f.readline().split('*')]
			    tools.append(tool)
			self.data['tools'] = tools	
			self.data['T'] = int(f.readline())
			self.data['task_type'] = [int(x) for x in f.readline().split('*')]
			self.data['O'] = int(f.readline())
			workers_by_task = []
			for i in range(self.data['T']):
			    worker_task = [int(x) for x in f.readline().split('*')]
			    workers_by_task.append(worker_task)
			tasks_by_worker = []
			for i in range(self.data['O']):
			    worker = []
			    for l in range(self.data['T']):
			        if i+1 in workers_by_task[l][1:]: worker.append(l+1)
			    tasks_by_worker.append(worker)
			self.data['workers_by_task'] = workers_by_task
			self.data['tasks_by_worker'] = tasks_by_worker
			self.data['NES'] = int(f.readline())
			self.data['CET'] = float(f.readline())
			self.data['workers_cost'] = [float(x) for x in f.readline().split('*')]
			self.data['tools_cost'] = [float(x) for x in f.readline().split('*')]
			self.data['successors_time'], self.data['numSucc'] = self.total_task_successors_data()
			f.close()
	
	def precedencies_successors(self, tuplist, N):
		prec_list, succ_list = [[] for i in range(N)], [[] for i in range(N)]
		for tup in tuplist:
			task_p, task_s = tup.split(',')
			prec_list[int(task_s) - 1].append(int(task_p))
			succ_list[int(task_p) - 1].append(int(task_s))
		return prec_list, succ_list

	def total_task_successors_data(self):
		"""
		Recursively looks through child tasks for each task until it finds one child task without more childs. 
		As we have the complete list of heritage for each task, we can calculate the remaining time and the number of successors.
		"""
		def total_task_successors(child_tasks):
			total_succ = set()
			for task in child_tasks:
				if self.data['successors'][task - 1] == []:
					total_succ = total_succ.union({task})
				else:
					total_succ = total_succ.union({task}.union(total_task_successors(self.data['successors'][task - 1])))
			return total_succ

		total_succ = [total_task_successors(child_tasks) for child_tasks in self.data['successors']]
		time_successors = list()
		for idx, successors in enumerate(total_succ):
			time_successors.append(sum([self.data['durations'][task - 1] for task in successors]) + self.data['durations'][idx])
		num_successors = [len(successors) for successors in total_succ]

		return time_successors, num_successors
		
	def return_data(self):
		return self.data


class WorkStation(object):
	def __init__(self, i):
		self.tasks = []
		self.temps = 0
		self.tools = set()
		self.operari = None
		self.taskTypes = set()
		self.idx = i

class Worker(object):
	def __init__(self, i, cost, taskTypes):
		self.idx = i
		self.cost = cost
		self.taskTypes = taskTypes 


class AssemblyLine(object):
	# INICIALIZATION methods
	def __init__(self, raw_data):
		self.stations_AL = list()
		self.data = raw_data.return_data()
		self.NES_workers = list()
		self.workers_pool, self.supervisor_worker, self.workers_sorted_pool = self.initialize_workers_pool()

	def initialize_workers_pool(self):
		workers_pool = []
		for idx in range(1, self.data['O'] + 1):
			worker = Worker(idx, self.data['workers_cost'][idx], self.data['tasks_by_worker'][idx - 1])
			workers_pool.append(worker)

		supervisor_worker = Worker(0, self.data['workers_cost'][0], [t+1 for t in range(self.data['T'])])

		workers_sorted_pool = [workers_pool[i] for i in [idx - 1 for _, idx in sorted([(worker.cost, worker.idx) for worker in workers_pool])]]

		return workers_pool, supervisor_worker, workers_sorted_pool

	def save_state(self):
		self.stations_AL_bkp = copy.deepcopy(self.stations_AL)
		self.NES_workers_bkp = copy.deepcopy(self.NES_workers)

	def load_state(self):
		self.stations_AL = copy.deepcopy(self.stations_AL_bkp)
		self.NES_workers = copy.deepcopy(self.NES_workers_bkp)

	# ASSIGNATION methods
	def task_candidates(self, ended_tasks):
		"""
		Evaluate task candidates to be evaluated given the rules of precedence and as a list of the current assigned tasks passed
		"""
		candidates = []
		not_ended_tasks = [i+1 for i in range(self.data['N']) if i+1 not in ended_tasks]

		for task in not_ended_tasks:
			if list_included(self.data['precedences'][task - 1], ended_tasks):
				candidates.append(task)

		return candidates

	def check_time(self, task, ws):
		return (self.data['durations'][task-1] + ws.temps) <= self.data['TCM']

	def check_precedences(self, task, ws):
		ended_tasks=[]
		for i in range(ws.idx):
			ended_tasks += self.stations_AL[i].tasks

		return task in self.task_candidates(ended_tasks)

	def check_successors(self, task, ws_idx, ws_tgt_idx):
		for i in range(ws_idx - 1, ws_tgt_idx - 1):
			n = 0
			if i == (ws_idx - 1):
				n = self.stations_AL[i].tasks.index(task)
			for check_task in self.stations_AL[i].tasks[n:]:
				if task in self.data['precedences'][check_task - 1]:
					return False
		return True

	def check_exists_worker_for_tasks(self, taskTypes):
		for worker in self.workers_pool:
			if list_included(taskTypes, worker.taskTypes):
				return True
		return False

	def check_worker(self, task, ws):
		if self.data['task_type'][task-1] in ws.taskTypes:
			return True
		else:
			needed_task_type = ws.taskTypes.union({self.data['task_type'][task-1]})
			return self.check_exists_worker_for_tasks(needed_task_type)

	def check(self, task, ws):	
		return self.check_time(task, ws) and self.check_worker(task, ws) and self.check_precedences(task, ws)

	def cheapest_worker(self, taskTypes):
		ws_worker = self.supervisor_worker
		for worker in self.workers_sorted_pool:
			if list_included(taskTypes, worker.taskTypes):
				ws_worker = worker
				break
		return ws_worker
		
	def add_task(self, task, ws, first = False):
		ws.temps += self.data['durations'][task-1]
		ws.tasks.insert((1 - first) * len(ws.tasks), task) #if first is True, then inserts at first position. Else inserts at last position
		ws.taskTypes.add(self.data['task_type'][task-1])
		ws.tools = ws.tools.union(self.data['tools'][task-1][1:])
		ws.operari = self.cheapest_worker(ws.taskTypes)

	def remove_task(self, task, ws):
		ws.temps -= self.data['durations'][task - 1]
		ws.tasks.remove(task)
		ws.taskTypes = set()
		ws.tools = set()
		for task in ws.tasks:
			ws.taskTypes.add(self.data['task_type'][task - 1])
			ws.tools = ws.tools.union(self.data['tools'][task - 1][1:])
			ws.operari = self.cheapest_worker(ws.taskTypes)

	def open_WS(self, task):
		self.stations_AL.append(WorkStation(len(self.stations_AL) + 1))
		self.add_task(task, self.stations_AL[-1])
		
	def open_empty_WS(self):
		self.stations_AL.append(WorkStation(len(self.stations_AL) + 1))

	def close_WS(self, ws):
		for ws_aux in self.stations_AL[ws.idx:]:
			ws_aux.idx -= 1
		del self.stations_AL[ws.idx - 1]
		self.NES_workers = self.substitution_workers()

	# SUBSTITUTION WORKERS ALGORITHM methods
	def substitution_workers(self, end = False):
		def step_1_group_workers(forward):
			""" Agrupación de empleados de sustitución comunes """
			sub_workers = [[1, ws.operari, ws.taskTypes] for ws in self.stations_AL]
			sub_workers = sub_workers[::(2 * forward  - 1)]
			T = 0
			for idx, sub_worker in enumerate(sub_workers):
				T += 1
				while (sub_worker[0] < self.data['NES']) and (T < len(self.stations_AL) - 1):
					needed_tasks = sub_worker[2].union(sub_workers[idx + 1][2])
					if self.check_exists_worker_for_tasks(needed_tasks):
						cheapest_worker = self.cheapest_worker(needed_tasks)
						if cheapest_worker.cost < (sub_worker[1].cost + sub_workers[idx + 1][1].cost):
							sub_worker[0] += 1
							sub_worker[1] = cheapest_worker
							sub_worker[2] = needed_tasks
							del sub_workers[idx + 1]
							T += 1
							continue
					break
			return sub_workers[::(2 * forward  - 1)]

		def step_2_group_supervisor(NES_workers):
			"""
			Mirar si sale más barato agrupar por encargados NES estaciones
			"""
			total_eval_ws = 0
			for idx, NES_worker in enumerate(NES_workers):

				count = 1
				num_ws = NES_worker[0]
				subs_worker_costs = NES_worker[1].cost
				tasks_done = NES_worker[2]

				while (idx + count) < len(NES_workers):
					if ((num_ws + NES_workers[idx + count][0]) <= self.data['NES']):
						num_ws += NES_workers[idx + count][0]
						subs_worker_costs += NES_workers[idx + count][1].cost
						tasks_done.union(NES_workers[idx + count][2])
						count += 1
					else:
						break

				if subs_worker_costs > self.supervisor_worker.cost:
					NES_workers[idx] = [num_ws, self.supervisor_worker, tasks_done]
					del NES_workers[idx + 1 : idx + count]
				
				total_eval_ws += num_ws
			return NES_workers

		def step_3_local_opt_movements(NES_workers, forward):
			NES_workers = NES_workers[::(2 * forward  - 1)]

			num_ws = len(self.stations_AL)
			eval_ws = 0
			for idx in range(len(NES_workers) - 1):
				if (NES_workers[idx][0] == 4) and (NES_workers[idx][1].idx == 0) and (NES_workers[idx + 1][0] == 1):
					eval_ws_idx = (forward * eval_ws) + ((1-forward) * (num_ws - 1 - eval_ws))
					eval_compara = (forward * 4) - ((1-forward) * 4)
					if self.stations_AL[eval_ws_idx].operari.cost < self.stations_AL[eval_ws_idx + eval_compara].operari.cost:
						NES_workers[idx + 1] = NES_workers[idx][::]
						NES_workers[idx] = [1, self.stations_AL[eval_ws_idx].operari, self.stations_AL[eval_ws_idx].taskTypes]

				eval_ws += NES_workers[idx][0]
				
			return NES_workers[::(2 * forward  - 1)]

		# Initialize subfunctions	
		NES_workers_1 = step_1_group_workers(forward = True)
		NES_workers_2 = step_1_group_workers(forward = False)

		if self.cost_NES_workers(NES_workers_1) <= self.cost_NES_workers(NES_workers_2):
			NES_workers = step_2_group_supervisor(NES_workers_1)
		else:
			NES_workers = step_2_group_supervisor(NES_workers_2)
		
		if end:
			NES_workers = step_3_local_opt_movements(step_3_local_opt_movements(NES_workers, forward = True), forward = False)

		return [[NES_worker[0], NES_worker[1].idx, NES_worker[2]] for NES_worker in NES_workers]

	# COST CALCULATION methods	
	def cost_AL(self):
		valor=0
		for ws in self.stations_AL:
			valor += self.data['workers_cost'][ws.operari.idx]
			valor += self.data['CET']
			for tool in ws.tools:
				valor += self.data['tools_cost'][tool - 1]
		for empleat in self.NES_workers:
			valor += self.data['workers_cost'][empleat[1]]
		return valor

	def cost_open_ws(self, task):
		cost = self.data['CET']
		if self.data['tools'][task-1][0] != 0:						
			for tool in self.data['tools'][task - 1][1:]:
				cost += self.data['tools_cost'][tool - 1]
		valor = max(self.data['workers_cost'])
		for treb in self.data['workers_by_task'][self.data['task_type'][task-1] - 1]:
			if self.data['workers_cost'][treb] < valor:
				valor = self.data['workers_cost'][treb]
		cost += valor
		return cost

	def cost_to_open_ws_by_task(self):
		llistaCost = []
		for task in range(1, self.data['N'] + 1):
			llistaCost.append(self.cost_open_ws(task))
		return llistaCost
	
	def delta_cost_AL_0(self, task):
		if len(self.stations_AL) > 0 and self.check(task, self.stations_AL[-1]):
			aux = copy.deepcopy(self)
			aux.add_task(task, aux.stations_AL[-1])
			aux.NES_workers = aux.substitution_workers()
			self.NES_workers = self.substitution_workers()
			val = aux.cost_AL() - self.cost_AL()
			del(aux)
		else:
			val = self.cost_open_ws(task)
		return val

	def delta_cost_AL(self, task):
		if len(self.stations_AL) > 0 and self.check(task, self.stations_AL[-1]):
			self.save_state()
			self.add_task(task, self.stations_AL[-1])
			self.NES_workers = self.substitution_workers()
			cost_change_AL = self.cost_AL()
			self.load_state()
			self.NES_workers = self.substitution_workers()
			val = cost_change_AL - self.cost_AL()

		else:
			val = self.cost_open_ws(task)
		return val


	def cost_NES_workers(self, NES_list):
		return sum([worker[1].cost for worker in NES_list])

	# MOVING ASSIGNED TASKS methods
	def move_task_forward(self, task, ws, ws_tgt):
		self.remove_task(task, ws)
		self.add_task(task, ws_tgt)
		self.NES_workers = self.substitution_workers()

	def move_task_backward(self,task, ws, ws_tgt):
		self.remove_task(task, ws)
		self.add_task(task, ws_tgt, first = True)
		self.NES_workers = self.substitution_workers()

	def check_backward(self, task, ws, ws_tgt):
		return self.check_time(task, ws_tgt) and self.check_worker(task, ws_tgt) and self.check_successors(task, ws_idx = ws.idx, ws_tgt_idx = ws_tgt.idx)

	def check_forward(self, task, ws_tgt):
		return self.check_time(task, ws_tgt) and self.check_worker(task, ws_tgt) and self.check_precedences(task, ws_tgt)