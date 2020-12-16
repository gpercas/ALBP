from objects import *
from utils import *

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
	ordreTasques = [x for (y,x) in sorted(zip(al.data['successors_time'], [x+1 for x in range(al.data['N'])]), reverse=True)]

	while ordreTasques != []:
		if len(al.stations_AL) > 0:
			for task in ordreTasques:
				open_ws = True
				for ws in al.stations_AL:
					if al.check(task, ws):
						al.add_task(task, ws)
						open_ws = False
						ordreTasques.remove(task)
						break
				if open_ws and al.check_precedences(task, al.stations_AL[-1]): #No haría falta porque ninguna precedencia puede tener un tsucesiones mas pequeño que una sucesora
					al.open_WS(task)
					ordreTasques.remove(task)
					break
		
		else:
			al.open_WS(ordreTasques[0])
			ordreTasques.remove(ordreTasques[0])		

	al.NES_workers = al.substitution_workers()
	al = OL(al)
	return al

def algoritme2(raw_data, alfa):
	"""
	Algoritmo Greedy basado en Estaciones - Estático
	"""
	al = AssemblyLine(raw_data)
	llista_ind = [al.data['successors_time'][task] + alfa * al.data['numSucc'][task] for task in range(al.data['N'])]
	ordreTasques = [x for (y,x) in sorted(zip(llista_ind, [x+1 for x in range(al.data['N'])]), reverse=True)]

	while ordreTasques != []:
		if len(al.stations_AL) > 0:
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

		else:
			al.open_WS(ordreTasques[0])
			ordreTasques.remove(ordreTasques[0])

	al.NES_workers = al.substitution_workers()
	al = OL(al)
	return al


def algoritme3 (raw_data, alfa, beta, beta_open, gamma, gamma_open):
	'''
	Algoritmo Greedy basado en estaciones - Dinámico
	'''
	al = AssemblyLine(raw_data)

	to_do_tasks = [task for task in range(1, al.data['N'] + 1)]
	open_ws_cost = al.cost_to_open_ws_by_task()
	ended_tasks = []

	while to_do_tasks != []:

		llista_ind = [al.data['successors_time'][task - 1] + alfa * al.data['numSucc'][task - 1] + beta * open_ws_cost[task - 1] - gamma * al.delta_cost_AL(task) for task in to_do_tasks]
		ordreTasques = [x for (y,x) in sorted(zip(llista_ind, to_do_tasks), reverse=True)]
		if len(al.stations_AL) > 0:
			open_ws = True
			task_open_ws_candidates = list()
			for task in ordreTasques:
				if al.check(task, al.stations_AL[-1]):
					al.add_task(task, al.stations_AL[-1])
					open_ws = False
					to_do_tasks.remove(task)
					break
				elif al.check_precedences(task, al.stations_AL[-1]):
						task_open_ws_candidates.append(task)

			if open_ws:
				llista_ind_open = [al.data['successors_time'][task - 1] + alfa * al.data['numSucc'][task - 1] + beta_open * open_ws_cost[task - 1] - gamma_open * al.delta_cost_AL(task) for task in task_open_ws_candidates]
				task_open_ws = [x for (y,x) in sorted(zip(llista_ind_open, task_open_ws_candidates), reverse=True)][0]
				al.open_WS(task_open_ws)
				to_do_tasks.remove(task_open_ws)
		
		else:
			first_candidate = [task for task in ordreTasques if task in al.task_candidates([])][0]
			al.open_WS(first_candidate)
			to_do_tasks.remove(first_candidate)			


	al.NES_workers = al.substitution_workers()
	al = OL(al, verbose = True)
	return al


############# A PARTIR DE AQUI HAY QUE OPTIMIZAR/COMPROBAR #######################
def algoritmet2(raw_data, cand):
	'''
	Metaheurística GRASP basada en el algoritmo1c
	'''
	al = AssemblyLine(raw_data)
	llista_ind=[]
	for task in range(al.data['N']):
		llista_ind.append(al.data['successors_time'][task]+19 * al.data['numSucc'][task])
	llistaInd=list(sorted(llista_ind,reverse=True))
	ordreTasques=[x for (y,x) in sorted(zip(llista_ind,[x+1 for x in range(al.data['N'])]), reverse=True)]
	while ordreTasques != []:
		evalTasca=[]
		evalDur=[]
		n=0
		for i in range(len(ordreTasques)):
			if len(al.stations_AL)==0:
				if ordreTasques[i] in al.task_candidates(ended_tasks = []):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llistaInd[i])
					n+=1
			else:
				if al.check(ordreTasques[i], al.stations_AL[len(al.stations_AL)-1]):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llistaInd[i])
					n+=1
			if n==cand: break
		if n==0:
			al.open_empty_WS()
			for i in range(len(ordreTasques)):
				if al.check_precedences(ordreTasques[i], al.stations_AL[len(al.stations_AL)-1]):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llistaInd[i])
					n+=1
					if n==cand: break	
		randnum=random.random()
		randDistrib=[0]
		for i in range(len(evalTasca)):
			randDistrib.append(randDistrib[i]+(evalDur[i]/sum(evalDur)))
		for i in range(len(evalTasca)):
			if randnum > randDistrib[i] and randnum <= randDistrib[i+1]:
				task=evalTasca[i]
				break		
		if len(al.stations_AL)!=0:
				al.add_task(task, al.stations_AL[len(al.stations_AL)-1])
				llistaInd.pop(ordreTasques.index(task))
				ordreTasques.remove(task)
		else: 
			al.open_WS(task)
			llistaInd.pop(ordreTasques.index(task))
			ordreTasques.remove(task)
	al.NES_workers=al.substitution_workers()
	al = OL(al)
	return al

def algoritmet2_0(raw_data, cand, alfa = 19):
	'''
	Metaheurística GRASP basada en el algoritmo1c
	'''
	al = AssemblyLine(raw_data)

	llista_ind = [al.data['successors_time'][task] + alfa * al.data['numSucc'][task] for task in range(al.data['N'])]
	ordreTasques = [x for (y,x) in sorted(zip(llista_ind, [x+1 for x in range(al.data['N'])]), reverse=True)]

	while ordreTasques != []:
		evalTasca = list()
		evalDur = list()
		n = 0
		for i in range(len(ordreTasques)):
			if len(al.stations_AL) == 0:
				if ordreTasques[i] in al.task_candidates(ended_tasks = []):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llista_ind[i])
					n+=1
			else:
				if al.check(ordreTasques[i], al.stations_AL[len(al.stations_AL)-1]):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llista_ind[i])
					n+=1
			if n==cand: break
		if n==0:
			al.open_empty_WS()
			for i in range(len(ordreTasques)):
				if al.check_precedences(ordreTasques[i], al.stations_AL[len(al.stations_AL)-1]):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llista_ind[i])
					n+=1
					if n==cand: break	
		randnum=random.random()
		randDistrib=[0]
		for i in range(len(evalTasca)):
			randDistrib.append(randDistrib[i]+(evalDur[i]/sum(evalDur)))
		for i in range(len(evalTasca)):
			if randnum > randDistrib[i] and randnum <= randDistrib[i+1]:
				task=evalTasca[i]
				break		
		if len(al.stations_AL)!=0:
				al.add_task(task, al.stations_AL[len(al.stations_AL)-1])
				llistaInd.pop(ordreTasques.index(task))
				ordreTasques.remove(task)
		else: 
			al.open_WS(task)
			llistaInd.pop(ordreTasques.index(task))
			ordreTasques.remove(task)
	al.NES_workers=al.substitution_workers()
	al = OL(al)
	return al

def algoritme3a (raw_data, alfa, beta):
	'''
	Algoritmo Greedy basado en estaciones - Dinámico
	'''
	al = AssemblyLine(raw_data)
	tasks=[x+1 for x in range(al.data['N'])]
	eval=0
	t_major=0
	for task in tasks:
		if al.data['successors_time'][task-1] > eval:     #+ 13*data['numSucc'][task-1]> eval:
			eval = al.data['successors_time'][task-1]       #+ 13*data['numSucc'][task-1]
			t_major = task
	al.open_WS(t_major)
	tasks.remove(t_major)
	i = 0
	while tasks != []:
		llista_pos=[]
		for task in tasks:
			if al.check(task, al.stations_AL[len(al.stations_AL)-1]):
				llista_pos.append(task)

		if llista_pos == []:
			for task in tasks:
				if al.check_precedences(task, al.stations_AL[len(al.stations_AL)-1]):
					llista_pos.append(task)
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(al.data['successors_time'][task-1]-alfa*al.delta_cost_AL(task))
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			al.open_WS(ordreTasques[0])
			tasks.remove(ordreTasques[0])

		else:
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(al.data['successors_time'][task-1]-beta * al.delta_cost_AL(task))
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			al.add_task(ordreTasques[0],al.stations_AL[len(al.stations_AL)-1])
			al.NES_workers=al.substitution_workers()
			tasks.remove(ordreTasques[0])
		i+=1
	al.NES_workers=al.substitution_workers()
	al = OL(al)
	return al


def algoritme3b (raw_data, alfa):
	"""
	Algoritmo Greedy basado en estaciones - Dinámico
	"""

	al = AssemblyLine(raw_data)
	tasks = [x+1 for x in range(al.data['N'])]
	llistaOpen = al.cost_to_open_ws_by_task()
	eval = 0
	t_major = 0
	pos = al.task_candidates(ended_tasks = [])
	for task in tasks:
		if task in pos:
			if al.data['successors_time'][task-1] + 13*al.data['numSucc'][task-1]> eval:
				eval = al.data['successors_time'][task-1] + 13*al.data['numSucc'][task-1]
				t_major = task
	al.open_WS(t_major)
	tasks.remove(t_major)
	while tasks != []:
		llista_pos=[]
		for task in tasks:
			if al.check(task, al.stations_AL[len(al.stations_AL)-1]):
				llista_pos.append(task)

		if llista_pos == []:
			for task in tasks:
				if al.check_precedences(task, al.stations_AL[len(al.stations_AL)-1]):
					llista_pos.append(task)
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(al.data['successors_time'][task-1]+13*al.data['numSucc'][task-1])
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			al.open_WS(ordreTasques[0])
			tasks.remove(ordreTasques[0])

		else:
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(al.data['successors_time'][task-1]+13*al.data['numSucc'][task-1]+alfa*(llistaOpen[task-1]-al.delta_cost_AL(task)))
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			al.add_task(ordreTasques[0],al.stations_AL[len(al.stations_AL)-1])
			al.NES_workers=al.substitution_workers()
			tasks.remove(ordreTasques[0])

	al.NES_workers = al.substitution_workers()
	al = OL(al)
	return al

def algoritmet3(raw_data, cand, alfa):
	'''
	Metaheurística GRASP basada en algoritmo 3b
	'''

	al = AssemblyLine(raw_data)
	tasks = [x+1 for x in range(al.data['N'])]
	llistaOpen = al.cost_to_open_ws_by_task()
	
	llistaInd=[]
	for task in tasks:
		llistaInd.append(al.data['successors_time'][task-1]+13*al.data['numSucc'][task-1])
	ordreTasques=[x for (y,x) in sorted(zip(llistaInd,tasks),reverse=True)]
	llistaIndOr=list(sorted(llistaInd,reverse=True))

	while tasks != []:
		bet=True
		evalTasca=[]
		evalDur=[]
		if len(al.stations_AL)==0:
			n=0
			candidaPos = al.task_candidates(ended_tasks = [])
			for i in range(len(ordreTasques)):
				if ordreTasques[i] in candidaPos:
					evalTasca.append(ordreTasques[i])
					evalDur.append(llistaIndOr[i])
					n+=1
					if n==cand: break
			bet=False
		else:
			llista_pos=[]
			for t in tasks:
				if al.check(t, al.stations_AL[len(al.stations_AL)-1]):
					llista_pos.append(t)
			if len(llista_pos) != 0:
				llista_ind=[]
				for t in llista_pos:
					llista_ind.append(llistaInd[t-1]+alfa*(llistaOpen[t-1]-al.delta_cost_AL(t)))
				evalTasca=[x for (y,x) in sorted(zip(llista_ind, llista_pos),reverse=True)][0:cand]
				evalDur=list(sorted(llista_ind,reverse=True))[0:cand]
			else:
				bet=False
				for t in tasks:
					if al.check_precedences(t, al.stations_AL[len(al.stations_AL)-1]):
						llista_pos.append(t)
				llista_ind=[]
				for t in llista_pos:
					llista_ind.append(llistaInd[t-1])
				evalTasca=[x for (y,x) in sorted(zip(llista_ind, llista_pos),reverse=True)][0:cand]
				evalDur=list(sorted(llista_ind,reverse=True))[0:cand]

		randnum=random.random()
		randDistrib=[0]
		for i in range(len(evalTasca)):
			randDistrib.append(randDistrib[i]+(evalDur[i]/sum(evalDur)))
		for i in range(len(evalTasca)):
			if randnum > randDistrib[i] and randnum <= randDistrib[i+1]:
				task=evalTasca[i]
				break		
		if len(al.stations_AL) !=0 and bet:
				al.add_task(task, al.stations_AL[len(al.stations_AL)-1])
				tasks.remove(task)
		else: 
			al.open_WS(task)
			tasks.remove(task)
	al.NES_workers=al.substitution_workers()
	al = OL(al)
	return al

def OL_0(al, verbose = False):
	def seek_for_movements(al_n, task, ws):
		for ws_tgt in recombine_list(al_n.stations_AL, ws.idx - 1):
			if (ws_tgt.idx > ws.idx) and (al_n.check_backward(task, ws, ws_tgt)):
				al_n.move_task_backward(task, ws, ws_tgt)
				break
				
			elif (ws_tgt.idx < ws.idx) and (al_n.check_forward(task, ws_tgt)):
				al_n.move_task_forward(task, ws, ws_tgt)
				break

	al_0 = copy.deepcopy(al)
	i = 0
	for ws in al_0.stations_AL:
		if verbose: print(str([ws_1.tasks for ws_1 in al_0.stations_AL])+'\n'+str(ws.tasks)+str(al_0.stations_AL[i].tasks)+'\n''\n\n')
		if len(ws.tasks) <= 2:
			cost_0 = al_0.cost_AL()
			al_0.save_state()
			for task in ws.tasks[::-1]:
				seek_for_movements(al_0, task, ws)

			if (cost_0 > al_0.cost_AL()) and ws.tasks == []:
				al_0.close_WS(ws)
			else:
				al_0.load_state()
				i += 1

	al_0.NES_workers = al_0.substitution_workers(end = True)
	al.NES_workers = al.substitution_workers(end = True)

	if al_0.cost_AL() < al.cost_AL():
		return al_0
	else: 
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
			al_0.save_state()
			for task in ws.tasks[::-1]:
				seek_for_movements(al_0, task, ws)

			if (cost_0 > al_0.cost_AL()) and ws.tasks == []:
				al_0.close_WS(ws)
				idx -= 1
			else:
				al_0.load_state()
		idx += 1

	al_0.NES_workers = al_0.substitution_workers(end = True)
	al.NES_workers = al.substitution_workers(end = True)

	if al_0.cost_AL() < al.cost_AL():
		return al_0
	else: 
		return al