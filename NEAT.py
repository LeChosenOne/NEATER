from genome import Genome
import random

class NEATModel:
    def __init__(self, population_size, input_size, output_size):
        self.genomes = []
        self.population_size = population_size
        self.species = []
        for g in range(self.population_size):
            new_genome = Genome(num_inputs=input_size, num_outputs=output_size)
            new_genome.mutate()
            new_genome.ave_weight = 0
            for conn in new_genome.connection_genes:
                new_genome.ave_weight += conn.weight / len(new_genome.connection_genes)
            self.genomes.append(new_genome)

    # helper function to determine the "distance" between two genomes
    def distance(genome1, genome2):
        disjoint_genes = 0
        similar_genes = 0
        similar_weight = 0
        innovation_lookup = {}
        for connection in list(set(genome1.connection_genes) | set(genome2.connection_genes)):
            if connection.innovation_number in innovation_lookup:
                disjoint_genes -= 1
                similar_genes += 1
                weight_difference = abs(innovation_lookup[connection.innovation_number] - connection.weight)
                similar_weight += weight_difference
            else:
                innovation_lookup[connection.innovation_number] = connection.weight
                disjoint_genes += 1
        N = max(len(genome1.connection_genes), len(genome2.connection_genes))
        # for small genomes, just use N = 1
        if N < 20:
            N = 1
        return disjoint_genes / N + similar_weight / similar_genes * 0.5

    # helper function to perform crossover
    def crossover(self, suitable_genomes):
        self.genomes = []
        population = 0
        while pop <= self.population_size:
            population += 1
            parents = random.sample(suitable_genomes,2)
            parent1 = parents[0]
            parent2 = parents[1]
            p1_gene_index = 0
            p2_gene_index = 0
            connection_genes = []
            neuron_genes = {}
            inputs = []
            outputs = []
            neuron_counter = 0

            # add initial neuron genes
            for i in parent1.inputs:
                neuron = NeuronGene(id=neuron_counter,layer = 0)
                neuron_genes[neuron_counter] = neuron
                inputs.append(neuron)
                neuron_counter += 1
            for o in parent1.outputs:
                neuron = NeuronGene(id=neuron_counter,layer = 1)
                neuron_genes[neuron_counter] = neuron
                outputs.append(neuron)
                neuron_counter += 1

            # add all connection genes and added neurons
            while p1_gene_index < len(parent1.connection_genes) or p2_gene_index < len(parent2.connection_genes):
                p1 = parent1.connection_genes[p1_gene_index]
                p2 = parent2.connection_genes[p2_gene_index]
                # randomly choose one of the alleles if they are the same gene
                if p1.innovation_number == p2.innovation_number:
                    chosen_connection = random.choice([p1, p2])
                    in_neuron = None
                    out_neuron = None
                    if chosen_connection.in_neuron.id in neuron_genes:
                        in_neuron = neuron_genes[chosen_connection.in_neuron.id]
                    else:
                        in_neuron = Neuron(id=neuron_counter, chosen_connection.in_neuron.layer)
                        neuron_genes[neuron_counter] = in_neuron
                        neuron_counter += 1
                    if chosen_connection.out_neuron.id in neuron_genes:
                        out_neuron = neuron_genes[chosen_connection.out_neuron.id]
                    else:
                        out_neuron = Neuron(id=neuron_counter, chosen_connection.out_neuron.layer)
                        neuron_genes[neuron_counter] = out_neuron
                        neuron_counter += 1
                    new_connection = ConnectionGene(in_neuron, out_neuron, chosen_connection.weight, chosen_connection.innovation_number)
                    out_neuron.add_connection(new_connection)
                    connection_genes.append(new_connection)
                    p2_gene_index += 1
                    p1_gene_index += 1

                # always take disjoint genes
                elif p1.innovation_number > p2.innovation_number:
                    in_neuron = None
                    out_neuron = None
                    if p2.in_neuron.id in neuron_genes:
                        in_neuron = neuron_genes[p2.in_neuron.id]
                    else:
                        in_neuron = Neuron(id=neuron_counter, p2.in_neuron.layer)
                        neuron_genes[neuron_counter] = in_neuron
                        neuron_counter += 1
                    if p2.out_neuron.id in neuron_genes:
                        out_neuron = neuron_genes[p2.out_neuron.id]
                    else:
                        out_neuron = Neuron(id=neuron_counter, p2.out_neuron.layer)
                        neuron_genes[neuron_counter] = out_neuron
                        neuron_counter += 1
                    new_connection = ConnectionGene(in_neuron, out_neuron, p2.weight, p2.innovation_number)
                    out_neuron.add_connection(new_connection)
                    connection_genes.append(new_connection)
                    p2_gene_index += 1
                else:
                    in_neuron = None
                    out_neuron = None
                    if p1.in_neuron.id in neuron_genes:
                        in_neuron = neuron_genes[p1.in_neuron.id]
                    else:
                        in_neuron = Neuron(id=neuron_counter, p1.in_neuron.layer)
                        neuron_genes[neuron_counter] = in_neuron
                        neuron_counter += 1
                    if p1.out_neuron.id in neuron_genes:
                        out_neuron = neuron_genes[p1.out_neuron.id]
                    else:
                        out_neuron = Neuron(id=neuron_counter, p1.out_neuron.layer)
                        neuron_genes[neuron_counter] = out_neuron
                        neuron_counter += 1
                    new_connection = ConnectionGene(in_neuron, out_neuron, p1.weight, p1.innovation_number)
                    out_neuron.add_connection(new_connection)
                    connection_genes.append(new_connection)
                    p1_gene_index += 1

            # take excess genes from more fit parent
            while p1_gene_index < len(parent1.connection_genes) and parent1.fitness > parent2.fitness:
                connection = parent1.connection_genes[p1_gene_index]
                in_neuron = None
                out_neuron = None
                if connection.in_neuron.id in neuron_genes:
                    in_neuron = neuron_genes[connection.in_neuron.id]
                else:
                    in_neuron = Neuron(id=neuron_counter, connection.in_neuron.layer)
                    neuron_genes[neuron_counter] = in_neuron
                    neuron_counter += 1
                if connection.out_neuron.id in neuron_genes:
                    out_neuron = neuron_genes[connection.out_neuron.id]
                else:
                    out_neuron = Neuron(id=neuron_counter, connection.out_neuron.layer)
                    neuron_genes[neuron_counter] = out_neuron
                    neuron_counter += 1
                new_connection = ConnectionGene(in_neuron, out_neuron, connection.weight, connection.innovation_number)
                out_neuron.add_connection(new_connection)
                connection_genes.append(new_connection)
                p1_gene_index += 1

            while p2_gene_index < len(parent2.connection_genes) and parent2.fitness > parent1.fitness:
                connection = parent2.connection_genes[p2_gene_index]
                in_neuron = None
                out_neuron = None
                if connection.in_neuron.id in neuron_genes:
                    in_neuron = neuron_genes[connection.in_neuron.id]
                else:
                    in_neuron = Neuron(id=neuron_counter, connection.in_neuron.layer)
                    neuron_genes[neuron_counter] = in_neuron
                    neuron_counter += 1
                if connection.out_neuron.id in neuron_genes:
                    out_neuron = neuron_genes[connection.out_neuron.id]
                else:
                    out_neuron = Neuron(id=neuron_counter, connection.out_neuron.layer)
                    neuron_genes[neuron_counter] = out_neuron
                    neuron_counter += 1
                new_connection = ConnectionGene(in_neuron, out_neuron, connection.weight, connection.innovation_number)
                out_neuron.add_connection(new_connection)
                connection_genes.append(new_connection)
                p2_gene_index += 1
            g = suitable_genomes[0]
            new_genome = Genome(len(inputs), len(outputs), g.weight_mutation, g.weight_randomize, g.neuron_mutation, g.connection_mutation)
            genome.inputs = inputs
            genome.outputs = outputs
            genome.neuron_genes = neuron_genes
            genome.connection_genes = connection_genes
            self.genomes.add(new_genome)

    def run(self, generations, fitness_function, species_threshold = 3.0):
        self.fitness_function = fitness_function
        for gen in range(generations):
            for genome in self.genomes:
                # determine fitness of each genome
                genome.fitness = fitness_function(genome)
                # speciate each genome
                if len(self.species) == 0:
                    self.species.append([genome])
                else:
                    found_species = False
                    for species in self.species:
                        if distance(genome, random.choice(species)) < species_threshold:
                            species.append(genome)
                            found_species = True
                            break
                    if not found_species:
                        self.species.append([genome])
            # determine which genomes are suitable for crossover
            suitable_genomes = []
            for species in self.species:
                # fitness tournament to find suitable genomes
                if len(species) > 2:
                    for x in range(len(species)/2):
                        genomes = random.sample(species, 2)
                        best_genome = max(genomes, key=lambda x: x.fitness)
                        suitable_genomes.add(best_genome)
            # crossover and mutate
            crossover(self, suitable_genomes)
            for genome in self.genomes:
                genome.mutate()
