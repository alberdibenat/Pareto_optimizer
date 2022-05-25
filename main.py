import numpy as np
import population

maxIt = 20
populationSize = 5
maxGradGun = 20.0
p_mix = 0.85
offspring_number = 2*populationSize
nArchive = 5
poolSize = 2*populationSize
initial_random_size =  20



pop = population.Population()
size = pop.population_size

while size < initial_random_size:
    pool = population.Population()
    pool.random_initialize(poolSize,maxGradGun)
    pool.objective_evaluation(pool.popX)
    pool.clean_population()
    pop.add_members(pool.head(pool.population_size))
    size = pop.population_size




pop.total_fitness()
pop.sort_population_by_array(pop.fitness)
pop.reset_numbers()

#Should I cut pop to only have the first populationSize number of entries?
pop.cut_population(populationSize)

for i in range(maxIt):
    if (i==0):
        Q = population.Population()
        Q.add_members(pop.head(pop.population_size))
    else:
        Q = population.Population()
        Q.add_members(pop.head(pop.population_size))
        Q.add_members(offsprings_final.head(offsprings_final.population_size))

    Q.clean_population()
    Q.total_fitness()
    Q.sort_population_by_array(Q.fitness)
    Q.reset_numbers()

    archiver = population.Population()
    archiver.add_members(Q.head(min(nArchive,Q.population_size)))
    archiver.plot_population(i)
    archiver.write_population(i)
    
    print(archiver.population)

    raw_fitness = archiver.calculate_raw_fitness()
    print(raw_fitness)
    if np.sum(raw_fitness) == 0:
        break
    
    offsprings_final = population.Population()
    size = offsprings_final.population_size
    while size < offspring_number:
        offsprings = population.Population()
        cnt = 0
        while cnt < offspring_number:
            value = np.random.random()
            if (value>p_mix):
                index1 = int(np.random.random()*Q.population_size)
                index2 = int(np.random.random()*Q.population_size)
                mutated_var_index, _ = Q.tournament_dominant(index1,index2)
                mutated_var = Q.mutation(mutated_var_index)
                if Q.check_limits(mutated_var):
                    cnt += 1
                    offsprings.add_variables(np.asarray([mutated_var]))
            else:
                index = []
                cross_var_index = []
                for i in range(8):
                    index.append(int(np.random.random()*Q.population_size))
                #index1 = int(np.random.random()*Q.population_size)
                #index2 = int(np.random.random()*Q.population_size)
                #index3 = int(np.random.random()*Q.population_size)
                #index4 = int(np.random.random()*Q.population_size)
                cross_var_index1,_ = Q.tournament_dominant(index[0],index[1])
                cross_var_index2,_ = Q.tournament_dominant(index[2],index[3])
                cross_var_index3,_ = Q.tournament_dominant(index[4],index[5])
                cross_var_index4,_ = Q.tournament_dominant(index[6],index[7])
                cross_var_index_final1 = Q.tournament_dominant(cross_var_index1,cross_var_index2)
                cross_var_index_final2 = Q.tournament_dominant(cross_var_index3,cross_var_index4)
                cross_var1, cross_var2 = Q.crossing(cross_var_index_final1,cross_var_index_final2)
                if Q.check_limits(cross_var1):
                    cnt += 1
                    offsprings.add_variables(np.asarray([cross_var1]))
                if Q.check_limits(cross_var2):
                    cnt += 1
                    offsprings.add_variables(np.asarray([cross_var2]))
        
        offsprings.reset_numbers_variables()
        offsprings.objective_evaluation(offsprings.popX)
        offsprings.clean_population()

        offsprings_final.add_members(offsprings.head(offsprings.population_size))
        size = offsprings_final.population_size

    #Should I cut offsprings_final to only have the offspring_number number of entries?
    offsprings_final.cut_population(offspring_number)
    offsprings_final.total_fitness()
    offsprings_final.sort_population_by_array(offsprings_final.fitness)
    offsprings_final.reset_numbers()
    
    
    
    pop = population.Population()
    pop.add_members(archiver.head(archiver.population_size))

    






