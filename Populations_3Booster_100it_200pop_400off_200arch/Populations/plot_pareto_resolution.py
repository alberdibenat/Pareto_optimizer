import matplotlib.pyplot as plt
import numpy as np
    

def read_population(iteration):
    filename = 'Iteration_'+str(iteration)+'.txt'
    with open(filename,'r') as infile:
        Input = np.loadtxt(infile, delimiter=',')
    infile.close()
    return Input


iteration = 19
values = read_population(iteration)
print(values[0][13])


radius1 = 300
x1 = np.linspace(0.0,radius1,100)
y1 = np.sqrt(radius1**2-x1**2)

radius2 = 700
x2 = np.linspace(0.0,radius2,100)
y2 = np.sqrt(radius2**2-x2**2)

fig, ax = plt.subplots()
ax.set_xlabel('Bunch length [fs]')
ax.set_ylabel('ToF jitter [fs]')
ax.set_xlim(0.0, 7500)
ax.set_ylim(0.0, 520)
plt.scatter(values[:,13],values[:,14],color = 'tab:blue', s=10)
plt.plot(x1,y1, label=r'$\tau$=300fs', linestyle='--',color = 'green')
plt.plot(x2,y2, label=r'$\tau$=700fs',linestyle='--',color= 'darkorange')
plt.legend()
plt.grid()
fig.savefig('Iteration_'+str(iteration)+'.png')
plt.show()
