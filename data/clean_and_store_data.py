import pandas as pd
import numpy as np
import sqlite3


def map_measure_id_to_description_and_unit(df):
    columns = ['Measure ID', 'Measure Description', 'Unit of Measure']
    data = [
        ['COMP_HIP_KNEE', 'Hip/knee replacement complications', 'Percent (%)'],
        ['Hybrid_HWM',	'Hospital-Wide Mortality', 'Percent (%)'],
        ['MORT_30_AMI',	'Heart Attack death rate', 'Percent (%)'],
        ['MORT_30_CABG', 'CABG death rate', 'Percent (%)'],
        ['MORT_30_COPD', 'COPD death rate', 'Percent (%)'],
        ['MORT_30_HF',	 'Heart Failure death rate', 'Percent (%)'],
        ['MORT_30_PN', 'Pneumonia death rate', 'Percent (%)'],
        ['MORT_30_STK',	'Stroke death rate', 'Percent (%)'],
        ['PSI_03', 'Pressure ulcer rate', 'Percent (%)'],
        ['PSI_3_ULCER', 'Pressure ulcer rate', 'Percent (%)'],
        ['PSI_04', 'Surgical inpatients with serious complications', 'Deaths/1000'],
        ['PSI_4_SURG_COMP', 'Surgical inpatients with serious complications', 'Deaths/1000'],
        ['PSI_06', 'Iatrogenic pneumothorax rate', 'Percent (%)'],
        ['PSI_6_IAT_PTX', 'Iatrogenic pneumothorax rate', 'Percent (%)'],
        ['PSI_08', 'In-hospital fall-associated fracture rate', 'Percent (%)'],
        ['PSI_8_POST_HIP', 'In-hospital fall-associated fracture rate', 'Percent (%)'],
        ['PSI_09', 'Postop. hemorrhage/hematoma rate', 'Percent (%)'],
        ['PSI_9_POST_HEM', 'Postop. hemorrhage/hematoma rate', 'Percent (%)'],
        ['PSI_10', 'Postop. acute kidney injury requiring dialysis rate', 'Percent (%)'],
        ['PSI_10_POST_KIDNEY',	'Postop. acute kidney injury requiring dialysis rate', 'Percent (%)'],
        ['PSI_11', 'Postop. respiratory failure rate', 'Percent (%)'],
        ['PSI_11_POST_RESP', 'Postop. respiratory failure rate', 'Percent (%)'],
        ['PSI_12', 'Periop. pulmonary embolism/deep vein thrombosis rate', 'Percent (%)'],
        ['PSI_12_POSTOP_PULMEMB_DVT', 'Periop. pulmonary embolism/deep vein thrombosis rate', 'Percent (%)'],
        ['PSI_13', 'Postop. sepsis rate', 'Percent (%)'],
        ['PSI_13_POST_SEPSIS', 'Postop. sepsis rate', 'Percent (%)'],
        ['PSI_14', 'Postop. wound dehiscence rate', 'Percent (%)'],
        ['PSI_14_POSTOP_DEHIS', 'Postop. wound dehiscence rate', 'Percent (%)'],
        ['PSI_15', 'Abdominopelvic accidental puncture/laceration rate', 'Percent (%)'],
        ['PSI_15_ACC_LAC', 'Abdominopelvic accidental puncture/laceration rate', 'Percent (%)'],
        ['PSI_90', 'Patient safety and adverse events composite', 'Percent (%)'],
        ['PSI_90_SAFETY', 'Patient safety and adverse events composite', 'Percent (%)']
    ]
    mid_desc_unit = pd.DataFrame(columns=columns, data=data)
    df = df.merge(mid_desc_unit, on=['Measure ID'], how='left')
    return df


def MDY_to_YMD(val):
    month = val.split('/')[0]
    day = val.split('/')[1]
    year = val.split('/')[2]
    ymd = f"{year}/{month}/{day}"
    return ymd


def switch_date_columns_to_YMD(df):
    df['Start Date'] = df['Start Date'].apply(MDY_to_YMD)
    df['End Date'] = df['End Date'].apply(MDY_to_YMD)
    return df


def data_extraction(filepaths):
    df_list = []
    for fp in filepaths:
        df = pd.read_csv(fp)
        df_list.append(df)

    # column names are consistent across files
    combined = pd.concat(df_list)
    return combined


def data_cleaning(df):
    # replace "Not Avalailable" with np.nan
    df = df.replace("Not Available", np.nan)

    # drop duplicate rows
    df = df.drop_duplicates()
    return df


if __name__ == '__main__':
    # complications and death - national file paths
    filepaths = [
        '2019/Complications and Deaths - National.csv',
        '2020/qqw3-t4ie.csv',
        '2021/Complications_and_Deaths-National.csv',
        '2022/Complications_and_Deaths-National.csv',
        '2023/Complications_and_Deaths-National.csv',
        '2024/Complications_and_Deaths-National.csv',
        '2025/Complications_and_Deaths-National.csv',
        '2026/Complications_and_Deaths-National.csv',
    ]


    # ETL pipeline (Extract-Transform-Load)
    # extraction 
    df = data_extraction(filepaths)  


    # cleaning 
    df = data_cleaning(df) 


    # feature engineering
    df = map_measure_id_to_description_and_unit(df)
    df = switch_date_columns_to_YMD(df)


    # load into SQLite database
    conn = sqlite3.connect('care_compare.db')

    column_types = {
        "Measure ID": "TEXT",
        "Measure Name": "TEXT",
        "National Rate": "REAL",
        "Number of Hospitals Worse": "INTEGER",
        "Number of Hospitals Same": "INTEGER",
        "Number of Hospitals Better": "INTEGER",
        "Number of Hospitals Too Few": "INTEGER",
        "Footnote": "TEXT",
        "Start Date": "TEXT",
        "End Date": "TEXT",
        "Measure Description": "TEXT",
        "Unit of Measure": "TEXT",
    }

    # 4. Write to the database
    df.to_sql(
        name="complications_and_deaths_national",
        con=conn,
        if_exists="replace",  # Options: 'fail', 'replace', 'append'
        index=False,  
        dtype=column_types,  # Forces specific data types
    )
    conn.close()
        
    # verify schemaa
    conn = sqlite3.connect("care_compare.db")
    df_p = pd.read_sql_query("PRAGMA table_info(complications_and_deaths_national);", 
                             conn
    )
    print('\nSchema of table complications_and_deaths_national:') 
    print(df_p.to_string(index=False))
    conn.close()

    # write output csv to check
    conn = sqlite3.connect("care_compare.db")
    query = "SELECT * FROM complications_and_deaths_national"
    df = pd.read_sql_query(query, conn)
    print('\nEntire table queried and exported to check_db_values.csv')
    df.to_csv('check_db_values.csv', index=False)
    conn.close()
