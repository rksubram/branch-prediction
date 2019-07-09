import bz2
from numpy import uint32,uint8,fromstring
import numpy as np
import os
import bz2
Pred_types = ["Static","G-Share","Tournament", "Perceptron"]
Error_Perception="Perceptron Bits are 0 when we have a perceptron predictor"
Error_Trace="Invalid Trace directory"
States = ["WNT","WT","SNT","ST"]

def apply_mask(bits, mask_input):
    """
    Apply a Mask with the specified number of bits to the input
    """
    mask_value = (1<<bits)-1
    if mask_value >= mask_input:
        print("There are too many bits to mask")
        return -1
    else:
        return mask_input & mask_value

def process_streams(traces):
    """
    Store all stream files
    """
    trace_file=[]
    for files in os.listdir(traces):
        trace_file.append(os.path.join(os.getcwd(),traces,files))
    return trace_file

def str2hex(hex_str):
    hex_int = int(hex_str, 16)
    new_int = hex_int + 0x200
    return hex(new_int)


class Branch_Predictor:
    """
    Initializes a predictor with global, branch and perceptron history bits for usage 
    """
    def __init__(self, predictor_type, global_history_bits, branch_history_bits, perceptron_bits):
         """
         Initalizing BP parameter variables
         """
         self.ghb = global_history_bits
         self.bhb = branch_history_bits
         self.pb  = perceptron_bits
    
    def check_predictor_type():
        """
        Check if we have required predictor bits for the predictor type
        """
        if self.pb!=0 and predictor_type==Pred_types[3]:
            raise ValueError(Error_Perceptron)
        elif self.bhb!=0:
            print("")
        else:
            print("GShare")

class Statistics:
    """
    Track Branch Prediction Statistics
    """
    def __init__(self,stream_list,types):
        self.branches = 0
        self.pc = 0
        self.outcome = 0
        self.file_number=0
        self.stream_list = stream_list
        self.type = types
    
    def make_prediction(self,pc_val,outcome_val):
        if self.type[0]==Pred_types[0]:
            if self.stype[t]=='NT':
                return [0]* len(outcome_val)
            elif self.stype[t]=='T':
                return [1] * len(outcome_val)
            else:
                raise ValueError("Invalid Type")
        else:
            print("NOT ACCRURAYE")

    def update_stats(self):
        self.branches+=1
        store_accuracy=dict()
        for files in self.stream_list:
            pc_list=[]
            outcome_list=[]
            for line in bz2.BZ2File(files,"r"):
                pc = str(line.split()[0]).replace("'","").replace("b","")
                outcome = str(line.split()[1]).replace("'","").replace("b","")
                self.pc =str2hex(pc)
                self.outcome=int(outcome,16)
                self.branches+=1
                pc_list.append(self.pc)
                outcome_list.append(self.outcome)
            prediction=make_prediction(pc_list,outcome_list)
            store_accuracy[files]=calculate_accuracy(prediction,outcome_list)
            self.file_number+=1
        assert self.file_number==len(self.stream_list), "Some files could not be processed"
        return store_accuracy

    def calculate_accuracy(a,b):
        assert len(a)==len(b), "Outcome and your predictions are of different lengths; possible overflow"
        mispred = 0
        for index in range(len(a)):
            if a[index]!=b[index]:
                mispred+=1
        return float(mispred/len(a))


    """
      // Make a prediction and compare with actual outcome
      uint8_t prediction = make_prediction(pc);
      if (prediction != outcome) {
        mispredictions++;
      }
      if (verbose != 0) {
        printf ("%d\n", prediction);
      }
    """


if __name__ == "__main__":
    
    # parse user arguments
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p_type', '--type', required=True, type=str, default='G-Share', help="Predictor Type")
    parser.add_argument('-t', '--traces', required=False, type=str, default='traces', help="Trace directory")
    parser.add_argument('-s_type', '--static_type', required=False, type=str, default='NT', help="Trace directory")
    args = parser.parse_args()
   
    #Assert commands to check user arguments
    assert args.type in Pred_types,"Predictor type is not found"
    assert args.type == Pred_types[0] and args.static_type!=None, "Prediction is Static but not specified T/NT"
    #Intialize branch predictor
    Branch_Predictor(args.type,4,5,3)
    
    if process_streams(args.traces):
        streams=process_streams(args.traces)
    else:
        raise ValueError(Error_Trace)
    
    Static_pred = Statistics(streams,[args.type,args.static_type])
    print(Static_pred.update_stats())
