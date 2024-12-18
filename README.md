# Google-Cloud-Data-Pipeline
## Let's discuss step by step process of how to implement the project.
## Create storage bucket
-	Open [Cloud Storage Bucket](https://console.cloud.google.com/storage/browser?project=term-project-418219&supportedpurview=project,organizationId,folder&prefix=&forceOnObjectsSortingFiltering=false&forceOnBucketsSortingFiltering=true) Click on Create
-	Give it any name of your choice, I used itjobs_1212 as my bucket name
-	In **Choose where to store your data** for Location type select **Region** then pick **us-central1 (Iowa)**, I selected us-central1 but for better performance you can select which ever region is located geographically closer to you.
-	You can leave the rest of the options in their default setting and click on create.

## Upload File into the Bucket
Once the bucket is created, you can open the bucket and select the **Upload Files** option and upload the itjobs.csv file. After the file is uploaded you can see it in the Bucket.

## Create Cloud composer:
[Cloud Composer](https://console.cloud.google.com/composer/environments?project=term-project-418219&supportedpurview=project,organizationId,folder&lastRefresh=1713039830116)
- When you go to this link it opens Cloud Composer, now click on Create and select “Composer2”.
- Give any name to your composer, I named it as itcomposer.
- Select the same location you previously selected while creating a bucket. I selected “us-central1”
- Leave rest of the options at their default setting and click on create.
- Your cloud composer will take around 20-25 minutes to be created.

## Create a cloud spanner table:
- Now go to Cloud Spanner and select **Create a Provisioned Instance** 
- Give an instance name, I have named my instance as 'itspanner'. Click on continue.
- Select “regional” and configuration as us-central1 (Iowa) and click on create.
- Once the instance is created, it gets opened and you will find an option 'Create Database', select it.
- Give the name of database, I have named by database as 'itdatabase12'.
- For 'Select database dialect' select ‘Google Standard SQL’.
- In Define your schema I have given the following DDL and clicked on create.

CREATE TABLE ittable12 (Year DATE,Total_IT_Job_Openings INT64,Web_Related_Jobs int64,Software_Development_Jobs int64,IT_Support_Jobs INT64,IT_Management_Jobs INT64,IT_Security_Jobs INT64,Hardware_Engineering_Jobs INT64,Impacting_Event string(30),Job_Loss_Percentage_Due_to_Event string(30),New_Emerging_IT_Roles string(30),prim int64,Total_IT_Job_Openings_Mean float64)primary key(prim);

- Once the table gets created go back to cloud composer.

Upload Python code file in Cloud composer
- Now open the respective created composer(itcomposer) by clicking on its name
- Then select DAGs folder and you will find an option to upload files, select it and upload the dfp.py python file.
dfp.py
- The dfp.py file first establishes a connection between the created bucket and cloud composer, at line 25 I gave the name of the bucket and in line 26 I gave the name of the csv file. This code loads data of the file into a dataframe.
- And then I performed certain transformations and preprocessing on the data.
- The datatype of 'Year' column is loaded as string so I converted it to datetime format.
- I have also converted the datatype of 'Impacting_Event' & 'Job_Loss_Percentage_Due_to_Event' to string.
- I have then calculated the mean of 'Total_IT_Job_Openings' on yearly basis and stored that data in a new column named 'Total_IT_Job_Openings_Mean'.
- Later I have dropped all the null values.
- Script also has code which will help us connect to cloud spanner table.
- In line 53 &54 I have given the cloud spanner instance name & database instance name respectively. 
- In line 60 I have given the table name.
- Rest of the script ensures the newly pre-processed and cleaned data is sent to the cloud spanner table.
- This script also created a DAG 'itjobs_data_to_spanner' which when triggered the itjobs.csv file is picked up from the bucket and loaded into dataframe, preprocessed, cleaned & then the data gets loaded into the cloud spanner table.

Once the setup is ready select the 'itcomposer' cloud composer instance and then go to 'Dags' and select 'itjobs_data_to_spanner' which was created by the dfp.py script.
Now on the top you can find the option Trigger dag, when you select it, let it run. Once the execution is completed you will find a green tick mark on the left section of All DAG runs. then you can go and check the cloud spanner table and data should be loaded into it.


## Load data from Cloud Spanner table to Bucket:

- Now we can load the cleaned data into a csv file in the bucket.
- We should go to Cloud Storage Bucket and create a new bucket, I have created a bucket named spannertostorage.
- Then navigate to [Dataflow Jobs](https://console.cloud.google.com/dataflow/jobs) in Google Cloud and select "Create Job from template".
- I gave the job name as stor, selected regional endpoint as “us-central1”.
- Selected dataflow template as "Cloud Spanner to Text Files on Cloud Storage"
- Then further options appear where I gave my Required Parameters.
- Spanner Table as "ittable12".
- Read data from Cloud Spanner Project Id as
- Read data from Cloud Spanner Instance as "itspanner".
- Read data from Cloud Spanner Database as "itdatabase12".
- Output file directory in Cloud Storage as
gs://spannertostorage/
- Temporary location as
gs://spannertostorage/temp/
- After giving all the above details you can leave the rest on default setting and select Run job.
- Then you can monitor the job to see if it succeeds, it takes a while for the job to be completed.
- Once its completed check the bucket for the file.

## Load the file from Cloud storage bucket to Big Query

### Create table in BigQuery
- For this first we have to create a dataset in BigQuery and then a table inside the dataset instance.
- You can create a dataset in multiple ways, I ran the following command in cloud shell "bq mk --dataset bqdataset". It created in a dataset named "bqdataset".
- Now run the following command to create a table
bq mk --table \
bqdataset.bqtable
- We don’t have to create a schema now itself, as we load the data we can create the schema for this table.

### Create a Dataflow Job
- I have then created a dataflow job to load the data from the file into the BigQuery table.
- For this we first need 2 files
- A json file which has the schema of the BigQuery table, containing details of column names and datatypes. I have used the "bq.json" file.
- A Javascript file which contains the information of which rows of the csv file will be loaded into the BigQuery table. I have used "udf.js" file.
- I have stored these two files in the same bucket where the csv file was created. The name of my csv file was "-00000-of-00001.csv".
- After placing all the files in the locations we have to go to the Dataflow jobs page and select "Create Job from template".
- Jobname is “storbq”
- For Regional endpoint I selected “us-central1”
- For dataflow template I selected "Text Files on Cloud Storage to BigQuery"
- For Cloud Storage Input File(s)
gs://spannertostorage/-00000-of-00001.csv
- For Cloud Storage location of your BigQuery schema file, described as a JSON
gs://spannertostorage/bq.json
- For BigQuery output table – term-project-420401:bqdataset.bqtable
- Temporary directory for BigQuery loading process
gs://spannertostorage/temp_dir/
- Temporary location
gs://spannertostorage/temp/
- In the Optional Parameters
- JavaScript UDF path in Cloud Storage
gs://spannertostorage/udf.js
- JavaScript UDF name is “udf.js”
- You can leave the rest of the parameters in their default setting and click on Run Job.
- Once the job runs successfully you can go to BigQuery and check if the data got loaded correctly.
