from constants import *
import numpy as np
import nengo

import ipdb

def get_similarity_array(x, thingys):
    return [np.dot(x, thing.v) for thing in thingys]

def toh_node_create(disk_count, D, vocab):
    with nengo.Network(label="Tower of Hanoi node") as toh_n:
        toh = TowerOfHanoi(disk_count, D, vocab)

        #### input nodes ####
        def focus_in_func(t, x):
            tmp_disks = get_similarity_array(x, toh.disks)
            toh.focus = tmp_disks.index(np.max(tmp_disks))

        toh_n.focus_in = nengo.Node(focus_in_func, size_in=D)


        def goal_peg_func(t, x):
            toh.goal_peg_data = get_similarity_array(x, toh.pegs)

        toh_n.goal_peg = nengo.Node(goal_peg_func, size_in=D)


        def goal_in_func(t, x):
            """Sets the goals for both the pegs and the disk"""
            disks = get_similarity_array(x, toh.disks)
            pegs = toh.goal_peg_data
            if np.max(pegs) > threshold and np.max(disks) > threshold:
                toh.goal = disks.index(np.max(disks))
                toh.target_peg = 'ABC'[pegs.index(np.max(pegs))]

        toh_n.goal_in = nengo.Node(goal_in_func, size_in=D)

        toh_n.motor = nengo.Network(label="Motor Cortex")

        with toh_n.motor as motor:
            def move_peg_func(t, x):
                toh.move_peg_data = get_similarity_array(x, toh.pegs)

            motor.move_peg = nengo.Node(move_peg_func, size_in=D)


            def move_func(t, x):
                disks = get_similarity_array(x, toh.disks)
                pegs = toh.move_peg_data
                disk = disks.index(np.max(disks))
                if(np.max(pegs) > threshold and np.max(disks) > threshold):


                    peg = 'ABC'[pegs.index(np.max(pegs))]
                    if peg != toh.peg(disk):
                        if toh.can_move(disk,peg):
                            toh.move(disk,peg)
                            print 'Moving D%d to %s'%(disk,peg)
                        else:    
                            print 'Cannot move D%d to %s'%(disk,peg)

            motor.move = nengo.Node(move_func, size_in=D)


        #### output nodes ####
        toh_n.largest = nengo.Node(lambda t: toh.disks[toh.largest].v)
        toh_n.focus_out = nengo.Node(lambda t: toh.disks[toh.focus].v)
        # HOW THE HELL IS THE GOAL EVEN BEING SET TO NONE
        toh_n.goal_peg_out = nengo.Node(lambda t: vocab.parse(toh.peg(toh.goal)).v)

        toh_n.target_peg = nengo.Node(lambda t: vocab.parse(toh.target_peg).v)


        # This just says where all the disks are supposed to end up. In this case, at the last peg
        # Put this into the visual cortex, then check the rules are flowing correctly
        toh_n.vis = nengo.Network(label="Visual Cortex")

        with toh_n.vis as vis:
            vis.goal_out = nengo.Node(lambda t: toh.disks[toh.goal].v)
            vis.goal_peg_final = nengo.Node(lambda t: vocab.parse(toh.target[toh.goal]).v)

            def focus_peg_func(t):
                if toh.focus >= disk_count:
                    return toh.zero
                return vocab.parse(toh.peg(toh.focus)).v

            vis.focus_peg = nengo.Node(focus_peg_func(toh))

        #### Visualization nodes ####

        toh_n.focus_viz = nengo.Node(lambda t: toh.focus, size_out=1, label="focus disk")
        toh_n.goal_viz = nengo.Node(lambda t: toh.goal, size_out=1, label="goal disk")
        toh_n.peg_viz = nengo.Node(lambda t: toh.location_dict[toh.target_peg], size_out=1, label="goal peg")


        def pos_viz_func(t):
            return_val = [0]*3
            for r_i, loc in enumerate(toh.location):
                return_val[r_i] = toh.location_dict[loc]
            return return_val

        toh_n.pos_viz = nengo.Node(pos_viz_func, size_out=3)



    return toh_n


class TowerOfHanoi(object):
    def __init__(self, disk_count, D, vocab):
        self.pstc = 0.01
        # make some matrices as well for faster dot-producting?
        self.pegs = [vocab.parse('A'), vocab.parse('B'), vocab.parse('C')]
        self.disks = [vocab.parse('D%d'%i) for i in range(disk_count)]+[vocab.parse('NONE')]
        self.reset()
        self.location_dict = {'A':0, 'B':1, 'C':2}
        self.zero = [0]*D
        self.vocab = vocab

    def reset(self,randomize=True):
        self.location = ['A']*disk_count
        #self.location=['A','C','C']
        self.focus = len(self.disks) - 1
        self.largest = disk_count - 1
        self.goal = 2
        self.target_peg = 'C'
        self.move_peg_data = [0] * disk_count
        self.goal_peg_data = [0] * disk_count
        # constant
        self.target = ['C'] * disk_count

    def move(self, disk, peg):
        assert self.can_move(disk,peg)
        self.location[disk] = peg
        
    def peg(self, disk):
        try:
            return self.location[disk]
        except IndexError:
            ipdb.set_trace()
        
    def can_move(self, disk, peg):
        assert peg in 'ABC'
        pegs = [self.peg(disk),peg]
        for i in range(disk):
            if self.peg(i) in pegs: return False
        return True

# focus peg is blue
# goal disc is blue
# focus disk is red
# when goal == focus, the disk is purple