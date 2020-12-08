from objects import *

def algoritme1(raw_data):
	"""
	Algoritmo Greedy basado en Tareas - Estático
	"""
	al = AssemblyLine(raw_data)
	ordreTasques=[x for (y,x) in sorted(zip(al.data['successors_time'],[x+1 for x in range(al.data['N'])]),reverse=True)]
	while ordreTasques != []:
		i=0
		while i < len(ordreTasques):
			if len(al.stations_AL)!=0:
				comp=0
				for ws in al.stations_AL:
					if al.check(ordreTasques[i], ws):
						al.add_task(ordreTasques[i], ws)
						comp=1
						ordreTasques.pop(i)
						break
				if comp==0 and al.check_precedences(ordreTasques[i],al.stations_AL[len(al.stations_AL)-1]): #No haría falta porque ninguna precedencia puede tener un tsucesiones mas pequeño que una sucesora
					al.open_WS(ordreTasques[i])
					ordreTasques.pop(i)
					break
				else:
					i+=1
			else: 
				al.open_WS(ordreTasques[i])
				ordreTasques.pop(i)
				break
	al.empleatsNES=al.substitution_workers()
	al = OL(al)[1]
	return al

def algoritme2a(raw_data):
	"""
	Algoritmo Greedy basado en Estaciones - Estático
	"""
	al = AssemblyLine(raw_data)
	ordreTasques=[x for (y,x) in sorted(zip(al.data['successors_time'],[x+1 for x in range(al.data['N'])]),reverse=True)]
	while ordreTasques != []:
		if len(al.stations_AL) != 0:
			ind=1
			for task in ordreTasques:
				if al.check(task, al.stations_AL[len(al.stations_AL)-1]):
					al.add_task(task, al.stations_AL[len(al.stations_AL)-1])
					ind=0
					ordreTasques.remove(task)
					break
			if ind:
				for task in ordreTasques:
					if al.check_precedences(task,al.stations_AL[len(al.stations_AL)-1]):
						al.open_WS(task)
						ordreTasques.remove(task)
						break
		else:
			al.open_WS(ordreTasques[0])
			ordreTasques.pop(0)
	al.empleatsNES=al.substitution_workers()
	al = OL(al)[1]
	return al

def algoritme2b(raw_data, alfa):
	"""
	Algoritmo Greedy basado en Estaciones - Estático
	"""
	al = AssemblyLine(raw_data)
	llista_ind=[]
	for task in range(al.data['N']):
		llista_ind.append(al.data['successors_time'][task] + alfa * al.data['numSucc'][task])
	ordreTasques=[x for (y,x) in sorted(zip(llista_ind,[x+1 for x in range(al.data['N'])]),reverse=True)]
	while ordreTasques != []:
		if len(al.stations_AL) != 0:
			ind=1
			for task in ordreTasques:
				if al.check(task, al.stations_AL[len(al.stations_AL)-1]):
					al.add_task(task, al.stations_AL[len(al.stations_AL)-1])
					ind=0
					ordreTasques.remove(task)
					break
			if ind:
				for task in ordreTasques:
					if al.check_precedences(task,al.stations_AL[len(al.stations_AL)-1]):
						al.open_WS(task)
						ordreTasques.remove(task)
						break
		else:
			for task in ordreTasques:
					if task in task_candidates(al.data['precedences'],[]):
						al.open_WS(task)
						ordreTasques.remove(task)
						break
	al.empleatsNES=al.substitution_workers()
	al = OL(al)[1]
	return al				

def algoritmet2(raw_data, cand):
	'''
	Metaheurística GRASP basada en el algoritmo1c
	'''
	al = AssemblyLine(raw_data)
	llista_ind=[]
	for task in range(al.data['N']):
		llista_ind.append(al.data['successors_time'][task]+19 * al.data['numSucc'][task])
	llistaInd=list(sorted(llista_ind,reverse=True))
	ordreTasques=[x for (y,x) in sorted(zip(llista_ind,[x+1 for x in range(al.data['N'])]),reverse=True)]
	while ordreTasques != []:
		evalTasca=[]
		evalDur=[]
		n=0
		for i in range(len(ordreTasques)):
			if len(al.stations_AL)==0:
				if ordreTasques[i] in task_candidates(al.data['precedences'], []):
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
	al.empleatsNES=al.substitution_workers()
	al = OL(al)[1]
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
			al.empleatsNES=al.substitution_workers()
			tasks.remove(ordreTasques[0])
	al.empleatsNES=al.substitution_workers()
	al = OL(al)[1]
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
	pos = task_candidates(al.data['precedences'],[])
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
			al.empleatsNES=al.substitution_workers()
			tasks.remove(ordreTasques[0])
	al.empleatsNES=al.substitution_workers()
	al=OL(al)[1]
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
			candidaPos=task_candidates(al.data['precedences'],[])
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
	al.empleatsNES=al.substitution_workers()
	al = OL(al)[1]
	return al

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
	cadena.empleatsNES = cadena.substitution_workers(end = 1)
	copycad.empleatsNES = copycad.substitution_workers(end = 1)
	if copycad.cost_AL() < cadena.cost_AL():
		return cadena, copycad
	else: return cadena, cadena