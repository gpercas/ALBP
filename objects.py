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
		self.operari = 0
		self.tipusTasques = set()
		self.idx = i

class Worker(object):
	def __init__(self, i, cost, taskTypes):
		self.idx = i
		self.cost = cost
		self.taskTypes = taskTypes 


class AssemblyLine(object):
	# INICIALIZATION methods
	def __init__(self, raw_data):
		self.stations_AL = []
		self.data = raw_data.return_data()
		self.empleatsNES = []
		self.workers_pool, self.supervisor_worker = self.initialize_workers_pool()

	def initialize_workers_pool(self):
		worker_pool = []
		for idx in range(1, self.data['O'] + 1):
			worker = Worker(idx, self.data['workers_cost'][idx], self.data['tasks_by_worker'][idx - 1])
			worker_pool.append(worker)

		supervisor_worker = Worker(0, self.data['workers_cost'][0], [t+1 for t in range(self.data['T'])])

		return worker_pool, supervisor_worker

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


	def check_successors(self, task, ws_tgt_idx, ws_idx):
		for i in range(ws_idx - 1, ws_tgt_idx - 1):
			for asgn_task in self.stations_AL[i].tasks:
				if task in self.data['precedences'][asgn_task-1]:
					return False
		return True

	def check_exists_worker_for_tasks(self, taskTypes):
		for worker in self.workers_pool:
			if list_included(taskTypes, worker.taskTypes):
				return True
		return False

	def check_worker(self, task, ws):
		if self.data['task_type'][task-1] in ws.tipusTasques:
			return True
		else:
			needed_task_type = ws.tipusTasques.union({self.data['task_type'][task-1]})
			return self.check_exists_worker_for_tasks(needed_task_type)

	def check(self, task, ws):	
		return self.check_time(task, ws) and self.check_worker(task, ws) and self.check_precedences(task, ws)

	def cheapest_worker(self, taskTypes):
		valor = max(self.data['workers_cost'])
		ws_worker = 0
		for worker_idx in range(self.data['O']):
			if list_included(taskTypes, self.data['tasks_by_worker'][worker_idx]):
				if self.data['workers_cost'][worker_idx + 1] < valor:
					valor = self.data['workers_cost'][worker_idx + 1]
					ws_worker = worker_idx + 1
		return ws_worker
		
	def add_task(self, task, ws, first = False):
		ws.temps += self.data['durations'][task-1]
		ws.tasks.insert((1 - first) * len(ws.tasks), task) #if first is True, then inserts at first position. Else inserts at last position
		ws.tipusTasques.add(self.data['task_type'][task-1])
		ws.tools = ws.tools.union(self.data['tools'][task-1][1:])
		ws.operari = self.cheapest_worker(ws.tipusTasques)

	def remove_task(self, task, ws):
		ws.temps -= self.data['durations'][task - 1]
		ws.tasks.remove(task)
		ws.tipusTasques = set()
		ws.tools = set()
		for task in ws.tasks:
			ws.tipusTasques.add(self.data['task_type'][task - 1])
			ws.tools = ws.tools.union(self.data['tools'][task - 1][1:])
			ws.operari = self.cheapest_worker(ws.tipusTasques)

	def open_WS(self, task):
		self.stations_AL.append(WorkStation(len(self.stations_AL) + 1))
		self.add_task(task, self.stations_AL[-1])
		
	def open_empty_WS(self):
		self.stations_AL.append(WorkStation(len(self.stations_AL) + 1))

	# SUBSTITUTION WORKERS ALGORITHM methods
	def substitution_workers_alt(self, end = 0):
		sub_workers = [[1, ws.operari, self.data['tasks_by_worker'][ws.operari - 1]] for ws in stations_AL]
		for idx, sub_worker in enumerate(sub_workers):
			pass

	def substitution_workers(self, end = 0):
		"""
		Evalua per parelles, a partir de parelles comprova grups de 3 i per últim grups de 4. 
		Per als primers algoritmes es podria prescindir de cridar-la cada vegada perquè no es té en compte.
		"""
		def check_worker(tipusTasques):
			valor=max(self.data['workers_cost'][1:])
			empleat = self.cheapest_worker(tipusTasques)
			if empleat != 0:
				return True, empleat
			else:
				return False, empleat
				
		def evalCost(llistaEmpleats):
			valor=0
			for empleatSub in llistaEmpleats:
				valor+=self.data['workers_cost'][empleatSub[1]]
			return valor

		def sumaestacions(llistaEmpleats):
			valor=0
			for empleatSub in llistaEmpleats:
				valor+=empleatSub[0]
			return valor

		def indexEst(llistaSub, n):
			val=0
			for ind in range(n-1):
				val+=llistaSub[ind][0]
			return val	
		
		def evaluate_consecutive_ws(empleatsSubs, backward = 0):
			if backward:
				n = len(empleatsSubs)-1
				incr = -1
				tgt = 0
			else:
				n = 0
				incr = 1
				tgt = len(empleatsSubs) - 1
			empleatsSubs_aux = [empleatsSubs[n].copy()]
			n += incr
			while ((1 - backward) * (n <= tgt)) or (backward * (n >= tgt)): #Cambio de condición segun si es back or forw
				if check_worker(empleatsSubs_aux[len(empleatsSubs_aux) - 1][2].union(empleatsSubs[n][2]))[0] and empleatsSubs_aux[len(empleatsSubs_aux) - 1][0] < self.data['NES']:
					if self.data['workers_cost'][check_worker(empleatsSubs_aux[len(empleatsSubs_aux) - 1][2].union(empleatsSubs[n][2]))[1]] < self.data['workers_cost'][empleatsSubs_aux[len(empleatsSubs_aux) - 1][1]]+self.data['workers_cost'][empleatsSubs[n][1]]:
						empleatsSubs_aux[len(empleatsSubs_aux) - 1][0] += 1
						empleatsSubs_aux[len(empleatsSubs_aux) - 1][1] = check_worker(empleatsSubs_aux[len(empleatsSubs_aux) - 1][2].union(empleatsSubs[n][2]))[1]
						empleatsSubs_aux[len(empleatsSubs_aux) - 1][2] = empleatsSubs_aux[len(empleatsSubs_aux) - 1][2].union(empleatsSubs[n][2])
					else:
						empleatsSubs_aux.append(empleatsSubs[n].copy())
				else:
					empleatsSubs_aux.append(empleatsSubs[n].copy())
				n += incr
			return empleatsSubs_aux
		
		empleatsSubs = []
		for ws in self.stations_AL:
			empleatsSubs.append([1, ws.operari, ws.tipusTasques])

		auxIt1 = evaluate_consecutive_ws(empleatsSubs, backward = 0)
		auxIt2 = evaluate_consecutive_ws(empleatsSubs, backward = 1)

		auxIt2.reverse()
		
		val1 = evalCost(auxIt1)
		val2 = evalCost(auxIt2)
		
		if val1 <= val2: auxIt = auxIt1
		else: auxIt = auxIt2
		
		#Comparacio amb combinacions de NES
		
		n=0
		auxNew=[]
		while n < len(auxIt):
			i=0
			cont=0
			while cont < self.data['NES'] and n+i < len(auxIt):
				if cont+auxIt[n+i][0]==self.data['NES']:
					cont+=auxIt[n+i][0]
					i+=1
					break
				elif cont+auxIt[n+i][0]>self.data['NES']:
					break
				else:
					cont+=auxIt[n+i][0]
					i+=1
			valor=0
			for p in range(n,n+i):
				valor+=self.data['workers_cost'][auxIt[p][1]]
			if self.data['workers_cost'][0]<valor:
				auxNew.append([cont,0,[x+1 for x in range(self.data['T'])]])
				n+=i
			else:
				auxNew.append(auxIt[n])
				n+=1

		if end == 1:
			#OPT_Local
		
			auxVell=copy.deepcopy(auxNew)
			
			while True:
				auxVell=copy.deepcopy(auxNew)
				for n in range(1, len(auxNew)):
					if auxNew[n-1][0]==self.data['NES'] and auxNew[n-1][1]==0 and auxNew[n][0]==1:
						ind1=indexEst(auxNew, n)
						if self.data['workers_cost'][self.stations_AL[ind1].operari] < self.data['workers_cost'][self.stations_AL[ind1+self.data['NES']].operari]:
							auxNew[n-1][0]=1
							auxNew[n-1][1]=self.stations_AL[ind1].operari
							auxNew[n-1][2]=set(self.data['tasks_by_worker'][auxNew[n-1][1]-1])
							auxNew[n][0]=self.data['NES']
							auxNew[n][1]=0
							auxNew[n][2]={x+1 for x in range(self.data['T'])}
			
				for n in range(0, len(auxNew)-1):
						if auxNew[n+1][0]==self.data['NES'] and auxNew[n+1][1]==0 and auxNew[n][0]==1:
							ind1=indexEst(auxNew, n+1)
							if self.data['workers_cost'][self.stations_AL[ind1+self.data['NES']].operari] < self.data['workers_cost'][self.stations_AL[ind1].operari]:
								auxNew[n+1][0]=1
								auxNew[n+1][1]=self.stations_AL[ind1+4].operari
								auxNew[n+1][2]=set(self.data['tasks_by_worker'][auxNew[n-1][1]-1])
								auxNew[n][0]=self.data['NES']
								auxNew[n][1]=0
								auxNew[n][2]={x+1 for x in range(self.data['T'])}
				if evalCost(auxNew) >= evalCost(auxVell):
					auxNew = auxVell
					break
		
		return auxNew

	# COST CALCULATION methods	
	def cost_AL(self):
		valor=0
		for ws in self.stations_AL:
			valor += self.data['workers_cost'][ws.operari]
			valor += self.data['CET']
			for tool in ws.tools:
				valor += self.data['tools_cost'][tool-1]
		for empleat in self.empleatsNES:
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
	
	def delta_cost_AL(self, task):
		if self.check(task, self.stations_AL[len(self.stations_AL) - 1]):
			aux = copy.deepcopy(self)
			aux.add_task(task, aux.stations_AL[len(aux.stations_AL) - 1])
			aux.empleatsNES = aux.substitution_workers()
			self.empleatsNES = self.substitution_workers()
			val = aux.cost_AL() - self.cost_AL()
			del(aux)
		else:
			val = self.cost_open_ws(task)
		return val

	# MOVING ASSIGNED TASKS methods
	def close_WS(self, ws):
		for ws_aux in self.stations_AL[ws.idx:]:
			ws_aux.idx -= 1
		del self.stations_AL[ws.idx - 1]
		self.empleatsNES = self.substitution_workers()

	def move_task_forward(self, task, ws, ws_tgt):
		self.remove_task(task, ws)
		self.add_task(task, ws_tgt)
		self.empleatsNES = self.substitution_workers()

	def move_task_backward(self,task, ws, ws_tgt):
		self.remove_task(task, ws)
		self.add_task(task, ws_tgt, first = True)
		self.empleatsNES = self.substitution_workers()

	def check_backward(self, task, ws, ws_tgt):
		return self.check_time(task, ws_tgt) and self.check_worker(task, ws_tgt) and self.check_successors(task, ws_tgt_idx = ws_tgt.idx, ws_idx = ws.idx)

	def check_forward(self, task, ws_tgt):
		return self.check_time(task, ws_tgt) and self.check_worker(task, ws_tgt) and self.check_precedences(task, ws_tgt)