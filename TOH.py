import nengo
import nengo.spa as spa
import constants
from toh_node import toh_node_create

model = spa.SPA()

vocab = spa.Vocabulary(dimensions)
vocab.parse("None")

with model:
    model.goal = spa.Buffer()
    model.focus = spa.Buffer()
    model.goalpeg = spa.Buffer()
    model.focuspeg = spa.Buffer()
    model.targetpeg = spa.Buffer()
    model.goalfinal = spa.Buffer()
    model.largest = spa.Buffer()

    mdoel.set_focus = spa.Buffer()
    mdoel.set_goal = spa.Buffer()
    mdoel.set_goalpeg = spa.Buffer()
    mdoel.move_disk = spa.Buffer()
    mdoel.move_peg = spa.Buffer()


    hanoi_node = toh_node_create
    bg_actions = spa.Actions("")

    nengo.Connection(hanoi_node.goal, model.goal, synapse=None)
    nengo.Connection(hanoi_node.focus, model.focus, synapse=None)
    nengo.Connection(hanoi_node.goal_peg, model.goal_peg, synapse=None)
    nengo.Connection(hanoi_node.focus_peg, model.focus_peg, synapse=None)
    nengo.Connection(hanoi_node.target_peg, model.target_peg, synapse=None)
    nengo.Connection(hanoi_node.goal_final, model.goal_final, synapse=None)
    nengo.Connection(hanoi_node.largest, model.largest, synapse=None)
        
        
    nengo.Connection(model.set_focus, hanoi_node.focus, synapse=None)
    nengo.Connection(model.set_goal, hanoi_node.goal, synapse=None)
    nengo.Connection(model.set_goal_peg, hanoi_node.goalpeg, synapse=None)
    nengo.Connection(model.move_disk, hanoi_node.move, synapse=None)
    nengo.Connection(model.move_peg, hanoi_node.movepeg, synapse=None)