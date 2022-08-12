import numpy as np
import matplotlib.pyplot as plt
import sys
import random
from runAstra_pareto import runAstraAperture, runAstra
from datetime import datetime
import multiprocessing as mp
from multiprocessing import cpu_count
import time
from scipy.optimize import minimize


def wrapper_function_aperture(args):
    arg0,arg1,arg2,arg3,arg4,solenoid_strength,arg6,arg7,arg8,arg9,arg10,arg11,arg12,solenoid_bounds=args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11],args[12],args[13]
    sol = minimize(runAstraAperture,solenoid_strength,args=(arg0,arg1,arg2,arg3,arg4,arg6,arg7,arg8,arg9,arg10,arg11,arg12),method = 'Nelder-Mead',bounds=[solenoid_bounds],options ={'xtol':0.0005})
    print(sol.fun)
    if (sol.fun>=1): #Newly added, need to check this properly
        return 0.0
    return sol.x[0]

def wrapper_function(args):
    return runAstra(*args)

class Population:

    ####### BOUNDS FOR VARIABLES 
    def __init__(self):#,initial_population_size,max_grad_gun):
        #Bounds for: q_bunch [nC], rms_time [ns], rms_laser [mm], phase_gun, amplitude_gun, amplitude_solenoid [T], phase_b1, amplitude_b1, phase_b2, amplitude_b2, phase_b3, amplitude_b3
        #self.population_size = initial_population_size
        #self.max_grad_gun = max_grad_gun
        self.bounds = [(0.5e-3,5.0e-3),(0.5e-3,8.5e-3),(0.1,1.5),(-30.0,30.0),(16.0,25.0),(0.055,0.09),(-180.0,180.0),(0.0,10.0),(-180.0,180.0),(0.0,10.0),(-180.0,180.0),(0.0,10.0)]
        self.popX = np.array([])
        self.population = np.array([])
        self.population_size = 0

    def population_length(self):
        return len(self.population)

    ####### RANDOM INITIALIZATION OF VARIABLES 
    def random_initialize(self,initial_population_size,max_grad_gun):
        self.population_size = initial_population_size
        self.max_grad_gun = max_grad_gun
        random.seed(datetime.now())
        self.popX = np.asarray([(random.random()*(self.bounds[0][1]-self.bounds[0][0])+self.bounds[0][0], random.random()*(self.bounds[1][1]-self.bounds[1][0])+self.bounds[1][0],
                random.random()*(self.bounds[2][1]-self.bounds[2][0])+self.bounds[2][0], random.random()*(self.bounds[3][1]-self.bounds[3][0])+self.bounds[3][0],
	        self.max_grad_gun,random.random()*(self.bounds[5][1]-self.bounds[5][0])+self.bounds[5][0],
	        random.random()*(self.bounds[6][1]-self.bounds[6][0])+self.bounds[6][0], random.random()*(self.bounds[7][1]-self.bounds[7][0])+self.bounds[7][0],
	        random.random()*(self.bounds[8][1]-self.bounds[8][0])+self.bounds[8][0], random.random()*(self.bounds[9][1]-self.bounds[9][0])+self.bounds[9][0],
	        random.random()*(self.bounds[10][1]-self.bounds[10][0])+self.bounds[10][0], random.random()*(self.bounds[11][1]-self.bounds[11][0])+self.bounds[11][0],
	        i) for i in range(self.population_size)])
        return self.popX


    def initialize_with_variables(self,variables_array):
        self.population_size = len(variables_array)
        self.max_grad_gun = variables_array[0][4]
        self.popX = variables_array
        return self.popX



    def solenoid_optimization(self,candidates):
        np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) #Ignore the deprecation warning for creating a list of lists with tuples inside (the bounds for sol.
        #For each of the initial parameter sets optimize gun solenoid fora certain charge behind aperture (50fC in this case)
        extended_candidates = []
        for i in range(len(candidates)):
            candidate = candidates[i].tolist()
            candidate.append(self.bounds[5])
            extended_candidates.append(candidate)
        pool = mp.Pool(cpu_count())
        self.result_solenoid = pool.map(wrapper_function_aperture,extended_candidates) #Returns solenoid strength to achieve the desired charge
        pool.close()
        #Change solenoid strength value for calculated value and detele the bounds from the carrier
        for i in range(len(extended_candidates)):
            extended_candidates[i][5] = self.result_solenoid[i]
            del extended_candidates[i][-1]
        self.popX = np.array([])
        self.popX = np.asarray(extended_candidates)
        return self.popX



    def objective_evaluation(self,candidates):
        pool = mp.Pool(cpu_count())
        self.popY = np.asarray(pool.map(wrapper_function, candidates)) #Returns bunch length and time of flight jitter corresponding to each population member in indexes [0] and [1], other parameters (bunch total energy in eV, ) 
        ##ToF_class = ToF_Jitter('Results_inverted.txt')
        ##jitter = ToF_class.Jitter_calculator(args[3], args[4], args[6], args[7], args[8], args[9], args[10], args[11])
        pool.close()
        self.population = np.hstack((candidates,self.popY))
        self.population_size = len(self.population)
        return self.population


    def add_members(self,members):
        initial_length = len(self.population)
        if (initial_length!=0) & (len(members)!=0): 
            if (len(self.population[0])==len(members[0])):
                self.population = np.vstack((self.population, members))
                final_length = len(self.population)
                for i in range(initial_length,final_length): #If we have effectively added members to the population, change the member numbers of thew added ones
                    self.population[i][12] = i
        elif (initial_length==0) & (len(members)!=0):
            if len(members[0])==19:
                self.population = members
                final_length = len(self.population)
                for i in range(initial_length,final_length): #If we have effectively added members to the population, change the member numbers of thew added ones
                    self.population[i][12] = i
        self.population_size = len(self.population)
        return self.population



    def add_variables(self,variables_array):
        initial_length = len(self.popX)
        if (initial_length!=0) & (len(variables_array)!=0): 
            if (len(self.popX[0])==len(variables_array[0])):
                self.popX = np.vstack((self.popX, variables_array))
                final_length = len(self.popX)
                for i in range(initial_length,final_length): #If we have effectively added members to the population, change the member numbers of thew added ones
                    self.popX[i][12] = i
        elif (initial_length==0) & (len(variables_array)!=0):
            if len(variables_array[0])==13:
                self.popX = variables_array
                final_length = len(self.popX)
                for i in range(initial_length,final_length): #If we have effectively added members to the population, change the member numbers of thew added ones
                    self.popX[i][12] = i
        return self.popX



    def check_limits(self,variables):
        cnt = 0
        for i in range(len(variables)-1):
            if (self.bounds[i][0]<= variables[i]) & (self.bounds[i][1]>=variables[i]):
                cnt += 1
        if cnt==(len(variables)-1):
            return True
        else:
            return False


    def clean_population(self):
        population_tmp = []
        rejected = 0
        for i in range(len(self.population)-1,-1,-1):
            if self.population[i][-1]==False:
                #self.population = np.delete(self.population,i)
                continue
            elif self.population[i][5]==0.0:
                continue
            elif self.population[i][17]>=-50.0:
                rejected += 1
                continue
                #self.population = np.delete(self.population,i)
            population_tmp.append(list(self.population[i]))
        self.population = np.array([])
        self.population = np.asarray(population_tmp)
        self.population_size = len(self.population)
        print(rejected)
        return self.population


    def cut_population(self,number):
        population_tmp = []
        for i in range(number):
            population_tmp.append(list(self.population[i]))
        self.population = np.array([])
        self.population = np.asarray(population_tmp)
        self.population_size = len(self.population)
        return self.population


    def calculate_strength(self):
        self.strength = []
        number = len(self.population) 
        for i in range(number):
            strength = 0
            bunch_length = self.population[i][13]
            ToF_jitter = self.population[i][14]
            for j in range(number):
                if i==j:
                    continue
                else:
                    if (bunch_length==self.population[j][13]) & (ToF_jitter==self.population[j][14]): #Both solutions give equal point
                        continue
                    elif (bunch_length<=self.population[j][13]) & (ToF_jitter<=self.population[j][14]): #j is dominated by i
                        strength += 1
            self.strength.append(strength)
        self.strength = np.asarray(self.strength)
        return self.strength



    def calculate_raw_fitness(self):
        self.strength = self.calculate_strength()
        self.raw_fitness = []
        number = len(self.population) 
        for i in range(number):
            raw_fitness = 0
            bunch_length = self.population[i][13]
            ToF_jitter = self.population[i][14]
            for j in range(number):
                if i==j:
                    continue
                else:
                    if (bunch_length==self.population[j][13]) & (ToF_jitter==self.population[j][14]): #Both solutions give equal point
                        continue
                    elif (bunch_length>=self.population[j][13]) & (ToF_jitter>=self.population[j][14]):
                        raw_fitness += self.strength[j]
            self.raw_fitness.append(raw_fitness)
        self.raw_fitness = np.asarray(self.raw_fitness)
        return self.raw_fitness



    def calculate_density(self):
        self.density = []
        number = self.population_size
        k = int(np.sqrt(number))
        #First we need to calculate the distances to the rest of solutions
        for i in range(number):
            distance_vector = []
            for j in range(number):
                if i==j:
                    distance = 0.0
                else:
                    distance = np.sqrt((self.population[i][13]-self.population[j][13])**2+(self.population[i][14]-self.population[j][14])**2)
                distance_vector.append([j,distance])
            #Sort new list by distance to i:
            sorted_distance = sorted(distance_vector,key=lambda l:l[1])
            #Get the distance corresponding to the k-th closest neighbour
            distance_k = sorted_distance[k][1] 
            density = 1.0/(distance_k+2)
            self.density.append(density)
        self.density=np.asarray(self.density)
        return self.density


    def total_fitness(self):
        self.strength = self.calculate_strength()
        self.raw_fitness = self.calculate_raw_fitness()
        self.density = self.calculate_density()
        self.fitness = self.raw_fitness + self.density
        return self.fitness


    def sort_population_by_array(self,array):
        if len(self.population) != len(array):
            return 0
        strength = list(self.strength)
        raw_fitness = list(self.raw_fitness)
        density = list(self.density)
        fitness = list(self.fitness)
        population = list(self.population)
        array = list(array)
        sorted_strength = [x for _, x in sorted(zip(array,strength), key=lambda pair: pair[0])]
        sorted_raw_fitness = [x for _, x in sorted(zip(array,raw_fitness), key=lambda pair: pair[0])]
        sorted_density = [x for _, x in sorted(zip(array,density), key=lambda pair: pair[0])]
        sorted_fitness = [x for _, x in sorted(zip(array,fitness), key=lambda pair: pair[0])]
        sorted_population = [x for _, x in sorted(zip(array,population), key=lambda pair: pair[0])]
        self.strength = np.asarray(sorted_strength)
        self.raw_fitness = np.asarray(sorted_raw_fitness)
        self.density = np.asarray(sorted_density)
        self.fitness = np.asarray(sorted_fitness)
        self.population = np.asarray(sorted_population)
        return self.population

    def reset_numbers(self):
        numbers = len(self.population)
        for i in range(numbers):
            self.population[i][12] = i
        return self.population

    def reset_numbers_variables(self):
        numbers = len(self.popX)
        for i in range(numbers):
            self.popX[i][12] = i
        return self.popX

    def get_variables(self,index):
        if index<=(len(self.population)-1):
            return self.population[index][:13]
        return 0
    
    def get_member(self,index):
        if index<=(len(self.population)-1):
            return self.population[index]
        return 0
    

    def head(self,number):
        if number<=(len(self.population)):
            returned = self.population[:number]
            return returned
        return 0
    
    def tail(self,number):
        if number<=(len(self.population)):
            returned = self.population[len(self.population)-number:]
            return returned
        return 0

    def tournament_dominant(self,index1,index2):
        self.fitness = self.total_fitness()
        if (index1<len(self.population)) & (index2<len(self.population)):
            fitness1 = self.fitness[index1]
            fitness2 = self.fitness[index2]
            if fitness1>fitness2:
                return index1,self.population[index1]
            else:
                return index2,self.population[index2]


    def mutation(self,index):
        variables = self.population[index][:13]
        for i in range(len(variables)-1):
            if i==4:
                continue
            variables[i] = variables[i]*(1+ (0.2*np.random.random()-0.1))
        return variables


    def crossing(self,index1,index2):
        mu, sigma = 0.5,0.1
        alpha = np.random.normal(mu,sigma,13)
        variables1 = self.population[index1][:13]
        variables2 = self.population[index2][:13]
        final_variable1 = []
        final_variable2 = []
        for i in range(len(variables1)-1):
            if i==4:
                final_variable1.append(variables1[4])
                final_variable2.append(variables2[4])
                continue
            y1 = alpha[i]*variables1[i] + (1-alpha[i])*variables2[i]
            y2 = alpha[i]*variables2[i] + (1-alpha[i])*variables1[i]
            final_variable1.append(y1)
            final_variable2.append(y2)
        final_variable1.append(variables1[-1])
        final_variable2.append(variables2[-1])
        final_variable1 = np.asarray(final_variable1)
        final_variable2 = np.asarray(final_variable2)
        return final_variable1, final_variable2


    def plot_population(self,iteration):
        fig, ax = plt.subplots()
        ax.set_xlabel('Bunch length [fs]')
        ax.set_ylabel('ToF jitter [fs]')
        plt.scatter(self.population[:,13],self.population[:,14])
        fig.savefig('Plots/Iteration_'+str(iteration)+'.png')
        return 0


    def write_population(self,iteration):
        filename = 'Populations/Iteration_'+str(iteration)+'.txt'
        with open(filename,'w') as outfile:
            Output = np.savetxt(outfile, self.population, delimiter=',')
        outfile.close()
        return 0
