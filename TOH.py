import nengo
import nengo.spa as spa
from constants import *
from toh_node import toh_node_create
import ipdb

model = spa.SPA()

vocab = spa.Vocabulary(dimensions, randomize=False)
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

    model.goal_target_peg_comp = spa.Compare(dimensions)
    model.focus_goal_comp = spa.Compare(dimensions)
    model.focus_goal_peg_comp = spa.Compare(dimensions)
    model.target_focus_peg_comp = spa.Compare(dimensions)

    model.cortical_actions = spa.Actions("goal_target_peg_comp_A = goal_peg", "goal_target_peg_comp_B = target_peg",
        "focus_goal_comp_A = focus", "focus_goal_comp_B = goal",
        "focus_goal_peg_comp_A = focus_peg", "focus_goal_peg_comp_B = goal_peg",
        "target_focus_peg_comp_A = target_peg", "target_focus_peg_comp_B = focus_peg"
    )

    model.cortical = spa.Cortical(model.cortical_actions)

    hanoi_node = toh_node_create(disk_count, dimensions, vocab)
    bg_actions = [
        "dot(focus, NONE) --> set_focus=largest, set_goal=largest, set_goal_peg=goal_final",
        "(dot(focus, D2-D1-D0) + dot(goal, D2) - goal_target_peg_comp)/(2**(1/2.0)) --> set_focus=D1",
        "(dot(focus, D2-D1-D0) + dot(goal, D2) + goal_target_peg_comp)*0.7/(3**(1/2.0)) --> set_focus=D1, set_goal=D1, goal_final=set_goal_peg",
        "(dot(focus, D1-D0) + dot(goal, D1) - goal_target_peg_comp)/(2**(1/2.0)) --> set_focus=D0",
        "(dot(focus, D1-D0) + dot(goal, D1) + goal_target_peg_comp)*0.7/(3**(1/2.0)) --> set_focus=D0, set_goal=D0, goal_final=set_goal_peg",
        "(dot(focus, D0) + goal_target_peg_comp)*0.7/(2**(1/2.0)) --> set_focus=NONE",
        "(dot(focus, D0) + dot(goal, D0) - goal_target_peg_comp)*0.9/(3**(1/2.0)) --> set_focus=NONE, move_disk=D0, goal_final=set_goal_peg",
        "(-focus_goal_comp + focus_goal_peg_comp - target_focus_peg_comp)*1.3 --> focus=set_goal, set_goal_peg=C+B+A, target_peg=-goal_peg, focus_peg=-set_goal_peg",
        "(-focus_goal_comp + focus_goal_peg_comp - target_focus_peg_comp)*1.3 --> focus=set_goal, set_goal_peg=C+B+A, target_peg=-goal_peg, goal_peg=-set_goal_peg",
        "dot(focus, D0) + dot(goal, -D0) - 2*target_focus_peg_comp - 2*goal_target_peg_comp - 2*focus_goal_peg_comp --> goal=move_disk, target_peg=move_peg",
        "(dot(focus, D1) + dot(goal, -D1) - target_focus_peg_comp - goal_target_peg_comp - focus_goal_peg_comp)*1.3 --> set_focus=D0"
        ]

    if(disk_count > 3):
        bg_actions.append(
            "(dot(focus, D2) + dot(goal, -D2) - target_focus_peg_comp - goal_target_peg_comp - focus_goal_peg_comp)*1.3 --> set_focus=D1",
            "(dot(focus, D3-D2-D1-D0) + dot(goal, D3) - goal_target_peg_comp)/(2**(1/2.0)) --> set_focus=D2",
            "(dot(focus, D3-D2-D1-D0) + dot(goal, D3) + goal_target_peg_comp)*0.7/(3**(1/2.0)) --> set_focus=D2, set_goal=D2, goal_final=set_goal_peg"
            )

    model.bg = spa.BasalGanglia(actions=spa.Actions(*tuple(bg_actions)))
    model.thal = spa.Thalamus(model.bg)

    # somehow connect buffer inputs to the compare networks?
    # Can I use cortical actions to accomplish this?

    #ipdb.set_trace()
    nengo.Connection(hanoi_node.goal_out, model.goal.state.input, synapse=None)
    nengo.Connection(hanoi_node.focus_out, model.focus.state.input, synapse=None)
    nengo.Connection(hanoi_node.goal_peg_out, model.goal_peg.state.input, synapse=None)
    nengo.Connection(hanoi_node.focus_peg, model.focus_peg.state.input, synapse=None)
    nengo.Connection(hanoi_node.target_peg, model.target_peg.state.input, synapse=None)
    nengo.Connection(hanoi_node.goal_final, model.goal_final.state.input, synapse=None)
    nengo.Connection(hanoi_node.largest, model.largest.state.input, synapse=None)
        
        
    nengo.Connection(model.set_focus.state.output, hanoi_node.focus_in, synapse=None)
    nengo.Connection(model.set_goal.state.output, hanoi_node.goal_in, synapse=None)
    nengo.Connection(model.set_goal_peg.state.output, hanoi_node.goal_peg, synapse=None)
    nengo.Connection(model.move_disk.state.output, hanoi_node.move, synapse=None)
    nengo.Connection(model.move_peg.state.output, hanoi_node.move_peg, synapse=None)

# Questions:
# On the poster, there's a bunch of different dimensions. How are those set?
# Is there a way to just subtely create a new component in nengo_gui? I know you can plug in arbitrary HTML, but does that mean it will trigger on resize and all those other fancy things that a normal component does?

# Aside:
# How the hell would this map onto Spaun?
# Who figured out these rules and how did they do it?
# How stupid would it be for the Thalamus to highlight which connections it's activating?
# How does Spaun deal with a bunch of different dimensions?