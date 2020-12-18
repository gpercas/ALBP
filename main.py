from objects import *
from algorithms import *
import time


def writeSol(rf, init_time):
	sol = "*".join([str(rf.cost_AL()), str(time.perf_counter() - init_time)])
	print(sol)
	return sol + "\n"


def prog(fileR, fileW, iW = False, tmax=240.0):
	print('\n')
	print(fileR)
	print('----------------------------------')
	sol = str()
	init_time = time.perf_counter()
	data = RawData(fileR)

	#Algoritme1
	r1 = algoritme1(data)
	rf = r1
	sol += writeSol(rf, init_time)

	#Algoritme2
	r2 = algoritme2(data, alfa = 0)
	if r2.cost_AL() < rf.cost_AL():
		rf = r2
		sol += writeSol(rf, init_time)
	
	#Algoritme 2 - 13
	r6 = algoritme2(data, alfa = 13)
	if r6.cost_AL() < rf.cost_AL():
		rf = r6
		sol += writeSol(rf, init_time)

	#Algoritme 2 - 19
	r11=algoritme2(data, alfa = 19)
	if r11.cost_AL() < rf.cost_AL(): 
		rf = r11
		sol += writeSol(rf, init_time)

	#Algoritme 2 - 170
	r7=algoritme2(data, alfa = 170)
	if r7.cost_AL() < rf.cost_AL():
		rf = r7
		sol += writeSol(rf, init_time)

	#Algoritme 3 - 4,65
	r5=algoritme3(data, 0, 0, 65)
	if r5.cost_AL() < rf.cost_AL():
		rf = r5
		sol += writeSol(rf, init_time)

	#Algoritme 3 - 4,65
	r8=algoritme3(data, 0, 0, 100)
	if r8.cost_AL() < rf.cost_AL():
		rf = r8
		sol += writeSol(rf, init_time)

	#Algoritme 3 - 8.3
	r9=algoritme3(data, 13, 8.3, 8.3)
	if r9.cost_AL() < rf.cost_AL():
		rf = r9
		sol += writeSol(rf, init_time)

	#Algoritme 3 - 30
	r10=algoritme3(data, 13, 30, 30)
	if r10.cost_AL() < rf.cost_AL():
		rf = r10
		sol += writeSol(rf, init_time)


	#Algoritme t2
	while (time.perf_counter() - init_time) < (tmax * 2.0 / 3.0):
		r3 = algoritmet2(data, alfa = 13)
		if r3.cost_AL() < rf.cost_AL():
			rf = r3
			sol += writeSol(rf, init_time)

	#Algoritme t3
	while (time.perf_counter() - init_time) < (tmax - 5):
		r4 = algoritmet3(data, 13, 8.3, 8.3)
		if r4.cost_AL() < rf.cost_AL():
			rf = r4
			sol += writeSol(rf, init_time)
	
	if iW:
		sol += writeSol(rf, init_time)
		writeFile(rf, fileW, sol)
	return rf


def writeFile(cadena, fileW, solutions_str):
	TC=0
	llistaEst = [len(cadena.stations_AL)]
	for ws in cadena.stations_AL:
		if ws.temps > TC:
			TC = ws.temps
		llistaEst.append(ws.operari.idx)	

	with open(fileW, 'w') as f:
		f.write(solutions_str)
		f.write(str(TC)+"\n")
		f.write("*".join([str(x) for x in llistaEst])+"\n")
		f.write(str(len(cadena.NES_workers))+"\n")
		for empleat in cadena.NES_workers:
			f.write("*".join([str(empleat[1]), str(empleat[0])])+"\n")
		for ws in cadena.stations_AL:
			l=[str(len(ws.tasks))]
			for task in ws.tasks:
				l.append(str(task))
			f.write("*".join(l)+"\n")
		for ws in cadena.stations_AL:
			l=[str(len(ws.tools))]
			for tool in list(set(ws.tools)):
				l.append(str(tool))
			f.write("*".join(l)+"\n")
		f.close()

def main():

	quest = int(input('Se quieren evaluar varios ejemplares numerados? 0 - NO  //  1 - SI: '))
	if quest == 0:
		eje = input('Nombre identificador del ejemplar (p.ej: ejemplar_prueba): ')
		sol = input('Nombre identificador de la solucion (p.ej: ejemplar_solucion): ')
		time = float(input('Tiempo de cálculo para el ejemplar (en segundos): '))
		prog(eje+'.txt',sol+'.txt', 1, time)	
	
	else:
		eje = input('Nombre identificador de los ejemplares (pred: ejemplar_prueba_): ')
		sol = input('Nombre identificador de las soluciones (pred: ejemplar_solucion_): ')

		if eje == '':
			eje = 'ejemplar_prueba_'
		if sol == '':
			sol = 'ejemplar_solucion_'

		num = int(input('Número de ejemplares (El primero debe ser el "1"): '))
		time = float(input('Tiempo de cálculo para cada ejemplar (en segundos): '))
		for n in range(1,num+1):
			prog(eje+str(n)+'.txt',sol+str(n)+'.txt', 1, time)	
	

if __name__ == "__main__":
	main()