import time
import random
import copy

def list_intersec(list_1, list_2):
	"""
	Evaluate if all the elements of list_1 are inside list_2.
	Returns True if positive

	>>> list_intersec([1,2,3], [1,2,3,4,5])
		True
	>>> list_intersec([], [1,2,3,4,5])
		True
	>>> list_intersec([66,1,2], [1,2,3,4,5])
		False
	"""

	set_A, set_B = set(list_1), set(list_2)
	return len(set_A.intersection(set_B))  ==  len(set_A)
	
def task_candidates(precedences, ended_tasks):
	"""
	Evaluate task candidates to be evaluated given the rules of precedence and as list of the current assigned tasks passed
	"""
	candidates = []
	not_ended_tasks = [i+1 for i in range(len(precedences)) if i+1 not in ended_tasks]

	for task in not_ended_tasks:
		if list_intersec(precedences[task - 1], ended_tasks):
			candidates.append(task)

	return candidates
	
class RawData(object):
	def __init__(self, filename):

		self.filename = filename
		self.data = self.read_data()
	
	def read_data(self):
		data = dict()
		with open(self.filename, 'r') as f:

			data['TCM'] = float(f.readline())
			data['N'] = int(f.readline())
			data['durations'] = [float(x) for x in f.readline().split('*')]
			preced = f.readline().split('*')
			data['NP'] = int(preced.pop(0))
			data['precedences'] = self.precedentFunc(preced,data['N'])
			data['successors'] = self.successionsFunc(preced,data['N'])
			data['H'] = int(f.readline())
			tools=[]
			for i in range(data['N']):
			    tool = [int(x) for x in f.readline().split('*')]
			    tools.append(tool)
			data['tools'] = tools	
			data['T'] = int(f.readline())
			data['task_type'] = [int(x) for x in f.readline().split('*')]
			data['O'] = int(f.readline())
			workers_by_task = []
			for i in range(data['T']):
			    worker_task = [int(x) for x in f.readline().split('*')]
			    workers_by_task.append(worker_task)
			tasks_by_worker = []
			for i in range(data['O']):
			    worker = []
			    for l in range(data['T']):
			        if i+1 in workers_by_task[l][1:]: worker.append(l+1)
			    tasks_by_worker.append(worker)
			data['workers_by_task'] = workers_by_task
			data['tasks_by_worker'] = tasks_by_worker
			data['NES'] = int(f.readline())
			data['CET'] = float(f.readline())
			data['workers_cost'] = [float(x) for x in f.readline().split('*')]
			data['tools_cost'] = [float(x) for x in f.readline().split('*')]
			data['successors_time'], data['numSucc']=self.llistaTR(data['successors'], data['durations'], data['N'])
			f.close()

		return data
	
	def precedentFunc(self, tuplist, N):
		llista_prec = []
		for i in range(N):
			llista_prec.append([])
		for tup in tuplist:
			tup=tup.split(',')
			llista_prec[int(tup[1])-1].append(int(tup[0]))
		return llista_prec

	def successionsFunc(self, tuplist, N):
		llista_succ=[]
		for i in range(N):
			llista_succ.append([])
		for tup in tuplist:
			tup=tup.split(',')
			llista_succ[int(tup[0])-1].append(int(tup[1]))
		return llista_succ

	def llistaTR(self, llistaSucc, durades, N):
		succAcum=[]
		def auxTR(ind):
			succInd=[]
			if llistaSucc[ind]==[]:
				return succInd
			else:
				for l in llistaSucc[ind]:
					succInd=succInd+[l]+auxTR(l-1)
			return list(set(succInd))

		for i in range(N):
			succAcum.append(auxTR(i))
		llistaTA=[]
		numsucc=[]
		for n in range(N):
			valor=durades[n]
			for i in succAcum[n]:
				valor=valor+durades[i-1]
			llistaTA.append(valor)
			numsucc.append(len(succAcum[n]))
		return llistaTA, numsucc
		
	def return_data(self):
		return self.data


class WorkStation(object):
	def __init__(self, i):
		self.tasks = []
		self.temps = 0
		self.tools = set()
		self.operari = 0
		self.tipusTasques = set()
		self.index = i

class AssemblyLine(object):
	def __init__(self, raw_data):
		self.stations_AL = []
		self.data = raw_data.return_data()
		self.empleatsNES = []

	def check_time(self, task, ws):
		return (self.data['durations'][task-1] + ws.temps) <= self.data['TCM']

	def check_precedences(self, task, ws):
		ended_tasks=[]
		for i in range(ws.index):
			ended_tasks+=self.stations_AL[i].tasks

		return task in task_candidates(self.data['precedences'], ended_tasks)


	def check_successors(self, task, ws_tgt_idx, ws_idx):
		for i in range(ws_idx - 1, ws_tgt_idx - 1):
			for asgn_task in self.stations_AL[i].tasks:
				if task in self.data['precedences'][asgn_task-1]:
					return False
		return True

	def check_worker(self, task, ws):
			if self.data['task_type'][task-1] in ws.tipusTasques:
				return True
			else:
				for treb in self.data['tasks_by_worker']:
					eval=1
					for tascaEval in ws.tipusTasques.union({self.data['task_type'][task-1]}):
						if tascaEval not in treb: eval=0
					if eval == 1:
						return True
				return False

	def check(self, task, ws):	
		return self.check_time(task, ws) and self.check_worker(task, ws) and self.check_precedences(task, ws)
		
	def add_task(self, task, ws):
		ws.temps += self.data['durations'][task-1]
		ws.tasks.append(task)
		ws.tipusTasques.add(self.data['task_type'][task-1])
		ws.tools = ws.tools.union(self.data['tools'][task-1][1:])
		valor = max(self.data['workers_cost'])
		for treb in range(self.data['O']):
			if list_intersec(ws.tipusTasques, self.data['tasks_by_worker'][treb]):
				if self.data['workers_cost'][treb+1] < valor:
					valor = self.data['workers_cost'][treb+1]
					ws.operari = treb+1

			
	def substitution_workers(self, end = 0):
		"""
		Evalua per parelles, a partir de parelles comprova grups de 3 i per últim grups de 4. 
		Per als primers algoritmes es podria prescindir de cridar-la cada vegada perquè no es té en compte.
		"""
		def check_worker(tipusTasques):
			valor=max(self.data['workers_cost'][1:])
			empleat=0
			for treb in range(self.data['O']):
				if list_intersec(tipusTasques, self.data['tasks_by_worker'][treb]):
					if self.data['workers_cost'][treb+1] < valor:
						valor=self.data['workers_cost'][treb+1]
						empleat=treb+1
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



	def open_WS(self, task):
		self.stations_AL.append(WorkStation(len(self.stations_AL)+1))
		self.add_task(task, self.stations_AL[len(self.stations_AL)-1])
		
	def open_empty_WS(self):
		self.stations_AL.append(WorkStation(len(self.stations_AL)+1))
		
	def cost_AL(self):
		valor=0
		for ws in self.stations_AL:
			valor+=self.data['workers_cost'][ws.operari]
			valor+=self.data['CET']
			for tool in ws.tools:
				valor+=self.data['tools_cost'][tool-1]
		for empleat in self.empleatsNES:
			valor+=self.data['workers_cost'][empleat[1]]
		return valor

	def cost_open_ws(self, task):
		cost=self.data['CET']
		if self.data['tools'][task-1][0] != 0:						
			for tool in self.data['tools'][task-1][1:]:
				cost+=self.data['tools_cost'][tool-1]
		valor=max(self.data['workers_cost'])
		for treb in self.data['workers_by_task'][self.data['task_type'][task-1]-1]:
			if self.data['workers_cost'][treb] < valor:
				valor = self.data['workers_cost'][treb]
		cost+=valor
		return cost

	def cost_to_open_ws_by_task(self):
		llistaCost=[]
		for task in range(1, self.data['N'] + 1):
			llistaCost.append(self.cost_open_ws(task))
		return llistaCost
	
	def delta_cost_AL(self, task):
		if self.check(task, self.stations_AL[len(self.stations_AL)-1]):
			aux = copy.deepcopy(self)
			aux.add_task(task, aux.stations_AL[len(aux.stations_AL)-1])
			aux.empleatsNES = aux.substitution_workers()
			self.empleatsNES = self.substitution_workers()
			val = aux.cost_AL() - self.cost_AL()
			del(aux)
		else:
			val = self.cost_open_ws(task)
		return val

	def remove_task(self, task, ws):
		ws.temps-=self.data['durations'][task-1]
		ws.tasks.remove(task)
		ws.tipusTasques=set()
		ws.tools=set()
		for task in ws.tasks:
			ws.tipusTasques.add(self.data['task_type'][task-1])
			ws.tools = ws.tools.union(self.data['tools'][task-1][1:])
			valor=max(self.data['workers_cost'])
			for treb in range(self.data['O']):
				if list_intersec(ws.tipusTasques, self.data['tasks_by_worker'][treb]):
					if self.data['workers_cost'][treb+1]<valor:
						valor=self.data['workers_cost'][treb+1]
						ws.operari=treb+1

	def close_WS(self, ws):
		for ws_aux in self.stations_AL[ws.index:]:
			ws_aux.index-=1
		del self.stations_AL[ws.index-1]
		self.empleatsNES=self.substitution_workers()

	def move_task_forward(self, task, ws, ws_tgt):
		self.remove_task(task, ws)
		self.add_task(task, ws_tgt)
		self.empleatsNES=self.substitution_workers()

	def move_task_backward(self,task, ws, ws_tgt):
		self.remove_task(task, ws)
		ws_tgt.temps += self.data['durations'][task - 1] 									
		ws_tgt.tasks.insert(0, task) 
		ws_tgt.tipusTasques.add(self.data['task_type'][task - 1])
		ws_tgt.tools = ws_tgt.tools.union(self.data['tools'][task - 1][1:])
		valor = max(self.data['workers_cost'])
		for treb in range(self.data['O']):
			if list_intersec(ws_tgt.tipusTasques, self.data['tasks_by_worker'][treb]):
				if self.data['workers_cost'][treb + 1]<valor:
					valor = self.data['workers_cost'][treb + 1]
					ws_tgt.operari = treb + 1
		self.empleatsNES=self.substitution_workers()

	def check_backward(self, task, ws, ws_tgt):
		return self.check_time(task, ws_tgt) and self.check_worker(task, ws_tgt) and self.check_successors(task, ws_tgt_idx=ws_tgt.index, ws_idx=ws.index)

	def check_forward(self, task, ws_tgt):
		return self.check_time(task, ws_tgt) and self.check_worker(task, ws_tgt) and self.check_precedences(task, ws_tgt)