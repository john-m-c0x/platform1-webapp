# AWS Setup Guide for Train Departures API

This guide will walk you through setting up the AWS serverless backend for the webapp. I did these steps through the AWS web console for clarity, but do what is comfortable.

## Prerequisites

Before starting, you'll need:
1. An AWS account with appropriate permissions
2. Your PTV API credentials (will be set as environment variables)
3. Basic understanding of AWS services (Lambda, DynamoDB, API Gateway)

## 1. Set Up DynamoDB Table

1. Go to the [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Click **Create table**
3. Enter the following details:
   - **Table name**: Choose a meaningful name for your table
   - **Partition key**: `id` (type: String)
4. Leave all other settings as default (On-demand capacity)
5. Click **Create table**

## 2. Create Lambda Layer for Dependencies

For a detailed video walkthrough of creating Lambda layers, see [this helpful tutorial](https://www.youtube.com/watch?v=grRW1Z_C9vw).

1. Go to the [Lambda Console](https://console.aws.amazon.com/lambda/)
2. Navigate to **Layers** in the left sidebar
3. Click **Create layer**
4. Enter the following details:
   - **Name**: Choose a meaningful name for your layer
   - **Description**: `Dependencies for Lambda functions`
5. Create the layer package:
   ```bash
   # Create a new folder on desktop
   mkdir lambda-layer
   cd lambda-layer

   # Create and activate virtual environment
   python -m venv myenv
   myenv/Scripts/activate  # On Windows
   # source myenv/bin/activate  # On Unix/Mac

   # Copy lambda_requirements.txt from the backend folder
   # Then install the requirements
   pip install -r lambda_requirements.txt

   # Create the required directory structure
   mkdir -p python/lib/python3.9/site-packages

   # Copy the installed packages
   # From myenv/Lib/site-packages to python/lib/python3.9/site-packages
   # Ensure you maintain the python/lib/python3.x/site-packages structure

   # Zip the folder containing the python directory
   # The zip should contain the 'python' folder at its root
   ```
6. Upload the ZIP file you created
7. Select compatible Python runtime version
8. Click **Create**
9. After creation, ensure each Lambda function has this layer added in its configuration

## 3. Create Fetcher Lambda Function

1. Go to the [Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click **Create function**
3. Choose **Author from scratch**
4. Enter the following details:
   - **Function name**: Choose a meaningful name
   - **Runtime**: Select your Python version
   - **Architecture**: x86_64
5. Click **Create function**
6. In the **Code** tab, upload the `fetch_departures_lambda.py` file
7. In the **Configuration** tab:
   - **General configuration**: Set appropriate timeout
   - **Environment variables**: Add your required environment variables (see .env.example)
   - **Permissions**: Configure appropriate DynamoDB write permissions
8. Add your Lambda layer

## 4. Create API Lambda Function

1. Go to the [Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click **Create function**
3. Choose **Author from scratch**
4. Configure similar to the fetcher function
5. Upload the `api_lambda.py` file
6. Configure environment variables and permissions
7. Add your Lambda layer

## 5. Set Up CloudWatch Events

1. Go to the [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
2. Navigate to **Events** > **Rules**
3. Create a rule for scheduled execution of your fetcher Lambda
4. Set appropriate rate/schedule
5. Add your Lambda as the target

## 6. Set Up API Gateway

1. Go to the [API Gateway Console](https://console.aws.amazon.com/apigateway/)
2. Create a new REST API
3. Configure your resources and methods
4. Enable CORS if needed
5. Deploy to a stage
6. Note your API endpoint URL

## 7. Frontend Configuration

Update your frontend environment variables with your API Gateway URL:

```javascript
// Your API URL should be configured in your environment variables
const API_URL = process.env.REACT_APP_API_GATEWAY_URL;

// Example React component setup
useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      setData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  fetchData();
  const interval = setInterval(fetchData, 60000);
  return () => clearInterval(interval);
}, []);
```

## 8. Security Best Practices

1. Use environment variables for all sensitive values
2. Configure appropriate IAM roles with least privilege
3. Enable CloudWatch logging
4. Set up appropriate CORS policies
5. Consider implementing rate limiting
6. Use appropriate authentication/authorization if needed

## 9. Testing Your Setup

1. Test your Lambda functions individually
2. Verify DynamoDB read/write operations
3. Test your API Gateway endpoint
4. Monitor CloudWatch logs for issues
5. Test your frontend integration

For detailed error messages and debugging, check CloudWatch logs for each Lambda function. 