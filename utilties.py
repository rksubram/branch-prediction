#import packages
import bz2 #used to unzip a bz2 encrypted file
from numpy import uint32,uint8,fromstring #import datatypes
import numpy as np #numpy
import os #os for file paths
import argparse # parse user arguments
import pandas #import pandas for pretty output rendering

#possible configurations
Pred_types = ["Static","G-Share","Tournament", "Perceptron"]
Error_Perception="Perceptron Bits are 0 when we have a perceptron predictor"
Error_Trace="Invalid Trace directory"
States = ["SNT","WNT","WT","ST"]
Static_States=["NT","T"]


#utility functions
def apply_mask(bits, mask_input,flag):
    """
    Apply a Mask with the specified number of bits to the input
    """
    mask_value = (1<<bits)-1
    if mask_value >= mask_input and flag==0:
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
    """
    Converts a string to a hexadecimal output
    """
    hex_int = int(hex_str, 16)
    new_int = hex_int + 0x200
    return hex_int

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
         self.predictor_type=predictor_type

    def check_predictor_type(self):
        """
        Check if we have required predictor bits for the predictor type
        """
        if self.pb!=0 and self.predictor_type==Pred_types[3]:
            raise ValueError(Error_Perceptron) #No perceptron_bits but perceptron predictor specified

        #TODO Other corner cases can be removed using smart checkers

    def initialize_registers(self,default_val):
        """
        Initialize the value of different registers based on predictor_type
        """
        if self.predictor_type==Pred_types[0]:
            pass
        elif self.predictor_type==Pred_types[1]:
            global_history = 0
            branch_history_size = (1<<self.ghb)
            GHT=[]
            for i in range(branch_history_size):
                GHT.append(States.index(default_val))
            return GHT,global_history

class Statistics:
    """
    Track Branch Prediction Statistics
    """
    def __init__(self,stream_list,types,b_predor):
            self.pc = 0 #initialize pc
            self.outcome = 0 #outcome= T/NT
            self.file_number=0 #the file number which is being analyzed
            self.stream_list = stream_list #list of stream files
            self.type = types #type of predictor
            self.store_accuracy =dict() #accuracy
            self.b_predor=b_predor #predictor class
            self.default_stype='NT' #default static prediction
            self.default_dtype='WNT' #default prediction
            if self.type==Pred_types[1]:
                self.GHT,self.global_history=self.b_predor.initialize_registers(self.default_dtype)


    def train_predictor(self,outcome,index):
        if self.type==Pred_types[0]:
            pass #static_type
        elif self.type==Pred_types[1]:
            if outcome==0 and self.GHT[index]!=0:
                self.GHT[index]-=1
            elif outcome==1 and self.GHT[index]!=3:
                self.GHT[index]+=1
            self.global_history= outcome | (self.global_history<<1)


    def make_prediction(self, pc_val=None, outcome_val=None):
        if self.type==Pred_types[0]:
            if self.default_stype in Static_States:
                return self.outcome!=Static_States.index(self.default_stype)
            else:
                self.b_predor.initialize_registers(self.default_stype)
                raise ValueError("Invalid Type")
        elif self.type==Pred_types[1]:
            #print("pc_val:",pc_val)
            #print("outcome_val:",outcome_val)
            if self.default_dtype not in States:
                raise ValueError("Invalid Type")
            else:
                #if outcome_val==1:
                #    print(self.GHT,self.global_history)
                mask_gval=apply_mask(b.ghb,self.global_history,1)
                mask_pcval=apply_mask(b.ghb,pc_val,1)
                index= mask_gval ^ mask_pcval
                #print(mask_gval,mask_pcval,index)
                prediction = self.GHT[index]
                return_val= ((prediction>=2)==outcome_val)
                self.train_predictor(outcome_val,index)
                return return_val
        else:
            print("NOT ACCURATE")

    def update_stats(self):
        if self.type in Pred_types:
            for files in self.stream_list:
                print("File:",files)
                pc_list=[]
                outcome_list=[]
                cnt=0
                prediction=0
                for line in bz2.BZ2File(files,"r"):
                    pc = str(line.split()[0]).replace("'","").replace("b","")
                    outcome = str(line.split()[1]).replace("'","").replace("b","")
                    self.pc =str2hex(pc)
                    self.outcome=int(outcome,16)
                    prediction+=self.make_prediction(self.pc,self.outcome)
                    cnt+=1
                print(str(round(100-float((prediction*100)/cnt),3))+str("%"))
                self.file_number+=1
                self.store_accuracy[files.split("/")[-1].split(".")[0]]=[str(round(100-float((prediction*100)/cnt),3))+str("%")]
            assert self.file_number==len(self.stream_list), "Some files could not be processed"

        return self.store_accuracy

    def calculate_accuracy(a,b):
        assert len(a)==len(b), "Outcome and your predictions are of different lengths; possible overflow"
        mispred = 0
        for index in range(len(a)):
            if a[index]!=b[index]:
                mispred+=1
        return float(mispred/len(a))


if __name__ == "__main__":

    #define input and default input arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p_type', '--type', required=True, type=str, help="Predictor Type")
    parser.add_argument('-t', '--traces', required=False, type=str, default='traces', help="Trace directory")
    args = parser.parse_args()

    assert args.type in Pred_types,"Predictor type is not found"

    b=Branch_Predictor(args.type,4,5,3)   #Intialize branch predictor
    b.check_predictor_type()

    if process_streams(args.traces): #there are traces defined
        streams=process_streams(args.traces)
        print(len(streams),"traces Identified:")
        for stream_i in streams:
            print("\t",stream_i.split("/")[-1].split(".")[0])
    else:
        raise ValueError(Error_Trace) #report no traces found



    Static_pred = Statistics(streams,args.type,b)
    print(pandas.DataFrame.from_dict(Static_pred.update_stats()))
