import struct
import collections

import nengo
import numpy as np

from nengo_gui.components.component import Component


class Value(Component):
    """The server-side system for a Value plot."""

    # the parameters to be stored in the .cfg file
    config_defaults = dict(max_value=1,
                         min_value=-1, 
                         **Component.config_defaults)

    def __init__(self, obj):
        super(Value, self).__init__()
        # the object whose decoded value should be displayed
        self.obj = obj

        # the pending data to be sent to the client
        self.data = collections.deque()

        # the number of data values to send
        self.n_lines = int(obj.size_out)

        # the binary data format to sent in.  In this case, it is a list of
        # floats, with the first float being the time stamp and the rest
        # being the vector values, one per dimension.
        self.struct = struct.Struct('<%df' % (1 + self.n_lines))

    def attach(self, page, config, uid):
        super(Value, self).attach(page, config, uid)
        # use the label of the object being plotted as our label
        self.label = "Tower of Hanoi"

    def add_nengo_objects(self, page):
        # create a Node and a Connection so the Node will be given the
        # data we want to show while the model is running.
        with page.model:
            self.node = nengo.Node(self.gather_data,
                                   size_in=self.obj.size_out)
            self.conn = nengo.Connection(self.obj, self.node, synapse=0.01)

    def remove_nengo_objects(self, page):
        # undo the changes made by add_nengo_objects
        page.model.connections.remove(self.conn)
        page.model.nodes.remove(self.node)

    def gather_data(self, t, x):
        # This is the Node function for the Node created in add_nengo_objects
        # It will be called by the running model, and will store the data
        # that should be sent to the client
        self.data.append(self.struct.pack(t, *x))

    def update_client(self, client):
        # while there is data that should be sent to the client
        while len(self.data) > 0:
            item = self.data.popleft()
            # send the data to the client
            client.write(item, binary=True)

    # THE FUCK? I guess we need that pull request more than we thought?
    def javascript(self):
        # generate the javascript that will create the client-side object
        info = dict(uid=id(self), label=self.label,
                    n_lines=self.n_lines, synapse=0)
        json = self.javascript_config(info)
        return 'new Nengo.Value(main, sim, %s);' % json

    def code_python_args(self, uids):
        # generate the list of strings for the .cfg file to save this Component
        # (this is the text that would be passed in to the constructor)
        return [uids[self.obj]]
