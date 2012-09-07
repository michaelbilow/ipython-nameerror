from wrapper import parallel_run
import time, sys
from IPython.parallel import Client

def is_not_a_stable_equilibrium_or_overskepticism(raw_dict):
    skepticism = raw_dict['skepticism']
    max_social_info = raw_dict['max_social_info']
    max_memory_length = max([int(x) for x in raw_dict['cooperator_types']])
    min_memory_length = min([int(x) for x in raw_dict['cooperator_types']])
    n_individuals = raw_dict['n_individuals']
    n_defectors = raw_dict['percent_defectors'] * n_individuals/100
    if raw_dict['operation'] == 'median':
        skepticism = (max_memory_length + max_social_info - 1)/2
    if skepticism*2 >= max_memory_length + max_social_info:
        print 'Skepticism too high', skepticism, max_memory_length + max_social_info, ' '.join([str(x) for x in raw_dict.items()])
        return False
    if max_social_info >= 2*n_defectors + 1 and skepticism >= 2*(n_defectors + max_memory_length):
        print 'Stable equlibrium', skepticism,max_social_info,n_defectors,' '.join([str(x) for x in raw_dict.items()])
        return False
    return True

def make_input_sets(inputs_dict,conditions):
    variable_values = inputs_dict.values()
    raw_variable_values = [[x] for x in variable_values.pop()]
    while len(variable_values) > 0:
        current_variable = variable_values.pop()
        raw_variable_values = [[x] + raw_list for raw_list in raw_variable_values for x in current_variable]
    
    keys = inputs_dict.keys()
    raw_output_dicts = [dict(zip(keys,raw_variable_set)) for raw_variable_set in raw_variable_values]
    output_dicts = [x for x in raw_output_dicts if all([condition(x) for condition in conditions])]
    return output_dicts

    
if __name__ == "__main__":

    if len(sys.argv) > 1: ## DO NOT USE
        input_fn = sys.argv[1]
        input_file = open(input_fn,'r')
        inputs = dict([line.strip().split('\t') for line in input_file])
    else:
        inputs = {'percent_defectors' : [10],
                   'max_social_info' : [2,4,8,16,32,64],
                   'cooperator_types': [[str(i)] for i in (2,4,8,16,32,64)],
                   'operation':['mean'],
                   'skepticism': [0] ,
                   'randomize':[False],
                   'n_individuals':[100],
                   'cutoff': [1 - .99],
                   'num_iters':[10],
                   'folder': ['test_parallel'],
                   'type':['dimensionless']
                   }
        
    conditions = [is_not_a_stable_equilibrium_or_overskepticism]
    input_pairs = make_input_sets(inputs,conditions)
    start_time = time.time()
    inputs = input_pairs
    client = Client()
    lbview = client.load_balanced_view()
    lbview.block = True
    lbview.map(parallel_run,inputs)
        
    print "Time elapsed: ", time.time() - start_time, "s"