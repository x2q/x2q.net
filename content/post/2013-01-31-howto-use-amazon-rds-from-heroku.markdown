---
categories:
- Heroku
- Amazon
- RDS
- rdscli
- Ubuntu
- Debian
comments: true
date: "2013-01-31T00:00:00Z"
title: Howto use Amazon RDS from Heroku
---

Heroku is quite popular for lightweight webservice and like projects. Until
recently Heroku only offered PostgreSQL-based database backend providers, but now Heroku
offers a quite large range of database backend providers; among them Amazon RDS.

This is a short run-down on how I managed to get a Heroku-based application to 
connect to a Amazon RDS-based database.

* Install the Amazon RDS command line tools
    
      $ sudo apt-get install rdscli

* Create a AWS Credential File (~/.aws/AwsCredentials.properties)

{% gist 4690345 %}

* Create a RDS db in the us-east region (if not run in this region, Heroku isn't able to connect to it)
       
       $ rds-create-db-instance --db-instance-identifier [name]\
         --allocated-storage 5 \
         --db-instance-class db.m1.small  \
         --engine MySQL5.1 \
         --master-username [user] \
         --master-user-password [pass] \
         --db-name [db-name] \
         --region us-east
         --headers \
         --aws-credential-file ~/.aws/AwsCredentials.properties

* Now authorize access from your public ip to the Amazon RDS instance

       $ rds-authorize-db-security-group-ingress default --cidr-ip 87.1.1.1/32 \
       --aws-credential-file ~/.aws/AwsCredentials.properties

* Test MySQL connectivy from your local machine to the Amazon RDS instance

       $ mysql -u root -p -h <your-amazon-rds-hostname>

* Now authorize access from the Heroku ip group ranges to the Amazon RDS instance

       $ rds-authorize-db-security-group-ingress --db-security-group-name default \
       --ec2-security-group-name default --ec2-security-group-owner-id 098166147350 \
       --aws-credential-file ~/.aws/AwsCredentials.properties

* Enabled the Amazon RDS plugin using the Heroku console toolbelt
    
      $ heroku addons:add amazon_rds url=mysql://<user>:<pass>@<your-amazon-rds-hostname>/<db-name>
