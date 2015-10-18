from Neuron import InputNeuron, RandomNeuron, Neuron


class Readiness:
    NOT_READY = 0
    READY = 1
    CALCULATED = 2


class _AbstractLayer():
    def __init__(self):
        # list of neurons of this layer
        self.neurons = []
        # list of input neurons
        self.input = []
        # list of input values, which used to calculate
        self.input_values = []
        # list of layers, which connected after this
        self.listeners = []

        self.ready_to_calculate = Readiness.NOT_READY

    def __getitem__(self, i):
        return self.neurons[i]

    def __len__(self):
        return len(self.neurons)

    def get_output_values(self):
        return [n.out for n in self]

    def calculate(self, x=None):
        if x is None:
            self.input_values = [n.out for n in self.input]
        else:
            self.input_values = x
        self._notify_listeners()

    def _notify_listeners(self):
        self.ready_to_calculate = Readiness.CALCULATED
        for listener in self.listeners:
            listener.ready_to_calculate = Readiness.READY

    def reset_state(self):
        self.ready_to_calculate = Readiness.NOT_READY

    def commit_teach(self):
        for neuron in self:
            neuron.commit_teach()


class InputLayer(_AbstractLayer):
    """
    Input layer with connection ONE to ONE. using just for providing values to the next layers
    """
    def __init__(self, size):
        _AbstractLayer.__init__(self)
        self.neurons = [InputNeuron() for _ in range(size)]
        self.input_values = [0] * len(self)

    def calculate(self, x=None):
        self._notify_listeners()
        if x is not None:
            self.input_values = x
        return [self[i].calculate(self.input_values[i]) for i in range(len(self))]

    def reset_state(self):
        _AbstractLayer.reset_state(self)
        self.ready_to_calculate = Readiness.READY


class RandomLayer(InputLayer):
    """
    Layer with connection ONE to ONE
    it adds some random value (-random_value ; +random_value) to output value of the previous layer
    """
    def __init__(self, size, input, random_value):
        _AbstractLayer.__init__(self)
        self.input = input
        self.neurons = [RandomNeuron(random_value) for _ in range(size)]

    def calculate(self, x=None):
        _AbstractLayer.calculate(self, x)
        return [self[i].calculate(self.input_values[i]) for i in range(len(self))]


class Layer(_AbstractLayer):
    """
    Layer with connection ALL_TO_ALL
    """
    def __init__(self, size, input):
        _AbstractLayer.__init__(self)
        self.input = input
        self.neurons = [Neuron(len(self.input)) for _ in range(size)]

    def add_input(self, input):
        self.input = self.input + input
        for neuron in self.neurons:
            neuron.add_synapse(len(input))

    def calculate(self, x=None):
        _AbstractLayer.calculate(self, x)
        return [neuron.calculate(self.input_values) for neuron in self.neurons]

    def teach_output_layer_by_sample(self, learn_rate, sample_out):
        outs = [neuron.out for neuron in self]
        for i in range(len(self)):
            self[i].dEdNET = (outs[i] - sample_out[i]) * (1 - outs[i]**2)
            self[i].dw = [-learn_rate * self[i].dEdNET * inp_value for inp_value in self.input_values]
            self[i].dw0 = learn_rate * self[i].dEdNET

    # function for backpropagation teach algorithm
    def _get_dEdOUT(self, target_neuron):
        neuron_index = self.input.index(target_neuron)
        return sum((neuron.w[neuron_index] * neuron.dEdNET for neuron in self))

    def teach_middle_layer(self, learn_rate):
        for ni in range(len(self)):
            neuron = self[ni]

            dEdOUT = sum(( \
                next_layer._get_dEdOUT(neuron) for next_layer in self.listeners if isinstance(next_layer, Layer) \
                ))
            neuron.dEdNET = (1 - neuron.out**2) * dEdOUT

            neuron.dw = [-learn_rate * neuron.dEdNET * inp_value for inp_value in self.input_values]
            neuron.dw0 = learn_rate * neuron.dEdNET


class ContextLayer(_AbstractLayer):
    def __init__(self, size, input):
        _AbstractLayer.__init__(self)
        self.input = input
        self.neurons = [InputNeuron() for _ in range(size)]
        self.input_values = [0] * len(self)
        # self._queue = [[0]*size]*delay
        # self._delay = delay

    def calculate(self, x=None):
        _AbstractLayer.calculate(self, x)
        # self._queue.insert(0,self.input_values)
        # new_out = self._queue.pop()
        for i in range(len(self)):
            self[i].out = self.input_values[i]

    def clean(self):
        for i in range(len(self)):
            self[i].out = 0