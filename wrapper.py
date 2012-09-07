from perceptions_cell import *
from perceptions_grid import *
import math
import time
import numpy
import random
import glob
import os
import csv
import sys
from collections import defaultdict
from operator import mul

def setup_individuals(n,percent_defectors,coop_types,operation,randomize,skepticism):
    n_defectors = n*percent_defectors/100
    n_cooperators = n - n_defectors
    individuals = [PCell('D') for i in range(n_defectors)]
    for i in range(len(coop_types)):
        individuals += [PCell(coop_types[i],operation,randomize,skepticism) for j in range(n_cooperators/len(coop_types))]
    random.shuffle(individuals)
    return individuals

def setup_grid(dimensions,percent_defectors,cooperator_types,operation,randomize,skepticism):
    length = dimensions[0]
    width = dimensions[1]
    n_individuals = length * width
    n_defectors = n_individuals*percent_defectors/100
    n_cooperators = n_individuals - n_defectors
    pairs = set([(x,y) for x in range(length) for y in range(width)])
    cell_dict = {}
    cell_dict['D'] = set(random.sample(pairs, n_defectors))
    pairs = pairs - cell_dict['D']
    for i in range(len(cooperator_types)):
        cell_dict[cooperator_types[i]] = set(random.sample(pairs,n_cooperators/len(cooperator_types)))
        pairs = pairs - cell_dict[cooperator_types[i]]
    if sum([len(cell_dict[k]) for k in cell_dict.keys()]) != n_individuals:
        raise ValueError
    all_cell_pairs = [zip(cell_dict[k],[k]*len(cell_dict[k])) for k in cell_dict.keys()]
    cell_pairs = [item for pair_list in all_cell_pairs for item in pair_list]
    inverted_cell_dict = dict(cell_pairs)
    grid = [[inverted_cell_dict[(x,y)] for x in range(length)] for y in range(width)]
    return PGrid(grid)

def initialize_social_information(individuals, max_social_information):
    prices = [individual.value for individual in individuals]
    social_info = random.sample(prices,max_social_information)
    return social_info

def initialize_grid_social_information(grid,max_social_information):
    prices = [grid.grid[i][j].value for i in range(grid.length) for j in range(grid.width)]
    social_info = random.sample(prices,max_social_information)
    return social_info

def dimensionless_run(n_individuals,percent_defectors,cooperator_types,operation,max_social_info,randomize,skepticism, cutoff,fn,type,extra_kwargs):
    mylocals = locals()
    output_file = open(fn,'w')
    for k in mylocals.keys():
        if k == 'fn':
            continue
        output_file.write(k + '\t' + str(mylocals[k]) + '\n')
    del mylocals
    individuals = setup_individuals(n_individuals,percent_defectors,cooperator_types,operation,randomize,skepticism)
    social_info = initialize_social_information(individuals,max_social_info)
    initial_stats = get_all_stats(individuals)
    output_stats = {}
    for subpopulation in initial_stats:
        output_stats[subpopulation] = dict([[k,[initial_stats[subpopulation][k]]] for k in initial_stats[subpopulation].keys()])
    while True:
        if type =='dimensionless':
            step_result = dimensionless_step(individuals, social_info)
        elif type == 'bipartite':
            step_result = bipartite_step(individuals,social_info)
        elif type == 'multicyclic':
            step_result = multicyclic_step(individuals,social_info, extra_kwargs['neighborhood'])
        else:
            print type, 'wtffffff'
            return
        individuals = step_result['individuals']
        social_info = step_result['social_info']
        stats = step_result['stats']
        for subpopulation in stats.keys():
            for k in stats[subpopulation].keys():
                output_stats[subpopulation][k].append(stats[subpopulation][k])
        if stats['all']['minimum_irrationality'] > cutoff:
            break
        else: pass
    write_stats(output_stats,output_file)
    return output_stats

def grid_run(dimensions, percent_defectors, cooperator_types,operation,randomize,skepticism,max_social_info,cutoff,fn):
    mylocals = locals()
    output_file = open(fn,'w')
    for k in mylocals.keys():
        if k == 'fn':
            continue
        output_file.write(k + '\t' + str(mylocals[k]) + '\n')
    del mylocals
    grid = setup_grid(dimensions,percent_defectors,cooperator_types,operation,randomize,skepticism)
    social_info = initialize_grid_social_information(grid,max_social_info)
    initial_stats = get_all_grid_stats(grid)
    output_stats = {}
    for subpopulation in initial_stats:
        output_stats[subpopulation] = dict([[k,[initial_stats[subpopulation][k]]] for k in initial_stats[subpopulation].keys()])
    count = 0
    while True:
        step_result = grid_step(grid, social_info)
        social_info = step_result['social_info']
        stats = step_result['stats']
        for subpopulation in stats.keys():
            for k in stats[subpopulation].keys():
                output_stats[subpopulation][k].append(stats[subpopulation][k])
        if stats['all']['minimum_irrationality'] > cutoff:
            break
        else: pass
    write_stats(output_stats,output_file)
    return output_stats

def grid_step(grid,social_information):
    price_grid = [[0 for i in range(grid.length)] for j in range(grid.width)]
    for i in range(grid.length):
        for j in range(grid.width):
            loc1 = (i,j)
            loc2 = random.choice(grid.neighbors(i,j))
            agent1 = grid.grid[loc1[0]][loc1[1]]
            agent2 = grid.grid[loc2[0]][loc2[1]]
            price = find_price(agent1,agent2)
            price_grid[i][j] = price
    for i in range(grid.length):
        for j in range(grid.width):
            agent = grid.grid[i][j]
            price = price_grid[i][j]
            agent.receive_message(price,social_information)
    flat_prices = [price for price_list in price_grid for price in price_list]
    new_social_information = random.sample(flat_prices,len(social_information))
    stats = get_all_grid_stats(grid)
    return {'social_info': new_social_information, 'stats': stats}

def dimensionless_step(individuals,social_information):
    random.shuffle(individuals)
    lumpy_prices = [[find_price(individuals[2*i],individuals[2*i+1])]*2 for i in range(len(individuals)/2)]
    flat_prices = [price for sublist in lumpy_prices for price in sublist]
    [individuals[i].receive_message(flat_prices[i],social_information) for i in range(len(individuals))]
    new_social_info = random.sample(flat_prices, len(social_information))
    stats = get_all_stats(individuals)
    return {'individuals': individuals, 'social_info': new_social_info, 'stats': stats}

def bipartite_step(individuals,social_information):
    pop_size = len(individuals)
    first_half = individuals[:pop_size/2]
    second_half = individuals[pop_size/2:]
    random.shuffle(first_half)
    random.shuffle(second_half)
    prices = [find_price(first_half[i],second_half[i]) for i in range(len(first_half))]
    [first_half[i].receive_message(prices[i],social_information) for i in range(len(prices))]
    [second_half[i].receive_message(prices[i], social_information) for i in range(len(prices))]
    new_social_info = random.sample(prices, len(social_information))
    stats = get_all_stats(individuals)
    individuals = first_half + second_half
    return {'individuals': individuals, 'social_info': new_social_info, 'stats': stats}

def multicyclic_step(individuals,social_information,neighborhood = 5):
    pop_size = len(individuals)
    partners = [(i - neighborhood + random.randint(0,2*neighborhood)) % pop_size for i in range(pop_size)]
    prices = [find_price(individuals[i],individuals[partners[i]]) for i in range(pop_size)]
    [individuals[i].receive_message(prices[i],social_information) for i in range(pop_size)]
    new_social_info = random.sample(prices, len(social_information))
    stats = get_all_stats(individuals)
    return {'individuals': individuals, 'social_info': new_social_info, 'stats': stats}

def write_stats(output_stats,output_file):
    subpopulations = output_stats.keys()
    stats_keys = output_stats['all'].keys()
    key_pairs = [(x,y) for x in subpopulations for y in stats_keys]
    stat_columns = [output_stats[key_pair[0]][key_pair[1]] for key_pair in key_pairs]
    stat_rows = zip(*stat_columns)
    pretty_keys = ['_'.join(x) for x in key_pairs]
    output_file.write('\t'.join(pretty_keys) + '\n')
    for row in stat_rows:
        output_file.write('\t'.join([str(x) for x in row]) +'\n')
    return

def get_all_stats(individuals):
    ## Returns stats for each group of cooperators individually and the population as a whole.
    cooperators = [x for x in individuals if x.strategy == 'C']
    cooperator_types = list(set([x.type for x in cooperators]))
    if len(cooperator_types) == 1:
        output_dict = {}
    else:
        subpopulations = [[x for x in cooperators if x.type == type] for type in cooperator_types]
        output_dict = {cooperator_types[i]:get_stats(subpopulations[i]) for i in range(len(subpopulations))}
    output_dict['all'] = get_stats(cooperators)
    return output_dict

def get_all_grid_stats(grid):
    individuals = grid.to_list()
    return get_all_stats(individuals)

def get_stats(subpopulation,hardcore = False):
    values = [x.value for x in subpopulation]
    mean = numpy.mean(values)
    std = numpy.std(values)
    median = numpy.median(values)
    mean_irrationality = float(mean)/DEFECTOR_VALUE
    median_irrationality = float(median)/DEFECTOR_VALUE
    minimum_irrationality = float(min(values))/DEFECTOR_VALUE
    if hardcore:
        all_memory = [item for x in subpopulation for item in x.memory]
        hardcore_minimum = float(min(all_memory))/DEFECTOR_VALUE
    mylocals = locals()
    good_keys = ['mean','median','std','median','mean_irrationality','median_irrationality','minimum_irrationality']
    if hardcore:
        good_keys += ['hardcore_minimum']
    output_dict = {k:mylocals[k] for k in mylocals.keys() if k in good_keys}
    return output_dict

def parallel_run(inputs):
    #import math, os
    num_iters = inputs['num_iters']
    folder = inputs['folder']
    zfill_amt = int(math.floor(math.log10(inputs['num_iters'])))
    for i in range(num_iters):
        run_num_str = str(i).zfill(zfill_amt)
        if not os.path.exists(folder + '/'):
            os.mkdir(folder)
        else: pass
        long_fn_start = inputs.items()
        long_fn_start = '__'.join([str(item) for sublist in long_fn_start for item in sublist])        
        fn = folder + '/' + long_fn_start + '_' + run_num_str + '.txt'
        percent_defectors = inputs['percent_defectors']
        cooperator_types = inputs['cooperator_types']
        operation = inputs['operation']
        max_social_info = inputs['max_social_info']
        randomize = inputs['randomize']
        skepticism = inputs['skepticism']
        cutoff = inputs['cutoff']
        if inputs['type'] == 'grid':
            dimensions = inputs['dimensions']            
            results = grid_run(dimensions, percent_defectors, cooperator_types,operation,randomize,skepticism,max_social_info,cutoff,fn)
        else:
            n_individuals = inputs['n_individuals']
            type = inputs['type']
            results = dimensionless_run(n_individuals,percent_defectors,cooperator_types,operation,max_social_info,randomize,skepticism,cutoff,fn,type,inputs)
    return
