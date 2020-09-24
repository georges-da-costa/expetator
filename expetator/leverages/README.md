# Documentation for leverages

Classical skeleton

    class Leverage:
        'Skeleton for leverages'
        
        def __init__(self, leverage_argument):
            'Mainly used to store arguments'
            pass
            
        def build(self, executor):
            'Used to build the binary or obtain information on the plateform'
            pass
            
        def available_states(self):
            'Returns the list of avaiable states'
            return [None]
            
        def start(self, state):
            'Use the leverage with the state in argument'
            pass
            
        def stop(self,output_file=None):
            'Stops the leverage and, if needed, write info in an output file'
            pass
            
        def get_state(self):
            'Retuns the current state in internal format'
            return None
            
        def state_to_str(self):
            'Returns the current state in string format'
            return 'None'
        
        def get_labels(self):
            'Retuns the string associated with the states'
            return 'Leverage'
