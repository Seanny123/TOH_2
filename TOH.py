import nengo
import nengo.spa as spa

model = spa.SPA()

dimensions =9 
n_neurons = 20
disk_count = 3
threshold = 0.5

vocab = spa.Vocabulary(dimensions)
vocab.parse("None")

with model: