from objects import *



def algoritme1(data):
	"""
	Algoritmo Greedy basado en Tareas - Estático
	"""
	cadena=AssemblyLine(data)
	ordreTasques=[x for (y,x) in sorted(zip(data['successors_time'],[x+1 for x in range(data['N'])]),reverse=True)]
	while ordreTasques != []:
		i=0
		while i < len(ordreTasques):
			if len(cadena.stations_AL)!=0:
				comp=0
				for ws in cadena.stations_AL:
					if cadena.check(ordreTasques[i], ws):
						cadena.add_task(ordreTasques[i], ws)
						comp=1
						ordreTasques.pop(i)
						break
				if comp==0 and cadena.check_precedences(ordreTasques[i],cadena.stations_AL[len(cadena.stations_AL)-1]): #No haría falta porque ninguna precedencia puede tener un tsucesiones mas pequeño que una sucesora
					cadena.open_WS(ordreTasques[i])
					ordreTasques.pop(i)
					break
				else:
					i+=1
			else: 
				cadena.open_WS(ordreTasques[i])
				ordreTasques.pop(i)
				break
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena

def algoritme2a(data):
	"""
	Algoritmo Greedy basado en Estaciones - Estático
	"""
	cadena=AssemblyLine(data)
	ordreTasques=[x for (y,x) in sorted(zip(data['successors_time'],[x+1 for x in range(data['N'])]),reverse=True)]
	while ordreTasques != []:
		if len(cadena.stations_AL) != 0:
			ind=1
			for task in ordreTasques:
				if cadena.check(task, cadena.stations_AL[len(cadena.stations_AL)-1]):
					cadena.add_task(task, cadena.stations_AL[len(cadena.stations_AL)-1])
					ind=0
					ordreTasques.remove(task)
					break
			if ind:
				for task in ordreTasques:
					if cadena.check_precedences(task,cadena.stations_AL[len(cadena.stations_AL)-1]):
						cadena.open_WS(task)
						ordreTasques.remove(task)
						break
		else:
			cadena.open_WS(ordreTasques[0])
			ordreTasques.pop(0)
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena

def algoritme2b(data, alfa):
	"""
	Algoritmo Greedy basado en Estaciones - Estático
	"""
	cadena=AssemblyLine(data)
	llista_ind=[]
	for task in range(data['N']):
		llista_ind.append(data['successors_time'][task]+alfa*data['numSucc'][task])
	ordreTasques=[x for (y,x) in sorted(zip(llista_ind,[x+1 for x in range(data['N'])]),reverse=True)]
	while ordreTasques != []:
		if len(cadena.stations_AL) != 0:
			ind=1
			for task in ordreTasques:
				if cadena.check(task, cadena.stations_AL[len(cadena.stations_AL)-1]):
					cadena.add_task(task, cadena.stations_AL[len(cadena.stations_AL)-1])
					ind=0
					ordreTasques.remove(task)
					break
			if ind:
				for task in ordreTasques:
					if cadena.check_precedences(task,cadena.stations_AL[len(cadena.stations_AL)-1]):
						cadena.open_WS(task)
						ordreTasques.remove(task)
						break
		else:
			for task in ordreTasques:
					if task in task_candidates(data['precedences'],[]):
						cadena.open_WS(task)
						ordreTasques.remove(task)
						break
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena				

def algoritmet2(data, cand):
	'''
	Metaheurística GRASP basada en el algoritmo1c
	'''
	cadena=AssemblyLine(data)
	llista_ind=[]
	for task in range(data['N']):
		llista_ind.append(data['successors_time'][task]+19*data['numSucc'][task])
	llistaInd=list(sorted(llista_ind,reverse=True))
	ordreTasques=[x for (y,x) in sorted(zip(llista_ind,[x+1 for x in range(data['N'])]),reverse=True)]
	while ordreTasques != []:
		evalTasca=[]
		evalDur=[]
		n=0
		for i in range(len(ordreTasques)):
			if len(cadena.stations_AL)==0:
				if ordreTasques[i] in task_candidates(data['precedences'], []):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llistaInd[i])
					n+=1
			else:
				if cadena.check(ordreTasques[i], cadena.stations_AL[len(cadena.stations_AL)-1]):
					evalTasca.append(ordreTasques[i])
					evalDur.append(llistaInd[i])
					n+=1
			if n==cand: break
		if n==0:
			cadena.open_empty_WS()
			for i in range(len(ordreTasques)):
				if cadena.check_precedences(ordreTasques[i], cadena.stations_AL[len(cadena.stations_AL)-1]):
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
		if len(cadena.stations_AL)!=0:
				cadena.add_task(task, cadena.stations_AL[len(cadena.stations_AL)-1])
				llistaInd.pop(ordreTasques.index(task))
				ordreTasques.remove(task)
		else: 
			cadena.open_WS(task)
			llistaInd.pop(ordreTasques.index(task))
			ordreTasques.remove(task)
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena


def algoritme3a (data, alfa, beta):
	'''
	Algoritmo Greedy basado en estaciones - Dinámico
	'''
	cadena=AssemblyLine(data)
	tasks=[x+1 for x in range(data['N'])]
	eval=0
	t_major=0
	for task in tasks:
		if data['successors_time'][task-1] > eval:     #+ 13*data['numSucc'][task-1]> eval:
			eval = data['successors_time'][task-1]       #+ 13*data['numSucc'][task-1]
			t_major = task
	cadena.open_WS(t_major)
	tasks.remove(t_major)
	while tasks != []:
		llista_pos=[]
		for task in tasks:
			if cadena.check(task, cadena.stations_AL[len(cadena.stations_AL)-1]):
				llista_pos.append(task)

		if llista_pos == []:
			for task in tasks:
				if cadena.check_precedences(task, cadena.stations_AL[len(cadena.stations_AL)-1]):
					llista_pos.append(task)
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(data['successors_time'][task-1]-alfa*cadena.delta_cost_AL(task))
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			cadena.open_WS(ordreTasques[0])
			tasks.remove(ordreTasques[0])

		else:
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(data['successors_time'][task-1]-beta*cadena.delta_cost_AL(task))
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			cadena.add_task(ordreTasques[0],cadena.stations_AL[len(cadena.stations_AL)-1])
			cadena.empleatsNES=cadena.substitution_workers()
			tasks.remove(ordreTasques[0])
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena


def algoritme3b (data, alfa):
	"""
	Algoritmo Greedy basado en estaciones - Dinámico
	"""
	def costOpen():
		llistaCost=[]
		for task in range(data['N']):
			cost=data['CET']
			if data['tools'][task] != 0:						
				for tool in data['tools'][task][1:]:
						cost+=data['tools_cost'][tool-1]
			valor=max(data['workers_cost'])
			for treb in data['workers_by_task'][data['task_type'][task]-1]:
					if data['workers_cost'][treb]<valor:
						valor=data['workers_cost'][treb]
			cost+=valor
			llistaCost.append(cost)
		return llistaCost

	cadena=AssemblyLine(data)
	tasks=[x+1 for x in range(data['N'])]
	llistaOpen=costOpen()
	eval=0
	t_major=0
	pos=task_candidates(data['precedences'],[])
	for task in tasks:
		if task in pos:
			if data['successors_time'][task-1] + 13*data['numSucc'][task-1]> eval:
				eval = data['successors_time'][task-1] + 13*data['numSucc'][task-1]
				t_major = task
	cadena.open_WS(t_major)
	tasks.remove(t_major)
	while tasks != []:
		llista_pos=[]
		for task in tasks:
			if cadena.check(task, cadena.stations_AL[len(cadena.stations_AL)-1]):
				llista_pos.append(task)

		if llista_pos == []:
			for task in tasks:
				if cadena.check_precedences(task, cadena.stations_AL[len(cadena.stations_AL)-1]):
					llista_pos.append(task)
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(data['successors_time'][task-1]+13*data['numSucc'][task-1])
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			cadena.open_WS(ordreTasques[0])
			tasks.remove(ordreTasques[0])

		else:
			llista_ind=[]
			for task in llista_pos:
				llista_ind.append(data['successors_time'][task-1]+13*data['numSucc'][task-1]+alfa*(llistaOpen[task-1]-cadena.delta_cost_AL(task)))
			ordreTasques=[x for (y,x) in sorted(zip(llista_ind, llista_pos), reverse=True)]
			cadena.add_task(ordreTasques[0],cadena.stations_AL[len(cadena.stations_AL)-1])
			cadena.empleatsNES=cadena.substitution_workers()
			tasks.remove(ordreTasques[0])
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena

def algoritmet3(data, cand, alfa):
	'''
	Metaheurística GRASP basada en algoritmo 3b
	'''
	def costOpen():
		llistaCost=[]
		for task in range(data['N']):
			cost=data['CET']
			if data['tools'][task] != 0:						
				for tool in data['tools'][task][1:]:
						cost+=data['tools_cost'][tool-1]
			valor=max(data['workers_cost'])
			for treb in data['workers_by_task'][data['task_type'][task]-1]:
					if data['workers_cost'][treb]<valor:
						valor=data['workers_cost'][treb]
			cost+=valor
			llistaCost.append(cost)
		return llistaCost

	tasks=[x+1 for x in range(data['N'])]
	llistaOpen=costOpen()	
	cadena=AssemblyLine(data)
	
	llistaInd=[]
	for task in tasks:
		llistaInd.append(data['successors_time'][task-1]+13*data['numSucc'][task-1])
	ordreTasques=[x for (y,x) in sorted(zip(llistaInd,tasks),reverse=True)]
	llistaIndOr=list(sorted(llistaInd,reverse=True))

	while tasks != []:
		bet=True
		evalTasca=[]
		evalDur=[]
		if len(cadena.stations_AL)==0:
			n=0
			candidaPos=task_candidates(data['precedences'],[])
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
				if cadena.check(t, cadena.stations_AL[len(cadena.stations_AL)-1]):
					llista_pos.append(t)
			if len(llista_pos) != 0:
				llista_ind=[]
				for t in llista_pos:
					llista_ind.append(llistaInd[t-1]+alfa*(llistaOpen[t-1]-cadena.delta_cost_AL(t)))
				evalTasca=[x for (y,x) in sorted(zip(llista_ind, llista_pos),reverse=True)][0:cand]
				evalDur=list(sorted(llista_ind,reverse=True))[0:cand]
			else:
				bet=False
				for t in tasks:
					if cadena.check_precedences(t, cadena.stations_AL[len(cadena.stations_AL)-1]):
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
		if len(cadena.stations_AL) !=0 and bet:
				cadena.add_task(task, cadena.stations_AL[len(cadena.stations_AL)-1])
				tasks.remove(task)
		else: 
			cadena.open_WS(task)
			tasks.remove(task)
	cadena.empleatsNES=cadena.substitution_workers()
	cadena=OL(cadena)[1]
	return cadena

def OL(cadena):
	copycad=copy.deepcopy(cadena)
	for ws in copycad.stations_AL:
			val_bool=True
			trob=True
			if len(ws.tasks)==1:
				for estacioDest in copycad.stations_AL[ws.index:]:
					if copycad.check_backward(ws.tasks[0], ws, estacioDest):
						copycad_ref=copy.deepcopy(copycad)
						copycad_ref.move_task_backward(ws.tasks[0], copycad_ref.stations_AL[ws.index-1], copycad_ref.stations_AL[estacioDest.index-1])
						copycad_ref.close_WS(copycad_ref.stations_AL[ws.index-1])
						if copycad_ref.cost_AL() < copycad.cost_AL():
							copycad.move_task_backward(ws.tasks[0], ws, estacioDest)
							copycad.close_WS(ws)
							trob=False
							break
				if trob:
					for estacioDest in copycad.stations_AL[0:ws.index-1]:
						if copycad.check_forward(ws.tasks[0], estacioDest):
							copycad_ref=copy.deepcopy(copycad)
							copycad_ref.move_task_forward(ws.tasks[0], copycad_ref.stations_AL[ws.index-1], copycad_ref.stations_AL[estacioDest.index-1])
							copycad_ref.close_WS(copycad_ref.stations_AL[ws.index-1])
							if copycad_ref.cost_AL() < copycad.cost_AL():
								copycad.move_task_forward(ws.tasks[0], ws, estacioDest)
								copycad.close_WS(ws)
								break
			if len(ws.tasks)==2:
				for estacioDest in copycad.stations_AL[ws.index:]:
					if copycad.check_backward(ws.tasks[1], ws, estacioDest):
						copycad_ref=copy.deepcopy(copycad)
						copycad_ref.move_task_backward(ws.tasks[1], copycad_ref.stations_AL[ws.index-1], copycad_ref.stations_AL[estacioDest.index-1])
						if copycad_ref.cost_AL() < copycad.cost_AL():
							copycad.move_task_backward(ws.tasks[1], ws, estacioDest)
							break
						else:
							for estacioDest2 in copycad.stations_AL[0:ws.index-1]:
								if copycad.check_forward(ws.tasks[0], estacioDest2):
									copycad_ref=copy.deepcopy(copycad)
									copycad_ref.move_task_backward(ws.tasks[1], copycad_ref.stations_AL[ws.index-1], copycad_ref.stations_AL[estacioDest.index-1])
									copycad_ref.move_task_forward(ws.tasks[0], copycad_ref.stations_AL[ws.index-1], copycad_ref.stations_AL[estacioDest2.index-1])
									copycad_ref.close_WS(ws)
									if copycad_ref.cost_AL() < copycad.cost_AL():
										copycad.move_task_backward(ws.tasks[1], ws, estacioDest)
										copycad.move_task_forward(ws.tasks[0], ws, estacioDest2)
										copycad.close_WS(ws)
										val_bool=False
										break
							if val_bool==False: break
				if val_bool:
					for estacioDest in copycad.stations_AL[0:ws.index-1]:
						if copycad.check_forward(ws.tasks[0], estacioDest):
							copycad_ref=copy.deepcopy(copycad)
							copycad_ref.move_task_forward(ws.tasks[0], copycad_ref.stations_AL[ws.index-1], copycad_ref.stations_AL[estacioDest.index-1])
							if copycad_ref.cost_AL() < copycad.cost_AL():
								copycad.move_task_forward(ws.tasks[0], ws, estacioDest)
								break
					if len(ws.tasks)==0:
						copycad.close_WS(ws)
	cadena.empleatsNES=cadena.substitution_workers(end = 1)
	copycad.empleatsNES=copycad.substitution_workers(end = 1)
	if copycad.cost_AL() < cadena.cost_AL():
		return cadena, copycad
	else: return cadena, cadena