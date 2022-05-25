import os
import subprocess
import sys
import numpy as np
from ToF_Jitter_callable import ToF_Jitter


class CompletedProcess:
    def __init__(self,args,returncode,stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def check_returncode(self):
        if self.returncode != 0:
            err = subprocess.CalledProcessError(self.returncode,self.args,output = self.stdout)
            raise err
        return self.returncode


def run_process(*popenargs,**kwargs):
    input = kwargs.pop("input", None)
    check = kwargs.pop("handle",False)

    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    try:
        outs, errs = process.communicate(input)
    except:
        process.kill()
        process.wait()
        raise
    returncode = process.poll()
    if check and returncode:
        raise subprocess.CalledProcessError(returncode, popenargs, output=outs)
    return CompletedProcess(popenargs,returncode, stdout=outs, stderr=errs)



def runAstraAperture(amplitude_solenoid, q_bunch,rms_time,laser_size,phase_gun,amplitude_gun,phase_booster1,amplitude_booster1,phase_booster2, amplitude_booster2, phase_booster3, amplitude_booster3, run_number):

    origin = os.getcwd() #to save in which folder we are
    
    generator_template = 'Astra_files/generator_updated.template' #The generator template to copy
    generator_file = 'Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in' #The changed generator file with our variables

    template_file_SC = 'Astra_files/Aperture_SC.template' #The template to copy
    input_file_SC = 'Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.in' #The changed template file with our variables


    #Copy the generator template file and introduce our parameters
    with open(generator_template, "r") as generator1:
        generator_contents = generator1.read()
        replaced_contents = generator_contents.replace('@Number@', str('{:06d}'.format(int(run_number))))
        replaced_contents = replaced_contents.replace('@Q_total@', str('{:.06f}'.format(q_bunch)))
        replaced_contents = replaced_contents.replace('@RMS_time@', str('{:.06f}'.format(rms_time)))
        replaced_contents = replaced_contents.replace('@LaserX@', str('{:.06f}'.format(laser_size)))
        replaced_contents = replaced_contents.replace('@LaserY@', str('{:.06f}'.format(laser_size)))
        #replaced_contents = replaced_contents.replace('@NEmitX@', str('{:.06f}'.format(nEmitX)))
        #replaced_contents = replaced_contents.replace('@NEmitY@', str('{:.06f}'.format(nEmitY)))
    generator1.close()


    with open(generator_file, "w") as generator2:
        generator2.write(replaced_contents)
    generator2.close()

        
    #Copy the template file and introduce our parameters
    with open(template_file_SC, "r") as file1:
        contents = file1.read()
        replaced_contents = contents.replace('@Number@', str('{:06d}'.format(int(run_number))))
        replaced_contents = replaced_contents.replace('@gun_phase@', str('%.5f'%phase_gun))
        replaced_contents = replaced_contents.replace('@E0_gun@', str('%.5f'%amplitude_gun))
        replaced_contents = replaced_contents.replace('@Bmax@', str('%.5f'%amplitude_solenoid))
    file1.close()

    with open(input_file_SC, "w") as file2:
        file2.write(replaced_contents)
    file2.close()

    subprocess.run = run_process
    try:
        generator_run = subprocess.run(['./Astra_files/generator', str(generator_file)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.run(['./Astra_files/Astra', str(input_file_SC)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    except:
    	print('--> Woops, something went wrong in run ' + '{:06d}'.format(int(run_number))+ ', this run will return np.inf')

    #-------------------------------------------OUTPUT ANALYSIS---------------------------------------
   

    charge = 0 
    output_file_ref = 'Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.0175.001'
    try:
        output_list = np.loadtxt(output_file_ref)
        #print(output_list)
    except:
        run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm generator'+'{:06d}'.format(int(run_number))+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Log.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Xemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Yemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Zemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.*.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        return np.inf

    status = output_list[:,9:10]
    for i in range(len(status)):
        if status[i]==5:
            charge += output_list[i][7]
    
    run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm generator'+'{:06d}'.format(int(run_number))+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.0175.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Xemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Yemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Zemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Aperture_SC'+'{:06d}'.format(int(run_number))+'.Log.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)

    print(str(charge*1e6)+'fC for run '+str(int(run_number)))
    return (charge*1e6+50.0)**2


def runAstra(q_bunch,rms_time,laser_size,phase_gun,amplitude_gun,solenoid_strength,phase_booster1,amplitude_booster1,phase_booster2, amplitude_booster2, phase_booster3, amplitude_booster3, run_number):
    

    origin = os.getcwd() #to save in which folder we are
    
    generator_template = 'Astra_files/generator_updated.template' #The generator template to copy
    generator_file = 'Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in' #The changed generator file with our variables

    template_file_SC = 'Astra_files/Target_SC.template' #The template to copy
    input_file_SC = 'Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.in' #The changed template file with our variables


    #Copy the generator template file and introduce our parameters
    with open(generator_template, "r") as generator1:
        generator_contents = generator1.read()
        replaced_contents = generator_contents.replace('@Number@', str('{:06d}'.format(int(run_number))))
        replaced_contents = replaced_contents.replace('@Q_total@', str('{:.06f}'.format(q_bunch)))
        replaced_contents = replaced_contents.replace('@RMS_time@', str('{:.06f}'.format(rms_time)))
        replaced_contents = replaced_contents.replace('@LaserX@', str('{:.06f}'.format(laser_size)))
        replaced_contents = replaced_contents.replace('@LaserY@', str('{:.06f}'.format(laser_size)))
        #replaced_contents = replaced_contents.replace('@NEmitX@', str('{:.06f}'.format(nEmitX)))
        #replaced_contents = replaced_contents.replace('@NEmitY@', str('{:.06f}'.format(nEmitY)))
    generator1.close()


    with open(generator_file, "w") as generator2:
        generator2.write(replaced_contents)
    generator2.close()

        
    #Copy the template file and introduce our parameters
    with open(template_file_SC, "r") as file1:
        contents = file1.read()
        replaced_contents = contents.replace('@Number@', str('{:06d}'.format(int(run_number))))
        replaced_contents = replaced_contents.replace('@gun_phase@', str('%.5f'%phase_gun))
        replaced_contents = replaced_contents.replace('@E0_gun@', str('%.5f'%amplitude_gun))
        replaced_contents = replaced_contents.replace('@Bmax@', str('%.5f'%solenoid_strength))
        replaced_contents = replaced_contents.replace('@cavity_phase1@', str('%.5f'%phase_booster1))
        replaced_contents = replaced_contents.replace('@E0max1@', str('%.5f'%amplitude_booster1))
        replaced_contents = replaced_contents.replace('@cavity_phase2@', str('%.5f'%phase_booster2))
        replaced_contents = replaced_contents.replace('@E0max2@', str('%.5f'%amplitude_booster2))
        replaced_contents = replaced_contents.replace('@cavity_phase3@', str('%.5f'%phase_booster3))
        replaced_contents = replaced_contents.replace('@E0max3@', str('%.5f'%amplitude_booster3))
    file1.close()

    with open(input_file_SC, "w") as file2:
        file2.write(replaced_contents)
    file2.close()

    subprocess.run = run_process
    try:
        generator_run = subprocess.run(['./Astra_files/generator', str(generator_file)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.run(['./Astra_files/Astra', str(input_file_SC)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    except:
    	print('--> Woops, something went wrong in run ' + '{:06d}'.format(int(run_number))+ ', this run will return np.inf')

    #-------------------------------------------OUTPUT ANALYSIS---------------------------------------
   
    Tracked = True
    bunch_length, ToF_jitter, charge = 0.0, 0.0, 0.0 
    output_file_ref = 'Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.0764.001'
    try:
        output_list = np.loadtxt(output_file_ref)
        #print(output_list)
    except:
        run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm generator'+'{:06d}'.format(int(run_number))+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Xemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Yemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Zemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Log.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.*.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        Tracked=False
        return 0.0,0.0,0.0,0.0,0.0,Tracked

    status = output_list[:,9:10]
    for i in range(len(status)):
        if status[i]==5:
            charge += output_list[i][7]

    ToF_class = ToF_Jitter('Results_inverted_0323.txt')
    #For the jitter calculations introduce amplitudes in MV/m (without the factor *1e6) and the phases in respect to On-crest phase, jitter output is in seconds
    ToF_jitter, E_jitter = ToF_class.Jitter_calculator(phase_gun, amplitude_gun, phase_booster1, amplitude_booster1, phase_booster2, amplitude_booster2, phase_booster3, amplitude_booster3)
    if (ToF_jitter == np.inf):
        run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm generator'+'{:06d}'.format(int(run_number))+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Xemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Yemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Zemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Log.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.*.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        Tracked=False
        return 0.0,0.0,0.0,0.0,0.0,Tracked

    output_file_bunch_z = 'Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Zemit.001'
    bunch_list_z = np.loadtxt(output_file_bunch_z)

    output_file_bunch_x = 'Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Xemit.001'
    bunch_list_x = np.loadtxt(output_file_bunch_x)
    
    #longitudinal emittance, bunch length, energy, energy deviation, time of flight, transverse spot size, normalized transverse emittance, final charge
    #bunch_list_z[-1,5],bunch_list_z[-1,3],bunch_list_z[-1,2],bunch_list_z[-1,4],bunch_list_z[-1,1],bunch_list_x[-1,3],bunch_list_x[-1,5], Qbunch_final
    
    bunch_length = bunch_list_z[-1,3]*1e-3 #in meters
    bunch_energy = bunch_list_z[-1,2]*1e6 + 0.511e6 #in eV
    gamma_bunch = bunch_energy/0.511e6
    beta_bunch = np.sqrt(gamma_bunch**2-1)/gamma_bunch
    bunch_duration = bunch_length/(beta_bunch*3e8)
    trans_norm_emittance = bunch_list_x[-1,5] #in pi mm mrad
        
    run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm generator'+'{:06d}'.format(int(run_number))+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.0764.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Xemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Yemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Zemit.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    run = subprocess.call('rm Astra_files/Target_SC'+'{:06d}'.format(int(run_number))+'.Log.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)

    return bunch_duration*1e15, ToF_jitter[0]*1e15, bunch_energy, trans_norm_emittance, charge*1e6, Tracked
