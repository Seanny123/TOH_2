import nengo
import nengo.spa as spa
from constants import *
from toh_node import toh_node_create

model = spa.SPA()

vocab = spa.Vocabulary(dimensions)
vocab.parse("NONE")

with model:
    model.goal = spa.Buffer(dimensions)
    model.focus = spa.Buffer(dimensions)
    model.goal_peg = spa.Buffer(dimensions)
    model.focus_peg = spa.Buffer(dimensions)
    model.target_peg = spa.Buffer(dimensions)
    model.goal_final = spa.Buffer(dimensions)
    model.largest = spa.Buffer(dimensions)

    model.set_focus = spa.Buffer(dimensions)
    model.set_goal = spa.Buffer(dimensions)
    model.set_goal_peg = spa.Buffer(dimensions)
    model.move_disk = spa.Buffer(dimensions)
    model.move_peg = spa.Buffer(dimensions)

    model.goal_target_peg_comp = spa.Compare()


    hanoi_node = toh_node_create
    bg_actions = [
        "dot(focus, NONE) --> set_focus=largest, set_goal=largest, set_goal_peg=goal_final",
        "(dot(focus, D2-D1-D0) + dot(goal, D2) - dot(goal_peg, target_peg))/(2**(1/2.0)) --> set_focus=D1",
        "(dot(focus, D2-D1-D0) + dot(goal, D2) + dot(goal_peg, target_peg))*0.7/(3**(1/2.0)) --> set_focus=D1, set_goal=D1, goal_final=set_goal_peg",
        "(dot(focus, D1-D0) + dot(goal, D1) - dot(goal_peg, target_peg))/(2**(1/2.0)) --> set_focus=D0",
        "(dot(focus, D1-D0) + dot(goal, D1) + dot(goal_peg, target_peg))*0.7/(3**(1/2.0)) --> set_focus=D0, set_goal=D0, goal_final=set_goal_peg",
        "(dot(focus, D0) + dot(goal_peg, target_peg))*0.7/(2**(1/2.0)) --> set_focus=NONE",
        "(dot(focus, D0) + dot(goal, D0) - dot(goal_peg, target_peg))*0.9/(3**(1/2.0)) --> set_focus=NONE, move_disk=D0, goal_final=set_goal_peg",
        "(-dot(focus, goal) + dot(focus_peg, goal_peg) - dot(target_peg, focus_peg))*1.3 --> focus=set_goal, set_goal_peg=C+B+A, target_peg=-goal_peg, focus_peg=-set_goal_peg",
        "(-dot(focus, goal) + dot(focus_peg, goal_peg) - dot(target_peg, focus_peg))*1.3 --> focus=set_goal, set_goal_peg=C+B+A, target_peg=-goal_peg, goal_peg=-set_goal_peg",
        "dot(focus, D0) + dot(goal, -D0) - 2*dot(target_peg, focus_peg) - 2*dot(target_peg, goal_peg) - 2*dot(focus_peg, goal_peg) --> goal=move_disk, target_peg=move_peg",
        "(dot(focus, D1) + dot(goal, -D1) - dot(target_peg, focus_peg) - dot(target_peg, goal_peg) - dot(focus_peg, goal_peg))*1.3 --> set_focus=D0"
        ]

    if(disk_count > 3):
        bg_actions.append(
            "(dot(focus, D2) + dot(goal, -D2) - dot(target_peg, focus_peg) - dot(target_peg, goal_peg) - dot(focus_peg, goal_peg))*1.3 --> set_focus=D1",
            "(dot(focus, D3-D2-D1-D0) + dot(goal, D3) - dot(goal_peg, target_peg))/(2**(1/2.0)) --> set_focus=D2",
            "(dot(focus, D3-D2-D1-D0) + dot(goal, D3) + dot(goal_peg, target_peg))*0.7/(3**(1/2.0)) --> set_focus=D2, set_goal=D2, goal_final=set_goal_peg"
            )

    model.bg = spa.BasalGanglia(actions=spa.Actions(*tuple(bg_actions)))
    model.thal = spa.Thalamus(model.bg)

    # somehow connect buffer inputs to the compare networks?
    # Can I use cortical actions to accomplish this?

    nengo.Connection(hanoi_node.goal, model.goal, synapse=None)
    nengo.Connection(hanoi_node.focus, model.focus, synapse=None)
    nengo.Connection(hanoi_node.goal_peg, model.goal_peg, synapse=None)
    nengo.Connection(hanoi_node.focus_peg, model.focus_peg, synapse=None)
    nengo.Connection(hanoi_node.target_peg, model.target_peg, synapse=None)
    nengo.Connection(hanoi_node.goal_final, model.goal_final, synapse=None)
    nengo.Connection(hanoi_node.largest, model.largest, synapse=None)
        
        
    nengo.Connection(model.set_focus, hanoi_node.focus, synapse=None)
    nengo.Connection(model.set_goal, hanoi_node.goal, synapse=None)
    nengo.Connection(model.set_goal_peg, hanoi_node.goal_peg, synapse=None)
    nengo.Connection(model.move_disk, hanoi_node.move, synapse=None)
    nengo.Connection(model.move_peg, hanoi_node.move_peg, synapse=None)

# Questions:
# On the poster, there's a bunch of different dimensions. How are those set?

# Aside:
# How the hell would this map onto Spaun?
# Who figured out these rules and how did they do it?
# How stupid would it be for the Thalamus to highlight which connections it's activating?
# How does Spaun deal with a bunch of different dimensions?