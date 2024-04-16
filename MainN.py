import pandas as pd
import sys
import os
import subprocess
from openpyxl import Workbook
import concurrent.futures
import multiprocessing

#from MainFunctionsN import create_template_files, softmax
from MainFunctionsNN import create_template_files, softmax
def operation(file_name, season, dir_path, out_path, consolePath):
    print(f"running {season} {file_name}.")
    file_path = os.path.join(dir_path, file_name)
    file_out = f"{out_path}\\output {file_name}.txt" #Should not be in same directory as pcsp since it might interfere with the for loop
    if not os.path.isfile(file_out):
        # Create destination file if it does not exist
        open(file_out, 'w').close()
    command = [consolePath, '-pcsp',file_path, file_out]
    result = subprocess.check_output(command)
    print(result)

### Make sure to replace all directory paths with your own to avoid the trouble of debugging later
#Create probability for every season
def readfile(season):
    consolePath = 'C:\\Program Files (x86)\\Process Analysis Toolkit\\Process Analysis Toolkit 3.5.1\\PAT3.Console.exe'
    thisDirPath = 'C:\\Users\\admin\\Downloads\\Project\\'
    
    #df_match = pd.read_csv(f"test/epl_matches_{season}.csv") #FOR TESTING. Use the test folder for testing particular cases. Make sure to use the right season in the excel file.
    df_match = pd.read_csv(f"matches/epl_matches_{season}.csv")
    df_ratings = pd.read_csv(f"eplratings/epl_ratings_{season}.csv")
    df_pass = pd.read_excel(f"Passes.xlsx",sheet_name=str(season))
    
    template_file_3f = '3rowTemplateNNN.pcsp'
    template_file_4f_3rows = '4rowsTemplateNNN.pcsp'
    template_file_4f = '4rowsTemplateNNN.pcsp'
    template_file_5f = '5rowsTemplateNNN.pcsp'
    template_file_5f_3rows = '5rowsTemplateNNN.pcsp'
    template_file_5f_4rows = '5rowsTemplateNNN.pcsp'
    
    match_url_arr = []
    
    # Create the PAT files
    match_url_arr = create_template_files(df_match, df_ratings,season, template_file_3f,template_file_4f_3rows,template_file_4f,template_file_5f,template_file_5f_3rows,template_file_5f_4rows,  match_url_arr,df_pass)
    #End of creating the PAT files

    # Define the directory path with YOUR own
    dir_path = thisDirPath + 'pcspDir\\' + str(season) # Change your directory
    out_path = thisDirPath + 'output\\' + str(season) # Change your directory
    # Get a list of all files in the directory
    file_list = os.listdir(dir_path)

    # # Run PAT
    try:
        executor = concurrent.futures.ProcessPoolExecutor(8)
        futures = [executor.submit(operation, file_name, season, dir_path, out_path, consolePath) for file_name in file_list]
        concurrent.futures.wait(futures)
    except:
        print('error in running pat file')
    #End of run Pat
    
    # Start of create the new probabilities/season.csv
    home_prob = 0
    away_prob = 0
    softmaxlist = []
    awy_list=[]
    for ind, file_name in enumerate(os.listdir(out_path)):
        file_name = thisDirPath + 'output\\' + str(season) + '\\' + file_name # Change your directory
        print(f"Adding probabilities from {file_name}")
        if ind % 2 == 0:               
            with open(file_name, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
                get_prob = lines[3].split(']')[0].split('[')[1].split(',')
                home_prob = (float(get_prob[0]) + float(get_prob[1]))/2
        if ind % 2 == 1:
            with open(file_name, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
                get_prob = lines[3].split(']')[0].split('[')[1].split(',')
                away_prob = (float(get_prob[0]) + float(get_prob[1]))/2
                softmaxlist.append(str(softmax([home_prob,away_prob])[0]))
                awy_list.append(1.0 - float(str(softmax([home_prob,away_prob])[0])))                  # Calculate softmax and append data after both probabilities are read
         
    rows={
            'match_url': match_url_arr,
            'home_prob_softmax': softmaxlist,
            'away_prob_softmax': awy_list
            }
 
    dff = pd.DataFrame(rows)
    csv_path = os.path.join('new_probabilities', f"{season}.csv")
    dff.to_csv(csv_path, index=False)
    # save_path = os.path.join('new_probabilities',f"{season}.csv")
    # workbook.save(save_path)
 
    # End of creation

if __name__ == "__main__":
    # seasons = [20152016,20162017]
    # seasons = [20152016]
    #seasons = [20162017]
    # seasons = [20172018]
    # seasons = [20182019]
    # seasons = [20192020]
    # seasons = [20202021]
    seasons = [20162017,20172018,20182019,20192020,20202021]
    #seasons = [20202021]
    for season in seasons:
        readfile(season)    

    