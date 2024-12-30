import pandas as pd
from datetime import datetime
import pytz
import sys

#list of all ids
valid_ids = [3038769203, 3037002580, 3036699813, 3039008442, 3040541741, 3040557250, 3039505289, 3037858618, 3038829354, 3038354906, 3038955571, 3040779212, 3036807973, 3037444644, 3039190468, 3038882914, 3037993038, 3037099111, 3040874918, 3038175220, 3037677983, 3037322388, 3037982014, 3038328425, 3040483813, 3037712615, 3040599877, 3036486588, 3039290711, 3037799533, 3038279272, 3038474493, 3039014890, 3039286226, 3040831459, 3038320053, 3036689738, 3036730077, 3037984900, 3036601621, 3036751976, 3038975201, 3038885904, 3038892820, 3038818213, 3039183188, 3039019752, 3037842199, 3039405033, 3036651869, 3038358091, 3038102472, 3037718270, 3039315619, 3038630207, 3039426548, 3038086235, 3038933952, 3040500674, 3035638306, 3038276360, 3040089692, 3038806435, 3037016087, 3038958587, 3038865117, 3036714074, 3038795801, 3038990528, 3038500415, 3037795997, 3040171176, 3036545890, 3039421634, 3037309635, 3036974460, 3039380190, 3039126287, 3039339474, 3038166237, 3039984236, 3035693686]
#list of all labs
output_columns = [
        "Student ID", "SIS User ID", "SIS Login ID", "Section",
        "Light Sensor Schematic", "Light Sensor Layout",
        "USB Charger Components", "USB Charger Schematic",
        "USB Charger Layout", "Hands on: Soldering",
        "Hands on: USB Charger", "Hands on: Trinket"
]

def collect_ids(file_path):
    global valid_ids
    ids = []
    with open(file_path, 'r') as file:
        for line in file:
            words = line.split()
            for word in words:
                if word.startswith('30'):
                    ids.append(int(word))

    # Return the list of words starting with '30'
    valid_ids= ids
    return None

def validate_student_ids(student_id, valid_ids):
    return student_id in valid_ids

def process_csv(input_csv, output_csv, valid_ids):
    global output_columns

    # Initialize a new DataFrame for the output
    output_df = pd.DataFrame(columns=output_columns)

    try:
        df = pd.read_csv(input_csv)
    except pd.errors.EmptyDataError as e1:
        print("ERROR: Input file not a CSV - did you type in the right name?")
        sys.exit()
    except FileNotFoundError as e:
        print("ERROR: Input file doesn't exist - did you type in the right name?")
        sys.exit()
         
    #error file
    pst = pytz.timezone('US/Pacific')
    file = open('error.txt', 'w') 
    file.write("ERROR FILE\n\n") 

    invalid_ids = []  # List to store invalid IDs that are excluded

    # Loop through the input DataFrame and fill the output DataFrame
    for index, row in df.iterrows():
        #info
        student_id = row['Student ID Number']
        
        if not validate_student_ids(student_id, valid_ids):
            invalid_ids.append(student_id)  
            file.write(str(row))
            file.write('\n')
            continue  
        
        section = row['Section']
        sis_user_id = f"SIS{student_id}"
        sis_login_id = f"{row['Name (First Last)'].split()[0].lower()}{student_id}" 

        
        #scoring
        checked_off = row['Checked Off?']
        value = 5 if str(checked_off).lower() == "y" else 3 if str(checked_off).lower() == "p" else 0

        #if SID not already in dataframe, initialize
        if sis_user_id not in output_df["SIS User ID"].values:
            output_row = {
                    "Student ID": student_id,
                    "SIS User ID": sis_user_id,
                    "SIS Login ID": sis_login_id,
                    "Section": section,
                    "Light Sensor Schematic": 0,
                    "Light Sensor Layout": 0,
                    "USB Charger Components": 0,
                    "USB Charger Schematic": 0,
                    "USB Charger Layout": 0,
                    "Hands on: Soldering": 0,
                    "Hands on: USB Charger": 0,
                    "Hands on: Trinket": 0
                }
            output_row[(row["Lab"])] = value
            output_row_df = pd.DataFrame([output_row])
            output_df = pd.concat([output_df, output_row_df], ignore_index=True)
        #if SID already in dataframe, edit the corresponding lab score
        else:
            output_df.loc[output_df['SIS User ID'] == sis_user_id, (row["Lab"])] = value

    # Write the output DataFrame to a CSV
    output_df.to_csv(output_csv, index=False)
    print(f"Output saved to {output_csv}\n")
    
    # Flag the invalid IDs
    if invalid_ids:
        print(f"ERROR: # of invalid ids {len(invalid_ids)}")
    
    file.close()  


def main():
    #select input files
    if len(sys.argv) > 1:
        input_csv = sys.argv[1] + ".csv"  # Path to the input CSV
        output_csv = sys.argv[2] + ".csv"  # Path to the output CSV
    else:
        input_csv = "input_data.csv"
        output_csv = "output_data.csv"
    
    #select the function to be called - ids will collect all IDs within a txt file, else will default to generating output csv
    if '--ids' in sys.argv:
        collect_ids(input_csv)
    else:
        process_csv(input_csv, output_csv, valid_ids)

main()