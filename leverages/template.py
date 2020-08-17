class Template:
    'Template for leverages'
    def __init__(self):
        'Initializes the internal variables using parameters'
        pass

    def build(self, executor):
        'Builds the executable and acquire data on the system'
        self.executor = executor
        pass
    
    def available_states(self):
        'Returns all the possible states as a list'
        return [None]

    def start(self, state):
        'Sets the right state on all hosts'
        pass
    
    def stop(self, output_file=None):
        'Reverts to the standard state on all nodes and saves some info in the right directory'
            
    def get_state(self):
        'Returns the current state'
        return None

    def state_to_str(self):
        'Converts a state in a string'
        return 'None'

    def get_labels(self):
        'Returns the labels for the leverage'
        return (Template)
