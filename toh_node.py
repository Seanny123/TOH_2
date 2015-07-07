import constants
import numpy as np

def toh_node_create(name, disk_count, D, vocab):
    with nengo.Network(label="Tower of Hanoi node") as toh_n:
        toh = TowerOfHanoi(name, disk_count, D, vocab)

        # input nodes
        def focus_in_func(t, x, toh=toh):
            # I am so confused with casting and vectorization here
            disks = [np.dot(x, v) for v in toh.disks] # this is repeated a lot
            toh.focus = disks.index(np.max(disks))
        focus_in = nengo.Node(focus_in_func)

        goal_peg = nengo.Node(lambda t, x: toh.goal_peg_data = [np.dot(x, v) for v in toh.pegs])

       def goal_in_func(t, x, toh=toh):
            disks = [np.dot(x, v) for v in toh.disks]
            pegs = toh.goal_peg_data
            if np.max(pegs)>threshold and np.max(disks)>threshold:
                toh.goal = disks.index(np.max(disks))
                # repeated twice, uncertain of function
                toh.target_peg = 'ABC'[pegs.index(np.max(pegs))]
        goal_in = nengo.Node(goal_in_func)

        move_peg = nengo.Node(lambda t, x: toh.move_peg_data=[np.dot(x, v) for v in toh.pegs])

        def move_func(t, x, toh=toh):
            disks = [np.dot(x, v) for v in toh.disks]
            pegs = toh.move_peg_data
            if np.max(pegs)>threshold and np.max(disks)>threshold:
                disk = disks.index(np.max(disks))
                peg = 'ABC'[pegs.index(np.max(pegs))]
                if peg != toh.peg(disk):
                    if toh.can_move(disk,peg):
                        toh.move(disk,peg)
                        print 'Moving D%d to %s'%(disk,peg)
                    else:    
                        print 'Cannot move D%d to %s'%(disk,peg)
        move = nengo.Node(move_func)


        # output nodes # might need to be made lambdas
        largest = nengo.Node(toh.disks[toh.largest].v)
        goal_out = nengo.Node(toh.disks[toh.goal].v)
        focus_out = nengo.Node(toh.disks[toh.focus].v)
        goal_peg_out = nengo.Node(vocab.parse(toh.peg(toh.goal)).v)
        target_peg = nengo.Node(vocab.parse(toh.target_peg).v)
        goal_final = nengo.Node(vocab.parse(toh.target[toh.goal]).v)
        def focus_peg_func(toh=toh):
            if toh.focus>=disk_count:
                return toh.zero
            return vocab.parse(toh.peg(toh.focus)).v
        focus_peg = nengo.Node(focus_peg_func(toh))


class TowerOfHanoi(object):
    def __init__(self, name, disk_count, D, vocab):
        self.pstc = 0.01
        self.pegs = [vocab.parse('A'),vocab.parse('B'),vocab.parse('C')]
        # why would you need to add the NONE vector?
        self.disks = [vocab.parse('D%d'%i) for i in range(disk_count)]+[vocab.parse('NONE')]
        self.reset()
        self.zero = [0]*D
        self.vocab = vocab

    def reset(self,randomize=True):
        self.location = ['A']*disk_count
        self.target = ['C']*disk_count
        #self.location=['A','C','C']
        self.focus = len(self.disks)-1
        self.largest = disk_count-1
        self.goal = 2
        self.target_peg = 'C'
        self.move_peg_data = [0]*disk_count
        self.goal_peg_data = [0]*disk_count

    def move(self,disk,peg):
        assert self.can_move(disk,peg)
        self.location[disk] = peg
        
    def peg(self,disk):
        return self.location[disk]    
        
    def can_move(self,disk,peg):
        assert peg in 'ABC'
        pegs = [self.peg(disk),peg]
        for i in range(disk):
            if self.peg(i) in pegs: return False
        return True