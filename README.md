**Web scraping of  AAN Students profiles** 
=========================================

This is a separate python application(apart from drupal+plugins) to fetch the Avanti Alumni Networks's member details and to 
save in  Google Sheet which will be consumed by AAN Drupal Portal.
Script will web-scrape  configured number of profiles( 40 or less) at a time. 
There will be an intermediate control sheet used to in web-scraping all profiles.

### What is this repository for? ###

* Web Scrapping Avanti Alumni Network page member details from LinkedIn using Python Selenium
* v1.0

### How do I get set up? ###

* Python packages to be installed. 
  - pip install -U selenium
  - pip install pandas
  - pip install PyYAML
  - pip install pygsheets


* **Chromedriver** should be downloaded and moved to parent folder. 
* How to run Scripts
  - Understand Configs from `cfg.yml` and update as per your preference
  - Install Chrome in AWS Box Login to Linked In with credentials mentioned in `cfg.yml` to avoid security question check while python script logs in
  - In case of Timeout error, run script *headless = false*`(cfg.yml)` mode, check if LinkedIn introduced any question
  - In case of any other failure suspect, run script in local system
  - Date column of the *control-sheet* should be 'YYYY-MM-DD' format to match the standard we followed in Scripts
  - Run **`main.py`** once or multiple times in a day preferably max four times by Setting up a Cron in AWS
  - Path of Google sheet : 
    https://docs.google.com/spreadsheets/u/1/d/110ZfOH5yFWHhZvKuReQEnTj91oJZG0W9JgYpr2Udr8o/edit#gid=1563303323
    
* Deployment instructions
  - Start the cron service `sudo service crond start`
  - Edit the crontab file using `crontab -e`
  - Add the file path of the file you want to run.
    Hit the “i” key to start editing the file and then add `0 */1 * * * python path/to/file` . Make sure you give the full path to the python script that you want to run. 
  - Reference:  
    https://praneeth-kandula.medium.com/running-python-scripts-on-an-aws-ec2-instance-8c01f9ee7b2f
    

### Code upgrade guidelines ###
* Do test in IDE after code changes
* Configs should be at `cfg.yml` 
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
