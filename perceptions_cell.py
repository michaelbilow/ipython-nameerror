import random
import time
import sys
import numpy

MUT_FREQ = 2**13
CELL_INFO_DICT = {'D': {'strategy': 'D', 'memory': []},
                  }

DEFECTOR_VALUE = 1024
EPSILON = .01 * DEFECTOR_VALUE

class PCell:
    def __init__(self,type = '10', operation='mean',randomize = False,skepticism=0,empty = False):
        self.type = type
        self.operation = operation
        self.skepticism = skepticism
        try:
            self.memory = [0 for i in range(int(self.type))]
            self.memory_size = int(self.type)
            self.strategy = 'C'
        except ValueError:
            try:
                self.strategy = CELL_INFO_DICT[type]['strategy']
                self.memory = CELL_INFO_DICT[type]['memory']
                self.memory_size = len(self.memory)
            except KeyError:
                print "Type:", type
                print "Bad Cell Type!"
                sys.exit(-1)
        if randomize:
            self.memory = [100*random.random() - 50 for i in range(self.memory_size)]
        if empty:
            self.memory = []
        if randomize and empty:
            print "Can't randomize and empty!"
            sys.exit(-1)
        self.update_value()
        return
    
    def __str__(self):
        return self.type
    
    def at_social_optimum(self,social_optimum_max=128):
        return self.strategy == 'D' or self.value < social_optimum_max
    
## Update_value updates the value stored in memory
## to the cell's operation applied to 
    def update_value(self,social_information = []):
        if self.strategy == 'D':
            self.value = DEFECTOR_VALUE
            return
        if self.memory == []:
            self.value = 0
        elif self.memory_size == 0:
            self.value = random.random() - .5
        else:
            operation = self.operation
            try:
                memory = self.memory
                all_information = memory + social_information
                if self.skepticism > 0:
                    k = self.skepticism
                    if 2*k >= len(all_information): # If the individual is too skeptical, just take the median.
                        all_information = [numpy.median(all_information)]
                    else:
                        sorted_information = sorted(all_information)
                        all_information = sorted_information[k:-k]
                else: pass
                
                if operation == 'mean':
                    new_val = numpy.mean(all_information)
                elif operation == 'median':
                    new_val = numpy.median(all_information)
                elif operation == 'random':
                    new_val = random.choice(all_information)
#                elif operation == 'interquartile_mean':
#                    data_len = len(all_information)
#                    sorted_data = sorted(all_information)
#                    new_val = numpy.mean(sorted_data[data_len/4:3*data_len/4])
                elif operation == 'min':
                    new_val = min(all_information)
                else:
                    raise ValueError
                self.value = new_val
            except:
                raise ValueError
        return
    
## 
    def add_to_memory(self,val, extra_information = []):
        old_memory = self.memory
        mem_size= self.memory_size
        if mem_size == 0:
            self.value = val
        else:
            if len(old_memory) == mem_size:
                new_memory = [val] + old_memory[:-1]
            else:
                new_memory = [val] + old_memory
            self.memory = new_memory
            self.update_value(extra_information)
        return
        
    
## Ways to run the program.
    def send_message(self):
        return self.value
    
    def receive_message(self,message,extra_information = []):
        if self.strategy == 'D':
            return
        else:
            self.add_to_memory(message, extra_information)
        return

## Execute a trade between two agents
def find_price(agent1,agent2):
    price = numpy.mean([agent1.value,agent2.value])
    return price


## Finds whether a group of 
def at_stable_equilibrium(agent_list):
    memories = [agent.memory for agent in agent_list if agent.memory != []]
    if memories == []:
        value_list = [agent.value for agent in agent_list]
        return max(value_list) - min(value_list) < EPSILON
    maxes = [max(x) for x in memories]
    mins = [min(x) for x in memories]
    grand_max = max(maxes)
    grand_min = min(mins)
    return grand_max - grand_min < EPSILON