import nengo
import nengo.spa as spa

from constants import *
from toh_node import toh_node_create
import ipdb

model = spa.SPA()

vocab = spa.Vocabulary(dimensions, randomize=False)
vocab.parse("NONE")

# From the paper
# ATTEND = focus

# Note, D0 is the smalles disk, D2+ is the largest
# Because in this model there is no memory, so it "has to rebuild it's plans every time"
# The whole process should take around 30 actions
# TODO: Set set_focus to none for the first 0.02 seconds with a pass-through-ish node
# TODO: Simulate all State objects directly and with one neuron

ens_conf = nengo.Config(nengo.Ensemble)
ens_conf[nengo.Ensemble].neuron_type = nengo.neurons.Direct()

conn_conf = nengo.Config(nengo.Connection)
conn_conf[nengo.Connection].synapse = None

with model:
    ## cortical states
    with ens_conf:
        model.goal = spa.State(dimensions, neurons_per_dimension=1)
        model.goal_peg = spa.State(dimensions, neurons_per_dimension=1)
        model.focus = spa.State(dimensions, neurons_per_dimension=1, feedback=1)
        model.focus_peg = spa.State(dimensions, neurons_per_dimension=1)
        model.target_peg = spa.State(dimensions, neurons_per_dimension=1)

        # constant states from the node
        model.largest = spa.State(dimensions, neurons_per_dimension=1)
        # gets changed based off of which disk is being considered
        model.goal_peg_final = spa.State(dimensions, neurons_per_dimension=1)

        # input to cortical states
        model.set_focus = spa.State(dimensions, neurons_per_dimension=1)
        model.set_goal = spa.State(dimensions, neurons_per_dimension=1)
        model.set_goal_peg = spa.State(dimensions, neurons_per_dimension=1)

        ## action states
        # what to move
        model.move_disk = spa.State(dimensions, neurons_per_dimension=1)
        # where to move it
        model.move_peg = spa.State(dimensions, neurons_per_dimension=1)

        model.goal_target_peg_comp = spa.Compare(dimensions, neurons_per_multiply=1)
        model.focus_goal_comp = spa.Compare(dimensions, neurons_per_multiply=1)
        model.focus_goal_peg_comp = spa.Compare(dimensions, neurons_per_multiply=1)
        model.target_focus_peg_comp = spa.Compare(dimensions, neurons_per_multiply=1)

    # Connect the inputs to the the compare networks
    model.cortical_actions = spa.Actions(
        "goal_target_peg_comp_A = goal_peg", "goal_target_peg_comp_B = target_peg",
        "focus_goal_comp_A = focus", "focus_goal_comp_B = goal",
        "focus_goal_peg_comp_A = focus_peg", "focus_goal_peg_comp_B = goal_peg",
        "target_focus_peg_comp_A = target_peg", "target_focus_peg_comp_B = focus_peg"
    )

    model.cortical = spa.Cortical(model.cortical_actions)

    # target_peg is temporary, goal is final except for goal disk which is current
    # D0 is the smallest disk
    hanoi_node = toh_node_create(disk_count, dimensions, vocab)
    bg_actions = spa.Actions(
        # If nothing is being focused on, focus on the largest
        start = "dot(focus, NONE) --> set_focus=largest, set_goal=largest, set_goal_peg=goal_peg_final",
        # If we're focused on D2 and D2 is our goal, but our goals and target don't match (we want to move it), focus on D1 instead
        look_not_done_1 = "( dot(focus, D2-D1-D0) + dot(goal, D2) - goal_target_peg_comp ) / (2**(1/2.0)) --> set_focus=D1",
        # If we're focused on D2 and D2 is our goal, but it's already at it's temporary resting place to keep it out of the way, focus on D1 instead and try to get it to the goal
        look_done_1 = "(dot(focus, D2-D1-D0) + dot(goal, D2) + goal_target_peg_comp)*0.7/(3**(1/2.0)) --> set_focus=D1, set_goal=D1, set_goal_peg=goal_peg_final",
        # If we're focused on D1 and D1 is our goal, but our goals and target don't match (we want to move it), focus on D0 instead
        look_not_done_2 = "(dot(focus, D1-D0) + dot(goal, D1) - goal_target_peg_comp)/(2**(1/2.0)) --> set_focus=D0",
        # If we're focused on D1 and D1 is our goal, but it's already where we want it, focus on D0 instead and try to get it to the goal
        look_done_2 = "(dot(focus, D1-D0) + dot(goal, D1) + goal_target_peg_comp)*0.7/(3**(1/2.0)) --> set_focus=D0, set_goal=D0, set_goal_peg=goal_peg_final",
        # When we've moved the smallest disk, go and look at the largest again
        special_D0 = "(dot(focus, D0) + goal_target_peg_comp)*0.7/(2**(1/2.0)) --> set_focus=NONE",
        # If D0 isn't in the right place, then move it. It's D0. It's the smallest. It can go anywhere.
        move_D0 = "(dot(focus, D0) + dot(goal, D0) - goal_target_peg_comp)*0.9/(3**(1/2.0)) --> set_focus=NONE, move_disk=D0, set_goal_peg=goal_peg_final",
        ## InTheWay1 and FindFree1
        # trying to move something, but smaller disk is on the target peg
        # WTF how are conflicts being represented in this rule?
        find_free_1 = "(-focus_goal_comp + focus_goal_peg_comp - target_focus_peg_comp)*1.3 --> set_goal=focus, set_goal_peg=C+B+A-focus_peg-target_peg",
        ## InTheWay2 and FindFree2
        find_free_2 = "(-focus_goal_comp - focus_goal_peg_comp + target_focus_peg_comp)*1.3 --> set_goal=focus, set_goal_peg=C+B+A-goal_peg-target_peg",
        # If we're focused smallest disk while trying to move our goal disk and we haven't found anything in the way, then move the goal disk
        # WTF is with all the negatives? CANNOT PARSE
        move_goal_1 = "dot(focus, D0) + dot(goal, -D0) - 2*target_focus_peg_comp - 2*goal_target_peg_comp - 2*focus_goal_peg_comp --> move_disk=goal, move_peg=target_peg",
        # If we're focused smallest disk while trying to move our goal disk and we haven't found anything in the way, then move the goal disk
        move_goal_2 = "(dot(focus, D1) + dot(goal, -D1) - target_focus_peg_comp - goal_target_peg_comp - focus_goal_peg_comp)*1.3 --> set_focus=D0"
        )

    if(disk_count > 3):
        print("appending actions");
        bg_actions.add(
            move_goal_3 = "(dot(focus, D2) + dot(goal, -D2) - target_focus_peg_comp - goal_target_peg_comp - focus_goal_peg_comp)*1.3 --> set_focus=D1",
            look_not_done_4 = "(dot(focus, D3-D2-D1-D0) + dot(goal, D3) - goal_target_peg_comp)/(2**(1/2.0)) --> set_focus=D2",
            look_done_4 = "(dot(focus, D3-D2-D1-D0) + dot(goal, D3) + goal_target_peg_comp)*0.7/(3**(1/2.0)) --> set_focus=D2, set_goal=D2, set_goal_peg=goal_peg_final"
            )

    model.bg = spa.BasalGanglia(actions=bg_actions)
    model.thal = spa.Thalamus(model.bg)

    # input to model output from node connections
    with conn_conf:
        nengo.Connection(hanoi_node.vis.goal_out, model.goal.input)
        nengo.Connection(hanoi_node.focus_out, model.focus.input)
        nengo.Connection(hanoi_node.goal_peg_out, model.goal_peg.input)
        nengo.Connection(hanoi_node.vis.focus_peg, model.focus_peg.input)
        nengo.Connection(hanoi_node.target_peg, model.target_peg.input)
        nengo.Connection(hanoi_node.vis.goal_peg_final, model.goal_peg_final.input)
        nengo.Connection(hanoi_node.largest, model.largest.input)

        # output from model input to node connections
        nengo.Connection(model.set_focus.output, hanoi_node.focus_in)
        nengo.Connection(model.set_goal.output, hanoi_node.goal_in)
        nengo.Connection(model.set_goal_peg.output, hanoi_node.goal_peg)
        nengo.Connection(model.move_disk.output, hanoi_node.motor.move)
        nengo.Connection(model.move_peg.output, hanoi_node.motor.move_peg)

    ##### Node for visualization #####
    def viz_func(t, x):
        focus_peg = [0]*3
        if x[0] < 3:
            focus_peg[int(x[0])] = 255
        #print("focus_peg: %s" %focus_peg)
        goal_disc = [0]*3
        if x[1] < 3:
            goal_disc[int(x[1])] = 255
        #print("goal_disc: %s" %goal_disc)
        focus_disc = [0]*3
        if x[1] < 3:
            focus_disc[int(x[2])] = 255
        #print("focus_disc: %s" %focus_disc)

        location = x[3:6]
        viz_func._nengo_html_ = '''
        <svg width="400" height="110">
          <rect x="50" y="0" width="10" height="600" style="fill:rgb(0,0,%i);" />
          <rect x="150" y="0" width="10" height="600" style="fill:rgb(0,0,%i);" />
          <rect x="250" y="0" width="10" height="600" style="fill:rgb(0,0,%i);" />

          <rect x="%i" y="40" width="40" height="20" style="fill:rgb(%i,0,%i);" />
          <rect x="%i" y="70" width="70" height="15" style="fill:rgb(%i,0,%i);" />
          <rect x="%i" y="100" width="100" height="10" style="fill:rgb(%i,0,%i);" />
        </svg>
        ''' %(focus_peg[0], focus_peg[1], focus_peg[2], (35+location[0]*100), focus_disc[0], goal_disc[0], (15+location[1]*100), focus_disc[1], goal_disc[1], (location[2]*100), focus_disc[2], goal_disc[2])

    viz_node = nengo.Node(viz_func, size_in=7)
    nengo.Connection(hanoi_node.focus_viz, viz_node[0])
    nengo.Connection(hanoi_node.goal_viz, viz_node[1])
    nengo.Connection(hanoi_node.peg_viz, viz_node[2])
    nengo.Connection(hanoi_node.pos_viz, viz_node[3:6])

# Aside:
# How the hell would this map onto Spaun?
# Who figured out these rules and how did they do it?
# How does Spaun deal with a bunch of different dimensions?