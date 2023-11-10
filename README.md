
# AWS Config Daily Reporter To JSON
 
The Config Daily Reporter solution can be used in order to generate a daily JSON report.
The report will include new or changed resources, gathering all the information about the resources to be processed through the Aardwolf Platform.
The reporter is triggered using a CloudWatch event, that will trigger a Lambda function. The Lambda will use S3 to create a file.


### Prerequisites
Before getting started, make sure that you have a basic understating of the following:
* Amazon EventBridge rule that runs on a schedule
* Multi-Account Multi-Region Data Aggregation
* AWS Lambda Function
* Python and Boto3.

You will also need to have a pre-configured Multi-Account AWS Config Aggregator and Amazon S3.


### Architecture
1. Amazon CloudWatch event - will trigger Lambda every day
2. AWS Lambda - will run Python3 code which includes an AWS Config Query and update a json file in S3 Bucket.
3. AWS Config - aggregator which will get a query from the Lambda function.
4. AWS S3 - will store the json data to be processed.


### Getting Started

1. ```git clone https://github.com/AbrictoSecurity/config-daily-json-to-S3-CF.git```
2. ```Create bucket: cdk-hnb659fds-assets-<Account_ID>-<Region_of_CF> [these is for supporting files]```
     a. Put the account id in the place of <Account_ID>
     b. Put the cloud formations region in the place of <Region_of_CF>
3. ```Upload supporting zips within the above created bucket. These will be found in Support folder.```
4. ```Create the bucket.```
5. ```Create an aggregator if you do not have one already established.```
6. ```Create new cloud formation stack , uploading the “Aardwolf_AWS_DailyConfig” file.```
7. ``` Input the parameters as follows:   ``` 
    * aggregator - Name of AWS Config Aggregator.
    * BUCKET_NAME - Name of the Bucket [these is to store the output of the service].
    * HOUR - The hour (UTC) the Lambda will run.
    * MINUTE - The minute (UTC) the Lambda will run.
8. Check S3 Bucket.
9. Configure cross account read access. 
      
* Create an IAM role in account to access bucket. (Within the reading organization account)
```
{
  "Version": "2012-10-17",
   "Statement": [
     {
      "Effect": "Allow",
       "Action": [
       "s3:GetObject",
       "s3:GetObjectVersion"
       ],
       "Resource": "arn:aws:s3:::<BUCKET>/*"

      }
    ]
} 
```

 * Configure Bucket policy. (Within the writing organization account)
   
 ```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<ReaderID>:role/<ROLENAME>"
            },
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
            "Resource": "arn:aws:s3:::<BUCKETNAME>/*"
        }
    ]
} 
```




## License
This library is licensed under the MIT-0 License. See the LICENSE file.

